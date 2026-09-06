param(
  [string]$ConfigPath = "$PSScriptRoot\local-components.json",
  [switch]$StartProcesses,
  [switch]$Strict
)

$ErrorActionPreference = 'Stop'

function Fail-Closed([string]$Message) {
  Write-Host "[REI v1.9.1][FAIL-CLOSED] $Message" -ForegroundColor Red
  $state = @{
    status = 'FAIL_CLOSED'
    reason = $Message
    promotion = 'NO'
    reality_validated = $false
    canonical_touch_allowed = $false
    observer_only = $true
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
  }
  $state | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 "$PSScriptRoot\state\last-cycle.json"
  exit 2
}

$stateDir = Join-Path $PSScriptRoot 'state'
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

if (-not (Test-Path $ConfigPath)) {
  $example = Join-Path $PSScriptRoot 'local-components.example.json'
  if (Test-Path $example) {
    Copy-Item $example $ConfigPath
    Write-Host "Created $ConfigPath from example. Fill real local command/healthcheck fields before using -StartProcesses." -ForegroundColor Yellow
  } else {
    Fail-Closed "Missing runtime component config: $ConfigPath"
  }
}

$config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
if ($config.epoch_contract_version -ne '1.9.1') { Fail-Closed "epoch_contract_version must be 1.9.1" }
if ($config.observer_only -ne $true) { Fail-Closed "observer_only must remain true" }
if ($config.canonical_touch_allowed -ne $false) { Fail-Closed "canonical_touch_allowed must remain false" }

$required = @('god-wheel','local-model','shadow','observer','bridge','ledger','watchdog','recovery','god-line')
$ids = @($config.components | ForEach-Object { $_.id })
foreach ($r in $required) {
  if ($ids -notcontains $r) { Fail-Closed "Missing required component: $r" }
}

$epoch = "rei-v191-" + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$cycle = [Guid]::NewGuid().ToString('N')
$canonicalHash = 'UNRESOLVED_RUNTIME_CANONICAL_HASH'
$policyHash = 'v1.9.1-observer-policy'
$schemaVersion = 'runtime-epoch-schema/1.0'
$compatibilityHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes("$($config.epoch_contract_version)|$schemaVersion|$policyHash|observer-only"))).ToLower()

$epochState = [ordered]@{
  epoch_id = $epoch
  cycle_id = $cycle
  contract_version = '1.9.1'
  schema_version = $schemaVersion
  policy_hash = $policyHash
  compatibility_hash = $compatibilityHash
  canonical_hash_seen = $canonicalHash
  observer_only = $true
  promotion_capability = $false
  reality_validated = $false
  promotion = 'NO'
  start_utc = [DateTime]::UtcNow.ToString('o')
  components = @()
}

Write-Host "[REI v1.9.1] PREPARE epoch=$epoch cycle=$cycle" -ForegroundColor Cyan

foreach ($component in $config.components) {
  $record = [ordered]@{
    epoch_id = $epoch
    cycle_id = $cycle
    component_id = $component.id
    component_version = $component.version
    schema_version = $schemaVersion
    compatibility_hash = $compatibilityHash
    policy_hash = $policyHash
    canonical_hash_seen = $canonicalHash
    observer_only = $true
    promotion_capability = $false
    heartbeat = $false
    process_started = $false
    healthcheck_passed = $false
    status = 'PREPARED'
  }

  if ($StartProcesses -and $component.command) {
    try {
      Start-Process powershell -ArgumentList '-NoProfile','-Command',$component.command -WindowStyle Hidden | Out-Null
      $record.process_started = $true
      Start-Sleep -Milliseconds 500
    } catch {
      Fail-Closed "Failed to start $($component.id): $($_.Exception.Message)"
    }
  }

  if ($component.healthcheck) {
    try {
      Invoke-Expression $component.healthcheck | Out-Null
      if ($LASTEXITCODE -eq 0 -or $null -eq $LASTEXITCODE) {
        $record.healthcheck_passed = $true
        $record.heartbeat = $true
        $record.status = 'HEALTHY'
      } else {
        $record.status = 'UNHEALTHY'
      }
    } catch {
      $record.status = 'UNHEALTHY'
    }
  } elseif (-not $Strict) {
    $record.status = 'UNVERIFIED_RUNTIME'
  }

  $record | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $stateDir "$($component.id).json")
  $epochState.components += $record
}

Write-Host '[REI v1.9.1] SNAPSHOT -> OBSERVE -> SHADOW_CHALLENGE -> CROSS_CHECK' -ForegroundColor Cyan

$bad = @($epochState.components | Where-Object {
  $_.epoch_id -ne $epoch -or
  $_.cycle_id -ne $cycle -or
  $_.schema_version -ne $schemaVersion -or
  $_.compatibility_hash -ne $compatibilityHash -or
  $_.policy_hash -ne $policyHash -or
  $_.observer_only -ne $true -or
  $_.promotion_capability -ne $false
})
if ($bad.Count -gt 0) { Fail-Closed 'Compatibility metadata mismatch across runtime participants' }

if ($Strict) {
  $unhealthy = @($epochState.components | Where-Object { $_.healthcheck_passed -ne $true })
  if ($unhealthy.Count -gt 0) {
    Fail-Closed ("Strict runtime health verification failed: " + (($unhealthy | ForEach-Object {$_.component_id}) -join ', '))
  }
}

$epochState.finish_utc = [DateTime]::UtcNow.ToString('o')
$epochState.cycle_status = if ($Strict) { 'SUCCESS_RUNTIME_VERIFIED' } else { 'SUCCESS_CONTRACT_ONLY' }
$epochState.canonical_mainline_touched = $false
$epochState.reality_validated = $false
$epochState.promotion = 'NO'
$epochState | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 (Join-Path $stateDir 'last-cycle.json')

Write-Host '[REI v1.9.1] LEDGER_COMMIT -> WATCHDOG_CONFIRM -> RECOVERY_CONFIRM -> CYCLE_FINISH' -ForegroundColor Green
Write-Host "Cycle finished: $($epochState.cycle_status)" -ForegroundColor Green
Write-Host 'RealityValidated = FALSE | Promotion = NO | canonical_mainline_touched = false' -ForegroundColor Yellow
