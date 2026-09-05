<#
REI-Ω Continuous Reality Loop v1 installer

Installs:
- continuous host guard;
- operational reality sidecar;
- reality-aware local-model overlay;
- SYSTEM orchestrator at startup + periodic cadence.

The installer proves the sidecar hash is bound into the local model state before
reporting the reality-feedback path as wired. It never writes canonical/main,
grants RealityValidated, promotes a candidate, or grants ascension.
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
$ContextRoot = 'C:\REI-Shadow\context'
$GuardLocal = Join-Path $RuntimeRoot 'REI-Continuous-Reality-Guard-V1.ps1'
$SidecarLocal = Join-Path $RuntimeRoot 'REI-Reality-Sidecar-V1.ps1'
$OrchestratorLocal = Join-Path $RuntimeRoot 'REI-Continuous-Reality-Orchestrator-V1.ps1'
$ContractLocal = Join-Path $RuntimeRoot 'continuous-reality-contract-v1.json'
$LocalModelTarget = 'C:\REI-Shadow\REI-LocalModel-VNext.ps1'
$TaskName = 'REI Continuous Reality Guard v1'
$EvidencePath = Join-Path $StateRoot 'continuous-reality-install.json'
$RealityInbox = 'C:\REI-Shadow\reality-inbox'
$SidecarState = Join-Path $StateRoot 'reality-feedback\latest.json'
$ModelState = Join-Path $ContextRoot 'model_vnext_state.json'
$BackupDir = Join-Path 'C:\REI-Shadow\backups' ('continuous-reality-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

$principalCheck = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principalCheck.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  throw 'Run from elevated PowerShell.'
}
if (-not (Test-Path -LiteralPath $Repo)) { throw "Repo missing: $Repo" }
$git = Get-Command git.exe -ErrorAction SilentlyContinue
if (-not $git) { throw 'git.exe not found' }

New-Item -ItemType Directory -Force -Path $RuntimeRoot,$StateRoot,$ContextRoot,$RealityInbox,$BackupDir | Out-Null

function Backup-File([string]$Path) {
  if (Test-Path -LiteralPath $Path) {
    $leaf = Split-Path -Leaf $Path
    Copy-Item -LiteralPath $Path -Destination (Join-Path $BackupDir $leaf) -Force
  }
}

