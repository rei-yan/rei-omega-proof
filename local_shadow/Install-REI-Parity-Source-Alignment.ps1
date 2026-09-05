<#
REI-Ω Parity Source Alignment hotfix.

Fixes a narrow routing mismatch: the authoritative v1.9.3 pipeline now writes fresh
closed-loop cycles under C:\REI-Shadow\outputs\closed_loop_v2, while the parity
transport's default runtime root still points at C:\REI.

This installer patches only C:\REI-Shadow\sync_shadow_to_github.py, backs it up,
validates Python syntax, bootstraps one sync against C:\REI-Shadow, verifies the
receipt points at the freshest Shadow-home cycle, and rolls back on failure.

It does NOT modify canonical/main, God Core, God Wheel logic, Observer, Bridge,
model payloads, checkpoints, or Task Scheduler configuration.
#>
[CmdletBinding()]
param(
    [string]$ReiHome = "C:\REI-Shadow",
    [string]$Repo = "C:\REI-Shadow\repo",
    [string]$PythonExe = "C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Target = Join-Path $ReiHome "sync_shadow_to_github.py"
$CycleDir = Join-Path $ReiHome "outputs\closed_loop_v2"
$Receipt = Join-Path $ReiHome "state\sync_parity_receipt.json"
$StateDir = Join-Path $ReiHome "state"

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
if (-not (Test-Path -LiteralPath $Target)) { throw "Parity transport not found: $Target" }
if (-not (Test-Path -LiteralPath $Repo)) { throw "Shadow repo not found: $Repo" }
if (-not (Test-Path -LiteralPath $CycleDir)) { throw "Authoritative cycle directory not found: $CycleDir" }

$latest = Get-ChildItem -LiteralPath $CycleDir -Filter "cycle_*.json" -File |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if (-not $latest) { throw "No cycle_*.json found under $CycleDir" }

$latestJson = Get-Content -LiteralPath $latest.FullName -Raw | ConvertFrom-Json
$expectedCycleId = $null
foreach ($name in @("cycle_id","cycle","id")) {
    if ($latestJson.PSObject.Properties.Name -contains $name) {
        $value = [string]$latestJson.$name
        if (-not [string]::IsNullOrWhiteSpace($value)) { $expectedCycleId = $value; break }
    }
}
if ([string]::IsNullOrWhiteSpace($expectedCycleId)) {
    $expectedCycleId = [IO.Path]::GetFileNameWithoutExtension($latest.Name)
    if ($expectedCycleId.StartsWith("cycle_")) { $expectedCycleId = $expectedCycleId.Substring(6) }
}

$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$backupDir = Join-Path $ReiHome "backups\parity-source-alignment-$stamp"
$backup = Join-Path $backupDir "sync_shadow_to_github.py"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
New-Item -ItemType Directory -Path $StateDir -Force | Out-Null
Copy-Item -LiteralPath $Target -Destination $backup -Force

try {
    $text = Get-Content -LiteralPath $Target -Raw
    $old = 'default=os.getenv("REI_RUNTIME_HOME", r"C:\REI")'
    $new = 'default=os.getenv("REI_RUNTIME_HOME", r"C:\REI-Shadow")'

    if ($text.Contains($old)) {
        $text = $text.Replace($old, $new)
        Write-AtomicUtf8 -Path $Target -Content $text
    }
    elseif (-not $text.Contains($new)) {
        throw "Expected runtime-home default pattern not found; refusing blind patch."
    }

    & $python -m py_compile $Target
    if ($LASTEXITCODE -ne 0) { throw "Python syntax validation failed." }

    Write-Host "Parity source aligned. Bootstrapping against authoritative runtime root..."
    $output = & $python $Target --home $ReiHome --runtime-home $ReiHome --repo $Repo 2>&1
    $code = $LASTEXITCODE
    $output | ForEach-Object { Write-Host $_ }
    if ($null -eq $code) { $code = 0 }
    if ($code -ne 0) { throw "Parity bootstrap failed with exit code $code." }

    if (-not (Test-Path -LiteralPath $Receipt)) { throw "Parity receipt missing after bootstrap: $Receipt" }
    $receiptJson = Get-Content -LiteralPath $Receipt -Raw | ConvertFrom-Json

    if ([string]$receiptJson.source_file -ne $latest.Name) {
        throw "Receipt source mismatch. Expected $($latest.Name), got $($receiptJson.source_file)."
    }
    if ([string]$receiptJson.source_cycle_id -ne $expectedCycleId) {
        throw "Receipt cycle mismatch. Expected $expectedCycleId, got $($receiptJson.source_cycle_id)."
    }
    if ([bool]$receiptJson.canonical_write_permission) {
        throw "Safety invariant failed: canonical_write_permission must remain false."
    }

    $state = [ordered]@{
        schema_version = 1
        repair = "REI Parity Source Alignment"
        status = "SOURCE_ALIGNED_BOOTSTRAP_VERIFIED"
        authoritative_runtime_home = $ReiHome
        source_cycle_id = [string]$receiptJson.source_cycle_id
        source_file = [string]$receiptJson.source_file
        source_sha256 = [string]$receiptJson.source_sha256
        installed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        backup_path = $backup
        canonical_mainline_touched = $false
        canonical_write_permission = $false
    } | ConvertTo-Json -Depth 5
    Write-AtomicUtf8 -Path (Join-Path $StateDir "parity_source_alignment.json") -Content $state

    Write-Host ""
    Write-Host "PARITY_SOURCE_ALIGNMENT_VERIFIED" -ForegroundColor Green
    Write-Host "Authoritative runtime home: $ReiHome"
    Write-Host "Source cycle: $($receiptJson.source_cycle_id)"
    Write-Host "Source file: $($receiptJson.source_file)"
    Write-Host "Canonical mainline touched: FALSE"
}
catch {
    Write-Warning "Parity source alignment failed: $($_.Exception.Message)"
    if (Test-Path -LiteralPath $backup) {
        Copy-Item -LiteralPath $backup -Destination $Target -Force
        Write-Warning "Previous parity transport restored from backup."
    }
    throw
}
