<#
PR #28 local-repair bootstrap v2.
Fixes the original repair script's invalid local_shadow path by pinning the
local payload to a verified shadow-node commit while keeping context pinned to
PR #28 / rei-v193-reconcile. Canonical/main is never modified.
#>
[CmdletBinding()]
param(
    [string]$ReiHome = 'C:\REI-Shadow',
    [string]$CoreDir = 'C:\REI',
    [int]$IntervalSeconds = 3600
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$SourceCommit = '807475e8657a17fa0ff03996e134b24a1b90fc26'
$PayloadCommit = 'd831e7b60eef51cbd9f0a8677b52dfb6a8df0895'
$SourceUrl = "https://raw.githubusercontent.com/rei-yan/rei-omega-proof/$SourceCommit/runtime/Repair-REI-Local-PR28.ps1"
$PayloadRoot = "https://raw.githubusercontent.com/rei-yan/rei-omega-proof/$PayloadCommit/local_shadow"
$TempScript = Join-Path $env:TEMP 'Repair-REI-Local-PR28-v2-inner.ps1'

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error 'Run this repair from an elevated PowerShell session.'
    exit 2
}

try {
    Write-Host "PR28 repair bootstrap v2" -ForegroundColor Cyan
    Write-Host "Repair source: $SourceCommit" -ForegroundColor DarkGray
    Write-Host "Pinned local payload: $PayloadCommit" -ForegroundColor DarkGray

    Invoke-WebRequest -UseBasicParsing -Uri $SourceUrl -OutFile $TempScript
    if (-not (Test-Path $TempScript) -or (Get-Item $TempScript).Length -eq 0) {
        throw 'Failed to download base PR28 repair script.'
    }

    $text = Get-Content -LiteralPath $TempScript -Raw
    $old = '$RawRoot = "https://raw.githubusercontent.com/rei-yan/rei-omega-proof/$Branch/local_shadow"'
    $new = '$RawRoot = "https://raw.githubusercontent.com/rei-yan/rei-omega-proof/' + $PayloadCommit + '/local_shadow"'
    if (-not $text.Contains($old)) {
        throw 'Base repair script layout changed; refusing an unsafe patch.'
    }
    $text = $text.Replace($old, $new)
    $text = $text.Replace("`$RuntimeRawRoot = \"https://raw.githubusercontent.com/rei-yan/rei-omega-proof/`$Branch/runtime\"", "`$RuntimeRawRoot = \"https://raw.githubusercontent.com/rei-yan/rei-omega-proof/$SourceCommit/runtime\"")

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($TempScript, $text, $utf8NoBom)

    $probe = "$PayloadRoot/REI-LocalSync.ps1"
    $probeResult = Invoke-WebRequest -UseBasicParsing -Uri $probe -Method Get
    if ($probeResult.StatusCode -ne 200) {
        throw "Pinned payload probe failed: HTTP $($probeResult.StatusCode)"
    }

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $TempScript -ReiHome $ReiHome -CoreDir $CoreDir -IntervalSeconds $IntervalSeconds
    $code = $LASTEXITCODE
    Write-Host "PR28_REPAIR_V2_EXITCODE=$code" -ForegroundColor Cyan
    exit $code
}
catch {
    Write-Error ("PR28_REPAIR_V2_FAILED: " + $_.Exception.Message)
    exit 2
}
finally {
    Remove-Item -LiteralPath $TempScript -Force -ErrorAction SilentlyContinue
}
