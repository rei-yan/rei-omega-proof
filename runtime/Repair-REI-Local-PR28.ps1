<#
REI-Ω v1.9.3 / PR #28 one-shot local repair + audit.
Purpose: migrate a Windows host to the reconciled candidate without touching canonical/main.
Run in an elevated PowerShell session.
#>
[CmdletBinding()]
param(
    [string]$ReiHome = 'C:\REI-Shadow',
    [string]$CoreDir = 'C:\REI',
    [int]$IntervalSeconds = 3600
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Branch = 'rei-v193-reconcile'
$RawRoot = "https://raw.githubusercontent.com/rei-yan/rei-omega-proof/$Branch/local_shadow"
$RuntimeRawRoot = "https://raw.githubusercontent.com/rei-yan/rei-omega-proof/$Branch/runtime"
$CandidatePR = 28
$CandidateHeadRef = 'rei-v193-reconcile'
$Protocol = 'REI-CLP/3.0-observer'
$ReportDir = Join-Path $ReiHome 'state'
$ReportPath = Join-Path $ReportDir 'local_repair_pr28.json'
$BackupDir = Join-Path $ReiHome ('backups\pr28-repair-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
$PipelineTask = 'REI Full Pipeline v1.9.1'
$StandaloneTask = 'REI Unattended Closed Loop'
$WatchdogTask = 'REI-Local-Watchdog'

function Fail([string]$Reason) {
    New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
    [ordered]@{
        schema_version = 1
        status = 'LOCAL_REPAIR_FAILED'
        reason = $Reason
        candidate_pull_request = $CandidatePR
        candidate_head_ref = $CandidateHeadRef
        protocol_version = $Protocol
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        canonical_write_permission = $false
    } | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $ReportPath
    Write-Error $Reason
    exit 2
}

function Download([string]$Url,[string]$Path) {
    $dir = Split-Path -Parent $Path
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Path
    if (-not (Test-Path $Path) -or (Get-Item $Path).Length -eq 0) { throw "Empty download: $Url" }
}

function Backup([string]$Path) {
    if (Test-Path $Path) {
        New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
        Copy-Item $Path (Join-Path $BackupDir ([IO.Path]::GetFileName($Path))) -Force
    }
}

function Resolve-Python {
    foreach ($candidate in @('python.exe','python','py.exe','py')) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    throw 'Python not found in PATH.'
}

function Read-JsonSafe([string]$Path) {
    if (-not (Test-Path $Path)) { return $null }
    try { return (Get-Content $Path -Raw | ConvertFrom-Json) } catch { return $null }
}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Fail 'Run this repair from an elevated PowerShell session.'
}

try {
    $python = Resolve-Python
    if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { throw 'git.exe not found.' }
    if (-not (Get-Command ollama.exe -ErrorAction SilentlyContinue)) { throw 'ollama.exe not found.' }

    New-Item -ItemType Directory -Force -Path $ReiHome,$CoreDir,$ReportDir,$BackupDir | Out-Null

    $manifest = @(
        @{src='REI-LocalSync.ps1'; dst=(Join-Path $ReiHome 'REI-LocalSync.ps1')},
        @{src='REI-LocalModel-VNext.ps1'; dst=(Join-Path $ReiHome 'REI-LocalModel-VNext.ps1')},
        @{src='sync_wheel_to_local.py'; dst=(Join-Path $ReiHome 'sync_wheel_to_local.py')},
        @{src='vnext_observer.py'; dst=(Join-Path $ReiHome 'vnext_observer.py')},
        @{src='bridge_to_wheel_vnext.py'; dst=(Join-Path $ReiHome 'bridge_to_wheel_vnext.py')},
        @{src='sync_shadow_to_github.py'; dst=(Join-Path $ReiHome 'sync_shadow_to_github.py')},
        @{src='REI-Unattended-Loop-VNext.ps1'; dst=(Join-Path $ReiHome 'REI-Unattended-Loop-VNext.ps1')},
        @{src='rei_shadow_closed_loop_v2.py'; dst=(Join-Path $CoreDir 'rei_shadow_closed_loop_v2.py')}
    )

    foreach ($m in $manifest) {
        Backup $m.dst
        Download "$RawRoot/$($m.src)" $m.dst
    }

    foreach ($py in @((Join-Path $ReiHome 'sync_wheel_to_local.py'),(Join-Path $ReiHome 'vnext_observer.py'),(Join-Path $ReiHome 'bridge_to_wheel_vnext.py'),(Join-Path $ReiHome 'sync_shadow_to_github.py'),(Join-Path $CoreDir 'rei_shadow_closed_loop_v2.py'))) {
        & $python -m py_compile $py
        if ($LASTEXITCODE -ne 0) { throw "Python syntax validation failed: $py" }
    }

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ReiHome 'REI-LocalSync.ps1') -Once -PullRequest 28 -ContextOnly
    if ($LASTEXITCODE -ne 0) { throw 'PR28 context sync failed.' }

    $ctx = Read-JsonSafe (Join-Path $ReiHome 'context\sync_state.json')
    if ($null -eq $ctx -or [int]$ctx.pull_request -ne 28 -or [string]$ctx.head_ref -ne $CandidateHeadRef -or [string]::IsNullOrWhiteSpace([string]$ctx.head_sha)) {
        throw 'Context is not pinned to PR #28 / rei-v193-reconcile.'
    }

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ReiHome 'REI-LocalModel-VNext.ps1') -ContextDir (Join-Path $ReiHome 'context')
    if ($LASTEXITCODE -ne 0) { throw 'Local vNext model refresh failed.' }

    $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 5
    $modelNames = @($tags.models | ForEach-Object { $_.name })
    if (-not ($modelNames | Where-Object { $_ -like 'rei-local-node-vnext*' })) { throw 'rei-local-node-vnext is missing from Ollama.' }

    $pipeline = Get-ScheduledTask -TaskName $PipelineTask -ErrorAction SilentlyContinue
    $standalone = Get-ScheduledTask -TaskName $StandaloneTask -ErrorAction SilentlyContinue
    if ($pipeline -and $standalone) {
        Stop-ScheduledTask -TaskName $StandaloneTask -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $StandaloneTask -Confirm:$false
        $standalone = $null
    }

    if (-not $pipeline) {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ReiHome 'REI-Unattended-Loop-VNext.ps1') -Install -ReiHome $ReiHome -PythonExe $python -IntervalSeconds $IntervalSeconds
        if ($LASTEXITCODE -ne 0) { throw 'vNext scheduler installation failed.' }
        $standalone = Get-ScheduledTask -TaskName $StandaloneTask -ErrorAction SilentlyContinue
    }

    if ($pipeline) {
        Start-ScheduledTask -TaskName $PipelineTask -ErrorAction Stop
    } else {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ReiHome 'REI-Unattended-Loop-VNext.ps1') -Once -ReiHome $ReiHome -PythonExe $python
        if ($LASTEXITCODE -ne 0) { throw 'One-shot vNext cycle failed.' }
    }

    Start-Sleep -Seconds 5

    $watchdog = Get-ScheduledTask -TaskName $WatchdogTask -ErrorAction SilentlyContinue
    if (-not $watchdog) { throw 'REI-Local-Watchdog task missing.' }
    $watchdogInfo = Get-ScheduledTaskInfo -TaskName $WatchdogTask
    if ($watchdogInfo.LastRunTime -eq [DateTime]::MinValue -or $watchdogInfo.LastTaskResult -ne 0) {
        throw "Watchdog unhealthy: LastTaskResult=$($watchdogInfo.LastTaskResult) LastRunTime=$($watchdogInfo.LastRunTime)"
    }

    $observer = Read-JsonSafe (Join-Path $ReiHome 'state\vnext_observer\latest.json')
    if ($null -eq $observer -or [string]$observer.protocol_version -ne $Protocol -or -not [bool]$observer.observer_mode -or [bool]$observer.canonical_write_permission) {
        throw 'vNext Observer / God Line state is missing or invalid.'
    }
    if ([bool]$observer.promotion_gate_v2.may_promote_canonical -or [bool]$observer.promotion_gate_v2.may_grant_reality_validation -or [bool]$observer.promotion_gate_v2.may_grant_ascension) {
        throw 'Observer authority boundary violated.'
    }

    $recoveryRoot = 'C:\REI_Resilience_Layer_v1\checkpoints'
    if (-not (Test-Path $recoveryRoot)) { throw 'Recovery checkpoint root missing.' }
    $checkpoint = Get-ChildItem $recoveryRoot -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($null -eq $checkpoint -or -not (Test-Path (Join-Path $checkpoint.FullName 'checkpoint.json'))) {
        throw 'No readable recovery checkpoint found.'
    }

    $heartbeat = Read-JsonSafe (Join-Path $ReiHome 'state\unattended_heartbeat.json')
    $runtimeState = Read-JsonSafe (Join-Path $ReiHome 'runtime-v191\state\last-cycle.json')
    $pipelineInfo = if ($pipeline) { Get-ScheduledTaskInfo -TaskName $PipelineTask } else { $null }

    $status = 'LOCAL_REPAIR_PASS'
    if ($pipeline -and ($pipelineInfo.LastRunTime -eq [DateTime]::MinValue -or $pipelineInfo.LastTaskResult -ne 0)) {
        $status = 'LOCAL_REPAIR_PASS_PIPELINE_FRESH_RUN_PENDING'
    }

    [ordered]@{
        schema_version = 1
        status = $status
        candidate_pull_request = 28
        candidate_head_ref = $CandidateHeadRef
        candidate_head_sha = [string]$ctx.head_sha
        protocol_version = $Protocol
        local_model = 'rei-local-node-vnext'
        model_present = $true
        scheduler_authority = $(if($pipeline){$PipelineTask}else{$StandaloneTask})
        duplicate_mutating_scheduler = $false
        watchdog_last_task_result = $watchdogInfo.LastTaskResult
        watchdog_last_run_time = $watchdogInfo.LastRunTime.ToString('o')
        observer_cycle_id = [string]$observer.cycle_id
        god_line_verified = $true
        recovery_checkpoint = $checkpoint.FullName
        heartbeat = $heartbeat
        runtime_state = $runtimeState
        canonical_write_permission = $false
        reality_validated = $false
        ascension_granted = $false
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        backup_path = $BackupDir
    } | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 $ReportPath

    Write-Host "LOCAL_REPAIR_RESULT=$status" -ForegroundColor Green
    Write-Host "REPORT=$ReportPath" -ForegroundColor Cyan
    Write-Host "Candidate: PR #28 / $CandidateHeadRef / $($ctx.head_sha)" -ForegroundColor Cyan
    Write-Host 'Canonical/main was not modified.' -ForegroundColor Green
}
catch {
    Fail $_.Exception.Message
}
