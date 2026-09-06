<#
REI-Ω Local Self-Heal v1
Bounded, PowerShell 5.1-safe local repair layer for the reconciled v1.9.3 runtime.

Goals:
- one mutating scheduler only;
- automatically retire known legacy Shadow/sentinel writers;
- migrate a verified legacy persistent Shadow worker after backup;
- remove only orphaned lock files after process verification;
- repair PR28 context / vNext model drift;
- repair the persistent pipeline action to rei_cycle_v193.ps1;
- retry only known recoverable FAIL_CLOSED states;
- HOLD on unknown failures instead of escalating destructively.

Never writes canonical/main.
#>
[CmdletBinding()]
param(
  [ValidateSet('Normal','Preflight','Postflight')][string]$Mode = 'Normal',
  [string]$DesiredSha = '',
  [ValidateRange(15,1440)][int]$PipelineIntervalMinutes = 60,
  [ValidateRange(5,120)][int]$CooldownMinutes = 15
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = 'C:\REI-Shadow'
$Core = 'C:\REI'
$RuntimeRoot = Join-Path $Root 'runtime-v191'
$RuntimeCycle = Join-Path $RuntimeRoot 'rei_cycle_v193.ps1'
$StateRoot = Join-Path $Root 'state\selfheal'
$ReportPath = Join-Path $StateRoot 'latest.json'
$HistoryPath = Join-Path $StateRoot 'history.jsonl'
$LastActionPath = Join-Path $StateRoot 'last-action.json'
$PipelineTask = 'REI Full Pipeline v1.9.1'
$WatchdogTask = 'REI-Local-Watchdog'
$AutoUpdateTask = 'REI Safe Auto Update v1.9.3'
$ContextState = Join-Path $Root 'context\sync_state.json'
$ContextSync = Join-Path $Root 'REI-LocalSync.ps1'
$LocalModel = Join-Path $Root 'REI-LocalModel-VNext.ps1'
$ShadowScript = Join-Path $Core 'rei_shadow_closed_loop_v2.py'
$CycleLock = Join-Path $RuntimeRoot 'cycle.lock'
$ShadowLocks = @(
  (Join-Path $Root 'state\resilience\runtime.lock'),
  (Join-Path $Core 'state\resilience\runtime.lock')
)
$LegacyTaskNames = @(
  'REI Runtime Continuity Guard v1',
  'REI Runtime Sentinel v1',
  'REI Shadow Closed Loop V2',
  'REI Shadow Watchdog V1',
  'REI Unattended Closed Loop'
)
$KnownRecoverable = 'Shadow exited 1|runtime\.lock|cycle\.lock|overlap prevented|observer.*missing|God Line observer bundle failed|Context is not pinned|vNext local model refresh not verified'

New-Item -ItemType Directory -Force -Path $StateRoot | Out-Null
$actions = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]
$backupDir = Join-Path $Root ('backups\selfheal-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Count-Items($Items) { return [int](($Items | Measure-Object).Count) }
function Read-JsonSafe([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return $null }
  try { return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json) } catch { return $null }
}
function Write-JsonAtomic([string]$Path,[object]$Value) {
  $dir = Split-Path -Parent $Path
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $tmp = Join-Path $dir ([IO.Path]::GetRandomFileName())
  $Value | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $tmp -Encoding UTF8
  Move-Item -LiteralPath $tmp -Destination $Path -Force
}
function Append-Jsonl([string]$Path,[object]$Value) {
  $line = $Value | ConvertTo-Json -Depth 14 -Compress
  Add-Content -LiteralPath $Path -Value $line -Encoding UTF8
}
function Backup-State {
  if (Test-Path -LiteralPath $backupDir) { return }
  New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
  foreach ($p in @(
    (Join-Path $Root 'state'),
    (Join-Path $Root 'context'),
    (Join-Path $RuntimeRoot 'state'),
    (Join-Path $Core 'state')
  )) {
    if (Test-Path -LiteralPath $p) {
      $name = (($p -replace ':','') -replace '[\\/]','_')
      Copy-Item -LiteralPath $p -Destination (Join-Path $backupDir $name) -Recurse -Force -ErrorAction SilentlyContinue
    }
  }
}
function Get-TaskXml([string]$Name) {
  try { return [string](Export-ScheduledTask -TaskName $Name -ErrorAction Stop) } catch { return '' }
}
function Get-ShadowProcesses {
  try {
    return @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
      $_.Name -match '^(python|pythonw)(\.exe)?$' -and $_.CommandLine -and
      $_.CommandLine -match 'rei_shadow_closed_loop_v2\.py'
    })
  } catch { return @() }
}
function Get-CycleProcesses {
  try {
    return @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
      $_.Name -match '^(powershell|pwsh)(\.exe)?$' -and $_.CommandLine -and
      $_.CommandLine -match 'rei_cycle_v19(1|3)\.ps1'
    })
  } catch { return @() }
}
function Disable-KnownLegacyTasks {
  foreach ($name in $LegacyTaskNames) {
    $task = Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
    if (-not $task) { continue }
    Backup-State
    try { Export-ScheduledTask -TaskName $name | Set-Content -Encoding UTF8 (Join-Path $backupDir (($name -replace '[^A-Za-z0-9._-]','_') + '.xml')) } catch {}
    Stop-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
    Disable-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue | Out-Null
    $actions.Add("disabled_legacy_task:$name") | Out-Null
  }

  # REI-Supervisor is touched only if its exported XML explicitly points at a legacy writer.
  $supervisor = Get-ScheduledTask -TaskName 'REI-Supervisor' -ErrorAction SilentlyContinue
  if ($supervisor) {
    $xml = Get-TaskXml 'REI-Supervisor'
    if ($xml -match 'rei_shadow_closed_loop_v2\.py|rei_cycle_v191\.ps1|runtime_sentinel') {
      Backup-State
      try { $xml | Set-Content -Encoding UTF8 (Join-Path $backupDir 'REI-Supervisor.xml') } catch {}
      Stop-ScheduledTask -TaskName 'REI-Supervisor' -ErrorAction SilentlyContinue
      Disable-ScheduledTask -TaskName 'REI-Supervisor' -ErrorAction SilentlyContinue | Out-Null
      $actions.Add('disabled_legacy_task:REI-Supervisor') | Out-Null
    }
  }
}
function Migrate-LegacyShadowWorker {
  $procs = @(Get-ShadowProcesses)
  $persistent = @($procs | Where-Object { $_.CommandLine -notmatch '(?:^|\s)--once(?:\s|$)' })
  foreach ($proc in $persistent) {
    $cmd = [string]$proc.CommandLine
    if ($cmd -notmatch 'C:\\REI\\rei_shadow_closed_loop_v2\.py') {
      $warnings.Add("unknown_persistent_shadow_pid:$($proc.ProcessId)") | Out-Null
      continue
    }
    Backup-State
    Stop-Process -Id ([int]$proc.ProcessId) -Force -ErrorAction Stop
    $actions.Add("migrated_legacy_shadow_pid:$($proc.ProcessId)") | Out-Null
  }
}
function Clear-OrphanLocks {
  if ((Count-Items (Get-ShadowProcesses)) -eq 0) {
    foreach ($lock in $ShadowLocks) {
      if (Test-Path -LiteralPath $lock) {
        Backup-State
        Copy-Item -LiteralPath $lock -Destination (Join-Path $backupDir ((Split-Path $lock -Leaf) + '.' + [Math]::Abs($lock.GetHashCode()))) -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $lock -Force -ErrorAction Stop
        $actions.Add("removed_orphan_shadow_lock:$lock") | Out-Null
      }
    }
  }
  if ((Count-Items (Get-CycleProcesses)) -eq 0 -and (Test-Path -LiteralPath $CycleLock)) {
    Backup-State
    Copy-Item -LiteralPath $CycleLock -Destination (Join-Path $backupDir 'cycle.lock') -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $CycleLock -Force -ErrorAction Stop
    $actions.Add('removed_orphan_cycle_lock') | Out-Null
  }
}
function Ensure-ContextAndModel {
  $ctx = Read-JsonSafe $ContextState
  $contextOk = ($null -ne $ctx -and [int]$ctx.pull_request -eq 28 -and [string]$ctx.head_ref -eq 'rei-v193-reconcile' -and -not [string]::IsNullOrWhiteSpace([string]$ctx.head_sha))
  if (-not $contextOk) {
    if (-not (Test-Path -LiteralPath $ContextSync)) { throw 'REI-LocalSync.ps1 missing' }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ContextSync -Once -PullRequest 28 -ContextOnly
    if ($LASTEXITCODE -ne 0) { throw 'PR28 context self-heal failed' }
    $actions.Add('repaired_pr28_context') | Out-Null
    $ctx = Read-JsonSafe $ContextState
  }
  if ($DesiredSha -and $ctx -and [string]$ctx.head_sha -ne $DesiredSha) {
    $warnings.Add("context_sha_differs_from_desired:$([string]$ctx.head_sha):$DesiredSha") | Out-Null
  }

  $modelOk = $false
  try {
    $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 5
    $modelOk = [bool](@($tags.models | ForEach-Object { $_.name }) | Where-Object { $_ -like 'rei-local-node-vnext*' })
  } catch { $modelOk = $false }
  if (-not $modelOk) {
    if (-not (Test-Path -LiteralPath $LocalModel)) { throw 'REI-LocalModel-VNext.ps1 missing' }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $LocalModel -ContextDir (Join-Path $Root 'context')
    if ($LASTEXITCODE -ne 0) { throw 'rei-local-node-vnext self-heal failed' }
    $actions.Add('rebuilt_rei_local_node_vnext') | Out-Null
  }
}
function Ensure-PipelineAction {
  if (-not (Test-Path -LiteralPath $RuntimeCycle)) { throw "v1.9.3 runtime missing: $RuntimeCycle" }
  $task = Get-ScheduledTask -TaskName $PipelineTask -ErrorAction SilentlyContinue
  if ($task) {
    $xml = Get-TaskXml $PipelineTask
    if ($xml -match 'rei_cycle_v193\.ps1') { return }
    if ($task.State -eq 'Running') { $warnings.Add('pipeline_action_old_but_task_running') | Out-Null; return }
    Backup-State
    try { $xml | Set-Content -Encoding UTF8 (Join-Path $backupDir 'pipeline-before-selfheal.xml') } catch {}
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$RuntimeCycle`""
    Set-ScheduledTask -TaskName $PipelineTask -Action $action | Out-Null
    $actions.Add('rebound_pipeline_to_rei_cycle_v193') | Out-Null
    return
  }

  $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
  $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$RuntimeCycle`""
  $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes($PipelineIntervalMinutes) -RepetitionInterval (New-TimeSpan -Minutes $PipelineIntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
  $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes ([Math]::Max(15,$PipelineIntervalMinutes-1))) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
  $principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Highest
  Register-ScheduledTask -TaskName $PipelineTask -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'REI reconciled synchronized pipeline; stable authority task; runtime engine may advance by verified updates.' | Out-Null
  $actions.Add('created_authoritative_pipeline_task') | Out-Null
}
function Can-RetryNow {
  $lastAction = Read-JsonSafe $LastActionPath
  if ($null -eq $lastAction -or [string]::IsNullOrWhiteSpace([string]$lastAction.timestamp_utc)) { return $true }
  try {
    $when = [DateTime]::Parse([string]$lastAction.timestamp_utc).ToUniversalTime()
    return (([DateTime]::UtcNow - $when).TotalMinutes -ge $CooldownMinutes)
  } catch { return $true }
}
function Retry-RecoverableFailure {
  $last = Read-JsonSafe (Join-Path $RuntimeRoot 'state\last-cycle.json')
  if ($null -eq $last -or [string]$last.status -ne 'FAIL_CLOSED') { return }
  $reason = [string]$last.reason
  if ($reason -notmatch $KnownRecoverable) {
    $warnings.Add("unknown_fail_closed_hold:$reason") | Out-Null
    return
  }
  if (-not (Can-RetryNow)) { $warnings.Add('recoverable_failure_in_cooldown') | Out-Null; return }
  $task = Get-ScheduledTask -TaskName $PipelineTask -ErrorAction SilentlyContinue
  if (-not $task -or $task.State -eq 'Running' -or (Count-Items (Get-CycleProcesses)) -gt 0) { return }
  Write-JsonAtomic $LastActionPath ([ordered]@{action='retry_recoverable_cycle';reason=$reason;timestamp_utc=[DateTime]::UtcNow.ToString('o')})
  Start-ScheduledTask -TaskName $PipelineTask
  $actions.Add("retried_recoverable_fail_closed:$reason") | Out-Null
}

$status = 'SELFHEAL_OK'
$reason = 'No repair required'
try {
  Disable-KnownLegacyTasks
  Migrate-LegacyShadowWorker
  Start-Sleep -Seconds 2
  Clear-OrphanLocks
  Ensure-ContextAndModel
  Ensure-PipelineAction
  if ($Mode -ne 'Preflight') { Retry-RecoverableFailure }
  if ((Count-Items $actions) -gt 0) { $status = 'SELFHEAL_REPAIRED'; $reason = ($actions -join '; ') }
  if ((Count-Items $warnings) -gt 0 -and $status -eq 'SELFHEAL_OK') { $status = 'SELFHEAL_HOLD'; $reason = ($warnings -join '; ') }
}
catch {
  $status = 'SELFHEAL_FAILED_CLOSED'
  $reason = $_.Exception.Message
}

$report = [ordered]@{
  schema_version=1; mode=$Mode; status=$status; reason=$reason;
  actions=@($actions); warnings=@($warnings); desired_sha=$DesiredSha;
  pipeline_task=$PipelineTask; pipeline_engine=$RuntimeCycle;
  canonical_write_permission=$false; reality_validated=$false; ascension_granted=$false;
  backup_path=$(if(Test-Path -LiteralPath $backupDir){$backupDir}else{''});
  timestamp_utc=[DateTime]::UtcNow.ToString('o')
}
Write-JsonAtomic $ReportPath $report
Append-Jsonl $HistoryPath $report
Write-Host "REI_SELFHEAL_STATUS=$status" -ForegroundColor $(if($status -eq 'SELFHEAL_FAILED_CLOSED'){'Red'}elseif($status -eq 'SELFHEAL_HOLD'){'Yellow'}else{'Green'})
Write-Host "REI_SELFHEAL_REASON=$reason"
Write-Host "REI_SELFHEAL_REPORT=$ReportPath" -ForegroundColor Cyan
if ($status -eq 'SELFHEAL_FAILED_CLOSED') { exit 2 }
exit 0
