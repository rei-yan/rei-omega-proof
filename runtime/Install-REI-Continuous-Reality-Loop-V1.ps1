<#
REI-Ω Continuous Reality Loop v1 installer

Installs the defensive host guard that proves continued runtime freshness over time.
The guard may observe, record, enable/start known defensive tasks, or request self-heal.
It may not write canonical/main, grant RealityValidated, promote a candidate, or grant ascension.
#>
[CmdletBinding()]
param(
  [ValidateRange(5,60)][int]$GuardIntervalMinutes = 10
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Repo = 'C:\REI-Shadow\repo'
$Branch = 'rei-v193-reconcile'
$RuntimeRoot = 'C:\REI-Shadow\runtime-v191'
$StateRoot = 'C:\REI-Shadow\state'
$GuardLocal = Join-Path $RuntimeRoot 'REI-Continuous-Reality-Guard-V1.ps1'
$ContractLocal = Join-Path $RuntimeRoot 'continuous-reality-contract-v1.json'
$TaskName = 'REI Continuous Reality Guard v1'
$EvidencePath = Join-Path $StateRoot 'continuous-reality-install.json'
$RealityInbox = 'C:\REI-Shadow\reality-inbox'
$BackupDir = Join-Path 'C:\REI-Shadow\backups' ('continuous-reality-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

$principalCheck = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principalCheck.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  throw 'Run from elevated PowerShell.'
}
if (-not (Test-Path -LiteralPath $Repo)) { throw "Repo missing: $Repo" }
$git = Get-Command git.exe -ErrorAction SilentlyContinue
if (-not $git) { throw 'git.exe not found' }

New-Item -ItemType Directory -Force -Path $RuntimeRoot,$StateRoot,$RealityInbox,$BackupDir | Out-Null

function Backup-File([string]$Path) {
  if (Test-Path -LiteralPath $Path) {
    Copy-Item -LiteralPath $Path -Destination (Join-Path $BackupDir (Split-Path -Leaf $Path)) -Force
  }
}

function Install-RepoFile([string]$RepoPath,[string]$LocalPath) {
  Backup-File $LocalPath
  $content = & $git.Source -C $Repo show "origin/$Branch`:$RepoPath"
  if ($LASTEXITCODE -ne 0 -or -not $content) { throw "Unable to retrieve $RepoPath" }
  $content | Set-Content -LiteralPath $LocalPath -Encoding UTF8
}

function Assert-PowerShellSyntax([string]$Path) {
  $tokens = $null
  $errors = $null
  [void][System.Management.Automation.Language.Parser]::ParseFile($Path,[ref]$tokens,[ref]$errors)
  if (($errors | Measure-Object).Count -gt 0) {
    throw "PowerShell syntax error in $Path : $($errors[0].Message)"
  }
}

function Backup-Task([string]$Name) {
  if (Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue) {
    try {
      Export-ScheduledTask -TaskName $Name | Set-Content -Encoding UTF8 (Join-Path $BackupDir (($Name -replace '[^A-Za-z0-9._-]','_') + '.xml'))
    } catch {}
  }
}

& $git.Source -C $Repo fetch origin $Branch --quiet
if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }
$head = (& $git.Source -C $Repo rev-parse "origin/$Branch").Trim()
if ([string]::IsNullOrWhiteSpace($head)) { throw 'Cannot resolve reconciled candidate head.' }

Install-RepoFile 'runtime/REI-Continuous-Reality-Guard-V1.ps1' $GuardLocal
Install-RepoFile 'runtime/continuous-reality-contract-v1.json' $ContractLocal
Assert-PowerShellSyntax $GuardLocal
try { $contract = Get-Content -LiteralPath $ContractLocal -Raw -Encoding UTF8 | ConvertFrom-Json } catch { throw "Contract JSON invalid: $($_.Exception.Message)" }
if ([string]$contract.contract_id -ne 'REI-CRL/1.0') { throw 'Unexpected continuous reality contract id.' }
if ([bool]$contract.authority.canonical_write_permission) { throw 'Contract illegally grants canonical write permission.' }
if ([bool]$contract.authority.automatic_promotion_permission) { throw 'Contract illegally grants automatic promotion permission.' }
if ([bool]$contract.authority.automatic_reality_validation_permission) { throw 'Contract illegally grants automatic reality validation.' }
if ([bool]$contract.authority.automatic_ascension_permission) { throw 'Contract illegally grants automatic ascension.' }

Backup-Task $TaskName
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
  Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$GuardLocal`" -ContractPath `"$ContractLocal`""
$startup = New-ScheduledTaskTrigger -AtStartup
$periodic = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $GuardIntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($startup,$periodic) -Settings $settings -Principal $principal -Description 'REI defensive continuous host-reality guard. Records freshness and bounded recovery; canonical writes and automatic promotion are forbidden.' | Out-Null

# First pass establishes installation evidence. A degraded first pass is allowed to remain visible;
# it is not rewritten into success. The task will continue sampling and requesting bounded recovery.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $GuardLocal -ContractPath $ContractLocal
$guardExit = $LASTEXITCODE
$latest = $null
try { $latest = Get-Content -LiteralPath (Join-Path $StateRoot 'continuous-reality\latest.json') -Raw -Encoding UTF8 | ConvertFrom-Json } catch {}

$payload = [ordered]@{
  schema_version = 1
  status = $(if($guardExit -eq 0){'CONTINUOUS_REALITY_INSTALLED'}elseif($guardExit -eq 1){'INSTALLED_GUARD_DEGRADED'}else{'INSTALLED_GUARD_HOLD'})
  branch = $Branch
  branch_head_sha = $head
  task = $TaskName
  task_principal = 'SYSTEM'
  interval_minutes = $GuardIntervalMinutes
  guard_path = $GuardLocal
  contract_path = $ContractLocal
  reality_inbox = $RealityInbox
  first_guard_status = $(if($latest){[string]$latest.status}else{'UNKNOWN'})
  stability_72h_verified = $(if($latest){[bool]$latest.stability_72h_verified}else{$false})
  canonical_write_permission = $false
  reality_validated = $false
  promotion = 'NO'
  ascension = 'NO'
  backup_path = $BackupDir
  timestamp_utc = [DateTime]::UtcNow.ToString('o')
}
$payload | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8

Write-Host "REI_CONTINUOUS_REALITY_INSTALL=$($payload.status)" -ForegroundColor $(if($guardExit -eq 0){'Green'}else{'Yellow'})
Write-Host "Guard: startup + every $GuardIntervalMinutes minutes as SYSTEM" -ForegroundColor Green
Write-Host "72h proof: $($payload.stability_72h_verified)" -ForegroundColor Cyan
Write-Host "Reality inbox: $RealityInbox" -ForegroundColor Cyan
Write-Host "Install evidence: $EvidencePath" -ForegroundColor Cyan
Write-Host 'Canonical/main was not modified. No reality validation or promotion was granted.' -ForegroundColor Green

# Installation itself succeeds if assets/task are installed, even when the first host sample is degraded.
exit 0
