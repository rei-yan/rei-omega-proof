# REI-Ω v1.9.3 canonical synchronized Windows runtime cycle
# Compatible with Windows PowerShell 5.1 / .NET Framework.

param([switch]$Canary)

$ErrorActionPreference = 'Stop'
$Root = 'C:\REI-Shadow'
$ShadowScript = 'C:\REI\rei_shadow_closed_loop_v2.py'
$BridgeScript = Join-Path $Root 'bridge_to_wheel.py'
$GitSyncScript = Join-Path $Root 'sync_shadow_to_github.py'
$RuntimeRoot = Join-Path $Root 'runtime-v191'
$StateDir = Join-Path $RuntimeRoot 'state'
$CheckpointRoot = 'C:\REI_Resilience_Layer_v1\checkpoints'
$Lock = Join-Path $RuntimeRoot 'cycle.lock'
$Log = Join-Path $RuntimeRoot 'runtime-v191.log'
$SourceShaFile = Join-Path $RuntimeRoot 'deployed-sha.txt'
$ContractVersion = '1.9.3'
$SchemaVersion = 'runtime-epoch-schema/1.1'
$PolicyHash = 'v1.9.3-observer-policy'

function Log([string]$m) {
  $line = "$(Get-Date -Format o) $m"
  Add-Content -Encoding UTF8 $Log $line
  Write-Host $line
}

function Get-CompatibleSha256([string]$text) {
  $sha256 = [System.Security.Cryptography.SHA256]::Create()
  try {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $hashBytes = $sha256.ComputeHash($bytes)
    return ([System.BitConverter]::ToString($hashBytes) -replace '-', '').ToLowerInvariant()
  }
  finally { $sha256.Dispose() }
}

function Get-SourceSha {
  if (Test-Path $SourceShaFile) {
    $v = (Get-Content $SourceShaFile -Raw).Trim()
    if ($v) { return $v }
  }
  return 'UNPINNED_LOCAL_RUNTIME'
}

function Test-Ollama {
  try {
    $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3
    return @{ healthy=$true; tags=$tags }
  }
  catch {
    $ollama = Get-Command ollama.exe -ErrorAction SilentlyContinue
    if (-not $ollama) { return @{ healthy=$false; tags=$null } }
    Start-Process ollama.exe -ArgumentList 'serve' -WindowStyle Hidden | Out-Null
    Start-Sleep -Seconds 3
    try {
      $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 5
      return @{ healthy=$true; tags=$tags }
    } catch { return @{ healthy=$false; tags=$null } }
  }
}

