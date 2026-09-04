# REI-Ω v1.9.3 Safe Auto-Update Gate
# Polls the reconciled candidate branch, requires complete successful candidate CI,
# stages/canaries, checkpoints, atomically switches the local cycle, verifies one
# full synchronized cycle, and rolls back on failure.

param(
  [switch]$Force,
  [int]$VerifyTimeoutSeconds = 300
)

$ErrorActionPreference = 'Stop'
$Repo = 'C:\REI-Shadow\repo'
$RuntimeRoot = 'C:\REI-Shadow\runtime-v191'
$StateDir = Join-Path $RuntimeRoot 'state'
$UpdateDir = Join-Path $RuntimeRoot 'autoupdate'
$StageDir = Join-Path $UpdateDir 'stage'
$ActiveCycle = Join-Path $RuntimeRoot 'rei_cycle_v191.ps1'
$ActiveShaFile = Join-Path $RuntimeRoot 'deployed-sha.txt'
$UpdaterState = Join-Path $UpdateDir 'last-update.json'
$UpdaterLog = Join-Path $UpdateDir 'safe-auto-update.log'
$PipelineTask = 'REI Full Pipeline v1.9.1'
$RemoteBranch = 'rei-v193-reconcile'
$RemoteRef = "origin/$RemoteBranch"
$GitHubApiBase = 'https://api.github.com/repos/rei-yan/rei-omega-proof'
$RecoveryRoot = 'C:\REI_Resilience_Layer_v1\autoupdate'
$candidate = ''
$previous = ''
$checkpoint = ''

New-Item -ItemType Directory -Force -Path $UpdateDir,$StageDir,$RecoveryRoot | Out-Null

function Write-Log([string]$message) {
  $line = "$(Get-Date -Format o) $message"
  Add-Content -Encoding UTF8 -Path $UpdaterLog -Value $line
}

function Write-State([string]$status,[string]$candidateSha,[string]$previousSha,[string]$reason,[string]$checkpointPath='') {
  [ordered]@{
    version='1.9.3'; status=$status; candidate_sha=$candidateSha; previous_sha=$previousSha;
    reason=$reason; checkpoint_path=$checkpointPath; observer_only=$true;
    candidate_branch=$RemoteBranch; reality_validated=$false; promotion='NO';
    canonical_mainline_touched=$false; timestamp_utc=[DateTime]::UtcNow.ToString('o')
  } | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $UpdaterState
  Write-Log ("STATE " + $status + " candidate=" + $candidateSha + " previous=" + $previousSha + " reason=" + $reason)
}

trap {
  $msg = $_.Exception.Message
  try { Write-State 'UPDATER_FAILED' $candidate $previous $msg $checkpoint } catch {}
  try { Write-Log ("UNHANDLED " + $msg) } catch {}
  exit 2
}

function Resolve-GitExe {
  $cmd = Get-Command git.exe -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  foreach ($p in @('C:\Program Files\Git\cmd\git.exe','C:\Program Files\Git\bin\git.exe','C:\Program Files (x86)\Git\cmd\git.exe')) {
    if (Test-Path $p) { return $p }
  }
  throw 'git.exe not found in PATH or standard Git for Windows locations'
}

function Get-CurrentSha {
  if (Test-Path $ActiveShaFile) { return (Get-Content $ActiveShaFile -Raw).Trim() }
  return ''
}

function Require-HealthyCurrentRuntime {
  $last = Join-Path $StateDir 'last-cycle.json'
  if (-not (Test-Path $last)) { throw 'Current runtime evidence missing' }
  $obj = Get-Content $last -Raw | ConvertFrom-Json
  if ($obj.cycle_status -ne 'SUCCESS_RUNTIME_VERIFIED') {
    throw "Current runtime is not healthy: $($obj.status)$($obj.cycle_status)"
  }
  foreach ($required in @('local-model','shadow','observer','bridge','ledger','watchdog','recovery','god-line')) {
    $component = @($obj.components | Where-Object { $_.component_id -eq $required })
    if ($component.Count -eq 0 -or -not [bool]$component[0].heartbeat -or -not [bool]$component[0].healthcheck_passed) {
      throw "Current runtime component not verified: $required"
    }
  }
}

