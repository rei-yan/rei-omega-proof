# REI-Ω v1.9.1 synchronized local runtime installer
# Windows / PowerShell. Safe-by-default: backups old scheduled-task definition and never touches canonical Git main.

param(
  [int]$IntervalMinutes = 60,
  [switch]$NoStart
)

$ErrorActionPreference = 'Stop'
$Root = 'C:\REI-Shadow'
$ShadowScript = 'C:\REI\rei_shadow_closed_loop_v2.py'
$BridgeScript = Join-Path $Root 'bridge_to_wheel.py'
$GitSyncScript = Join-Path $Root 'sync_shadow_to_github.py'
$Repo = Join-Path $Root 'repo'
$RuntimeRoot = Join-Path $Root 'runtime-v191'
$StateDir = Join-Path $RuntimeRoot 'state'
$CheckpointRoot = 'C:\REI_Resilience_Layer_v1\checkpoints'
$CycleScript = Join-Path $RuntimeRoot 'rei_cycle_v191.ps1'
$TaskName = 'REI Full Pipeline v1.9.1'
$OldTaskName = 'REI Shadow Closed Loop V2'
$OllamaWatchdog = 'REI-Local-Watchdog'
$ShadowWatchdog = 'REI Shadow Watchdog V1'

function Require-Path([string]$p) {
  if (-not (Test-Path $p)) { throw "Required path missing: $p" }
}

Require-Path $Root
Require-Path $ShadowScript
Require-Path $BridgeScript
Require-Path $GitSyncScript
Require-Path $Repo
New-Item -ItemType Directory -Force -Path $RuntimeRoot,$StateDir,$CheckpointRoot | Out-Null

# Backup existing task definition before disabling legacy direct-cycle task.
$legacyTask = Get-ScheduledTask -TaskName $OldTaskName -ErrorAction SilentlyContinue
if ($legacyTask) {
  $backupDir = Join-Path $RuntimeRoot 'task-backup'
  New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
  $xml = Export-ScheduledTask -TaskName $OldTaskName
  $xml | Set-Content -Encoding UTF8 (Join-Path $backupDir "$OldTaskName.xml")
  Disable-ScheduledTask -TaskName $OldTaskName | Out-Null
  Write-Host "Backed up and disabled legacy direct task: $OldTaskName" -ForegroundColor Yellow
}

$cycle = @'
param()
$ErrorActionPreference = 'Stop'
$Root = 'C:\REI-Shadow'
$ShadowScript = 'C:\REI\rei_shadow_closed_loop_v2.py'
$BridgeScript = Join-Path $Root 'bridge_to_wheel.py'
$GitSyncScript = Join-Path $Root 'sync_shadow_to_github.py'
$Repo = Join-Path $Root 'repo'
$RuntimeRoot = Join-Path $Root 'runtime-v191'
$StateDir = Join-Path $RuntimeRoot 'state'
$CheckpointRoot = 'C:\REI_Resilience_Layer_v1\checkpoints'
$Lock = Join-Path $RuntimeRoot 'cycle.lock'
$Log = Join-Path $RuntimeRoot 'runtime-v191.log'

