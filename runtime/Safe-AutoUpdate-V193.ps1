# REI-Ω v1.9.3 Safe Auto-Update Gate
# Reconciled updater with bounded local self-heal, exact merge-tree CI binding,
# checkpoint, canary, first-cycle verification and rollback.

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
$ActiveCycle = Join-Path $RuntimeRoot 'rei_cycle_v193.ps1'
$ActiveCanonicalGuard = Join-Path $RuntimeRoot 'REI-Canonical-Mainline-Observation-V1.ps1'
$SelfHeal = Join-Path $RuntimeRoot 'REI-Local-SelfHeal-V1.ps1'
$ActiveShaFile = Join-Path $RuntimeRoot 'deployed-sha.txt'
$ActiveCandidateHeadFile = Join-Path $RuntimeRoot 'deployed-candidate-head.txt'
$UpdaterState = Join-Path $UpdateDir 'last-update.json'
$UpdaterLog = Join-Path $UpdateDir 'safe-auto-update.log'
$PipelineTask = 'REI Full Pipeline v1.9.1'
$PrNumber = 28
$RemoteBranch = 'rei-v193-reconcile'
$RemoteRef = "origin/$RemoteBranch"
$PrMergeRef = "refs/rei/pr$PrNumber-merge"
$ValidatedStatusContext = 'rei/validated-merge-tree'
$GitHubApiBase = 'https://api.github.com/repos/rei-yan/rei-omega-proof'
$RecoveryRoot = 'C:\REI_Resilience_Layer_v1\autoupdate'
$candidate = ''
$previous = ''
$previousCandidateHead = ''
$checkpoint = ''
$script:ValidatedBaseSha = ''
$script:ValidatedMergeSha = ''

New-Item -ItemType Directory -Force -Path $UpdateDir,$StageDir,$RecoveryRoot | Out-Null

