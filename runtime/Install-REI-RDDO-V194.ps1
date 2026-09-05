<#
REI-Ω RDDO guarded installer.

Installs only the observer-only RDDO runtime asset from the exact reconciled
candidate SHA. It creates a checkpoint, compiles and self-tests the staged
Python file, then writes a local attestation. It does not create a scheduler,
expand authority, or touch canonical/main.
#>
[CmdletBinding()]
param(
  [string]$CandidateRef = 'rei-v193-reconcile'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = 'C:\REI-Shadow'
$Repo = Join-Path $Root 'repo'
$StateDir = Join-Path $Root 'state\rddo'
$RuntimeAsset = Join-Path $Root 'rddo_reference.py'
$ContractAsset = Join-Path $Root 'rddo-extension-contract-v194.json'
$RecoveryRoot = 'C:\REI_Resilience_Layer_v1\rddo'
$SourcePath = 'research/rddo_reference.py'
$ContractPath = 'runtime/rddo-extension-contract-v194.json'
$RemoteRef = "origin/$CandidateRef"

function Resolve-Git {
  foreach ($p in @('git.exe','C:\Program Files\Git\cmd\git.exe','C:\Program Files\Git\bin\git.exe')) {
    $cmd = Get-Command $p -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    if (Test-Path -LiteralPath $p) { return $p }
  }
  throw 'git.exe not found'
}

function Resolve-Python {
  foreach ($p in @('python.exe','python','py.exe','py')) {
    $cmd = Get-Command $p -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
  }
  throw 'Python not found'
}

function Write-AtomicJson([string]$Path,[object]$Value) {
  $dir = Split-Path -Parent $Path
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $tmp = Join-Path $dir ([IO.Path]::GetRandomFileName())
  $Value | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $tmp -Encoding UTF8
  Move-Item -LiteralPath $tmp -Destination $Path -Force
}

if (-not (Test-Path -LiteralPath $Repo)) { throw "Repo missing: $Repo" }
New-Item -ItemType Directory -Force -Path $StateDir,$RecoveryRoot | Out-Null
$git = Resolve-Git
$python = Resolve-Python

& $git -C $Repo fetch origin $CandidateRef --quiet
if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }
$candidateSha = (& $git -C $Repo rev-parse $RemoteRef).Trim()
if ($LASTEXITCODE -ne 0 -or -not $candidateSha) { throw 'candidate SHA resolution failed' }

$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$checkpoint = Join-Path $RecoveryRoot "$stamp-$($candidateSha.Substring(0,8))"
New-Item -ItemType Directory -Force -Path $checkpoint | Out-Null
if (Test-Path -LiteralPath $RuntimeAsset) { Copy-Item -LiteralPath $RuntimeAsset -Destination (Join-Path $checkpoint 'rddo_reference.previous.py') -Force }
if (Test-Path -LiteralPath $ContractAsset) { Copy-Item -LiteralPath $ContractAsset -Destination (Join-Path $checkpoint 'rddo-contract.previous.json') -Force }

$stage = Join-Path $env:TEMP ('rei-rddo-' + $candidateSha.Substring(0,8))
New-Item -ItemType Directory -Force -Path $stage | Out-Null
$stagedPython = Join-Path $stage 'rddo_reference.py'
$stagedContract = Join-Path $stage 'rddo-extension-contract-v194.json'

try {
  $code = & $git -C $Repo show "$RemoteRef`:$SourcePath"
  if ($LASTEXITCODE -ne 0) { throw "Unable to stage $SourcePath" }
  $code | Set-Content -LiteralPath $stagedPython -Encoding UTF8

  $contractText = & $git -C $Repo show "$RemoteRef`:$ContractPath"
  if ($LASTEXITCODE -ne 0) { throw "Unable to stage $ContractPath" }
  $contractText | Set-Content -LiteralPath $stagedContract -Encoding UTF8

  & $python -m py_compile $stagedPython
  if ($LASTEXITCODE -ne 0) { throw 'RDDO py_compile failed' }

  $out = & $python $stagedPython --x '[0,1,2,3]' --y '[0,1,4,9]' --max-order 3
  if ($LASTEXITCODE -ne 0) { throw 'RDDO deterministic self-test failed' }
  $obj = $out | ConvertFrom-Json
  if (-not [bool]$obj.observer_only) { throw 'RDDO observer_only marker missing' }
  if ([bool]$obj.promotion_capability) { throw 'RDDO promotion authority expansion detected' }
  if ([bool]$obj.reality_validated) { throw 'RDDO reality-validation authority expansion detected' }
  if ([bool]$obj.nonfinite_detected) { throw 'RDDO self-test returned nonfinite telemetry' }
  if ([int]$obj.max_order -gt 8) { throw 'RDDO order bound violated' }

  Copy-Item -LiteralPath $stagedPython -Destination $RuntimeAsset -Force
  Copy-Item -LiteralPath $stagedContract -Destination $ContractAsset -Force

  $state = [ordered]@{
    schema_version = 'rddo-runtime-state/1.0'
    status = 'RDDO_DEPLOYED_VERIFIED'
    candidate_pull_request = 28
    candidate_head_ref = $CandidateRef
    candidate_head_sha = $candidateSha
    runtime_asset = $RuntimeAsset
    contract_asset = $ContractAsset
    observer_only = $true
    promotion_capability = $false
    reality_validated = $false
    max_recursive_order = 8
    checkpoint = $checkpoint
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
  }
  Write-AtomicJson (Join-Path $StateDir 'latest.json') $state
  Write-Host 'RDDO_DEPLOYED_VERIFIED' -ForegroundColor Green
  exit 0
}
catch {
  $reason = $_.Exception.Message
  $prevPython = Join-Path $checkpoint 'rddo_reference.previous.py'
  $prevContract = Join-Path $checkpoint 'rddo-contract.previous.json'
  if (Test-Path -LiteralPath $prevPython) { Copy-Item -LiteralPath $prevPython -Destination $RuntimeAsset -Force }
  elseif (Test-Path -LiteralPath $RuntimeAsset) { Remove-Item -LiteralPath $RuntimeAsset -Force }
  if (Test-Path -LiteralPath $prevContract) { Copy-Item -LiteralPath $prevContract -Destination $ContractAsset -Force }
  elseif (Test-Path -LiteralPath $ContractAsset) { Remove-Item -LiteralPath $ContractAsset -Force }

  Write-AtomicJson (Join-Path $StateDir 'latest.json') ([ordered]@{
    schema_version='rddo-runtime-state/1.0'; status='RDDO_ROLLED_BACK'; reason=$reason;
    candidate_head_sha=$candidateSha; observer_only=$true; promotion_capability=$false;
    reality_validated=$false; checkpoint=$checkpoint; timestamp_utc=[DateTime]::UtcNow.ToString('o')
  })
  throw
}
finally {
  Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
}