function Log([string]$m) {
  $line = "$(Get-Date -Format o) $m"
  Add-Content -Encoding UTF8 $Log $line
  Write-Host $line
}
function FailClosed([string]$reason) {
  $state = [ordered]@{
    contract_version='1.9.1'; status='FAIL_CLOSED'; reason=$reason;
    observer_only=$true; promotion='NO'; reality_validated=$false;
    canonical_mainline_touched=$false; timestamp_utc=[DateTime]::UtcNow.ToString('o')
  }
  $state | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 (Join-Path $StateDir 'last-cycle.json')
  Log "FAIL-CLOSED: $reason"
  if (Test-Path $Lock) { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
  exit 2
}

New-Item -ItemType Directory -Force -Path $StateDir,$CheckpointRoot | Out-Null
if (Test-Path $Lock) { FailClosed 'Previous cycle lock still present; overlap prevented' }
New-Item -ItemType File -Path $Lock -Force | Out-Null

try {
  $epoch = 'rei-v191-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
  $cycleId = [Guid]::NewGuid().ToString('N')
  $schemaVersion = 'runtime-epoch-schema/1.0'
  $policyHash = 'v1.9.1-observer-policy'
  $compatSeed = "1.9.1|$schemaVersion|$policyHash|observer-only"
  $compatHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($compatSeed))).ToLower()
  Log "PREPARE epoch=$epoch cycle=$cycleId"

  # Local model / Ollama health and recovery start.
  $ollamaHealthy = $false
  try {
    $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3
    $ollamaHealthy = $true
  } catch {
    $ollama = Get-Command ollama.exe -ErrorAction SilentlyContinue
    if ($ollama) {
      Start-Process ollama.exe -ArgumentList 'serve' -WindowStyle Hidden | Out-Null
      Start-Sleep -Seconds 3
      try {
        $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 5
        $ollamaHealthy = $true
      } catch { $ollamaHealthy = $false }
    }
  }
  if (-not $ollamaHealthy) { FailClosed 'Ollama API unavailable' }
  $modelNames = @($tags.models | ForEach-Object { $_.name })
  if (-not ($modelNames | Where-Object { $_ -like 'rei-local-node*' })) {
    FailClosed 'rei-local-node model missing from Ollama'
  }

  # Checkpoint before mutation-producing cycle.
  $cp = Join-Path $CheckpointRoot $cycleId
  New-Item -ItemType Directory -Force -Path $cp | Out-Null
  foreach ($f in @('shadow_ledger.jsonl','divine_wheel_inbox.jsonl','bridge_to_wheel.py','sync_shadow_to_github.py')) {
    $src = Join-Path $Root $f
    if (Test-Path $src) { Copy-Item $src $cp -Force }
  }
  @{epoch_id=$epoch;cycle_id=$cycleId;compatibility_hash=$compatHash;created_utc=[DateTime]::UtcNow.ToString('o')} |
    ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $cp 'checkpoint.json')
  Log "SNAPSHOT checkpoint=$cp"

  # Main observer cycle.
  Log 'OBSERVE: Shadow cycle'
  & python $ShadowScript --home $Root --once
  if ($LASTEXITCODE -ne 0) { FailClosed "Shadow exited $LASTEXITCODE" }

  Log 'CROSS_CHECK: Bridge to God Wheel'
  & python $BridgeScript
  if ($LASTEXITCODE -ne 0) { FailClosed "Bridge exited $LASTEXITCODE" }

  Log 'LEDGER_COMMIT: GitHub sync'
  & python $GitSyncScript
  if ($LASTEXITCODE -ne 0) { FailClosed "Git sync exited $LASTEXITCODE" }

  # Runtime evidence.
  $shadowLedger = Join-Path $Root 'shadow_ledger.jsonl'
  $wheelInbox = Join-Path $Root 'divine_wheel_inbox.jsonl'
  if (-not (Test-Path $shadowLedger)) { FailClosed 'shadow_ledger.jsonl missing' }
  if (-not (Test-Path $wheelInbox)) { FailClosed 'divine_wheel_inbox.jsonl missing' }

  $ollamaWatchdog = Get-ScheduledTask -TaskName 'REI-Local-Watchdog' -ErrorAction SilentlyContinue
  if (-not $ollamaWatchdog) { FailClosed 'REI-Local-Watchdog scheduled task missing' }
  $shadowWatchdog = Get-ScheduledTask -TaskName 'REI Shadow Watchdog V1' -ErrorAction SilentlyContinue
  $recoveryReady = Test-Path 'C:\REI_Resilience_Layer_v1'
  if (-not $recoveryReady) { FailClosed 'Recovery root missing: C:\REI_Resilience_Layer_v1' }

  $components = @(
    @{id='god-wheel';version='REI-CLP/3.0-observer';heartbeat=(Test-Path $wheelInbox);healthcheck_passed=(Test-Path $wheelInbox)},
    @{id='local-model';version='rei-local-node-vnext';heartbeat=$ollamaHealthy;healthcheck_passed=$ollamaHealthy},
    @{id='shadow';version='Shadow V2.3+fusion';heartbeat=(Test-Path $shadowLedger);healthcheck_passed=$true},
    @{id='observer';version='vNext+Fusion-v1.9.1';heartbeat=$true;healthcheck_passed=$true},
    @{id='bridge';version='v1.9.1-contract';heartbeat=(Test-Path $BridgeScript);healthcheck_passed=$true},
    @{id='ledger';version='v1.9.1-contract';heartbeat=(Test-Path $shadowLedger);healthcheck_passed=$true},
    @{id='watchdog';version='v1.9.1-contract';heartbeat=($null -ne $ollamaWatchdog);healthcheck_passed=($null -ne $ollamaWatchdog)},
    @{id='recovery';version='v1.9.1-contract';heartbeat=$recoveryReady;healthcheck_passed=$recoveryReady},
    @{id='god-line';version='v1.9.1-contract';heartbeat=(Test-Path $wheelInbox);healthcheck_passed=$true}
  )

  $records = foreach ($c in $components) {
    [ordered]@{
      epoch_id=$epoch; cycle_id=$cycleId; component_id=$c.id; component_version=$c.version;
      schema_version=$schemaVersion; compatibility_hash=$compatHash; policy_hash=$policyHash;
      canonical_hash_seen='RUNTIME_OBSERVER_BRANCH'; checkpoint_id=$cycleId; rollback_id=$cycleId;
      observer_only=$true; promotion_capability=$false; heartbeat=[bool]$c.heartbeat;
      healthcheck_passed=[bool]$c.healthcheck_passed
    }
  }
  foreach ($r in $records) {
    $r | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $StateDir "$($r.component_id).json")
  }

  $bad = @($records | Where-Object {
    $_.epoch_id -ne $epoch -or $_.cycle_id -ne $cycleId -or
    $_.schema_version -ne $schemaVersion -or $_.compatibility_hash -ne $compatHash -or
    $_.policy_hash -ne $policyHash -or $_.observer_only -ne $true -or
    $_.promotion_capability -ne $false -or $_.heartbeat -ne $true -or
    $_.healthcheck_passed -ne $true
  })
  if ($bad.Count -gt 0) { FailClosed ('Runtime sync failed: ' + (($bad | ForEach-Object {$_.component_id}) -join ', ')) }

  $final = [ordered]@{
    contract_version='1.9.1'; epoch_id=$epoch; cycle_id=$cycleId;
    cycle_status='SUCCESS_RUNTIME_VERIFIED'; compatibility_hash=$compatHash;
    checkpoint_id=$cycleId; rollback_id=$cycleId; observer_only=$true;
    canonical_mainline_touched=$false; reality_validated=$false; promotion='NO';
    components=$records; finish_utc=[DateTime]::UtcNow.ToString('o')
  }
  $final | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 (Join-Path $StateDir 'last-cycle.json')
  Log 'WATCHDOG_CONFIRM -> RECOVERY_CONFIRM -> CYCLE_FINISH'
  Log 'Cycle finished: SUCCESS_RUNTIME_VERIFIED'
  Log 'RealityValidated = FALSE | Promotion = NO | canonical_mainline_touched = false'
}
catch {
  FailClosed $_.Exception.Message
}
finally {
  if (Test-Path $Lock) { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
}
'@

$cycle | Set-Content -Encoding UTF8 $CycleScript

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$CycleScript`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes ([Math]::Max(15,$IntervalMinutes-1)))
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null

Write-Host "Installed synchronized task: $TaskName (every $IntervalMinutes minutes)" -ForegroundColor Green
Write-Host "Cycle script: $CycleScript" -ForegroundColor Green
Write-Host "State: $StateDir\last-cycle.json" -ForegroundColor Green
Write-Host 'Legacy direct Shadow task is backed up/disabled to prevent double-running.' -ForegroundColor Yellow

if (-not $NoStart) {
  Start-ScheduledTask -TaskName $TaskName
  Write-Host 'Started first synchronized v1.9.1 local cycle.' -ForegroundColor Cyan
}

Write-Host 'Completion criterion: runtime-v191\state\last-cycle.json must show SUCCESS_RUNTIME_VERIFIED.' -ForegroundColor Cyan