function Write-Log([string]$message) {
  $line = "$(Get-Date -Format o) $message"
  Add-Content -Encoding UTF8 -Path $UpdaterLog -Value $line
}
function Write-State([string]$status,[string]$candidateSha,[string]$previousSha,[string]$reason,[string]$checkpointPath='') {
  [ordered]@{
    version='1.9.3'; status=$status; candidate_head_sha=$candidateSha; previous_source_sha=$previousSha;
    validated_base_sha=$script:ValidatedBaseSha; validated_merge_sha=$script:ValidatedMergeSha;
    reason=$reason; checkpoint_path=$checkpointPath; observer_only=$true;
    candidate_branch=$RemoteBranch; active_runtime='rei_cycle_v193.ps1';
    self_heal_enabled=(Test-Path -LiteralPath $SelfHeal);
    canonical_mainline_write_permission=$false;
    canonical_mainline_observation='RUNTIME_CYCLE_REQUIRED';
    reality_validated=$false; promotion='NO';
    timestamp_utc=[DateTime]::UtcNow.ToString('o')
  } | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $UpdaterState
  Write-Log ("STATE " + $status + " candidate=" + $candidateSha + " source=" + $script:ValidatedMergeSha + " previous=" + $previousSha + " reason=" + $reason)
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
  $cmd = Get-Command git -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  foreach ($p in @('C:\Program Files\Git\cmd\git.exe','C:\Program Files\Git\bin\git.exe','C:\Program Files (x86)\Git\cmd\git.exe')) {
    if (Test-Path $p) { return $p }
  }
  throw 'git executable not found in PATH or standard Git locations'
}
function Get-CurrentSha {
  if (Test-Path $ActiveShaFile) { return (Get-Content $ActiveShaFile -Raw).Trim() }
  return ''
}
function Get-CurrentCandidateHead {
  if (Test-Path $ActiveCandidateHeadFile) { return (Get-Content $ActiveCandidateHeadFile -Raw).Trim() }
  return ''
}
function Invoke-SelfHeal([string]$Mode,[string]$sha) {
  if (-not (Test-Path -LiteralPath $SelfHeal)) {
    Write-Log 'Self-Heal not installed; continuing with updater gates only'
    return
  }
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $SelfHeal -Mode $Mode -DesiredSha $sha
  if ($LASTEXITCODE -ne 0) { throw "Local Self-Heal $Mode failed closed" }
  Write-Log "Self-Heal $Mode completed"
}
function Ensure-PipelineUsesV193 {
  $task = Get-ScheduledTask -TaskName $PipelineTask -ErrorAction SilentlyContinue
  if (-not $task) { throw "Pipeline task missing: $PipelineTask" }
  $xml = ''
  try { $xml = [string](Export-ScheduledTask -TaskName $PipelineTask) } catch {}
  if ($xml -match 'rei_cycle_v193\.ps1') { return }
  if ($task.State -eq 'Running') { throw 'Pipeline must be idle before runtime action migration' }
  $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ActiveCycle`""
  Set-ScheduledTask -TaskName $PipelineTask -Action $action | Out-Null
  Write-Log 'Pipeline action rebound to rei_cycle_v193.ps1'
}
function Require-HealthyCurrentRuntime {
  $last = Join-Path $StateDir 'last-cycle.json'
  if (-not (Test-Path $last)) { throw 'Current runtime evidence missing' }
  $obj = Get-Content $last -Raw | ConvertFrom-Json
  if ($obj.cycle_status -ne 'SUCCESS_RUNTIME_VERIFIED') {
    throw "Current runtime is not healthy: $($obj.status)$($obj.cycle_status) reason=$($obj.reason)"
  }
  foreach ($required in @('local-model','shadow','observer','bridge','ledger','watchdog','recovery','god-line')) {
    $component = @($obj.components | Where-Object { $_.component_id -eq $required })
    if (($component | Measure-Object).Count -eq 0 -or -not [bool]$component[0].heartbeat -or -not [bool]$component[0].healthcheck_passed) {
      throw "Current runtime component not verified: $required"
    }
  }
}
function Get-GitHubHeaders {
  try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch {}
  return @{ 'User-Agent'='REI-v1.9.3-safe-updater'; 'Accept'='application/vnd.github+json' }
}
function Resolve-CurrentValidatedMerge([string]$sha) {
  & $script:GitExe -C $Repo fetch origin main --quiet
  if ($LASTEXITCODE -ne 0) { return @{pass=$false;reason='Unable to fetch origin/main'} }
  & $script:GitExe -C $Repo fetch origin "+refs/pull/$PrNumber/merge`:$PrMergeRef" --quiet
  if ($LASTEXITCODE -ne 0) { return @{pass=$false;reason='Unable to fetch current PR merge ref'} }

  $currentMain = (& $script:GitExe -C $Repo rev-parse origin/main).Trim()
  $mergeSha = (& $script:GitExe -C $Repo rev-parse $PrMergeRef).Trim()
  if ($currentMain -notmatch '^[0-9a-fA-F]{40}$' -or $mergeSha -notmatch '^[0-9a-fA-F]{40}$') {
    return @{pass=$false;reason='Current main or merge SHA invalid'}
  }

  $parentLine = (& $script:GitExe -C $Repo rev-list --parents -n 1 $mergeSha).Trim()
  if ($LASTEXITCODE -ne 0) { return @{pass=$false;reason='Unable to inspect PR merge parents'} }
  $parents = @($parentLine -split '\s+')
  if ($parents.Count -ne 3) { return @{pass=$false;reason="PR merge is not exactly two-parent: $parentLine"} }
  $testedBase = [string]$parents[1]
  $testedHead = [string]$parents[2]

  if ($testedHead -ne $sha) {
    return @{pass=$false;reason="CI head mismatch: tested=$testedHead candidate=$sha"}
  }
  if ($testedBase -ne $currentMain) {
    return @{pass=$false;reason="CI base stale: tested=$testedBase current=$currentMain"}
  }

  try {
    $headers = Get-GitHubHeaders
    $statusUri = "$GitHubApiBase/commits/$mergeSha/status"
    $status = Invoke-RestMethod -Uri $statusUri -Headers $headers -TimeoutSec 20
    $bound = @($status.statuses | Where-Object {
      [string]$_.context -eq $ValidatedStatusContext -and [string]$_.state -eq 'success'
    } | Sort-Object created_at -Descending)
    if (($bound | Measure-Object).Count -eq 0) {
      return @{pass=$false;reason="Exact merge tree lacks success status context $ValidatedStatusContext"}
    }
  }
  catch { return @{pass=$false;reason=('Exact merge status query failed: ' + $_.Exception.Message)} }

  return @{pass=$true;reason='Exact current PR merge tree is bound to current main';merge_sha=$mergeSha;base_sha=$testedBase;head_sha=$testedHead}
}
function Require-CandidateCI([string]$sha) {
  try {
    $binding = Resolve-CurrentValidatedMerge $sha
    if (-not $binding.pass) { return $binding }

    $headers = Get-GitHubHeaders
    $suiteUri = "$GitHubApiBase/commits/$sha/check-suites?per_page=100"
    $suites = Invoke-RestMethod -Uri $suiteUri -Headers $headers -TimeoutSec 20
    $allSuites = @($suites.check_suites)
    if (($allSuites | Measure-Object).Count -eq 0) { return @{pass=$false;reason='Candidate check suites missing'} }
    $unfinished = @($allSuites | Where-Object { $_.status -ne 'completed' })
    if (($unfinished | Measure-Object).Count -gt 0) { return @{pass=$false;reason="Candidate CI unfinished=$(($unfinished | Measure-Object).Count)/$(($allSuites | Measure-Object).Count)"} }
    $badSuites = @($allSuites | Where-Object { $_.conclusion -ne 'success' })
    if (($badSuites | Measure-Object).Count -gt 0) {
      $summary = (($badSuites | ForEach-Object { [string]$_.conclusion }) -join ',')
      return @{pass=$false;reason="Candidate CI non-success suites=$(($badSuites | Measure-Object).Count): $summary"}
    }

    $runsUri = "$GitHubApiBase/actions/runs?head_sha=$sha&event=pull_request&per_page=100"
    $runs = Invoke-RestMethod -Uri $runsUri -Headers $headers -TimeoutSec 20
    $g2 = @($runs.workflow_runs | Where-Object { $_.name -eq 'G2 Lean Proof Gate' -and $_.head_sha -eq $sha } | Sort-Object run_number -Descending)
    if (($g2 | Measure-Object).Count -eq 0) { return @{pass=$false;reason='G2 run missing'} }
    if ($g2[0].status -ne 'completed') { return @{pass=$false;reason="G2 status=$($g2[0].status)"} }
    if ($g2[0].conclusion -ne 'success') { return @{pass=$false;reason="G2 conclusion=$($g2[0].conclusion)"} }
    $g2Base = ''
    try { $g2Base = [string]$g2[0].pull_requests[0].base.sha } catch {}
    if ([string]::IsNullOrWhiteSpace($g2Base)) { return @{pass=$false;reason='G2 base SHA unavailable'} }
    if ($g2Base -ne [string]$binding.base_sha) {
      return @{pass=$false;reason="G2 base stale: run=$g2Base current=$($binding.base_sha)"}
    }

    return @{
      pass=$true;
      reason="Exact merge tree $($binding.merge_sha) bound to base $($binding.base_sha); all $(($allSuites | Measure-Object).Count) head check suites success; G2 success on same base";
      merge_sha=[string]$binding.merge_sha;
      base_sha=[string]$binding.base_sha;
      head_sha=[string]$binding.head_sha
    }
  }
  catch { return @{pass=$false;reason=('Candidate CI query failed: ' + $_.Exception.Message)} }
}
function Stage-File([string]$sourceSha,[string]$repoPath,[string]$destination) {
  $content = & $script:GitExe -C $Repo show "$sourceSha`:$repoPath"
  if ($LASTEXITCODE -ne 0) { throw "Unable to stage $repoPath from $sourceSha" }
  $content | Set-Content -Encoding UTF8 $destination
}
function Test-PowerShellSyntax([string]$path) {
  $tokens = $null; $errors = $null
  [void][System.Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
  if (($errors | Measure-Object).Count -gt 0) { throw ('PowerShell syntax failed: ' + ($errors[0].Message)) }
}

Write-Log 'BEGIN safe auto-update check'
if (-not (Test-Path $Repo)) { throw "Repo missing: $Repo" }
if (-not (Test-Path $ActiveCycle)) { throw "Active v1.9.3 cycle missing: $ActiveCycle" }
if (-not (Get-ScheduledTask -TaskName $PipelineTask -ErrorAction SilentlyContinue)) { throw "Pipeline task missing: $PipelineTask" }
$script:GitExe = Resolve-GitExe
Write-Log ("Using git: " + $script:GitExe)

& $script:GitExe -C $Repo fetch origin $RemoteBranch --quiet
if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }
$candidate = (& $script:GitExe -C $Repo rev-parse $RemoteRef).Trim()
if ($LASTEXITCODE -ne 0 -or -not $candidate) { throw 'Cannot resolve candidate SHA' }
$previous = Get-CurrentSha
$previousCandidateHead = Get-CurrentCandidateHead
Write-Log ("Resolved candidate_head=" + $candidate + " previous_source=" + $previous + " previous_head=" + $previousCandidateHead)

