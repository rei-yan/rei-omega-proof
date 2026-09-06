<#
REI-Ω PR #28 local repair v3.
Migrates the existing Windows Full Pipeline task from the legacy v1.9.1 cycle
engine to the reconciled v1.9.3 observer runtime while preserving the task
name for Sentinel compatibility. Never writes canonical/main.
#>
[CmdletBinding()]
param(
    [string]$ReiHome = 'C:\REI-Shadow',
    [string]$CoreDir = 'C:\REI',
    [ValidateRange(15,1440)][int]$IntervalMinutes = 60
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Repo = 'rei-yan/rei-omega-proof'
$CandidatePR = 28
$CandidateHeadRef = 'rei-v193-reconcile'
$Protocol = 'REI-CLP/3.0-observer'
$PayloadCommit = 'd831e7b60eef51cbd9f0a8677b52dfb6a8df0895'
$PayloadRoot = "https://raw.githubusercontent.com/$Repo/$PayloadCommit/local_shadow"
$RuntimeRoot = Join-Path $ReiHome 'runtime-v191'
$StateDir = Join-Path $RuntimeRoot 'state'
$CycleScript = Join-Path $RuntimeRoot 'rei_cycle_v193.ps1'
$SourceShaFile = Join-Path $RuntimeRoot 'deployed-sha.txt'
$TaskName = 'REI Full Pipeline v1.9.1'
$StandaloneTask = 'REI Unattended Closed Loop'
$WatchdogTask = 'REI-Local-Watchdog'
$ReportDir = Join-Path $ReiHome 'state'
$ReportPath = Join-Path $ReportDir 'local_repair_pr28.json'
$BackupDir = Join-Path $ReiHome ('backups\pr28-v3-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Write-AtomicJson([string]$Path,[System.Collections.IDictionary]$Value) {
    $dir = Split-Path -Parent $Path
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $tmp = Join-Path $dir ([IO.Path]::GetRandomFileName())
    $Value | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $tmp -Encoding UTF8
    Move-Item -LiteralPath $tmp -Destination $Path -Force
}

function Fail([string]$Reason) {
    Write-AtomicJson $ReportPath ([ordered]@{
        schema_version = 3
        status = 'LOCAL_REPAIR_FAILED'
        reason = $Reason
        candidate_pull_request = $CandidatePR
        candidate_head_ref = $CandidateHeadRef
        protocol_version = $Protocol
        canonical_write_permission = $false
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        backup_path = $BackupDir
    })
    Write-Error $Reason
    exit 2
}

function Download([string]$Url,[string]$Path) {
    $dir = Split-Path -Parent $Path
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Path
    if (-not (Test-Path -LiteralPath $Path) -or (Get-Item -LiteralPath $Path).Length -eq 0) {
        throw "Empty download: $Url"
    }
}

function Backup-File([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
        Copy-Item -LiteralPath $Path -Destination (Join-Path $BackupDir ([IO.Path]::GetFileName($Path))) -Force
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
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try { return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}

$principalCheck = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principalCheck.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Fail 'Run this repair from an elevated PowerShell session.'
}

try {
    $python = Resolve-Python
    if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { throw 'git.exe not found.' }
    if (-not (Get-Command ollama.exe -ErrorAction SilentlyContinue)) { throw 'ollama.exe not found.' }

    New-Item -ItemType Directory -Force -Path $ReiHome,$CoreDir,$RuntimeRoot,$StateDir,$ReportDir,$BackupDir | Out-Null

    Write-Host 'PR28 local repair v3: payload refresh' -ForegroundColor Cyan
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
        Backup-File $m.dst
        Download "$PayloadRoot/$($m.src)" $m.dst
    }

    foreach ($py in @(
        (Join-Path $ReiHome 'sync_wheel_to_local.py'),
        (Join-Path $ReiHome 'vnext_observer.py'),
        (Join-Path $ReiHome 'bridge_to_wheel_vnext.py'),
        (Join-Path $ReiHome 'sync_shadow_to_github.py'),
        (Join-Path $CoreDir 'rei_shadow_closed_loop_v2.py')
    )) {
        & $python -m py_compile $py
        if ($LASTEXITCODE -ne 0) { throw "Python syntax validation failed: $py" }
    }

    Write-Host 'Synchronizing reconciled PR28 context...' -ForegroundColor Cyan
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ReiHome 'REI-LocalSync.ps1') -Once -PullRequest 28 -ContextOnly
    if ($LASTEXITCODE -ne 0) { throw 'PR28 context sync failed.' }

    $ctx = Read-JsonSafe (Join-Path $ReiHome 'context\sync_state.json')
    if ($null -eq $ctx -or [int]$ctx.pull_request -ne 28 -or [string]$ctx.head_ref -ne $CandidateHeadRef -or [string]::IsNullOrWhiteSpace([string]$ctx.head_sha)) {
        throw 'Context is not pinned to PR #28 / rei-v193-reconcile.'
    }
    $candidateSha = [string]$ctx.head_sha

    Write-Host "Pinning v1.9.3 runtime to $candidateSha" -ForegroundColor Cyan
    Backup-File $CycleScript
    Download "https://raw.githubusercontent.com/$Repo/$candidateSha/runtime/rei_cycle_v193.ps1" $CycleScript
    Set-Content -LiteralPath $SourceShaFile -Value $candidateSha -Encoding ASCII

    $parseErrors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($CycleScript,[ref]$null,[ref]$parseErrors)
    if ($parseErrors -and $parseErrors.Count -gt 0) {
        throw ('v1.9.3 runtime PowerShell parse failed: ' + (($parseErrors | ForEach-Object {$_.Message}) -join '; '))
    }

    Write-Host 'Refreshing exact local vNext model...' -ForegroundColor Cyan
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ReiHome 'REI-LocalModel-VNext.ps1') -ContextDir (Join-Path $ReiHome 'context')
    if ($LASTEXITCODE -ne 0) { throw 'Local vNext model refresh failed.' }
    $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 5
    $modelNames = @($tags.models | ForEach-Object { $_.name })
    if (-not ($modelNames | Where-Object { $_ -like 'rei-local-node-vnext*' })) { throw 'rei-local-node-vnext is missing from Ollama.' }

    Write-Host 'Quiescing legacy schedulers...' -ForegroundColor Cyan
    $oldTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($oldTask) {
        try { Export-ScheduledTask -TaskName $TaskName | Set-Content -Encoding UTF8 (Join-Path $BackupDir 'REI Full Pipeline v1.9.1.xml') } catch { }
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    }
    $standalone = Get-ScheduledTask -TaskName $StandaloneTask -ErrorAction SilentlyContinue
    if ($standalone) {
        try { Export-ScheduledTask -TaskName $StandaloneTask | Set-Content -Encoding UTF8 (Join-Path $BackupDir 'REI Unattended Closed Loop.xml') } catch { }
        Stop-ScheduledTask -TaskName $StandaloneTask -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $StandaloneTask -Confirm:$false
    }
    Start-Sleep -Seconds 2

    $lockPath = Join-Path $RuntimeRoot 'cycle.lock'
    if (Test-Path -LiteralPath $lockPath) {
        $ageMinutes = ((Get-Date) - (Get-Item -LiteralPath $lockPath).LastWriteTime).TotalMinutes
        if ($ageMinutes -lt 5) { throw "Runtime cycle lock is still fresh ($([Math]::Round($ageMinutes,1)) min); another cycle may still be active." }
        Backup-File $lockPath
        Remove-Item -LiteralPath $lockPath -Force
        Write-Host 'Removed stale runtime cycle lock after scheduler quiesce.' -ForegroundColor Yellow
    }

    Write-Host 'Executing one full v1.9.3 synchronized verification cycle...' -ForegroundColor Cyan
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $CycleScript
    $cycleExit = $LASTEXITCODE
    if ($cycleExit -ne 0) {
        $failedState = Read-JsonSafe (Join-Path $StateDir 'last-cycle.json')
        $reason = if ($failedState -and $failedState.reason) { [string]$failedState.reason } else { "exit code $cycleExit" }
        throw "v1.9.3 synchronized cycle failed: $reason"
    }

    $last = Read-JsonSafe (Join-Path $StateDir 'last-cycle.json')
    if ($null -eq $last -or [string]$last.cycle_status -ne 'SUCCESS_RUNTIME_VERIFIED') {
        throw 'Runtime did not produce SUCCESS_RUNTIME_VERIFIED.'
    }

    $observer = Read-JsonSafe (Join-Path $ReiHome 'state\vnext_observer\latest.json')
    if ($null -eq $observer -or [string]$observer.protocol_version -ne $Protocol -or -not [bool]$observer.observer_mode -or [bool]$observer.canonical_write_permission) {
        throw 'vNext Observer / God Line state is missing or invalid after the v1.9.3 cycle.'
    }
    if ([bool]$observer.promotion_gate_v2.may_promote_canonical -or [bool]$observer.promotion_gate_v2.may_grant_reality_validation -or [bool]$observer.promotion_gate_v2.may_grant_ascension) {
        throw 'Observer authority boundary violated.'
    }

    $watchdog = Get-ScheduledTask -TaskName $WatchdogTask -ErrorAction SilentlyContinue
    if (-not $watchdog) { throw 'REI-Local-Watchdog task missing.' }
    $watchdogInfo = Get-ScheduledTaskInfo -TaskName $WatchdogTask
    if ($watchdogInfo.LastRunTime -eq [DateTime]::MinValue -or $watchdogInfo.LastTaskResult -ne 0) {
        throw "Watchdog unhealthy: LastTaskResult=$($watchdogInfo.LastTaskResult) LastRunTime=$($watchdogInfo.LastRunTime)"
    }

    $checkpointId = [string]$last.checkpoint_id
    $checkpointJson = Join-Path (Join-Path 'C:\REI_Resilience_Layer_v1\checkpoints' $checkpointId) 'checkpoint.json'
    if ([string]::IsNullOrWhiteSpace($checkpointId) -or -not (Test-Path -LiteralPath $checkpointJson)) {
        throw 'Recovery checkpoint for the verified v1.9.3 cycle is missing.'
    }
    try { Get-Content -LiteralPath $checkpointJson -Raw | ConvertFrom-Json | Out-Null } catch { throw 'Recovery checkpoint JSON is unreadable.' }

    Write-Host 'Replacing persistent Full Pipeline action with v1.9.3 engine...' -ForegroundColor Cyan
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$CycleScript`""
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes($IntervalMinutes) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes ([Math]::Max(15,$IntervalMinutes-1))) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'REI v1.9.3 reconciled PR28 synchronized local runtime; vNext Observer/God Line; canonical/main forbidden.' | Out-Null

    $installed = Get-ScheduledTask -TaskName $TaskName
    $actionText = (($installed.Actions | ForEach-Object { $_.Execute + ' ' + $_.Arguments }) -join ' ')
    if ($actionText -notmatch 'rei_cycle_v193\.ps1') { throw 'Persistent Full Pipeline action did not migrate to rei_cycle_v193.ps1.' }
    if (Get-ScheduledTask -TaskName $StandaloneTask -ErrorAction SilentlyContinue) { throw 'Duplicate standalone mutating scheduler still exists.' }

    Write-AtomicJson $ReportPath ([ordered]@{
        schema_version = 3
        status = 'LOCAL_REPAIR_PASS'
        candidate_pull_request = 28
        candidate_head_ref = $CandidateHeadRef
        candidate_head_sha = $candidateSha
        protocol_version = $Protocol
        local_model = 'rei-local-node-vnext'
        model_present = $true
        scheduler_authority = $TaskName
        scheduler_engine = $CycleScript
        duplicate_mutating_scheduler = $false
        runtime_cycle_status = [string]$last.cycle_status
        runtime_cycle_id = [string]$last.cycle_id
        observer_cycle_id = [string]$observer.cycle_id
        god_line_verified = $true
        watchdog_last_task_result = $watchdogInfo.LastTaskResult
        watchdog_last_run_time = $watchdogInfo.LastRunTime.ToString('o')
        recovery_checkpoint = $checkpointJson
        canonical_write_permission = $false
        reality_validated = $false
        ascension_granted = $false
        next_scheduled_cycle_after_minutes = $IntervalMinutes
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        backup_path = $BackupDir
    })

    Write-Host 'LOCAL_REPAIR_RESULT=LOCAL_REPAIR_PASS' -ForegroundColor Green
    Write-Host "Candidate: PR #28 / $CandidateHeadRef / $candidateSha" -ForegroundColor Cyan
    Write-Host "Runtime: $($last.cycle_status) / cycle $($last.cycle_id)" -ForegroundColor Green
    Write-Host "Observer/GodLine: VERIFIED / cycle $($observer.cycle_id)" -ForegroundColor Green
    Write-Host "Watchdog: LastTaskResult=$($watchdogInfo.LastTaskResult)" -ForegroundColor Green
    Write-Host "Recovery: $checkpointJson" -ForegroundColor Green
    Write-Host "Persistent scheduler engine: $CycleScript" -ForegroundColor Green
    Write-Host "REPORT=$ReportPath" -ForegroundColor Cyan
    Write-Host 'Canonical/main was not modified.' -ForegroundColor Green
}
catch {
    Fail $_.Exception.Message
}
