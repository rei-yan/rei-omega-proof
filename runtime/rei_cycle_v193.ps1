# REI-Ω v1.9.3 synchronized Windows runtime cycle
# Windows PowerShell 5.1 / .NET Framework. Observer-only, fail-closed.

param([switch]$Canary)

$ErrorActionPreference = 'Stop'
$Root = 'C:\REI-Shadow'
$ShadowScript = 'C:\REI\rei_shadow_closed_loop_v2.py'
$ContextSyncScript = Join-Path $Root 'REI-LocalSync.ps1'
$LocalModelScript = Join-Path $Root 'REI-LocalModel-VNext.ps1'
$WheelPullScript = Join-Path $Root 'sync_wheel_to_local.py'
$ObserverScript = Join-Path $Root 'vnext_observer.py'
$BridgeScript = Join-Path $Root 'bridge_to_wheel_vnext.py'
$GitSyncScript = Join-Path $Root 'sync_shadow_to_github.py'
$ContextState = Join-Path $Root 'context\sync_state.json'
$ObserverState = Join-Path $Root 'state\vnext_observer\latest.json'
$RuntimeRoot = Join-Path $Root 'runtime-v191'
$StateDir = Join-Path $RuntimeRoot 'state'
$CheckpointRoot = 'C:\REI_Resilience_Layer_v1\checkpoints'
$Lock = Join-Path $RuntimeRoot 'cycle.lock'
$OverlapState = Join-Path $StateDir 'last-overlap.json'
$Log = Join-Path $RuntimeRoot 'runtime-v191.log'
$SourceShaFile = Join-Path $RuntimeRoot 'deployed-sha.txt'
$MutexName = 'Global\REI_Omega_v193_Synchronized_Cycle'
$ContractVersion = '1.9.3'
$SchemaVersion = 'runtime-epoch-schema/1.2'
$PolicyHash = 'v1.9.3-observer-policy-pr28-vnext'
$CandidatePullRequest = 28
$CandidateHeadRef = 'rei-v193-reconcile'
$ProtocolVersion = 'REI-CLP/3.0-observer'
$script:CycleMutex = $null
$script:CycleMutexOwned = $false

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

function Resolve-Python {
  foreach ($candidate in @('python.exe','python','py.exe','py')) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
  }
  throw 'Python not found'
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

function Test-ReconciledContext {
  if (-not (Test-Path $ContextState)) { return $false }
  try {
    $ctx = Get-Content $ContextState -Raw | ConvertFrom-Json
    return ([int]$ctx.pull_request -eq $CandidatePullRequest -and
            [string]$ctx.head_ref -eq $CandidateHeadRef -and
            -not [string]::IsNullOrWhiteSpace([string]$ctx.head_sha))
  }
  catch { return $false }
}

function Test-GodLineState {
  if (-not (Test-Path $ObserverState)) { return @{healthy=$false;cycle='';reason='observer state missing'} }
  try {
    $o = Get-Content $ObserverState -Raw -Encoding UTF8 | ConvertFrom-Json
    $promotion = $o.promotion_gate_v2
    $lineage = $o.lineage
    $hypotheses = $o.hypothesis_state
    $failure = $o.failure_recurrence
    $healthy = (
      [string]$o.protocol_version -eq $ProtocolVersion -and
      [bool]$o.observer_mode -eq $true -and
      [bool]$o.canonical_write_permission -eq $false -and
      -not [string]::IsNullOrWhiteSpace([string]$o.cycle_id) -and
      $null -ne $lineage -and $null -ne $hypotheses -and $null -ne $failure -and
      $null -ne $promotion -and
      [bool]$promotion.may_promote_canonical -eq $false -and
      [bool]$promotion.may_grant_reality_validation -eq $false -and
      [bool]$promotion.may_grant_ascension -eq $false
    )
    return @{healthy=$healthy;cycle=[string]$o.cycle_id;reason=$(if($healthy){'vNext observer line bundle verified'}else{'observer line bundle invalid'})}
  }
  catch { return @{healthy=$false;cycle='';reason=$_.Exception.Message} }
}

function Invoke-Python([string]$name,[string]$script,[string[]]$arguments=@()) {
  if (-not (Test-Path $script)) { throw "$name missing: $script" }
  & $script:PythonExe $script @arguments
  if ($LASTEXITCODE -ne 0) { throw "$name exited $LASTEXITCODE" }
}

