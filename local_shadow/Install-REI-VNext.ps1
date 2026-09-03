<#
Transactional one-time installer for REI Closed Loop Sync vNext.
Stages an immutable pinned revision, validates Python + PowerShell syntax,
backs up replaced files, runs observer self-test, installs the vNext scheduled
supervisor, and rolls files back if deployment fails.
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
$ProtocolVersion = "REI-CLP/3.0-observer"
$PinnedCommit = "90478956d0ca0bc3ac316ed25039062256aac911"
$RawRoot = "https://raw.githubusercontent.com/rei-yan/rei-omega-proof/$PinnedCommit/local_shadow"
$TaskName = "REI Unattended Closed Loop"

function Resolve-Python {
    if (Test-Path -LiteralPath $PythonExe) { return $PythonExe }
    foreach ($candidate in @("python.exe", "python", "py.exe", "py")) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    throw "Python not found."
}

function Write-AtomicUtf8 {
    param([string]$Path, [string]$Content)
    $directory = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    $temporary = Join-Path $directory ([IO.Path]::GetRandomFileName())
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($temporary, $Content, $utf8NoBom)
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

$resolvedPython = Resolve-Python
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) { throw "Git is not available in PATH." }
if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) { throw "Ollama is not available in PATH." }

New-Item -ItemType Directory -Path $ReiHome -Force | Out-Null
New-Item -ItemType Directory -Path $CoreDir -Force | Out-Null
$stamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$stage = Join-Path $env:TEMP "rei-vnext-$stamp"
$backup = Join-Path $ReiHome "backups\vnext-$stamp"
New-Item -ItemType Directory -Path $stage -Force | Out-Null
New-Item -ItemType Directory -Path $backup -Force | Out-Null

$manifest = @(
    @{ Source = "rei_shadow_closed_loop_v2.py"; Destination = (Join-Path $CoreDir "rei_shadow_closed_loop_v2.py") },
    @{ Source = "sync_wheel_to_local.py"; Destination = (Join-Path $ReiHome "sync_wheel_to_local.py") },
    @{ Source = "sync_shadow_to_github.py"; Destination = (Join-Path $ReiHome "sync_shadow_to_github.py") },
    @{ Source = "REI-LocalSync.ps1"; Destination = (Join-Path $ReiHome "REI-LocalSync.ps1") },
    @{ Source = "vnext_observer.py"; Destination = (Join-Path $ReiHome "vnext_observer.py") },
    @{ Source = "bridge_to_wheel_vnext.py"; Destination = (Join-Path $ReiHome "bridge_to_wheel_vnext.py") },
    @{ Source = "REI-LocalModel-VNext.ps1"; Destination = (Join-Path $ReiHome "REI-LocalModel-VNext.ps1") },
    @{ Source = "REI-Unattended-Loop-VNext.ps1"; Destination = (Join-Path $ReiHome "REI-Unattended-Loop-VNext.ps1") },
    @{ Source = "VNEXT_CLOSED_LOOP_PROTOCOL.md"; Destination = (Join-Path $ReiHome "VNEXT_CLOSED_LOOP_PROTOCOL.md") }
)

$deployed = $false
try {
    foreach ($item in $manifest) {
        $stagedPath = Join-Path $stage $item.Source
        Invoke-WebRequest -Uri "$RawRoot/$($item.Source)" -OutFile $stagedPath -UseBasicParsing
        if (-not (Test-Path -LiteralPath $stagedPath) -or (Get-Item -LiteralPath $stagedPath).Length -eq 0) {
            throw "Downloaded file is empty: $($item.Source)"
        }
        $item.Staged = $stagedPath
        $item.HadExisting = Test-Path -LiteralPath ([string]$item.Destination)
    }

    $pythonFiles = $manifest | Where-Object { $_.Source.EndsWith(".py") } | ForEach-Object { $_.Staged }
    & $resolvedPython -m py_compile @pythonFiles
    if ($LASTEXITCODE -ne 0) { throw "Python syntax validation failed; deployment not started." }

    $observerStage = ($manifest | Where-Object { $_.Source -eq "vnext_observer.py" }).Staged
    & $resolvedPython $observerStage --self-test
    if ($LASTEXITCODE -ne 0) { throw "vNext observer self-test failed; deployment not started." }

    foreach ($psItem in ($manifest | Where-Object { $_.Source.EndsWith(".ps1") })) {
        $tokens = $null
        $errors = $null
        [void][System.Management.Automation.Language.Parser]::ParseFile($psItem.Staged, [ref]$tokens, [ref]$errors)
        if ($errors.Count -gt 0) {
            throw "PowerShell syntax validation failed for $($psItem.Source): $($errors[0].Message)"
        }
    }

    foreach ($item in $manifest) {
        $destination = [string]$item.Destination
        if ($item.HadExisting) {
            Copy-Item -LiteralPath $destination -Destination (Join-Path $backup ([IO.Path]::GetFileName($destination))) -Force
        }
        Copy-Item -LiteralPath $item.Staged -Destination $destination -Force
    }

    $supervisor = Join-Path $ReiHome "REI-Unattended-Loop-VNext.ps1"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $supervisor `
        -Install -ReiHome $ReiHome -PythonExe $resolvedPython -IntervalSeconds $IntervalSeconds
    if ($LASTEXITCODE -ne 0) { throw "vNext scheduled-task installation failed." }

    $installState = [ordered]@{
        schema_version = 1
        protocol_version = $ProtocolVersion
        pinned_commit = $PinnedCommit
        installed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        backup_path = $backup
        task_name = $TaskName
        observer_mode = $true
        canonical_write_permission = $false
    } | ConvertTo-Json -Depth 5
    Write-AtomicUtf8 -Path (Join-Path $ReiHome "state\vnext_installation.json") -Content $installState
    $deployed = $true

    Write-Host "REI vNext lockstep closed loop installed and started."
    Write-Host "Protocol: $ProtocolVersion"
    Write-Host "Pinned source commit: $PinnedCommit"
    Write-Host "Backup: $backup"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $supervisor -Status -ReiHome $ReiHome
}
catch {
    Write-Warning "vNext deployment failed: $($_.Exception.Message)"
    Write-Warning "Restoring pre-install files."
    foreach ($item in $manifest) {
        $destination = [string]$item.Destination
        $backupFile = Join-Path $backup ([IO.Path]::GetFileName($destination))
        if ($item.HadExisting -and (Test-Path -LiteralPath $backupFile)) {
            Copy-Item -LiteralPath $backupFile -Destination $destination -Force
        }
        elseif (-not $item.HadExisting -and (Test-Path -LiteralPath $destination)) {
            Remove-Item -LiteralPath $destination -Force -ErrorAction SilentlyContinue
        }
    }
    $oldSupervisor = Join-Path $ReiHome "REI-Unattended-Loop.ps1"
    if (Test-Path -LiteralPath $oldSupervisor) {
        try {
            & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $oldSupervisor `
                -Install -ReiHome $ReiHome -PythonExe $resolvedPython -IntervalSeconds $IntervalSeconds | Out-Null
            Write-Warning "Previous unattended supervisor was reinstalled."
        }
        catch { Write-Warning "Automatic previous-supervisor restore failed; files were restored but task should be checked." }
    }
    throw
}
finally {
    Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
}
