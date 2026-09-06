<#
Install REI Local Self-Heal v1.
Creates one low-overhead startup + 15-minute bounded repair task.
#>
[CmdletBinding()]
param(
  [ValidateRange(5,120)][int]$IntervalMinutes = 15,
  [switch]$NoStart
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Repo='C:\REI-Shadow\repo'
$RuntimeRoot='C:\REI-Shadow\runtime-v191'
$SelfHeal=Join-Path $RuntimeRoot 'REI-Local-SelfHeal-V1.ps1'
$TaskName='REI Local Self Heal v1'
$RemoteBranch='rei-v193-reconcile'

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  throw 'Run installer from an elevated PowerShell session.'
}
if (-not (Test-Path -LiteralPath $Repo)) { throw "Repo missing: $Repo" }
New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null

$git=(Get-Command git.exe -ErrorAction SilentlyContinue)
if (-not $git) { throw 'git.exe not found' }
& $git.Source -C $Repo fetch origin $RemoteBranch --quiet
if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }
$content=& $git.Source -C $Repo show "origin/$RemoteBranch`:runtime/REI-Local-SelfHeal-V1.ps1"
if ($LASTEXITCODE -ne 0 -or -not $content) { throw 'Unable to retrieve REI-Local-SelfHeal-V1.ps1' }
$content | Set-Content -LiteralPath $SelfHeal -Encoding UTF8

$tokens=$null;$errors=$null
[void][System.Management.Automation.Language.Parser]::ParseFile($SelfHeal,[ref]$tokens,[ref]$errors)
if (($errors | Measure-Object).Count -gt 0) { throw ('Self-Heal syntax error: ' + $errors[0].Message) }

$identity=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$SelfHeal`" -Mode Normal"
$startup=New-ScheduledTaskTrigger -AtStartup
$periodic=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 8) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$taskPrincipal=New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Highest
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($startup,$periodic) -Settings $settings -Principal $taskPrincipal -Description 'Bounded REI local self-heal: legacy migration, orphan-lock cleanup, version/context/model drift repair, recoverable fail-closed retry. Never writes canonical/main.' | Out-Null

if (-not $NoStart) {
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $SelfHeal -Mode Normal
  if ($LASTEXITCODE -ne 0) { throw 'Initial Self-Heal pass failed closed; inspect latest.json' }
}
Write-Host 'REI_LOCAL_SELFHEAL_INSTALLED=TRUE' -ForegroundColor Green
Write-Host "Task: $TaskName" -ForegroundColor Green
Write-Host "Interval: $IntervalMinutes minutes + startup" -ForegroundColor Green
Write-Host 'Evidence: C:\REI-Shadow\state\selfheal\latest.json' -ForegroundColor Cyan
