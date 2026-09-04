# REI-Ω v1.9.3 one-time local lineage migration
# Re-points the already-installed Safe Auto Update task from the legacy observer branch
# to the reconciled PR #25 + PR #27 lineage without touching canonical/main.

param(
  [switch]$NoStart
)

$ErrorActionPreference = 'Stop'
$Repo = 'C:\REI-Shadow\repo'
$RuntimeRoot = 'C:\REI-Shadow\runtime-v191'
$InstalledUpdater = Join-Path $RuntimeRoot 'safe_auto_update_v193.ps1'
$TaskName = 'REI Safe Auto Update v1.9.3'
$RemoteBranch = 'rei-v193-reconcile'
$RemoteRef = "origin/$RemoteBranch"
$BackupRoot = Join-Path $RuntimeRoot 'autoupdate\migration-backup'

function Resolve-GitExe {
  $cmd = Get-Command git.exe -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  foreach ($p in @('C:\Program Files\Git\cmd\git.exe','C:\Program Files\Git\bin\git.exe','C:\Program Files (x86)\Git\cmd\git.exe')) {
    if (Test-Path $p) { return $p }
  }
  throw 'git.exe not found'
}

if (-not (Test-Path $Repo)) { throw "Repo missing: $Repo" }
New-Item -ItemType Directory -Force -Path $RuntimeRoot,$BackupRoot | Out-Null
$git = Resolve-GitExe

& $git -C $Repo fetch origin $RemoteBranch --quiet
if ($LASTEXITCODE -ne 0) { throw 'git fetch reconciled branch failed' }
$candidate = (& $git -C $Repo rev-parse $RemoteRef).Trim()
if ($LASTEXITCODE -ne 0 -or -not $candidate) { throw 'Cannot resolve reconciled candidate SHA' }

$newContent = (& $git -C $Repo show "$RemoteRef`:runtime/Safe-AutoUpdate-V193.ps1") -join [Environment]::NewLine
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($newContent)) { throw 'Unable to retrieve reconciled updater' }
if ($newContent -notmatch "\$RemoteBranch\s*=\s*'rei-v193-reconcile'") { throw 'Reconciled updater branch pin verification failed' }

$tmp = Join-Path $RuntimeRoot 'safe_auto_update_v193.ps1.migrating'
$newContent | Set-Content -Encoding UTF8 $tmp
$tokens = $null
$errors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile($tmp,[ref]$tokens,[ref]$errors)
if ($errors.Count -gt 0) { Remove-Item $tmp -Force -ErrorAction SilentlyContinue; throw ('Updater syntax error: ' + $errors[0].Message) }

if (Test-Path $InstalledUpdater) {
  $stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
  Copy-Item $InstalledUpdater (Join-Path $BackupRoot "safe_auto_update_v193.$stamp.ps1") -Force
}
Move-Item $tmp $InstalledUpdater -Force

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if (-not $task) { throw "Scheduled task missing after updater migration: $TaskName" }

Write-Host "MIGRATION_READY candidate=$candidate" -ForegroundColor Green
Write-Host "Updater=$InstalledUpdater" -ForegroundColor Green
Write-Host "RemoteBranch=$RemoteBranch" -ForegroundColor Green
Write-Host 'canonical/main untouched; promotion remains NO.' -ForegroundColor Cyan

if (-not $NoStart) {
  Start-ScheduledTask -TaskName $TaskName
  Write-Host 'Started safe updater against reconciled lineage.' -ForegroundColor Cyan
}
