<#
REI-Ω Continuous Reality Guard v1

Purpose:
- prove that the reconciled Windows runtime is actually alive over time;
- distinguish process/task presence from fresh successful cycles;
- request bounded recovery when the authoritative pipeline becomes stale;
- keep rolling 24h / 72h / 7d host evidence;
- accept reality-feedback artifacts as evidence inputs without treating them as truth or promotion authority.

This guard is defensive only. It never writes canonical/main and never grants
RealityValidated, promotion, or ascension.
#>
[CmdletBinding()]
param(
  [string]$ContractPath = 'C:\REI-Shadow\runtime-v191\continuous-reality-contract-v1.json'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'C:\REI-Shadow'
$RuntimeRoot = Join-Path $Root 'runtime-v191'
$CycleState = Join-Path $RuntimeRoot 'state\last-cycle.json'
$ContextState = Join-Path $Root 'context\sync_state.json'
$SelfHealState = Join-Path $Root 'state\selfheal\latest.json'
$GuardStateRoot = Join-Path $Root 'state\continuous-reality'
$LatestPath = Join-Path $GuardStateRoot 'latest.json'
$HistoryPath = Join-Path $GuardStateRoot 'history.jsonl'
$RecoveryStampPath = Join-Path $GuardStateRoot 'last-recovery.json'
$PipelineTask = 'REI Full Pipeline v1.9.1'
$SelfHealTask = 'REI Local Self Heal v1'

New-Item -ItemType Directory -Force -Path $GuardStateRoot | Out-Null

function Read-JsonSafe([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return $null }
  try { return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}

function Write-JsonAtomic([string]$Path,[object]$Value) {
  $dir = Split-Path -Parent $Path
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $tmp = Join-Path $dir ([IO.Path]::GetRandomFileName())
  $Value | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath $tmp -Encoding UTF8
  Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function Append-Jsonl([string]$Path,[object]$Value) {
  $line = $Value | ConvertTo-Json -Depth 16 -Compress
  Add-Content -LiteralPath $Path -Value $line -Encoding UTF8
}

function Has-Property([object]$Object,[string]$Name) {
  if ($null -eq $Object) { return $false }
  return [bool]($Object.PSObject.Properties.Name -contains $Name)
}

function Get-TaskSnapshot([string]$Name) {
  $task = Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue
  if (-not $task) {
    return [ordered]@{ name=$Name; exists=$false; enabled=$false; state='MISSING'; last_run_utc=''; last_result=$null }
  }
  $info = $null
  try { $info = Get-ScheduledTaskInfo -TaskName $Name -ErrorAction Stop } catch {}
  $lastRun = ''
  $lastResult = $null
  if ($info) {
    try {
      if ($info.LastRunTime -and $info.LastRunTime.Year -gt 2000) { $lastRun = $info.LastRunTime.ToUniversalTime().ToString('o') }
    } catch {}
    try { $lastResult = [int64]$info.LastTaskResult } catch {}
  }
  return [ordered]@{
    name=$Name; exists=$true; enabled=([string]$task.State -ne 'Disabled'); state=[string]$task.State;
    last_run_utc=$lastRun; last_result=$lastResult
  }
}

function Get-CycleStatus([object]$Cycle) {
  if ($null -eq $Cycle) { return 'MISSING' }
  if (Has-Property $Cycle 'cycle_status') { return [string]$Cycle.cycle_status }
  if (Has-Property $Cycle 'status') { return [string]$Cycle.status }
  return 'UNKNOWN'
}

function Get-CycleTimestamp([object]$Cycle) {
  if ($null -eq $Cycle) { return $null }
  foreach ($name in @('finish_utc','timestamp_utc','created_utc')) {
    if (Has-Property $Cycle $name) {
      $raw = [string]$Cycle.$name
      if (-not [string]::IsNullOrWhiteSpace($raw)) {
        try { return [DateTime]::Parse($raw).ToUniversalTime() } catch {}
      }
    }
  }
  return $null
}

function Test-RequiredComponents([object]$Cycle,[string[]]$Required) {
  $found = @{}
  if ($Cycle -and (Has-Property $Cycle 'components') -and $Cycle.components) {
    foreach ($component in @($Cycle.components)) {
      $id = ''
      if (Has-Property $component 'component_id') { $id = [string]$component.component_id }
      elseif (Has-Property $component 'id') { $id = [string]$component.id }
      if (-not [string]::IsNullOrWhiteSpace($id)) { $found[$id] = $component }
    }
  }
  $missing = New-Object System.Collections.Generic.List[string]
  $bad = New-Object System.Collections.Generic.List[string]
  foreach ($id in $Required) {
    if (-not $found.ContainsKey($id)) { $missing.Add($id) | Out-Null; continue }
    $component = $found[$id]
    $heartbeat = $false
    $healthcheck = $false
    try { $heartbeat = [bool]$component.heartbeat } catch {}
    try { $healthcheck = [bool]$component.healthcheck_passed } catch {}
    if (-not ($heartbeat -and $healthcheck)) { $bad.Add($id) | Out-Null }
  }
  return [ordered]@{ healthy=($missing.Count -eq 0 -and $bad.Count -eq 0); missing=@($missing); unhealthy=@($bad) }
}

function Get-RealityFeedbackSummary([object]$Contract) {
  $inbox = [string]$Contract.reality_feedback.inbox
  $required = @($Contract.reality_feedback.required_fields | ForEach-Object { [string]$_ })
  $validTypes = @($Contract.reality_feedback.valid_source_types | ForEach-Object { [string]$_ })
  $valid = 0
  $invalid = 0
  $latest = $null
  if (Test-Path -LiteralPath $inbox) {
    foreach ($file in @(Get-ChildItem -LiteralPath $inbox -Filter '*.json' -File -ErrorAction SilentlyContinue)) {
      $item = Read-JsonSafe $file.FullName
      if ($null -eq $item) { $invalid++; continue }
      $ok = $true
      foreach ($field in $required) {
        if (-not (Has-Property $item $field) -or [string]::IsNullOrWhiteSpace([string]$item.$field)) { $ok = $false; break }
      }
      if ($ok -and ($validTypes -notcontains [string]$item.source_type)) { $ok = $false }
      $when = $null
      if ($ok) {
        try { $when = [DateTime]::Parse([string]$item.observed_at_utc).ToUniversalTime() } catch { $ok = $false }
      }
      if ($ok) {
        $valid++
        if ($null -eq $latest -or $when -gt $latest) { $latest = $when }
      } else { $invalid++ }
    }
  }
  return [ordered]@{
    inbox=$inbox; valid_artifacts=$valid; invalid_artifacts=$invalid;
    latest_observed_utc=$(if($latest){$latest.ToString('o')}else{''});
    feedback_present=($valid -gt 0); reality_validated=$false; promotion_authority=$false
  }
}

function Test-RecoveryCooldown([int]$Minutes) {
  $stamp = Read-JsonSafe $RecoveryStampPath
  if ($null -eq $stamp -or -not (Has-Property $stamp 'timestamp_utc')) { return $true }
  try {
    $when = [DateTime]::Parse([string]$stamp.timestamp_utc).ToUniversalTime()
    return (([DateTime]::UtcNow - $when).TotalMinutes -ge $Minutes)
  } catch { return $true }
}

function Save-RecoveryStamp([string]$Action,[string]$Reason) {
  Write-JsonAtomic $RecoveryStampPath ([ordered]@{ action=$Action; reason=$Reason; timestamp_utc=[DateTime]::UtcNow.ToString('o') })
}

function Get-RollingStability([object]$Contract) {
  $records = New-Object System.Collections.Generic.List[object]
  if (Test-Path -LiteralPath $HistoryPath) {
    foreach ($line in @(Get-Content -LiteralPath $HistoryPath -Tail 5000 -Encoding UTF8 -ErrorAction SilentlyContinue)) {
      if ([string]::IsNullOrWhiteSpace($line)) { continue }
      try { $records.Add(($line | ConvertFrom-Json)) | Out-Null } catch {}
    }
  }
  $now = [DateTime]::UtcNow
  $results = [ordered]@{}
  foreach ($hoursValue in @($Contract.stability_windows_hours)) {
    $hours = [int]$hoursValue
    $cutoff = $now.AddHours(-$hours)
    $window = @($records | Where-Object {
      try { [DateTime]::Parse([string]$_.timestamp_utc).ToUniversalTime() -ge $cutoff } catch { $false }
    } | Sort-Object { [DateTime]::Parse([string]$_.timestamp_utc) })
    $healthy = @($window | Where-Object { [string]$_.status -eq 'HEALTHY' }).Count
    $ratio = if ($window.Count -gt 0) { [Math]::Round($healthy / [double]$window.Count, 6) } else { 0.0 }
    $coverage = 0.0
    $maxGap = 0.0
    if ($window.Count -gt 1) {
      $first = [DateTime]::Parse([string]$window[0].timestamp_utc).ToUniversalTime()
      $last = [DateTime]::Parse([string]$window[$window.Count-1].timestamp_utc).ToUniversalTime()
      $coverage = [Math]::Round(($last - $first).TotalHours, 3)
      for ($i=1; $i -lt $window.Count; $i++) {
        $a = [DateTime]::Parse([string]$window[$i-1].timestamp_utc).ToUniversalTime()
        $b = [DateTime]::Parse([string]$window[$i].timestamp_utc).ToUniversalTime()
        $gap = ($b - $a).TotalMinutes
        if ($gap -gt $maxGap) { $maxGap = $gap }
      }
    }
    $cycleIds = @($window | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_.cycle_id) -and [string]$_.cycle_status -eq 'SUCCESS_RUNTIME_VERIFIED' } | ForEach-Object { [string]$_.cycle_id } | Sort-Object -Unique)
    $holds = @($window | Where-Object { [string]$_.status -eq 'HOLD_UNKNOWN' }).Count
    $touches = @($window | Where-Object { [bool]$_.canonical_mainline_touched }).Count
    $results["h$hours"] = [ordered]@{
      samples=$window.Count; healthy_samples=$healthy; health_sample_ratio=$ratio;
      coverage_hours=$coverage; max_guard_gap_minutes=[Math]::Round($maxGap,3);
      unique_successful_cycles=$cycleIds.Count; unknown_hold_samples=$holds; canonical_touch_samples=$touches
    }
  }
  return $results
}

if (-not (Test-Path -LiteralPath $ContractPath)) {
  $failure = [ordered]@{
    schema_version=1; contract_id='REI-CRL/1.0'; status='HOLD_UNKNOWN'; reason='continuous reality contract missing';
    canonical_mainline_touched=$false; reality_validated=$false; promotion='NO'; ascension='NO';
    timestamp_utc=[DateTime]::UtcNow.ToString('o')
  }
  Append-Jsonl $HistoryPath $failure
  Write-JsonAtomic $LatestPath $failure
  Write-Host 'REI_CONTINUOUS_REALITY=HOLD_UNKNOWN' -ForegroundColor Yellow
  exit 2
}

$contract = Read-JsonSafe $ContractPath
if ($null -eq $contract) { throw 'continuous reality contract is invalid JSON' }

$requiredComponents = @($contract.required_components | ForEach-Object { [string]$_ })
$requiredTasks = @($contract.required_tasks | ForEach-Object { [string]$_ })
$staleAfter = [int]$contract.stale_after_minutes
$cooldown = [int]$contract.recovery_cooldown_minutes
$now = [DateTime]::UtcNow
$actions = New-Object System.Collections.Generic.List[string]
$problems = New-Object System.Collections.Generic.List[string]

$cycle = Read-JsonSafe $CycleState
$cycleStatus = Get-CycleStatus $cycle
$cycleWhen = Get-CycleTimestamp $cycle
$cycleAge = if ($cycleWhen) { [Math]::Round(($now - $cycleWhen).TotalMinutes,3) } else { 999999.0 }
$cycleId = if ($cycle -and (Has-Property $cycle 'cycle_id')) { [string]$cycle.cycle_id } else { '' }
$components = Test-RequiredComponents $cycle $requiredComponents

$context = Read-JsonSafe $ContextState
$contextOk = $false
if ($context) {
  try {
    $contextOk = ([int]$context.pull_request -eq [int]$contract.candidate_pull_request -and
                  [string]$context.head_ref -eq [string]$contract.candidate_head_ref -and
                  -not [string]::IsNullOrWhiteSpace([string]$context.head_sha))
  } catch { $contextOk = $false }
}

$taskSnapshots = @()
foreach ($name in $requiredTasks) { $taskSnapshots += (Get-TaskSnapshot $name) }
$pipeline = @($taskSnapshots | Where-Object { [string]$_.name -eq $PipelineTask })[0]
$selfHeal = @($taskSnapshots | Where-Object { [string]$_.name -eq $SelfHealTask })[0]

foreach ($task in $taskSnapshots) {
  if (-not [bool]$task.exists) { $problems.Add("task_missing:$([string]$task.name)") | Out-Null }
  elseif (-not [bool]$task.enabled) { $problems.Add("task_disabled:$([string]$task.name)") | Out-Null }
}

$canonicalTouched = $false
$observerOnly = $false
$candidateOk = $false
if ($cycle) {
  try { $canonicalTouched = [bool]$cycle.canonical_mainline_touched } catch {}
  try { $observerOnly = [bool]$cycle.observer_only } catch {}
  try {
    $candidateOk = ([int]$cycle.candidate_pull_request -eq [int]$contract.candidate_pull_request -and
                    [string]$cycle.candidate_head_ref -eq [string]$contract.candidate_head_ref)
  } catch { $candidateOk = $false }
}

if ($cycleStatus -ne 'SUCCESS_RUNTIME_VERIFIED') { $problems.Add("cycle_status:$cycleStatus") | Out-Null }
if ($cycleAge -gt $staleAfter) { $problems.Add("cycle_stale_minutes:$cycleAge") | Out-Null }
if (-not [bool]$components.healthy) { $problems.Add('component_set_unhealthy') | Out-Null }
if (-not $contextOk) { $problems.Add('context_not_pr28_reconciled') | Out-Null }
if (-not $candidateOk) { $problems.Add('cycle_candidate_mismatch') | Out-Null }
if (-not $observerOnly) { $problems.Add('observer_only_boundary_missing') | Out-Null }
if ($canonicalTouched) { $problems.Add('canonical_mainline_touched') | Out-Null }

# Defensive recovery only. Unknown failures are held rather than rewritten.
$knownRecoverable = ($cycleStatus -eq 'MISSING' -or $cycleStatus -eq 'SUCCESS_RUNTIME_VERIFIED' -or $cycleStatus -eq 'FAIL_CLOSED')
$canRecover = Test-RecoveryCooldown $cooldown
if ($canRecover) {
  foreach ($task in $taskSnapshots) {
    if ([bool]$task.exists -and -not [bool]$task.enabled) {
      try {
        Enable-ScheduledTask -TaskName ([string]$task.name) -ErrorAction Stop | Out-Null
        $actions.Add("enabled_task:$([string]$task.name)") | Out-Null
        Save-RecoveryStamp 'enable_known_task' ([string]$task.name)
        $canRecover = $false
        break
      } catch { $problems.Add("enable_failed:$([string]$task.name):$($_.Exception.Message)") | Out-Null }
    }
  }
}

if ($canRecover -and $knownRecoverable -and ($cycleAge -gt $staleAfter -or $cycleStatus -eq 'FAIL_CLOSED' -or $cycleStatus -eq 'MISSING')) {
  if ($selfHeal -and [bool]$selfHeal.exists -and [bool]$selfHeal.enabled -and [string]$selfHeal.state -ne 'Running') {
    try {
      Start-ScheduledTask -TaskName $SelfHealTask -ErrorAction Stop
      $actions.Add('requested_self_heal') | Out-Null
      Save-RecoveryStamp 'request_self_heal' "cycle=$cycleStatus age=$cycleAge"
      $canRecover = $false
    } catch { $problems.Add("selfheal_start_failed:$($_.Exception.Message)") | Out-Null }
  }
}

if ($canRecover -and $knownRecoverable -and $cycleAge -gt $staleAfter -and $pipeline -and [bool]$pipeline.exists -and [bool]$pipeline.enabled -and [string]$pipeline.state -ne 'Running') {
  $interactiveUser = ''
  try { $interactiveUser = [string](Get-CimInstance Win32_ComputerSystem -ErrorAction Stop).UserName } catch {}
  if (-not [string]::IsNullOrWhiteSpace($interactiveUser)) {
    try {
      Start-ScheduledTask -TaskName $PipelineTask -ErrorAction Stop
      $actions.Add('requested_pipeline_cycle') | Out-Null
      Save-RecoveryStamp 'start_known_task' "stale=$cycleAge user=$interactiveUser"
      $canRecover = $false
    } catch { $problems.Add("pipeline_start_failed:$($_.Exception.Message)") | Out-Null }
  } else {
    $problems.Add('stale_pipeline_no_interactive_user') | Out-Null
  }
}

$reality = Get-RealityFeedbackSummary $contract

$status = 'HEALTHY'
$reason = 'fresh synchronized runtime evidence present'
if ($canonicalTouched) {
  $status = 'HOLD_UNKNOWN'; $reason = 'canonical mainline touch detected; automatic action prohibited'
} elseif (-not $knownRecoverable) {
  $status = 'HOLD_UNKNOWN'; $reason = "unknown cycle state: $cycleStatus"
} elseif ($actions.Count -gt 0) {
  $status = 'RECOVERY_REQUESTED'; $reason = ($actions -join '; ')
} elseif ($problems.Count -gt 0) {
  $status = 'DEGRADED'; $reason = ($problems -join '; ')
}

$record = [ordered]@{
  schema_version=1; contract_id=[string]$contract.contract_id; status=$status; reason=$reason;
  cycle_status=$cycleStatus; cycle_id=$cycleId; cycle_age_minutes=$cycleAge;
  component_set_healthy=[bool]$components.healthy; missing_components=@($components.missing); unhealthy_components=@($components.unhealthy);
  context_reconciled=$contextOk; candidate_cycle_match=$candidateOk; observer_only=$observerOnly;
  tasks=$taskSnapshots; actions=@($actions); problems=@($problems); reality_feedback=$reality;
  canonical_mainline_touched=$canonicalTouched; canonical_write_permission=$false;
  reality_validated=$false; promotion='NO'; ascension='NO';
  timestamp_utc=$now.ToString('o')
}

Append-Jsonl $HistoryPath $record
$stability = Get-RollingStability $contract
$h72 = $stability.h72
$threshold = $contract.stability_72h
$maxAllowedGap = [Math]::Max(20.0, ([double]$contract.guard_interval_minutes * 3.0))
$stable72 = $false
if ($h72) {
  $stable72 = (
    [double]$h72.coverage_hours -ge [double]$threshold.minimum_coverage_hours -and
    [double]$h72.health_sample_ratio -ge [double]$threshold.minimum_health_sample_ratio -and
    [int]$h72.unique_successful_cycles -ge [int]$threshold.minimum_unique_successful_cycles -and
    [int]$h72.unknown_hold_samples -le [int]$threshold.maximum_unknown_hold_samples -and
    [int]$h72.canonical_touch_samples -le [int]$threshold.maximum_canonical_touch_samples -and
    [double]$h72.max_guard_gap_minutes -le $maxAllowedGap -and
    $status -eq 'HEALTHY'
  )
}

$latest = [ordered]@{
  schema_version=1; contract_id=[string]$contract.contract_id; status=$status; reason=$reason;
  cycle_status=$cycleStatus; cycle_id=$cycleId; cycle_age_minutes=$cycleAge;
  component_set_healthy=[bool]$components.healthy; context_reconciled=$contextOk; candidate_cycle_match=$candidateOk;
  tasks=$taskSnapshots; actions=@($actions); problems=@($problems); reality_feedback=$reality;
  rolling_stability=$stability; stability_72h_verified=$stable72;
  stability_72h_rule="coverage>=$([double]$threshold.minimum_coverage_hours)h; health_ratio>=$([double]$threshold.minimum_health_sample_ratio); cycles>=$([int]$threshold.minimum_unique_successful_cycles); max_guard_gap<=$maxAllowedGap min";
  canonical_mainline_touched=$canonicalTouched; canonical_write_permission=$false;
  reality_validated=$false; promotion='NO'; ascension='NO';
  timestamp_utc=$now.ToString('o')
}
Write-JsonAtomic $LatestPath $latest

$color = if ($status -eq 'HEALTHY') { 'Green' } elseif ($status -eq 'RECOVERY_REQUESTED') { 'Cyan' } elseif ($status -eq 'DEGRADED') { 'Yellow' } else { 'Red' }
Write-Host "REI_CONTINUOUS_REALITY=$status" -ForegroundColor $color
Write-Host "Cycle=$cycleStatus age_minutes=$cycleAge components=$([bool]$components.healthy) stable72=$stable72" -ForegroundColor $color
Write-Host "Evidence=$LatestPath" -ForegroundColor Cyan

if ($status -eq 'HOLD_UNKNOWN') { exit 2 }
if ($status -eq 'DEGRADED') { exit 1 }
exit 0
