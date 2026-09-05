# REI-Ω v1.9.1/v1.9.2 local runtime scheduled-task repair
# Fixes HRESULT 0x80070057 / UserId by using the fully-qualified Windows identity.

param(
  [int]$IntervalMinutes = 60,
  [switch]$NoStart
)

$ErrorActionPreference = 'Stop'
$RuntimeRoot = 'C:\REI-Shadow\runtime-v191'
$CycleScript = Join-Path $RuntimeRoot 'rei_cycle_v191.ps1'
$TaskName = 'REI Full Pipeline v1.9.1'
$OldTaskName = 'REI Shadow Closed Loop V2'

if (-not (Test-Path $CycleScript)) {
  throw "Cycle script not found: $CycleScript. Re-run the main installer first."
}

$currentIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
if ([string]::IsNullOrWhiteSpace($currentIdentity) -or $currentIdentity -notmatch '\\') {
  $currentIdentity = "$env:USERDOMAIN\$env:USERNAME"
}
Write-Host "Using scheduled-task principal: $currentIdentity" -ForegroundColor Cyan

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$CycleScript`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes ([Math]::Max(15,$IntervalMinutes-1)))
$principal = New-ScheduledTaskPrincipal -UserId $currentIdentity -LogonType Interactive -RunLevel Highest

try {
  if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  }

  Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

  $registered = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
  Write-Host "Registered: $($registered.TaskName)" -ForegroundColor Green
  Write-Host "State: $($registered.State)" -ForegroundColor Green
  Write-Host "Principal: $($registered.Principal.UserId)" -ForegroundColor Green

  # Keep legacy direct Shadow task disabled to prevent duplicate closed-loop execution.
  $legacy = Get-ScheduledTask -TaskName $OldTaskName -ErrorAction SilentlyContinue
  if ($legacy -and $legacy.State -ne 'Disabled') {
    Disable-ScheduledTask -TaskName $OldTaskName | Out-Null
  }

  if (-not $NoStart) {
    Start-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 2
    Write-Host 'Started synchronized runtime task.' -ForegroundColor Cyan
  }

  Write-Host "Next check: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
  Write-Host 'Runtime result: Get-Content C:\REI-Shadow\runtime-v191\state\last-cycle.json' -ForegroundColor Cyan
}
catch {
  Write-Host "Registration failed: $($_.Exception.Message)" -ForegroundColor Red
  # Restore legacy cycle so the machine is not left with both old and new pipelines stopped.
  $legacy = Get-ScheduledTask -TaskName $OldTaskName -ErrorAction SilentlyContinue
  if ($legacy) {
    Enable-ScheduledTask -TaskName $OldTaskName | Out-Null
    Write-Host "Safety fallback: re-enabled legacy task '$OldTaskName'." -ForegroundColor Yellow
  }
  throw
}
