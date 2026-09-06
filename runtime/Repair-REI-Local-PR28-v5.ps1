<#
REI-Ω PR #28 local repair v5.
PowerShell 5.1-safe process-aware lock guard.
Avoids scalar .Count semantics and pins delegated scripts by exact commit SHA.
Never force-kills a runtime process and never writes canonical/main.
#>
[CmdletBinding()]
param(
    [ValidateRange(15,1440)][int]$IntervalMinutes = 60,
    [ValidateRange(30,300)][int]$WaitSeconds = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Repo = 'rei-yan/rei-omega-proof'
$TaskName = 'REI Full Pipeline v1.9.1'
$StandaloneTask = 'REI Unattended Closed Loop'
$RuntimeRoot = 'C:\REI-Shadow\runtime-v191'
$LockPath = Join-Path $RuntimeRoot 'cycle.lock'
$BackupDir = 'C:\REI-Shadow\backups\pr28-v5-' + (Get-Date -Format 'yyyyMMdd_HHmmss')
$TempV3 = Join-Path $env:TEMP 'Repair-REI-Local-PR28-v3-pinned.ps1'
$V3Commit = 'd641b1e01d9b391b561c42900993d54c7e45ada3'

function Get-ReiCycleProcesses {
    try {
        Get-CimInstance Win32_Process -ErrorAction Stop |
            Where-Object {
                $_.Name -match '^(powershell|pwsh)(\.exe)?$' -and
                $_.CommandLine -and
                $_.CommandLine -match 'rei_cycle_v19(1|3)\.ps1'
            }
    }
    catch {
        Write-Warning ('Process inspection failed: ' + $_.Exception.Message)
    }
}

function Get-ProcessCount($Items) {
    return [int](($Items | Measure-Object).Count)
}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error 'Run this repair from an elevated PowerShell session.'
    exit 2
}

try {
    Write-Host 'PR28 local repair v5: PS5-safe process-aware lock guard' -ForegroundColor Cyan
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

    foreach ($task in @($TaskName,$StandaloneTask)) {
        $t = Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
        if ($t) {
            try { Export-ScheduledTask -TaskName $task | Set-Content -Encoding UTF8 (Join-Path $BackupDir (($task -replace '[^A-Za-z0-9._-]','_') + '.xml')) } catch { }
            Stop-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
        }
    }

    $deadline = (Get-Date).AddSeconds($WaitSeconds)
    do {
        $active = @(Get-ReiCycleProcesses)
        $activeCount = Get-ProcessCount $active
        if ($activeCount -eq 0) { break }
        $ids = ($active | ForEach-Object { [string]$_.ProcessId }) -join ','
        Write-Host "Waiting for active REI runtime cycle process(es): PID $ids" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    } while ((Get-Date) -lt $deadline)

    $active = @(Get-ReiCycleProcesses)
    $activeCount = Get-ProcessCount $active
    if ($activeCount -gt 0) {
        $detail = ($active | ForEach-Object { "PID=$($_.ProcessId) CMD=$($_.CommandLine)" }) -join ' | '
        throw "A real REI runtime cycle is still active after $WaitSeconds seconds. Refusing to remove lock. $detail"
    }

    if (Test-Path -LiteralPath $LockPath) {
        Copy-Item -LiteralPath $LockPath -Destination (Join-Path $BackupDir 'cycle.lock') -Force
        $age = ((Get-Date) - (Get-Item -LiteralPath $LockPath).LastWriteTime).TotalMinutes
        Remove-Item -LiteralPath $LockPath -Force
        Write-Host "Removed orphaned runtime lock after process verification (age=$([Math]::Round($age,1)) min)." -ForegroundColor Yellow
    } else {
        Write-Host 'No runtime lock present after scheduler quiesce.' -ForegroundColor Green
    }

    $v3Url = "https://raw.githubusercontent.com/$Repo/$V3Commit/runtime/Repair-REI-Local-PR28-v3.ps1"
    Invoke-WebRequest -UseBasicParsing -Uri $v3Url -OutFile $TempV3
    if (-not (Test-Path -LiteralPath $TempV3) -or (Get-Item -LiteralPath $TempV3).Length -eq 0) {
        throw 'Failed to download pinned v3 repair payload.'
    }

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $TempV3 -IntervalMinutes $IntervalMinutes
    $code = $LASTEXITCODE
    Write-Host "PR28_REPAIR_V5_EXITCODE=$code" -ForegroundColor Cyan
    exit $code
}
catch {
    Write-Error ('PR28_REPAIR_V5_FAILED: ' + $_.Exception.Message)
    exit 2
}
finally {
    Remove-Item -LiteralPath $TempV3 -Force -ErrorAction SilentlyContinue
}