function Invoke-PowerShell([string]$name,[string]$script,[string[]]$arguments=@()) {
  if (-not (Test-Path $script)) { throw "$name missing: $script" }
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script @arguments
  if ($LASTEXITCODE -ne 0) { throw "$name exited $LASTEXITCODE" }
}

function FailClosed([string]$reason) {
  New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
  $state = [ordered]@{
    contract_version=$ContractVersion; schema_version=$SchemaVersion; status='FAIL_CLOSED'; reason=$reason;
    observer_source_sha=(Get-SourceSha); observer_only=$true; promotion='NO';
    reality_validated=$false; canonical_mainline_touched=$false;
    candidate_pull_request=$CandidatePullRequest; candidate_head_ref=$CandidateHeadRef;
    timestamp_utc=[DateTime]::UtcNow.ToString('o')
  }
  $state | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 (Join-Path $StateDir 'last-cycle.json')
  Log "FAIL-CLOSED: $reason"
  if ($script:CycleMutexOwned -and (Test-Path $Lock)) { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
  exit 2
}

function Record-OverlapSkip {
  New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
  $state = [ordered]@{
    contract_version=$ContractVersion; schema_version=$SchemaVersion; status='SKIPPED_OVERLAP';
    reason='Another synchronized v1.9.3 runtime cycle currently owns the Windows mutex';
    observer_source_sha=(Get-SourceSha); observer_only=$true; promotion='NO';
    reality_validated=$false; canonical_mainline_touched=$false;
    candidate_pull_request=$CandidatePullRequest; candidate_head_ref=$CandidateHeadRef;
    timestamp_utc=[DateTime]::UtcNow.ToString('o')
  }
  $state | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $OverlapState
  Log 'SKIP_OVERLAP: another synchronized runtime cycle is active; existing cycle left untouched'
}

$script:PythonExe = Resolve-Python

# Dependency-only canary. It deliberately does not run a Shadow cycle or write the wheel ledger.
if ($Canary) {
  foreach ($p in @($Root,$ShadowScript,$ContextSyncScript,$LocalModelScript,$WheelPullScript,$ObserverScript,$BridgeScript,$GitSyncScript,'C:\REI_Resilience_Layer_v1')) {
    if (-not (Test-Path $p)) { Write-Error "CANARY missing path: $p"; exit 2 }
  }
  $ollama = Test-Ollama
  if (-not $ollama.healthy) { Write-Error 'CANARY Ollama unavailable'; exit 2 }
  $names = @($ollama.tags.models | ForEach-Object { $_.name })
  if (-not ($names | Where-Object { $_ -like 'rei-local-node-vnext*' })) {
    Write-Error 'CANARY rei-local-node-vnext model missing'; exit 2
  }
  if (-not (Get-ScheduledTask -TaskName 'REI-Local-Watchdog' -ErrorAction SilentlyContinue)) {
    Write-Error 'CANARY REI-Local-Watchdog missing'; exit 2
  }
  Write-Host 'CANARY_PASS' -ForegroundColor Green
  exit 0
}

New-Item -ItemType Directory -Force -Path $StateDir,$CheckpointRoot | Out-Null

# OS mutex is the authority. cycle.lock is only a visible marker and may be safely
# replaced after the mutex is acquired. An overlap must never overwrite last-cycle
# or remove the active owner's marker.
$script:CycleMutex = New-Object System.Threading.Mutex($false, $MutexName)
try {
  try {
    $script:CycleMutexOwned = $script:CycleMutex.WaitOne(0, $false)
  }
  catch [System.Threading.AbandonedMutexException] {
    $script:CycleMutexOwned = $true
    Log 'SELF_HEAL: recovered abandoned synchronized runtime mutex'
  }

  if (-not $script:CycleMutexOwned) {
    Record-OverlapSkip
    $script:CycleMutex.Dispose()
    $script:CycleMutex = $null
    exit 0
  }

  if (Test-Path $Lock) {
    Remove-Item $Lock -Force -ErrorAction SilentlyContinue
    Log 'SELF_HEAL: removed stale cycle.lock marker after exclusive mutex acquisition'
  }
  [ordered]@{pid=$PID;created_utc=[DateTime]::UtcNow.ToString('o');contract_version=$ContractVersion} |
    ConvertTo-Json | Set-Content -Encoding UTF8 $Lock

  $sourceSha = Get-SourceSha
  $epoch = 'rei-v193-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
  $cycleId = [Guid]::NewGuid().ToString('N')
  $compatSeed = "$ContractVersion|$SchemaVersion|$PolicyHash|$ProtocolVersion|PR$CandidatePullRequest|$CandidateHeadRef|observer-only|$sourceSha"
  $compatHash = Get-CompatibleSha256 $compatSeed
  Log "PREPARE epoch=$epoch cycle=$cycleId source=$sourceSha candidate=PR#$CandidatePullRequest/$CandidateHeadRef"

  $ollama = Test-Ollama
  if (-not $ollama.healthy) { FailClosed 'Ollama API unavailable' }
  $modelNames = @($ollama.tags.models | ForEach-Object { $_.name })
  if (-not ($modelNames | Where-Object { $_ -like 'rei-local-node-vnext*' })) {
    FailClosed 'rei-local-node-vnext model missing from Ollama'
  }

  $cp = Join-Path $CheckpointRoot $cycleId
  New-Item -ItemType Directory -Force -Path $cp | Out-Null
  foreach ($f in @('shadow_ledger.jsonl','divine_wheel_inbox.jsonl','bridge_to_wheel_vnext.py','sync_shadow_to_github.py')) {
    $src = Join-Path $Root $f
    if (Test-Path $src) { Copy-Item $src $cp -Force }
  }
  @{epoch_id=$epoch;cycle_id=$cycleId;compatibility_hash=$compatHash;observer_source_sha=$sourceSha;candidate_pull_request=$CandidatePullRequest;created_utc=[DateTime]::UtcNow.ToString('o')} |
    ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $cp 'checkpoint.json')
  Log "SNAPSHOT checkpoint=$cp"

  Log 'CONTEXT_SYNC -> PR28 reconciled candidate'
  Invoke-PowerShell 'ContextSync' $ContextSyncScript @('-Once','-PullRequest',[string]$CandidatePullRequest,'-ContextOnly')
  if (-not (Test-ReconciledContext)) { FailClosed 'Context is not pinned to PR #28 / rei-v193-reconcile' }

  Log 'WHEEL_PULL -> correlated internal receipts only'
  Invoke-Python 'WheelPull' $WheelPullScript @('--home',$Root)

  Log 'LOCAL_MODEL -> exact vNext overlay'
  Invoke-PowerShell 'LocalModel' $LocalModelScript @('-ContextDir',(Join-Path $Root 'context'))
  $ollama = Test-Ollama
  $modelNames = @($ollama.tags.models | ForEach-Object { $_.name })
  if (-not ($modelNames | Where-Object { $_ -like 'rei-local-node-vnext*' })) { FailClosed 'vNext local model refresh not verified' }

  $env:REI_MODEL='rei-local-node-vnext'
  $env:REI_VALIDATOR_MODEL='rei-local-node-vnext'
  $env:REI_CLOSED_LOOP_PROTOCOL=$ProtocolVersion
  $env:REI_OBSERVER_MODE='true'

  Log 'OBSERVE -> SHADOW_CHALLENGE'
  Invoke-Python 'Shadow' $ShadowScript @('--home',$Root,'--once')

  Log 'OBSERVER -> VNEXT GOVERNANCE'
  Invoke-Python 'VNextObserver' $ObserverScript @('--home',$Root)
  $godLine = Test-GodLineState
  if (-not $godLine.healthy) { FailClosed ('God Line observer bundle failed: ' + $godLine.reason) }

  Log 'CROSS_CHECK -> VNEXT BRIDGE'
  Invoke-Python 'VNextBridge' $BridgeScript @('--home',$Root)

  Log 'LEDGER_COMMIT -> GIT_SYNC'
  Invoke-Python 'GitSync' $GitSyncScript @('--home',$Root,'--repo',(Join-Path $Root 'repo'))

  $shadowLedger = Join-Path $Root 'shadow_ledger.jsonl'
  $wheelInbox = Join-Path $Root 'divine_wheel_inbox.jsonl'
  if (-not (Test-Path $shadowLedger)) { FailClosed 'shadow_ledger.jsonl missing' }
  if (-not (Test-Path $wheelInbox)) { FailClosed 'divine_wheel_inbox.jsonl missing' }

  $ollamaWatchdog = Get-ScheduledTask -TaskName 'REI-Local-Watchdog' -ErrorAction SilentlyContinue
  if (-not $ollamaWatchdog) { FailClosed 'REI-Local-Watchdog scheduled task missing' }
  $recoveryReady = Test-Path 'C:\REI_Resilience_Layer_v1'
  if (-not $recoveryReady) { FailClosed 'Recovery root missing' }
  $observerHealthy = (Test-Path $ObserverState) -and $godLine.healthy
  $bridgeHealthy = Test-Path $BridgeScript

  $components = @(
    @{id='god-wheel';version='REI-CLP/3.0-observer+v1.9.3';heartbeat=(Test-Path $wheelInbox);healthcheck_passed=(Test-Path $wheelInbox)},
    @{id='local-model';version='rei-local-node-vnext';heartbeat=$ollama.healthy;healthcheck_passed=([bool]($modelNames | Where-Object { $_ -like 'rei-local-node-vnext*' }))},
    @{id='shadow';version='Shadow V2.3+fusion';heartbeat=(Test-Path $shadowLedger);healthcheck_passed=(Test-Path $shadowLedger)},
    @{id='observer';version='vNext+Fusion-v1.9.3';heartbeat=$observerHealthy;healthcheck_passed=$observerHealthy},
    @{id='bridge';version='vNext-v1.9.3-contract';heartbeat=$bridgeHealthy;healthcheck_passed=$bridgeHealthy},
    @{id='ledger';version='v1.9.3-contract';heartbeat=((Test-Path $shadowLedger) -and (Test-Path $wheelInbox));healthcheck_passed=((Test-Path $shadowLedger) -and (Test-Path $wheelInbox))},
    @{id='watchdog';version='v1.9.3-contract';heartbeat=($null -ne $ollamaWatchdog);healthcheck_passed=($null -ne $ollamaWatchdog)},
    @{id='recovery';version='v1.9.3-contract';heartbeat=$recoveryReady;healthcheck_passed=$recoveryReady},
    @{id='god-line';version='v1.9.3-vnext-line-bundle';heartbeat=$godLine.healthy;healthcheck_passed=$godLine.healthy}
  )

  $records = foreach ($c in $components) {
    [ordered]@{
      epoch_id=$epoch; cycle_id=$cycleId; component_id=$c.id; component_version=$c.version;
      schema_version=$SchemaVersion; compatibility_hash=$compatHash; policy_hash=$PolicyHash;
      canonical_hash_seen='RUNTIME_OBSERVER_BRANCH'; observer_source_sha=$sourceSha;
      candidate_pull_request=$CandidatePullRequest; candidate_head_ref=$CandidateHeadRef;
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
    contract_version=$ContractVersion; schema_version=$SchemaVersion; epoch_id=$epoch; cycle_id=$cycleId;
    cycle_status='SUCCESS_RUNTIME_VERIFIED'; compatibility_hash=$compatHash;
    observer_source_sha=$sourceSha; candidate_pull_request=$CandidatePullRequest; candidate_head_ref=$CandidateHeadRef;
    god_line_source_cycle=$godLine.cycle; checkpoint_id=$cycleId; rollback_id=$cycleId;
    observer_only=$true; canonical_mainline_touched=$false; reality_validated=$false;
    promotion='NO'; components=$records; finish_utc=[DateTime]::UtcNow.ToString('o')
  }
  $final | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 (Join-Path $StateDir 'last-cycle.json')
  Log 'WATCHDOG_CONFIRM -> RECOVERY_CONFIRM -> CYCLE_FINISH'
  Log 'Cycle finished: SUCCESS_RUNTIME_VERIFIED'
}
catch { FailClosed $_.Exception.Message }
finally {
  if ($script:CycleMutexOwned) {
    if (Test-Path $Lock) { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
    try { $script:CycleMutex.ReleaseMutex() } catch {}
  }
  if ($null -ne $script:CycleMutex) {
    try { $script:CycleMutex.Dispose() } catch {}
  }
}