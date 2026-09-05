<#
REI-Ω Continuous Reality Orchestrator v1
Runs the non-authoritative reality sidecar first, then the host continuity guard.
The host guard remains authoritative for continuity status. A sidecar failure is
reported as degraded and never rewritten into success.
#>
[CmdletBinding()]
param(
  [string]$RuntimeRoot = 'C:\REI-Shadow\runtime-v191'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Sidecar = Join-Path $RuntimeRoot 'REI-Reality-Sidecar-V1.ps1'
$Guard = Join-Path $RuntimeRoot 'REI-Continuous-Reality-Guard-V1.ps1'
$Contract = Join-Path $RuntimeRoot 'continuous-reality-contract-v1.json'

if (-not (Test-Path -LiteralPath $Sidecar)) { Write-Error "Reality sidecar missing: $Sidecar"; exit 2 }
if (-not (Test-Path -LiteralPath $Guard)) { Write-Error "Continuous guard missing: $Guard"; exit 2 }
if (-not (Test-Path -LiteralPath $Contract)) { Write-Error "Continuous contract missing: $Contract"; exit 2 }

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Sidecar
$sidecarExit = $LASTEXITCODE

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Guard -ContractPath $Contract
$guardExit = $LASTEXITCODE

Write-Host "REALITY_SIDECAR_EXIT=$sidecarExit" -ForegroundColor $(if($sidecarExit -eq 0){'Green'}else{'Yellow'})
Write-Host "CONTINUITY_GUARD_EXIT=$guardExit" -ForegroundColor $(if($guardExit -eq 0){'Green'}elseif($guardExit -eq 1){'Yellow'}else{'Red'})
Write-Host 'Canonical/main untouched; RealityValidated=FALSE; Promotion=NO.' -ForegroundColor Green

if ($guardExit -ge 2) { exit 2 }
if ($guardExit -eq 1 -or $sidecarExit -ne 0) { exit 1 }
exit 0
