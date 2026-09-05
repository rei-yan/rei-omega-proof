# REI-Ω v1.9.3 Safe Auto-Update installer
# Installs a guarded polling task. Polling never bypasses CI/canary/checkpoint/rollback gates.

param(
  [int]$IntervalMinutes = 15,
  [switch]$NoStart
)

$ErrorActionPreference = 'Stop'
$Repo = 'C:\REI-Shadow\repo'
$RuntimeRoot = 'C:\REI-Shadow\runtime-v191'
$StateDir = Join-Path $RuntimeRoot 'state'
$Updater = Join-Path $RuntimeRoot 'safe_auto_update_v193.ps1'
$TaskName = 'REI Safe Auto Update v1.9.3'
$PipelineTask = 'REI Full Pipeline v1.9.1'
$RemoteBranch = 'rei-v193-reconcile'

if (-not (Test-Path $Repo)) { throw "Repo missing: $Repo" }
if (-not (Get-ScheduledTask -TaskName $PipelineTask -ErrorAction SilentlyContinue)) {
  throw "Healthy synchronized pipeline must exist first: $PipelineTask"
}
$last = Join-Path $StateDir 'last-cycle.json'
if (-not (Test-Path $last)) { throw 'Runtime verification evidence missing' }
$current = Get-Content $last -Raw | ConvertFrom-Json
if ($current.cycle_status -ne 'SUCCESS_RUNTIME_VERIFIED') {
  throw 'Current runtime must be SUCCESS_RUNTIME_VERIFIED before auto-update can be installed'
}

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
& git -C $Repo fetch origin $RemoteBranch --quiet
if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }

$content = & git -C $Repo show "origin/$RemoteBranch`:runtime/Safe-AutoUpdate-V193.ps1"
if ($LASTEXITCODE -ne 0) { throw 'Unable to retrieve Safe-AutoUpdate-V193.ps1' }
$content | Set-Content -Encoding UTF8 $Updater

$tokens = $null
$errors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile($Updater,[ref]$tokens,[ref]$errors)
if ($errors.Count -gt 0) { throw ('Updater syntax error: ' + $errors[0].Message) }

$currentIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
if ([string]::IsNullOrWhiteSpace($currentIdentity) -or $currentIdentity -notmatch '\\') {
  $currentIdentity = "$env:USERDOMAIN\$env:USERNAME"
}

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Updater`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
$principal = New-ScheduledTaskPrincipal -UserId $currentIdentity -LogonType Interactive -RunLevel Highest

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

$registered = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
Write-Host "Registered: $($registered.TaskName)" -ForegroundColor Green
Write-Host "Principal: $($registered.Principal.UserId)" -ForegroundColor Green
Write-Host "Poll interval: $IntervalMinutes minutes" -ForegroundColor Green
Write-Host 'Gate chain: FETCH -> G2 -> CHECKPOINT -> STAGE -> SYNTAX -> CANARY -> SWITCH -> FIRST CYCLE -> VERIFY/ROLLBACK' -ForegroundColor Cyan

if (-not $NoStart) {
  Start-ScheduledTask -TaskName $TaskName
  Write-Host 'Started first safe update check.' -ForegroundColor Cyan
}

Write-Host 'Update evidence:' -ForegroundColor Cyan
Write-Host '  Get-Content C:\REI-Shadow\runtime-v191\autoupdate\last-update.json' -ForegroundColor Cyan
Write-Host 'Runtime evidence:' -ForegroundColor Cyan
Write-Host '  Get-Content C:\REI-Shadow\runtime-v191\state\last-cycle.json' -ForegroundColor Cyan