Invoke-SelfHeal 'Preflight' $candidate
Ensure-PipelineUsesV193

try { Require-HealthyCurrentRuntime }
catch {
  Invoke-SelfHeal 'Normal' $candidate
  Write-State 'WAIT_SELFHEAL' $candidate $previous $_.Exception.Message
  exit 0
}

$ci = Require-CandidateCI $candidate
if (-not $ci.pass) { Write-State 'WAIT_CI' $candidate $previous $ci.reason; exit 0 }
$script:ValidatedBaseSha = [string]$ci.base_sha
$script:ValidatedMergeSha = [string]$ci.merge_sha
Write-Log ("Validated head=" + $candidate + " base=" + $script:ValidatedBaseSha + " merge=" + $script:ValidatedMergeSha)

if (-not $Force -and $script:ValidatedMergeSha -eq $previous -and $candidate -eq $previousCandidateHead) {
  Write-State 'NO_CHANGE' $candidate $previous 'Exact validated merge tree already active; self-heal preflight completed'
  exit 0
}

$task = Get-ScheduledTask -TaskName $PipelineTask
if ($task.State -eq 'Running') { Write-State 'WAIT_PIPELINE_IDLE' $candidate $previous 'Pipeline currently running'; exit 0 }

$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$checkpoint = Join-Path $RecoveryRoot "$stamp-$($script:ValidatedMergeSha.Substring(0,8))"
New-Item -ItemType Directory -Force -Path $checkpoint | Out-Null
Copy-Item $ActiveCycle (Join-Path $checkpoint 'rei_cycle_previous.ps1') -Force
if (Test-Path $ActiveCanonicalGuard) { Copy-Item $ActiveCanonicalGuard (Join-Path $checkpoint 'canonical-mainline-guard.previous.ps1') -Force }
if (Test-Path $ActiveShaFile) { Copy-Item $ActiveShaFile (Join-Path $checkpoint 'deployed-sha.previous.txt') -Force }
if (Test-Path $ActiveCandidateHeadFile) { Copy-Item $ActiveCandidateHeadFile (Join-Path $checkpoint 'deployed-candidate-head.previous.txt') -Force }
Export-ScheduledTask -TaskName $PipelineTask | Set-Content -Encoding UTF8 (Join-Path $checkpoint 'pipeline-task.xml')
Copy-Item (Join-Path $StateDir 'last-cycle.json') (Join-Path $checkpoint 'last-cycle.previous.json') -Force