function Install-RepoFile([string]$RepoPath,[string]$LocalPath) {
  Backup-File $LocalPath
  $content = & $git.Source -C $Repo show "origin/$Branch`:$RepoPath"
  if ($LASTEXITCODE -ne 0 -or -not $content) { throw "Unable to retrieve $RepoPath" }
  $dir = Split-Path -Parent $LocalPath
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $tmp = Join-Path $dir ([IO.Path]::GetRandomFileName())
  $content | Set-Content -LiteralPath $tmp -Encoding UTF8
  Move-Item -LiteralPath $tmp -Destination $LocalPath -Force
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

function Read-JsonSafe([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return $null }
  try { return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}

& $git.Source -C $Repo fetch origin $Branch --quiet
if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }
$head = (& $git.Source -C $Repo rev-parse "origin/$Branch").Trim()
if ([string]::IsNullOrWhiteSpace($head)) { throw 'Cannot resolve reconciled candidate head.' }

Install-RepoFile 'runtime/REI-Continuous-Reality-Guard-V1.ps1' $GuardLocal
Install-RepoFile 'runtime/REI-Reality-Sidecar-V1.ps1' $SidecarLocal
Install-RepoFile 'runtime/REI-Continuous-Reality-Orchestrator-V1.ps1' $OrchestratorLocal
Install-RepoFile 'runtime/continuous-reality-contract-v1.json' $ContractLocal
Install-RepoFile 'runtime/REI-LocalModel-Reality-VNext.ps1' $LocalModelTarget

foreach ($script in @($GuardLocal,$SidecarLocal,$OrchestratorLocal,$LocalModelTarget)) {
  Assert-PowerShellSyntax $script
}

try { $contract = Get-Content -LiteralPath $ContractLocal -Raw -Encoding UTF8 | ConvertFrom-Json } catch { throw "Contract JSON invalid: $($_.Exception.Message)" }
if ([string]$contract.contract_id -ne 'REI-CRL/1.0') { throw 'Unexpected continuous reality contract id.' }
if ([bool]$contract.authority.canonical_write_permission) { throw 'Contract illegally grants canonical write permission.' }
if ([bool]$contract.authority.automatic_promotion_permission) { throw 'Contract illegally grants automatic promotion permission.' }
if ([bool]$contract.authority.automatic_reality_validation_permission) { throw 'Contract illegally grants automatic reality validation.' }
if ([bool]$contract.authority.automatic_ascension_permission) { throw 'Contract illegally grants automatic ascension.' }

# Build the bounded sidecar first. A malformed observation is visible and blocks
# the model-binding verification rather than being silently discarded.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $SidecarLocal
$sidecarExit = $LASTEXITCODE
if ($sidecarExit -ne 0) {
  throw "Reality sidecar is not clean enough for initial model binding (exit $sidecarExit). Inspect $SidecarState"
}
$sidecar = Read-JsonSafe $SidecarState
if ($null -eq $sidecar -or [string]::IsNullOrWhiteSpace([string]$sidecar.context_sha256)) {
  throw 'Reality sidecar did not produce a context SHA256.'
}

# Force one local-model rebuild so installation proves that the separate reality
# context is actually consumed by the model that the synchronized Shadow cycle uses.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $LocalModelTarget -ContextDir $ContextRoot -Force
$modelExit = $LASTEXITCODE
if ($modelExit -ne 0) {
  throw "Reality-aware local model refresh failed (exit $modelExit)."
}
$model = Read-JsonSafe $ModelState
if ($null -eq $model) { throw 'Reality-aware local model state is missing.' }
if ([string]$model.reality_context_sha256 -ne [string]$sidecar.context_sha256) {
  throw 'Reality sidecar/model SHA binding mismatch.'
}
if ([bool]$model.canonical_write_permission -or [bool]$model.reality_validated -or [string]$model.promotion -ne 'NO') {
  throw 'Reality-aware local model authority boundary violated.'
}

Backup-Task $TaskName
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
  Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$OrchestratorLocal`" -RuntimeRoot `"$RuntimeRoot`""
$startup = New-ScheduledTaskTrigger -AtStartup
$periodic = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $GuardIntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($startup,$periodic) -Settings $settings -Principal $principal -Description 'REI continuous reality loop: bounded reality sidecar + defensive host guard. Canonical writes and automatic promotion are forbidden.' | Out-Null

# First orchestrated pass establishes installation evidence. A degraded host guard
# remains visible and is not rewritten into success.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $OrchestratorLocal -RuntimeRoot $RuntimeRoot
$orchestratorExit = $LASTEXITCODE
$latest = Read-JsonSafe (Join-Path $StateRoot 'continuous-reality\latest.json')
$sidecar = Read-JsonSafe $SidecarState
$model = Read-JsonSafe $ModelState
$bindingOk = ($null -ne $sidecar -and $null -ne $model -and [string]$sidecar.context_sha256 -eq [string]$model.reality_context_sha256)

$payload = [ordered]@{
  schema_version = 2
  status = $(if($orchestratorExit -eq 0){'CONTINUOUS_REALITY_INSTALLED'}elseif($orchestratorExit -eq 1){'INSTALLED_REALITY_LOOP_DEGRADED'}else{'INSTALLED_REALITY_LOOP_HOLD'})
  branch = $Branch
  branch_head_sha = $head
  task = $TaskName
  task_principal = 'SYSTEM'
  interval_minutes = $GuardIntervalMinutes
  guard_path = $GuardLocal
  sidecar_path = $SidecarLocal
  orchestrator_path = $OrchestratorLocal
  local_model_path = $LocalModelTarget
  contract_path = $ContractLocal
  reality_inbox = $RealityInbox
  reality_context_path = $(if($sidecar){[string]$sidecar.context_path}else{''})
  reality_context_sha256 = $(if($sidecar){[string]$sidecar.context_sha256}else{''})
  model_reality_context_sha256 = $(if($model){[string]$model.reality_context_sha256}else{''})
  reality_sidecar_bound_to_model = $bindingOk
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

Write-Host "REI_CONTINUOUS_REALITY_INSTALL=$($payload.status)" -ForegroundColor $(if($orchestratorExit -eq 0){'Green'}else{'Yellow'})
Write-Host "Guard/sidecar: startup + every $GuardIntervalMinutes minutes as SYSTEM" -ForegroundColor Green
Write-Host "Reality sidecar bound to local model: $bindingOk" -ForegroundColor $(if($bindingOk){'Green'}else{'Red'})
Write-Host "Reality context SHA256: $($payload.reality_context_sha256)" -ForegroundColor Cyan
Write-Host "72h proof: $($payload.stability_72h_verified)" -ForegroundColor Cyan
Write-Host "Reality inbox: $RealityInbox" -ForegroundColor Cyan
Write-Host "Install evidence: $EvidencePath" -ForegroundColor Cyan
Write-Host 'Canonical/main was not modified. No reality validation or promotion was granted.' -ForegroundColor Green

if (-not $bindingOk) { exit 2 }
# Installation succeeds once the loop and model binding are installed; current host
# continuity may still be degraded and remains visible in the evidence files.
exit 0