function Get-GitHubHeaders {
  try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch {}
  return @{ 'User-Agent'='REI-v1.9.3-safe-updater'; 'Accept'='application/vnd.github+json' }
}

function Require-CandidateCI([string]$sha) {
  try {
    $headers = Get-GitHubHeaders

    # First require every GitHub Actions check suite attached to the exact candidate SHA
    # to be completed/success. This prevents deployment while a broader regression gate
    # is still queued, running, cancelled, or failed.
    $suiteUri = "$GitHubApiBase/commits/$sha/check-suites?per_page=100"
    $suites = Invoke-RestMethod -Uri $suiteUri -Headers $headers -TimeoutSec 20
    $allSuites = @($suites.check_suites)
    if ($allSuites.Count -eq 0) { return @{pass=$false;reason='Candidate check suites missing'} }
    $unfinished = @($allSuites | Where-Object { $_.status -ne 'completed' })
    if ($unfinished.Count -gt 0) { return @{pass=$false;reason="Candidate CI unfinished=$($unfinished.Count)/$($allSuites.Count)"} }
    $badSuites = @($allSuites | Where-Object { $_.conclusion -ne 'success' })
    if ($badSuites.Count -gt 0) {
      $summary = (($badSuites | ForEach-Object { [string]$_.conclusion }) -join ',')
      return @{pass=$false;reason="Candidate CI non-success suites=$($badSuites.Count): $summary"}
    }

    # Preserve an explicit G2 proof-gate check instead of assuming suite success alone
    # identifies the proof workflow.
    $runsUri = "$GitHubApiBase/actions/runs?head_sha=$sha&event=pull_request&per_page=100"
    $runs = Invoke-RestMethod -Uri $runsUri -Headers $headers -TimeoutSec 20
    $g2 = @($runs.workflow_runs | Where-Object { $_.name -eq 'G2 Lean Proof Gate' -and $_.head_sha -eq $sha } | Sort-Object run_number -Descending)
    if ($g2.Count -eq 0) { return @{pass=$false;reason='G2 run missing'} }
    if ($g2[0].status -ne 'completed') { return @{pass=$false;reason="G2 status=$($g2[0].status)"} }
    if ($g2[0].conclusion -ne 'success') { return @{pass=$false;reason="G2 conclusion=$($g2[0].conclusion)"} }

    return @{pass=$true;reason="All $($allSuites.Count) check suites completed/success + G2 completed/success"}
  }
  catch {
    return @{pass=$false;reason=('Candidate CI query failed: ' + $_.Exception.Message)}
  }
}

function Stage-File([string]$repoPath,[string]$destination) {
  $content = & $script:GitExe -C $Repo show "$RemoteRef`:$repoPath"
  if ($LASTEXITCODE -ne 0) { throw "Unable to stage $repoPath" }
  $content | Set-Content -Encoding UTF8 $destination
}

function Test-PowerShellSyntax([string]$path) {
  $tokens = $null
  $errors = $null
  [void][System.Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
  if ($errors.Count -gt 0) { throw ('PowerShell syntax failed: ' + ($errors[0].Message)) }
}

Write-Log 'BEGIN safe auto-update check'
if (-not (Test-Path $Repo)) { throw "Repo missing: $Repo" }
if (-not (Test-Path $ActiveCycle)) { throw "Active cycle missing: $ActiveCycle" }
if (-not (Get-ScheduledTask -TaskName $PipelineTask -ErrorAction SilentlyContinue)) { throw "Pipeline task missing: $PipelineTask" }

$script:GitExe = Resolve-GitExe
Write-Log ("Using git: " + $script:GitExe)

& $script:GitExe -C $Repo fetch origin $RemoteBranch --quiet
if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }
$candidate = (& $script:GitExe -C $Repo rev-parse $RemoteRef).Trim()
if ($LASTEXITCODE -ne 0 -or -not $candidate) { throw 'Cannot resolve candidate SHA' }
$previous = Get-CurrentSha
Write-Log ("Resolved candidate=" + $candidate + " previous=" + $previous)

if (-not $Force -and $candidate -eq $previous) {
  Write-State 'NO_CHANGE' $candidate $previous 'Candidate already active'
  exit 0
}