$stagedCycle = Join-Path $StageDir "rei_cycle_v193-$($script:ValidatedMergeSha).ps1"
$stagedGuard = Join-Path $StageDir "canonical-mainline-guard-$($script:ValidatedMergeSha).ps1"
Stage-File $script:ValidatedMergeSha 'runtime/rei_cycle_v193.ps1' $stagedCycle
Stage-File $script:ValidatedMergeSha 'runtime/REI-Canonical-Mainline-Observation-V1.ps1' $stagedGuard
Test-PowerShellSyntax $stagedCycle
Test-PowerShellSyntax $stagedGuard

$probeA = '1111111111111111111111111111111111111111'
$probeB = '2222222222222222222222222222222222222222'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $stagedGuard -Mode Compare -BeforeSha $probeA -AfterSha $probeA
if ($LASTEXITCODE -ne 0) { Write-State 'CANARY_FAILED' $candidate $previous 'Canonical mainline guard unchanged control failed' $checkpoint; exit 2 }
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $stagedGuard -Mode Compare -BeforeSha $probeA -AfterSha $probeB *> $null
if ($LASTEXITCODE -eq 0) { Write-State 'CANARY_FAILED' $candidate $previous 'Canonical mainline guard mutation survived' $checkpoint; exit 2 }

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $stagedCycle -Canary
if ($LASTEXITCODE -ne 0) { Write-State 'CANARY_FAILED' $candidate $previous 'Staged runtime canary failed' $checkpoint; exit 2 }

