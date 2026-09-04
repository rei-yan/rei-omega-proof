<#
REI-Ω Autonomic Maintenance v1 installer.
One-time install for ongoing local self-heal + guarded auto-update.
Does not require canonical/main access and does not require a healthy runtime to install.
#>
[CmdletBinding()]
param(
  [ValidateRange(5,120)][int]$SelfHealIntervalMinutes = 15,
  [ValidateRange(10,240)][int]$UpdateIntervalMinutes = 30
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Repo='C:\REI-Shadow\repo'
$RuntimeRoot='C:\REI-Shadow\runtime-v191'
$Branch='rei-v193-reconcile'
$SelfHeal=Join-Path $RuntimeRoot 'REI-Local-SelfHeal-V1.ps1'
$Updater=Join-Path $RuntimeRoot 'safe_auto_update_v193.ps1'
$SelfHealTask='REI Local Self Heal v1'
$UpdaterTask='REI Safe Auto Update v1.9.3'
$BackupDir=Join-Path 'C:\REI-Shadow\backups' ('autonomic-maintenance-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
$Evidence=Join-Path 'C:\REI-Shadow\state' 'autonomic-maintenance.json'

$principalCheck=New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principalCheck.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Run from elevated PowerShell.' }
if (-not (Test-Path -LiteralPath $Repo)) { throw "Repo missing: $Repo" }
$git=Get-Command git.exe -ErrorAction SilentlyContinue
if (-not $git) { throw 'git.exe not found' }
New-Item -ItemType Directory -Force -Path $RuntimeRoot,$BackupDir,(Split-Path -Parent $Evidence) | Out-Null

function Backup-File([string]$Path) {
  if (Test-Path -LiteralPath $Path) { Copy-Item -LiteralPath $Path -Destination (Join-Path $BackupDir (Split-Path -Leaf $Path)) -Force }
}
function Install-RepoFile([string]$RepoPath,[string]$LocalPath) {
  Backup-File $LocalPath
  $content=& $git.Source -C $Repo show "origin/$Branch`:$RepoPath"
  if ($LASTEXITCODE -ne 0 -or -not $content) { throw "Unable to retrieve $RepoPath" }
  $content | Set-Content -LiteralPath $LocalPath -Encoding UTF8
  $tokens=$null;$errors=$null
  [void][System.Management.Automation.Language.Parser]::ParseFile($LocalPath,[ref]$tokens,[ref]$errors)
  if (($errors | Measure-Object).Count -gt 0) { throw "$RepoPath syntax error: $($errors[0].Message)" }
}
function Backup-Task([string]$Name) {
  if (Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue) {
    try { Export-ScheduledTask -TaskName $Name | Set-Content -Encoding UTF8 (Join-Path $BackupDir (($Name -replace '[^A-Za-z0-9._-]','_') + '.xml')) } catch {}
  }
}

& $git.Source -C $Repo fetch origin $Branch --quiet
if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }
$head=(& $git.Source -C $Repo rev-parse "origin/$Branch").Trim()
if (-not $head) { throw 'Cannot resolve reconciled candidate head.' }

Install-RepoFile 'runtime/REI-Local-SelfHeal-V1.ps1' $SelfHeal
Install-RepoFile 'runtime/Safe-AutoUpdate-V193.ps1' $Updater

$identity=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$taskPrincipal=New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Highest
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Backup-Task $SelfHealTask
$selfAction=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$SelfHeal`" -Mode Normal"
$selfStartup=New-ScheduledTaskTrigger -AtStartup
$selfPeriodic=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $SelfHealIntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
if (Get-ScheduledTask -TaskName $SelfHealTask -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $SelfHealTask -Confirm:$false }
Register-ScheduledTask -TaskName $SelfHealTask -Action $selfAction -Trigger @($selfStartup,$selfPeriodic) -Settings $settings -Principal $taskPrincipal -Description 'REI bounded local self-heal and legacy migration. Unknown failures HOLD; canonical/main forbidden.' | Out-Null

Backup-Task $UpdaterTask
$updateAction=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Updater`""
$updateTrigger=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(3) -RepetitionInterval (New-TimeSpan -Minutes $UpdateIntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
if (Get-ScheduledTask -TaskName $UpdaterTask -ErrorAction SilentlyContinue) {
  Set-ScheduledTask -TaskName $UpdaterTask -Action $updateAction -Trigger $updateTrigger -Settings $settings -Principal $taskPrincipal | Out-Null
} else {
  Register-ScheduledTask -TaskName $UpdaterTask -Action $updateAction -Trigger $updateTrigger -Settings $settings -Principal $taskPrincipal -Description 'REI guarded candidate updater: self-heal preflight, complete CI, checkpoint, canary, v1.9.3 switch, first-cycle verify, rollback.' | Out-Null
}

# Run one bounded self-heal pass now. It will not overlap a running v1.9.3 cycle.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $SelfHeal -Mode Normal -DesiredSha $head
$selfCode=$LASTEXITCODE

$payload=[ordered]@{
  schema_version=1; status=$(if($selfCode -eq 0){'AUTONOMIC_MAINTENANCE_INSTALLED'}else{'INSTALLED_SELFHEAL_FAILED_CLOSED'});
  candidate_branch=$Branch; candidate_head_sha=$head;
  self_heal_task=$SelfHealTask; self_heal_interval_minutes=$SelfHealIntervalMinutes;
  updater_task=$UpdaterTask; updater_interval_minutes=$UpdateIntervalMinutes;
  active_runtime='rei_cycle_v193.ps1'; canonical_write_permission=$false;
  backup_path=$BackupDir; timestamp_utc=[DateTime]::UtcNow.ToString('o')
}
$payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Evidence -Encoding UTF8

Write-Host "REI_AUTONOMIC_MAINTENANCE=$($payload.status)" -ForegroundColor $(if($selfCode -eq 0){'Green'}else{'Yellow'})
Write-Host "Self-Heal: startup + every $SelfHealIntervalMinutes minutes" -ForegroundColor Green
Write-Host "Safe Auto Update: every $UpdateIntervalMinutes minutes" -ForegroundColor Green
Write-Host 'Upgrade chain: SELFHEAL_PRE -> COMPLETE_CI -> CHECKPOINT -> CANARY -> V193_SWITCH -> FIRST_CYCLE -> SELFHEAL_POST -> VERIFY/ROLLBACK' -ForegroundColor Cyan
Write-Host "Evidence: $Evidence" -ForegroundColor Cyan
Write-Host 'Canonical/main was not modified.' -ForegroundColor Green
if ($selfCode -ne 0) { exit 2 }
exit 0
