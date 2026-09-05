<#
REI-Ω Scheduler Continuity Repair
Purpose:
  - Keep "REI Full Pipeline v1.9.1" as the only authoritative mutating scheduler.
  - Remove the PT59M execution kill-switch that can terminate a 3600s loop before wake-up.
  - Preserve IgnoreNew single-instance semantics.
  - Add bounded restart / StartWhenAvailable / battery continuity.
  - Disable the legacy "REI Shadow Closed Loop V2" scheduler to prevent parallel writers.
  - Back up Task Scheduler XML and roll back automatically on repair failure.

This script does NOT modify canonical/main, God Core logic, God Wheel logic, or model payloads.
#>
[CmdletBinding()]
param(
    [string]$TaskName = "REI Full Pipeline v1.9.1",
    [string]$LegacyTaskName = "REI Shadow Closed Loop V2",
    [string]$ExpectedPipelineScript = "C:\REI-Shadow\runtime-v191\rei_cycle_v193.ps1"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($id)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    throw "Run this installer from an elevated PowerShell window (Administrator)."
}

$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$backupDir = "C:\REI-Shadow\backups\scheduler_continuity_$stamp"
$stateDir = "C:\REI-Shadow\state"
$statePath = Join-Path $stateDir "scheduler_continuity_repair.json"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
New-Item -ItemType Directory -Path $stateDir -Force | Out-Null

$mainBackup = Join-Path $backupDir "full_pipeline.xml"
$legacyBackup = Join-Path $backupDir "legacy_closed_loop.xml"
$legacyWasPresent = $false

function Save-TaskXml {
    param([string]$Name, [string]$Path)
    $xml = Export-ScheduledTask -TaskName $Name -ErrorAction Stop
    Set-Content -LiteralPath $Path -Value $xml -Encoding UTF8
}

function Restore-TaskXml {
    param([string]$Name, [string]$Path)
    if (Test-Path -LiteralPath $Path) {
        $xml = Get-Content -LiteralPath $Path -Raw
        Register-ScheduledTask -TaskName $Name -Xml $xml -Force | Out-Null
    }
}

try {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
    Save-TaskXml -Name $TaskName -Path $mainBackup

    if (-not (Test-Path -LiteralPath $ExpectedPipelineScript)) {
        throw "Authoritative pipeline script is missing: $ExpectedPipelineScript"
    }

    $actionMatch = $false
    foreach ($action in @($task.Actions)) {
        if (([string]$action.Execute -match "powershell") -and ([string]$action.Arguments -like "*$ExpectedPipelineScript*")) {
            $actionMatch = $true
            break
        }
    }
    if (-not $actionMatch) {
        throw "Task action does not point to expected authoritative pipeline script: $ExpectedPipelineScript"
    }

    $legacy = Get-ScheduledTask -TaskName $LegacyTaskName -ErrorAction SilentlyContinue
    if ($legacy) {
        $legacyWasPresent = $true
        Save-TaskXml -Name $LegacyTaskName -Path $legacyBackup
    }

    if ($task.State -eq "Running") {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }

    # Patch only task settings. Actions and triggers are preserved.
    $settings = (Get-ScheduledTask -TaskName $TaskName).Settings
    $settings.ExecutionTimeLimit = "PT0S"       # no scheduler kill at 59 minutes
    $settings.MultipleInstances = "IgnoreNew"   # never overlap mutating pipelines
    $settings.StartWhenAvailable = $true
    $settings.RestartCount = 3
    $settings.RestartInterval = "PT1M"
    $settings.DisallowStartIfOnBatteries = $false
    $settings.StopIfGoingOnBatteries = $false
    $settings.WakeToRun = $true
    Set-ScheduledTask -TaskName $TaskName -Settings $settings | Out-Null

    if ($legacyWasPresent) {
        Stop-ScheduledTask -TaskName $LegacyTaskName -ErrorAction SilentlyContinue
        Disable-ScheduledTask -TaskName $LegacyTaskName | Out-Null
    }

    Start-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 5

    $verified = Get-ScheduledTask -TaskName $TaskName
    $info = Get-ScheduledTaskInfo -TaskName $TaskName
    $legacyState = if ($legacyWasPresent) { (Get-ScheduledTask -TaskName $LegacyTaskName).State.ToString() } else { "ABSENT" }

    $limitOk = ([string]$verified.Settings.ExecutionTimeLimit -eq "PT0S")
    $instanceOk = ([string]$verified.Settings.MultipleInstances -eq "IgnoreNew")
    $legacyOk = (-not $legacyWasPresent) -or ($legacyState -eq "Disabled")
    $actionOk = $false
    foreach ($action in @($verified.Actions)) {
        if (([string]$action.Arguments -like "*$ExpectedPipelineScript*")) { $actionOk = $true }
    }

    if (-not ($limitOk -and $instanceOk -and $legacyOk -and $actionOk)) {
        throw "Post-repair verification failed: limitOk=$limitOk instanceOk=$instanceOk legacyOk=$legacyOk actionOk=$actionOk"
    }

    $result = [ordered]@{
        schema_version = 1
        status = "SCHEDULER_CONTINUITY_REPAIRED"
        repaired_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        authoritative_task = $TaskName
        authoritative_action = $ExpectedPipelineScript
        task_state = $verified.State.ToString()
        last_run_time = $info.LastRunTime.ToString("o")
        next_run_time = $info.NextRunTime.ToString("o")
        last_task_result = $info.LastTaskResult
        execution_time_limit = [string]$verified.Settings.ExecutionTimeLimit
        multiple_instances = [string]$verified.Settings.MultipleInstances
        start_when_available = [bool]$verified.Settings.StartWhenAvailable
        restart_count = [int]$verified.Settings.RestartCount
        restart_interval = [string]$verified.Settings.RestartInterval
        wake_to_run = [bool]$verified.Settings.WakeToRun
        legacy_task = $LegacyTaskName
        legacy_state = $legacyState
        canonical_mainline_touched = $false
        canonical_write_permission = $false
        backup_directory = $backupDir
    }
    $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statePath -Encoding UTF8

    Write-Host "" 
    Write-Host "SCHEDULER_CONTINUITY_REPAIRED" -ForegroundColor Green
    Write-Host "Authoritative task: $TaskName"
    Write-Host "State: $($verified.State)"
    Write-Host "ExecutionTimeLimit: $($verified.Settings.ExecutionTimeLimit)"
    Write-Host "MultipleInstances: $($verified.Settings.MultipleInstances)"
    Write-Host "Legacy task state: $legacyState"
    Write-Host "LastTaskResult: $($info.LastTaskResult)"
    Write-Host "Backup: $backupDir"
    Write-Host "Canonical mainline touched: FALSE"
}
catch {
    Write-Warning "Repair failed: $($_.Exception.Message)"
    try {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Restore-TaskXml -Name $TaskName -Path $mainBackup
        if ($legacyWasPresent) { Restore-TaskXml -Name $LegacyTaskName -Path $legacyBackup }
        Write-Warning "Task Scheduler XML restored from backup."
    }
    catch {
        Write-Warning "Automatic rollback also encountered an error: $($_.Exception.Message)"
    }
    throw
}