try {
  Copy-Item $stagedGuard $ActiveCanonicalGuard -Force
  Copy-Item $stagedCycle $ActiveCycle -Force
  $script:ValidatedMergeSha | Set-Content -Encoding ASCII $ActiveShaFile
  $candidate | Set-Content -Encoding ASCII $ActiveCandidateHeadFile
  Ensure-PipelineUsesV193
  Start-ScheduledTask -TaskName $PipelineTask
  $deadline = (Get-Date).AddSeconds($VerifyTimeoutSeconds)
  $verified = $false
  $failureReason = 'Timed out waiting for first full cycle'

  while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 5
    $lastPath = Join-Path $StateDir 'last-cycle.json'
    if (-not (Test-Path $lastPath)) { continue }
    try { $last = Get-Content $lastPath -Raw | ConvertFrom-Json } catch { continue }
    if ($last.observer_source_sha -eq $script:ValidatedMergeSha) {
      if ($last.cycle_status -eq 'SUCCESS_RUNTIME_VERIFIED') {
        $bad = @($last.components | Where-Object {
          -not [bool]$_.heartbeat -or -not [bool]$_.healthcheck_passed -or
          [bool]$_.promotion_capability -ne $false -or [bool]$_.observer_only -ne $true
        })
        $requiredIds = @('god-wheel','local-model','shadow','observer','bridge','ledger','watchdog','recovery','god-line')
        $presentIds = @($last.components | ForEach-Object { [string]$_.component_id })
        $missingIds = @($requiredIds | Where-Object { $_ -notin $presentIds })
        $mainlineObserved = ([string]$last.canonical_mainline_observation_status -eq 'VERIFIED_UNCHANGED' -and [bool]$last.canonical_mainline_touched -eq $false)
        if (($bad | Measure-Object).Count -eq 0 -and ($missingIds | Measure-Object).Count -eq 0 -and [int]$last.candidate_pull_request -eq $PrNumber -and $mainlineObserved) {
          $verified = $true; break
        }
        $failureReason = 'First cycle component/mainline observation/authority/version check failed'; break
      }
      if ($last.status -eq 'FAIL_CLOSED') { $failureReason = "First cycle fail-closed: $($last.reason)"; break }
    }
  }

  if (-not $verified) { throw $failureReason }
  Invoke-SelfHeal 'Postflight' $candidate
  Write-State 'DEPLOYED_VERIFIED' $candidate $previous ($ci.reason + ' + exact-tree staging + guard mutation control + canary + first full synchronized cycle + observed mainline unchanged + self-heal postflight passed') $checkpoint
  exit 0
}
catch {
  $reason = $_.Exception.Message
  Copy-Item (Join-Path $checkpoint 'rei_cycle_previous.ps1') $ActiveCycle -Force
  $guardBackup = Join-Path $checkpoint 'canonical-mainline-guard.previous.ps1'
  if (Test-Path $guardBackup) { Copy-Item $guardBackup $ActiveCanonicalGuard -Force }
  elseif (Test-Path $ActiveCanonicalGuard) { Remove-Item $ActiveCanonicalGuard -Force }
  $prevShaBackup = Join-Path $checkpoint 'deployed-sha.previous.txt'
  if (Test-Path $prevShaBackup) { Copy-Item $prevShaBackup $ActiveShaFile -Force }
  elseif (Test-Path $ActiveShaFile) { Remove-Item $ActiveShaFile -Force }
  $prevHeadBackup = Join-Path $checkpoint 'deployed-candidate-head.previous.txt'
  if (Test-Path $prevHeadBackup) { Copy-Item $prevHeadBackup $ActiveCandidateHeadFile -Force }
  elseif (Test-Path $ActiveCandidateHeadFile) { Remove-Item $ActiveCandidateHeadFile -Force }
  $taskXmlPath = Join-Path $checkpoint 'pipeline-task.xml'
  if (Test-Path $taskXmlPath) {
    try { Register-ScheduledTask -TaskName $PipelineTask -Xml (Get-Content $taskXmlPath -Raw) -Force | Out-Null } catch {}
  }
  Start-ScheduledTask -TaskName $PipelineTask -ErrorAction SilentlyContinue
  Write-State 'ROLLED_BACK' $candidate $previous $reason $checkpoint
  exit 2
}
