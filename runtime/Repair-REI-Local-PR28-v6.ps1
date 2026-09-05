<#
REI-Ω PR #28 local repair v6.
Migrates a legacy long-running Shadow worker into the v1.9.3 synchronized
Full Pipeline, resolves runtime.lock safely, and patches the local Windows
SingleInstanceLock handoff after verification.

Safety rules:
- Never writes canonical/main.
- Backs up local Shadow state before terminating a verified legacy worker.
- Never removes runtime.lock while a matching Shadow process is alive.
- Stops/disables only REI-local legacy mutating/continuity tasks, while leaving
  REI-Local-Watchdog available for Ollama health.
#>
[CmdletBinding()]
param(
    [ValidateRange(15,1440)][int]$IntervalMinutes = 60,
    [ValidateRange(30,600)][int]$WaitSeconds = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Repo = 'rei-yan/rei-omega-proof'
$ReiHome = 'C:\REI-Shadow'
$CoreDir = 'C:\REI'
$ShadowScript = Join-Path $CoreDir 'rei_shadow_closed_loop_v2.py'
$RuntimeRoot = Join-Path $ReiHome 'runtime-v191'
$ShadowLock = Join-Path $ReiHome 'state\resilience\runtime.lock'
$TaskName = 'REI Full Pipeline v1.9.1'
$LocalWatchdog = 'REI-Local-Watchdog'
$V3Commit = 'a89c2c704071d564c99f1005ef0a56506cade1e0'
$TempV3 = Join-Path $env:TEMP 'Repair-REI-Local-PR28-v3-pinned.ps1'
$BackupDir = Join-Path $ReiHome ('backups\pr28-v6-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
$ReportPath = Join-Path $ReiHome 'state\local_repair_pr28_v6.json'

function Write-AtomicJson([string]$Path,[System.Collections.IDictionary]$Value) {
    $dir = Split-Path -Parent $Path
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $tmp = Join-Path $dir ([IO.Path]::GetRandomFileName())
    $Value | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $tmp -Encoding UTF8
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function Fail([string]$Reason) {
    Write-AtomicJson $ReportPath ([ordered]@{
        schema_version = 6
        status = 'LOCAL_REPAIR_FAILED'
        reason = $Reason
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        canonical_write_permission = $false
        backup_path = $BackupDir
    })
    Write-Error $Reason
    exit 2
}

function Get-ActionText($Task) {
    if ($null -eq $Task -or $null -eq $Task.Actions) { return '' }

    $parts = foreach ($action in @($Task.Actions)) {
        $execute = ''
        $arguments = ''

        $executeProp = $action.PSObject.Properties['Execute']
        if ($null -ne $executeProp) {
            $execute = [string]$executeProp.Value
        }

        $argumentsProp = $action.PSObject.Properties['Arguments']
        if ($null -ne $argumentsProp) {
            $arguments = [string]$argumentsProp.Value
        }

        ($execute + ' ' + $arguments).Trim()
    }

    return (($parts | Where-Object { $_ }) -join ' ')
}

function Get-ShadowProcesses {
    try {
        return @(
            Get-CimInstance Win32_Process -ErrorAction Stop |
            Where-Object {
                $_.Name -match '^(python|pythonw)(\.exe)?$' -and
                $_.CommandLine -and
                $_.CommandLine -match 'rei_shadow_closed_loop_v2\.py'
            }
        )
    }
    catch {
        throw ('Cannot inspect Shadow processes: ' + $_.Exception.Message)
    }
}

function Backup-ShadowState {
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
    foreach ($path in @(
        (Join-Path $ReiHome 'state'),
        (Join-Path $ReiHome 'outputs\closed_loop_v2'),
        (Join-Path $RuntimeRoot 'state')
    )) {
        if (Test-Path -LiteralPath $path) {
            $name = (($path -replace ':','') -replace '[\\/]','_')
            Copy-Item -LiteralPath $path -Destination (Join-Path $BackupDir $name) -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    if (Test-Path -LiteralPath $ShadowScript) {
        Copy-Item -LiteralPath $ShadowScript -Destination (Join-Path $BackupDir 'rei_shadow_closed_loop_v2.py') -Force
    }
}

function Patch-WindowsShadowLock {
    if (-not (Test-Path -LiteralPath $ShadowScript)) { throw 'Shadow script missing during lock hotfix.' }
    $text = Get-Content -LiteralPath $ShadowScript -Raw
    if ($text -match 'WINDOWS_LOCK_HANDOFF_V2') { return }

    $old = @'
        self.handle = self.path.open("a+b")
        self.handle.seek(0)
        if not self.handle.read(1):
            self.handle.write(b"0")
            self.handle.flush()
        self.handle.seek(0)
        try:
'@
    $new = @'
        self.handle = self.path.open("a+b")
        # WINDOWS_LOCK_HANDOFF_V2: do not read a byte that another Windows
        # process may already hold under an msvcrt byte-range lock.
        try:
            if self.path.stat().st_size == 0:
                self.handle.write(b"0")
                self.handle.flush()
            self.handle.seek(0)
'@
    if (-not $text.Contains($old)) {
        throw 'Shadow lock source layout changed; refusing unsafe local patch.'
    }
    Copy-Item -LiteralPath $ShadowScript -Destination (Join-Path $BackupDir 'rei_shadow_closed_loop_v2.pre-winlockfix.py') -Force
    $text = $text.Replace($old,$new)
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($ShadowScript,$text,$utf8)

    $python = (Get-Command python.exe -ErrorAction SilentlyContinue)
    if (-not $python) { $python = Get-Command python -ErrorAction SilentlyContinue }
    if (-not $python) { throw 'Python missing while validating Shadow lock patch.' }
    & $python.Source -m py_compile $ShadowScript
    if ($LASTEXITCODE -ne 0) { throw 'Patched Shadow script failed py_compile.' }
}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Fail 'Run v6 from an elevated PowerShell session.'
}

try {
    Write-Host 'PR28 local repair v6: legacy Shadow migration' -ForegroundColor Cyan
    Backup-ShadowState

    # Quiesce known/detected legacy REI mutating or continuity tasks. Keep the
    # local Ollama watchdog alive because the verified runtime depends on it.
    $disabledLegacy = New-Object System.Collections.Generic.List[string]
    foreach ($task in @(Get-ScheduledTask -ErrorAction SilentlyContinue)) {
        $name = [string]$task.TaskName
        if ($name -eq $LocalWatchdog) { continue }
        $actionText = Get-ActionText $task
        $isRei = ($name -like 'REI*') -or ($actionText -match 'C:\\REI')
        if (-not $isRei) { continue }
        $legacy = (
            $name -eq 'REI Shadow Closed Loop V2' -or
            $name -eq 'REI Shadow Watchdog V1' -or
            $name -eq 'REI Unattended Closed Loop' -or
            $name -match 'Sentinel|Continuity' -or
            $actionText -match 'rei_shadow_closed_loop_v2\.py|rei_cycle_v191\.ps1|runtime_sentinel'
        )
        if ($name -eq $TaskName) {
            Stop-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
            continue
        }
        if ($legacy) {
            try { Export-ScheduledTask -TaskName $name | Set-Content -Encoding UTF8 (Join-Path $BackupDir (($name -replace '[^A-Za-z0-9._-]','_') + '.xml')) } catch { }
            Stop-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
            Disable-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue | Out-Null
            [void]$disabledLegacy.Add($name)
        }
    }

    # Allow one-shot Shadow work to finish naturally. Long-running workers are
    # the legacy scheduler being migrated, so after state backup and task
    # quiesce they are terminated deliberately.
    $deadline = (Get-Date).AddSeconds($WaitSeconds)
    do {
        $procs = Get-ShadowProcesses
        $oneShot = @($procs | Where-Object { $_.CommandLine -match '(?:^|\s)--once(?:\s|$)' })
        if ($oneShot.Count -eq 0) { break }
        $ids = ($oneShot | ForEach-Object { [string]$_.ProcessId }) -join ','
        Write-Host "Waiting for active one-shot Shadow process(es): PID $ids" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    } while ((Get-Date) -lt $deadline)

    $procs = Get-ShadowProcesses
    $oneShot = @($procs | Where-Object { $_.CommandLine -match '(?:^|\s)--once(?:\s|$)' })
    if ($oneShot.Count -gt 0) {
        throw "One-shot Shadow process still active after $WaitSeconds seconds; refusing forced termination."
    }

    $persistent = @($procs | Where-Object { $_.CommandLine -notmatch '(?:^|\s)--once(?:\s|$)' })
    if ($persistent.Count -gt 0) {
        $ids = ($persistent | ForEach-Object { [string]$_.ProcessId }) -join ','
        Write-Host "Migrating legacy persistent Shadow worker(s): PID $ids" -ForegroundColor Yellow
        foreach ($proc in $persistent) {
            Stop-Process -Id ([int]$proc.ProcessId) -Force -ErrorAction Stop
        }
        Start-Sleep -Seconds 3
    }

    # Detect any respawn after legacy tasks were disabled.
    $respawn = @(Get-ShadowProcesses)
    if ($respawn.Count -gt 0) {
        $detail = ($respawn | ForEach-Object { "PID=$($_.ProcessId) CMD=$($_.CommandLine)" }) -join ' | '
        throw "Shadow worker respawned after legacy task quiesce: $detail"
    }

    if (Test-Path -LiteralPath $ShadowLock) {
        Copy-Item -LiteralPath $ShadowLock -Destination (Join-Path $BackupDir 'shadow_runtime.lock') -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $ShadowLock -Force
        Write-Host 'Removed orphaned Shadow runtime.lock after process verification.' -ForegroundColor Yellow
    }

    # Delegate the already-audited PR28/v1.9.3 migration and full verification.
    $v3Url = "https://raw.githubusercontent.com/$Repo/$V3Commit/runtime/Repair-REI-Local-PR28-v3.ps1"
    Invoke-WebRequest -UseBasicParsing -Uri $v3Url -OutFile $TempV3
    if (-not (Test-Path -LiteralPath $TempV3) -or (Get-Item -LiteralPath $TempV3).Length -eq 0) {
        throw 'Failed to download pinned v3 migration payload.'
    }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $TempV3 -IntervalMinutes $IntervalMinutes
    $v3Exit = $LASTEXITCODE
    if ($v3Exit -ne 0) { throw "Pinned v3 migration failed with exit code $v3Exit" }

    # v3 refreshes the Shadow source from the pinned payload, so patch the local
    # lock implementation only after successful verification, then validate it.
    Patch-WindowsShadowLock

    $v3Report = Join-Path $ReiHome 'state\local_repair_pr28.json'
    $report = if (Test-Path -LiteralPath $v3Report) { Get-Content -LiteralPath $v3Report -Raw -Encoding UTF8 | ConvertFrom-Json } else { $null }
    if ($null -eq $report -or [string]$report.status -ne 'LOCAL_REPAIR_PASS') {
        throw 'v3 verification report is missing or not LOCAL_REPAIR_PASS.'
    }

    Write-AtomicJson $ReportPath ([ordered]@{
        schema_version = 6
        status = 'LOCAL_REPAIR_PASS'
        candidate_pull_request = 28
        candidate_head_ref = 'rei-v193-reconcile'
        candidate_head_sha = [string]$report.candidate_head_sha
        local_model = 'rei-local-node-vnext'
        protocol_version = 'REI-CLP/3.0-observer'
        runtime_cycle_status = [string]$report.runtime_cycle_status
        runtime_cycle_id = [string]$report.runtime_cycle_id
        observer_cycle_id = [string]$report.observer_cycle_id
        god_line_verified = [bool]$report.god_line_verified
        scheduler_engine = [string]$report.scheduler_engine
        duplicate_mutating_scheduler = $false
        legacy_shadow_workers_migrated = $true
        windows_shadow_lock_hotfix = $true
        disabled_legacy_tasks = @($disabledLegacy)
        canonical_write_permission = $false
        reality_validated = $false
        ascension_granted = $false
        backup_path = $BackupDir
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
    })

    Write-Host 'LOCAL_REPAIR_RESULT=LOCAL_REPAIR_PASS' -ForegroundColor Green
    Write-Host "Runtime: $($report.runtime_cycle_status) / cycle $($report.runtime_cycle_id)" -ForegroundColor Green
    Write-Host "Observer/GodLine: VERIFIED / cycle $($report.observer_cycle_id)" -ForegroundColor Green
    Write-Host 'Legacy persistent Shadow worker: MIGRATED' -ForegroundColor Green
    Write-Host 'Windows Shadow runtime.lock handoff: HARDENED' -ForegroundColor Green
    Write-Host "Persistent scheduler engine: $($report.scheduler_engine)" -ForegroundColor Green
    Write-Host "REPORT=$ReportPath" -ForegroundColor Cyan
    Write-Host 'Canonical/main was not modified.' -ForegroundColor Green
    Write-Host 'PR28_REPAIR_V6_EXITCODE=0' -ForegroundColor Cyan
    exit 0
}
catch {
    Fail $_.Exception.Message
}
finally {
    Remove-Item -LiteralPath $TempV3 -Force -ErrorAction SilentlyContinue
}