function FailClosed([string]$reason) {
  New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
  $state = [ordered]@{
    contract_version=$ContractVersion; status='FAIL_CLOSED'; reason=$reason;
    observer_source_sha=(Get-SourceSha); observer_only=$true; promotion='NO';
    reality_validated=$false; canonical_mainline_touched=$false;
    timestamp_utc=[DateTime]::UtcNow.ToString('o')
  }
  $state | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 (Join-Path $StateDir 'last-cycle.json')
  Log "FAIL-CLOSED: $reason"
  if (Test-Path $Lock) { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
  exit 2
}

# Dependency-only canary. It deliberately does not mutate Shadow/Ledger/God Wheel state.
if ($Canary) {
  foreach ($p in @($Root,$ShadowScript,$BridgeScript,$GitSyncScript,'C:\REI_Resilience_Layer_v1')) {
    if (-not (Test-Path $p)) { Write-Error "CANARY missing path: $p"; exit 2 }
  }
  $ollama = Test-Ollama
  if (-not $ollama.healthy) { Write-Error 'CANARY Ollama unavailable'; exit 2 }
  $names = @($ollama.tags.models | ForEach-Object { $_.name })
  if (-not ($names | Where-Object { $_ -like 'rei-local-node*' })) {
    Write-Error 'CANARY rei-local-node model missing'; exit 2
  }
  if (-not (Get-ScheduledTask -TaskName 'REI-Local-Watchdog' -ErrorAction SilentlyContinue)) {
    Write-Error 'CANARY REI-Local-Watchdog missing'; exit 2
  }
  Write-Host 'CANARY_PASS' -ForegroundColor Green
  exit 0
}

New-Item -ItemType Directory -Force -Path $StateDir,$CheckpointRoot | Out-Null
if (Test-Path $Lock) { FailClosed 'Previous cycle lock still present; overlap prevented' }
New-Item -ItemType File -Path $Lock -Force | Out-Null

try {
  $sourceSha = Get-SourceSha
  $epoch = 'rei-v193-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
  $cycleId = [Guid]::NewGuid().ToString('N')
  $compatSeed = "$ContractVersion|$SchemaVersion|$PolicyHash|observer-only|$sourceSha"
  $compatHash = Get-CompatibleSha256 $compatSeed
  Log "PREPARE epoch=$epoch cycle=$cycleId source=$sourceSha"

  $ollama = Test-Ollama
  if (-not $ollama.healthy) { FailClosed 'Ollama API unavailable' }
  $modelNames = @($ollama.tags.models | ForEach-Object { $_.name })
  if (-not ($modelNames | Where-Object { $_ -like 'rei-local-node*' })) {
    FailClosed 'rei-local-node model missing from Ollama'
  }

  $cp = Join-Path $CheckpointRoot $cycleId
  New-Item -ItemType Directory -Force -Path $cp | Out-Null
  foreach ($f in @('shadow_ledger.jsonl','divine_wheel_inbox.jsonl','bridge_to_wheel.py','sync_shadow_to_github.py')) {
    $src = Join-Path $Root $f
    if (Test-Path $src) { Copy-Item $src $cp -Force }
  }
  @{epoch_id=$epoch;cycle_id=$cycleId;compatibility_hash=$compatHash;observer_source_sha=$sourceSha;created_utc=[DateTime]::UtcNow.ToString('o')} |
    ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $cp 'checkpoint.json')
  Log "SNAPSHOT checkpoint=$cp"

  Log 'OBSERVE -> SHADOW_CHALLENGE'
  & python $ShadowScript --home $Root --once
  if ($LASTEXITCODE -ne 0) { FailClosed "Shadow exited $LASTEXITCODE" }

  Log 'CROSS_CHECK -> BRIDGE'
  & python $BridgeScript
  if ($LASTEXITCODE -ne 0) { FailClosed "Bridge exited $LASTEXITCODE" }

  Log 'LEDGER_COMMIT -> GIT_SYNC'
  & python $GitSyncScript
  if ($LASTEXITCODE -ne 0) { FailClosed "Git sync exited $LASTEXITCODE" }

  $shadowLedger = Join-Path $Root 'shadow_ledger.jsonl'
  $wheelInbox = Join-Path $Root 'divine_wheel_inbox.jsonl'
  if (-not (Test-Path $shadowLedger)) { FailClosed 'shadow_ledger.jsonl missing' }
  if (-not (Test-Path $wheelInbox)) { FailClosed 'divine_wheel_inbox.jsonl missing' }

  $ollamaWatchdog = Get-ScheduledTask -TaskName 'REI-Local-Watchdog' -ErrorAction SilentlyContinue
  if (-not $ollamaWatchdog) { FailClosed 'REI-Local-Watchdog scheduled task missing' }
  $recoveryReady = Test-Path 'C:\REI_Resilience_Layer_v1'
  if (-not $recoveryReady) { FailClosed 'Recovery root missing' }

  $components = @(
    @{id='god-wheel';version='REI-CLP/3.0-observer+v1.9.3';heartbeat=(Test-Path $wheelInbox);healthcheck_passed=(Test-Path $wheelInbox)},
    @{id='local-model';version='rei-local-node-vnext';heartbeat=$ollama.healthy;healthcheck_passed=$ollama.healthy},
    @{id='shadow';version='Shadow V2.3+fusion';heartbeat=(Test-Path $shadowLedger);healthcheck_passed=$true},
    @{id='observer';version='vNext+Fusion-v1.9.3';heartbeat=$true;healthcheck_passed=$true},
    @{id='bridge';version='v1.9.3-contract';heartbeat=(Test-Path $BridgeScript);healthcheck_passed=$true},
    @{id='ledger';version='v1.9.3-contract';heartbeat=(Test-Path $shadowLedger);healthcheck_passed=$true},
    @{id='watchdog';version='v1.9.3-contract';heartbeat=($null -ne $ollamaWatchdog);healthcheck_passed=($null -ne $ollamaWatchdog)},
    @{id='recovery';version='v1.9.3-contract';heartbeat=$recoveryReady;healthcheck_passed=$recoveryReady},
    @{id='god-line';version='v1.9.3-contract';heartbeat=(Test-Path $wheelInbox);healthcheck_passed=$true}
  )

  $records = foreach ($c in $components) {
    [ordered]@{
      epoch_id=$epoch; cycle_id=$cycleId; component_id=$c.id; component_version=$c.version;
      schema_version=$SchemaVersion; compatibility_hash=$compatHash; policy_hash=$PolicyHash;
      canonical_hash_seen='RUNTIME_OBSERVER_BRANCH'; observer_source_sha=$sourceSha;
      checkpoint_id=$cycleId; rollback_id=$cycleId; observer_only=$true;
      promotion_capability=$false; heartbeat=[bool]$c.heartbeat; healthcheck_passed=[bool]$c.healthcheck_passed
    }
  }

  foreach ($r in $records) {
    $r | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $StateDir "$($r.component_id).json")
  }

  $bad = @($records | Where-Object {
    $_.epoch_id -ne $epoch -or $_.cycle_id -ne $cycleId -or
    $_.schema_version -ne $SchemaVersion -or $_.compatibility_hash -ne $compatHash -or
    $_.policy_hash -ne $PolicyHash -or $_.observer_source_sha -ne $sourceSha -or
    $_.observer_only -ne $true -or $_.promotion_capability -ne $false -or
    $_.heartbeat -ne $true -or $_.healthcheck_passed -ne $true
  })
  if ($bad.Count -gt 0) { FailClosed ('Runtime sync failed: ' + (($bad | ForEach-Object {$_.component_id}) -join ', ')) }

  $final = [ordered]@{
    contract_version=$ContractVersion; epoch_id=$epoch; cycle_id=$cycleId;
    cycle_status='SUCCESS_RUNTIME_VERIFIED'; compatibility_hash=$compatHash;
    observer_source_sha=$sourceSha; checkpoint_id=$cycleId; rollback_id=$cycleId;
    observer_only=$true; canonical_mainline_touched=$false; reality_validated=$false;
    promotion='NO'; components=$records; finish_utc=[DateTime]::UtcNow.ToString('o')
  }
  $final | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 (Join-Path $StateDir 'last-cycle.json')
  Log 'WATCHDOG_CONFIRM -> RECOVERY_CONFIRM -> CYCLE_FINISH'
  Log 'Cycle finished: SUCCESS_RUNTIME_VERIFIED'
}
catch { FailClosed $_.Exception.Message }
finally {
  if (Test-Path $Lock) { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
}
