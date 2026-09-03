<#
One-time installer for the REI-Ω / 无相神核 bidirectional unattended loop.
Downloads an immutable, pinned GitHub revision, validates Python syntax, backs
up replaced files, installs the Windows scheduled task, and starts it.
#>

[CmdletBinding()]
param(
    [string]$ReiHome = "C:\REI-Shadow",
    [string]$CoreDir = "C:\REI",
    [string]$PythonExe = "C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe",
    [ValidateRange(300, 86400)]
    [int]$IntervalSeconds = 3600
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PinnedCommit = "d8fcebd838bb9efcb1d7cf6e59f4b2ccacc21538"
$RawRoot = "https://raw.githubusercontent.com/rei-yan/rei-omega-proof/$PinnedCommit/local_shadow"

function Resolve-Python {
    if (Test-Path -LiteralPath $PythonExe) { return $PythonExe }
    foreach ($candidate in @("python.exe", "python", "py.exe", "py")) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    throw "Python not found. Install Python or pass -PythonExe with the full path."
}

$resolvedPython = Resolve-Python
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) { throw "Git is not available in PATH." }
if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) { throw "Ollama is not available in PATH." }

New-Item -ItemType Directory -Path $ReiHome -Force | Out-Null
New-Item -ItemType Directory -Path $CoreDir -Force | Out-Null
$stamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$stage = Join-Path $env:TEMP "rei-closed-loop-$stamp"
$backup = Join-Path $ReiHome "backups\closed-loop-$stamp"
New-Item -ItemType Directory -Path $stage -Force | Out-Null
New-Item -ItemType Directory -Path $backup -Force | Out-Null

$manifest = @(
    @{ Source = "rei_shadow_closed_loop_v2.py"; Destination = (Join-Path $CoreDir "rei_shadow_closed_loop_v2.py") },
    @{ Source = "sync_wheel_to_local.py"; Destination = (Join-Path $ReiHome "sync_wheel_to_local.py") },
    @{ Source = "bridge_to_wheel.py"; Destination = (Join-Path $ReiHome "bridge_to_wheel.py") },
    @{ Source = "sync_shadow_to_github.py"; Destination = (Join-Path $ReiHome "sync_shadow_to_github.py") },
    @{ Source = "REI-Unattended-Loop.ps1"; Destination = (Join-Path $ReiHome "REI-Unattended-Loop.ps1") },
    @{ Source = "REI-LocalSync.ps1"; Destination = (Join-Path $ReiHome "REI-LocalSync.ps1") },
    @{ Source = "README.md"; Destination = (Join-Path $ReiHome "REI-CLOSED-LOOP.md") }
)

try {
    foreach ($item in $manifest) {
        $stagedPath = Join-Path $stage $item.Source
        Invoke-WebRequest -Uri "$RawRoot/$($item.Source)" -OutFile $stagedPath -UseBasicParsing
        if (-not (Test-Path -LiteralPath $stagedPath) -or (Get-Item -LiteralPath $stagedPath).Length -eq 0) {
            throw "Downloaded file is empty: $($item.Source)"
        }
        $item.Staged = $stagedPath
    }

    $pythonFiles = $manifest | Where-Object { $_.Source.EndsWith(".py") } | ForEach-Object { $_.Staged }
    & $resolvedPython -m py_compile @pythonFiles
    if ($LASTEXITCODE -ne 0) { throw "Python syntax validation failed; no installed file was replaced." }

    foreach ($item in $manifest) {
        $destination = [string]$item.Destination
        if (Test-Path -LiteralPath $destination) {
            Copy-Item -LiteralPath $destination -Destination (Join-Path $backup ([IO.Path]::GetFileName($destination))) -Force
        }
        Copy-Item -LiteralPath $item.Staged -Destination $destination -Force
    }

    $supervisor = Join-Path $ReiHome "REI-Unattended-Loop.ps1"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $supervisor `
        -Install -ReiHome $ReiHome -PythonExe $resolvedPython -IntervalSeconds $IntervalSeconds
    if ($LASTEXITCODE -ne 0) { throw "Scheduled-task installation failed. Backups remain at $backup" }

    Write-Host "REI bidirectional unattended loop installed and started."
    Write-Host "Pinned source commit: $PinnedCommit"
    Write-Host "Backup: $backup"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $supervisor -Status -ReiHome $ReiHome
}
finally {
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
}
