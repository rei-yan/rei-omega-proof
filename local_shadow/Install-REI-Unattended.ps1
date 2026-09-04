<#
LEGACY ENTRYPOINT RETIRED.
This file is retained only so old bookmarks/commands fail safe instead of
silently reinstalling the pre-vNext PR #25 closed-loop payload.

Use Install-REI-VNext.ps1 for the current REI-CLP/3.0-observer local stack.
#>
[CmdletBinding()]
param(
    [string]$ReiHome = "C:\REI-Shadow",
    [string]$CoreDir = "C:\REI",
    [string]$PythonExe = "C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe",
    [ValidateRange(300, 86400)][int]$IntervalSeconds = 3600
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$replacement = Join-Path $PSScriptRoot "Install-REI-VNext.ps1"
Write-Warning "Install-REI-Unattended.ps1 is retired. The legacy payload could restore PR #25-era context and is blocked."

if (-not (Test-Path -LiteralPath $replacement)) {
    throw "Current installer not found: $replacement. Obtain Install-REI-VNext.ps1 from the shadow-node branch before installing."
}

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $replacement `
    -ReiHome $ReiHome -CoreDir $CoreDir -PythonExe $PythonExe -IntervalSeconds $IntervalSeconds
exit $LASTEXITCODE
