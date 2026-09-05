<#
REI Sync Parity Guard v1 transactional hot-patch installer.

Scope is deliberately narrow: replace only sync_shadow_to_github.py with the
pinned parity-aware transport, validate it, run one bootstrap sync, and roll
back the old file if validation or bootstrap fails.

This installer does NOT modify canonical/main, God Core, God Wheel logic, the
scheduler, Ollama, Observer, Bridge, or any checkpoint/rollback policy.
#>
[CmdletBinding()]
param(
    [string]$ReiHome = "C:\REI-Shadow",
    [string]$RuntimeHome = "C:\REI",
    [string]$Repo = "C:\REI-Shadow\repo",
    [string]$PythonExe = "C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PinnedCommit = "0d50680106f8488e9f417bacaa299a6366248a27"
$RawUrl = "https://raw.githubusercontent.com/rei-yan/rei-omega-proof/$PinnedCommit/local_shadow/sync_shadow_to_github.py"
$Target = Join-Path $ReiHome "sync_shadow_to_github.py"
$StateDir = Join-Path $ReiHome "state"
$Receipt = Join-Path $StateDir "sync_parity_receipt.json"

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

$python = Resolve-Python
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) { throw "Git is not available in PATH." }
if (-not (Test-Path -LiteralPath $Repo)) { throw "Shadow repo not found: $Repo" }
if (-not (Test-Path -LiteralPath $RuntimeHome)) { throw "Runtime home not found: $RuntimeHome" }

$stamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$stage = Join-Path $env:TEMP "rei-sync-parity-$stamp.py"
$backupDir = Join-Path $ReiHome "backups\sync-parity-$stamp"
$backup = Join-Path $backupDir "sync_shadow_to_github.py"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
$hadExisting = Test-Path -LiteralPath $Target

try {
    Invoke-WebRequest -Uri $RawUrl -OutFile $stage -UseBasicParsing
    if (-not (Test-Path -LiteralPath $stage) -or (Get-Item -LiteralPath $stage).Length -lt 1024) {
        throw "Downloaded parity transport is missing or unexpectedly small."
    }

    & $python -m py_compile $stage
    if ($LASTEXITCODE -ne 0) { throw "Python syntax validation failed." }

    if ($hadExisting) { Copy-Item -LiteralPath $Target -Destination $backup -Force }
    Copy-Item -LiteralPath $stage -Destination $Target -Force

    Write-Host "Sync Parity Guard payload installed. Bootstrapping one receipt..."
    $output = & $python $Target --home $ReiHome --runtime-home $RuntimeHome --repo $Repo 2>&1
    $code = $LASTEXITCODE
    $output | ForEach-Object { Write-Host $_ }
    if ($null -eq $code) { $code = 0 }
    if ($code -ne 0) { throw "Bootstrap parity sync failed with exit code $code." }

    if (-not (Test-Path -LiteralPath $Receipt)) {
        throw "Bootstrap completed but local parity receipt was not created: $Receipt"
    }

    $receiptJson = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace([string]$receiptJson.source_cycle_id)) {
        throw "Parity receipt is missing source_cycle_id."
    }
    if ([string]::IsNullOrWhiteSpace([string]$receiptJson.source_sha256)) {
        throw "Parity receipt is missing source_sha256."
    }
    if ([bool]$receiptJson.canonical_write_permission) {
        throw "Safety invariant failed: canonical_write_permission must remain false."
    }

    $state = [ordered]@{
        schema_version = 1
        guard = "REI Sync Parity Guard v1"
        status = "INSTALLED_BOOTSTRAP_VERIFIED"
        pinned_commit = $PinnedCommit
        installed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        source_cycle_id = [string]$receiptJson.source_cycle_id
        source_sha256 = [string]$receiptJson.source_sha256
        backup_path = $(if ($hadExisting) { $backup } else { $null })
        canonical_mainline_touched = $false
        canonical_write_permission = $false
    } | ConvertTo-Json -Depth 5
    Write-AtomicUtf8 -Path (Join-Path $StateDir "sync_parity_guard.json") -Content $state

    Write-Host ""
    Write-Host "SYNC_PARITY_GUARD_INSTALLED" -ForegroundColor Green
    Write-Host "Status: INSTALLED_BOOTSTRAP_VERIFIED"
    Write-Host "Source cycle: $($receiptJson.source_cycle_id)"
    Write-Host "Source SHA256: $($receiptJson.source_sha256)"
    Write-Host "Pinned commit: $PinnedCommit"
    Write-Host "Canonical mainline touched: FALSE"
}
catch {
    Write-Warning "Sync Parity Guard install failed: $($_.Exception.Message)"
    if ($hadExisting -and (Test-Path -LiteralPath $backup)) {
        Copy-Item -LiteralPath $backup -Destination $Target -Force
        Write-Warning "Previous sync transport restored from backup."
    }
    elseif (-not $hadExisting -and (Test-Path -LiteralPath $Target)) {
        Remove-Item -LiteralPath $Target -Force -ErrorAction SilentlyContinue
    }
    throw
}
finally {
    Remove-Item -LiteralPath $stage -Force -ErrorAction SilentlyContinue
}