Require-HealthyCurrentRuntime
$ci = Require-CandidateCI $candidate
if (-not $ci.pass) {
  Write-State 'WAIT_CI' $candidate $previous $ci.reason
  exit 0
}

$task = Get-ScheduledTask -TaskName $PipelineTask
if ($task.State -eq 'Running') {
  Write-State 'WAIT_PIPELINE_IDLE' $candidate $previous 'Pipeline currently running'
  exit 0
}

$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$checkpoint = Join-Path $RecoveryRoot "$stamp-$($candidate.Substring(0,8))"
New-Item -ItemType Directory -Force -Path $checkpoint | Out-Null
Copy-Item $ActiveCycle (Join-Path $checkpoint 'rei_cycle_previous.ps1') -Force
if (Test-Path $ActiveShaFile) { Copy-Item $ActiveShaFile (Join-Path $checkpoint 'deployed-sha.previous.txt') -Force }
Export-ScheduledTask -TaskName $PipelineTask | Set-Content -Encoding UTF8 (Join-Path $checkpoint 'pipeline-task.xml')
Copy-Item (Join-Path $StateDir 'last-cycle.json') (Join-Path $checkpoint 'last-cycle.previous.json') -Force

$stagedCycle = Join-Path $StageDir "rei_cycle_v193-$candidate.ps1"
Stage-File 'runtime/rei_cycle_v193.ps1' $stagedCycle
Test-PowerShellSyntax $stagedCycle

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $stagedCycle -Canary
if ($LASTEXITCODE -ne 0) {
  Write-State 'CANARY_FAILED' $candidate $previous 'Staged runtime canary failed' $checkpoint
  exit 2
}

try {
  Copy-Item $stagedCycle $ActiveCycle -Force
  $candidate | Set-Content -Encoding ASCII $ActiveShaFile

  Start-ScheduledTask -TaskName $PipelineTask
  $deadline = (Get-Date).AddSeconds($VerifyTimeoutSeconds)
  $verified = $false
  $failureReason = 'Timed out waiting for first full cycle'

  while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 5
    $lastPath = Join-Path $StateDir 'last-cycle.json'
    if (-not (Test-Path $lastPath)) { continue }
    try { $last = Get-Content $lastPath -Raw | ConvertFrom-Json } catch { continue }

    if ($last.observer_source_sha -eq $candidate) {
      if ($last.cycle_status -eq 'SUCCESS_RUNTIME_VERIFIED') {
        $bad = @($last.components | Where-Object {
          -not [bool]$_.heartbeat -or -not [bool]$_.healthcheck_passed -or
          [bool]$_.promotion_capability -ne $false -or [bool]$_.observer_only -ne $true
        })
        $requiredIds = @('god-wheel','local-model','shadow','observer','bridge','ledger','watchdog','recovery','god-line')
        $presentIds = @($last.components | ForEach-Object { [string]$_.component_id })
        $missingIds = @($requiredIds | Where-Object { $_ -notin $presentIds })
        if ($bad.Count -eq 0 -and $missingIds.Count -eq 0 -and [int]$last.candidate_pull_request -eq 28) {
          $verified = $true
          break
        }
        $failureReason = 'First cycle component health/authority/version check failed'
        break
      }
      if ($last.status -eq 'FAIL_CLOSED') {
        $failureReason = "First cycle fail-closed: $($last.reason)"
        break
      }
    }
  }

  if (-not $verified) { throw $failureReason }
  Write-State 'DEPLOYED_VERIFIED' $candidate $previous ($ci.reason + ' + canary + first full synchronized cycle passed') $checkpoint
  exit 0
}
catch {
  $reason = $_.Exception.Message
  Copy-Item (Join-Path $checkpoint 'rei_cycle_previous.ps1') $ActiveCycle -Force
  $prevShaBackup = Join-Path $checkpoint 'deployed-sha.previous.txt'
  if (Test-Path $prevShaBackup) {
    Copy-Item $prevShaBackup $ActiveShaFile -Force
  } elseif (Test-Path $ActiveShaFile) {
    Remove-Item $ActiveShaFile -Force
  }
  Start-ScheduledTask -TaskName $PipelineTask -ErrorAction SilentlyContinue
  Write-State 'ROLLED_BACK' $candidate $previous $reason $checkpoint
  exit 2
}
