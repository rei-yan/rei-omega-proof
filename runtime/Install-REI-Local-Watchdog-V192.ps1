# REI-Ω v1.9.2 local Ollama watchdog installer
# Creates the exact scheduled task expected by the synchronized runtime cycle.

param(
  [int]$IntervalMinutes = 5,
  [switch]$NoStart
)

$ErrorActionPreference = 'Stop'
$Root = 'C:\REI-Shadow'
$RuntimeRoot = Join-Path $Root 'runtime-v191'
$WatchdogScript = Join-Path $RuntimeRoot 'rei_local_watchdog_v192.ps1'
$TaskName = 'REI-Local-Watchdog'
$PipelineTask = 'REI Full Pipeline v1.9.1'

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null

$watchdog = @'
$ErrorActionPreference = 'Stop'
$RuntimeRoot = 'C:\REI-Shadow\runtime-v191'
$Log = Join-Path $RuntimeRoot 'local-watchdog.log'

function Log([string]$m) {
  $line = "$(Get-Date -Format o) $m"
  Add-Content -Encoding UTF8 $Log $line
}

try {
  $healthy = $false
  try {
    $null = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3
    $healthy = $true
  } catch {
    $ollama = Get-Command ollama.exe -ErrorAction SilentlyContinue
    if (-not $ollama) {
      Log 'FAIL: ollama.exe not found in PATH'
      exit 2
    }
    Start-Process ollama.exe -ArgumentList 'serve' -WindowStyle Hidden | Out-Null
    Start-Sleep -Seconds 3
    try {
      $null = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 5
      $healthy = $true
    } catch {
      $healthy = $false
    }
  }

  if ($healthy) {
    Log 'PASS: Ollama API healthy'
    exit 0
  }
  Log 'FAIL: Ollama API unavailable after recovery attempt'
  exit 2
}
catch {
  Log ('FAIL: ' + $_.Exception.Message)
  exit 2
}
'@

$watchdog | Set-Content -Encoding UTF8 $WatchdogScript

$currentIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
if ([string]::IsNullOrWhiteSpace($currentIdentity) -or $currentIdentity -notmatch '\\') {
  $currentIdentity = "$env:USERDOMAIN\$env:USERNAME"
}

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$WatchdogScript`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 3)
$principal = New-ScheduledTaskPrincipal -UserId $currentIdentity -LogonType Interactive -RunLevel Highest

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

$registered = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
Write-Host "Registered watchdog: $($registered.TaskName)" -ForegroundColor Green
Write-Host "Principal: $($registered.Principal.UserId)" -ForegroundColor Green
Write-Host "Interval: $IntervalMinutes minutes" -ForegroundColor Green

if (-not $NoStart) {
  Start-ScheduledTask -TaskName $TaskName
  Start-Sleep -Seconds 2
  Write-Host 'Started local watchdog.' -ForegroundColor Cyan
}

# Re-run the main synchronized pipeline immediately after installing the missing dependency.
if (Get-ScheduledTask -TaskName $PipelineTask -ErrorAction SilentlyContinue) {
  Start-ScheduledTask -TaskName $PipelineTask
  Write-Host "Restarted synchronized pipeline: $PipelineTask" -ForegroundColor Cyan
}

Write-Host 'Next checks:' -ForegroundColor Cyan
Write-Host "  Get-ScheduledTaskInfo -TaskName '$TaskName' | Select LastRunTime,LastTaskResult,NextRunTime" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTaskInfo -TaskName '$PipelineTask' | Select LastRunTime,LastTaskResult,NextRunTime" -ForegroundColor Cyan
Write-Host '  Get-Content C:\REI-Shadow\runtime-v191\state\last-cycle.json' -ForegroundColor Cyan
