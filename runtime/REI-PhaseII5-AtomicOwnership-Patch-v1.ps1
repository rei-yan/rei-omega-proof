# REI-Ω Recovery Hardening Phase II.5
# Atomic Ownership Through Destructive Act — Candidate Installer v1
# Hash-pinned. No canonical/main, task-definition, promotion, or RealityValidated writes.

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PythonSource    = 'C:\REI\rei_shadow_closed_loop_v2.py'
$SelfHealSource = 'C:\REI-Shadow\runtime-v191\REI-Local-SelfHeal-V1.ps1'
$RuntimeLock     = 'C:\REI-Shadow\state\resilience\runtime.lock'
$PipelineTask    = 'REI Full Pipeline v1.9.1'
$SelfHealTask    = 'REI Local Self Heal v1'
$MutexName       = 'Global\REI_Omega_v193_Synchronized_Cycle'

$ExpectedPythonSha   = '6752672711E1FF7BA5F7035221E88403EAAEE716E444573D82477A62D51EC3DB'
$ExpectedSelfHealSha = '11CECB2192E7555029804A8A75BB3FB6394302F11F09FF1E5CF2DA1D69CF4323'

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$BackupRoot = "C:\REI-Shadow\backups\phaseii5-atomic-ownership-$Stamp"
$BackupSelfHeal = Join-Path $BackupRoot 'REI-Local-SelfHeal-V1.ps1.before'
$Desktop = [Environment]::GetFolderPath('Desktop')
if ([string]::IsNullOrWhiteSpace($Desktop)) { $Desktop = $env:USERPROFILE }
$Evidence = Join-Path $Desktop "REI_PhaseII5_AtomicOwnership_Patch_v1_$Stamp.txt"

$Lines = New-Object System.Collections.Generic.List[string]
$Mutex = $null
$MutexOwned = $false
$PatchWritten = $false
$Final = 'FAIL_PHASEII5_ATOMIC_OWNERSHIP_PATCH_V1'

function Add([string]$s='') {
    $Lines.Add($s) | Out-Null
    Write-Host $s
}

function Get-Sha([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return '' }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToUpperInvariant()
}

function Parse-PowerShell([string]$Path) {
    $tokens = $null
    $errors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile($Path,[ref]$tokens,[ref]$errors)
    return [pscustomobject]@{ Ast=$ast; Errors=@($errors) }
}

function Replace-ExactlyOnce([string]$Text,[string]$Old,[string]$New,[string]$Label) {
    $first = $Text.IndexOf($Old,[System.StringComparison]::Ordinal)
    if ($first -lt 0) { throw "Patch anchor not found: $Label" }
    $second = $Text.IndexOf($Old,$first + $Old.Length,[System.StringComparison]::Ordinal)
    if ($second -ge 0) { throw "Patch anchor is not unique: $Label" }
    return $Text.Remove($first,$Old.Length).Insert($first,$New)
}

function Write-SourceSafely([string]$Path,[string]$Content) {
    $raw = [System.IO.File]::ReadAllBytes($Path)
    $hasBom = ($raw.Length -ge 3 -and $raw[0] -eq 0xEF -and $raw[1] -eq 0xBB -and $raw[2] -eq 0xBF)
    $utf8 = New-Object System.Text.UTF8Encoding($hasBom)
    [System.IO.File]::WriteAllText($Path,$Content,$utf8)
}

function Get-ReiProcesses {
    return @(
        Get-CimInstance Win32_Process -ErrorAction Stop |
        Where-Object {
            $_.CommandLine -and (
                $_.CommandLine -match 'rei_cycle_v193\.ps1' -or
                $_.CommandLine -match 'rei_shadow_closed_loop_v2\.py'
            )
        } |
        Select-Object ProcessId,Name,CreationDate,CommandLine
    )
}

try {
    Add 'REI-Ω PHASE II.5 ATOMIC OWNERSHIP THROUGH DELETE — CANDIDATE INSTALLER v1'
    Add ('GeneratedLocal={0:o}' -f (Get-Date))

    $pyBefore = Get-Sha $PythonSource
    $shBefore = Get-Sha $SelfHealSource
    Add "PYTHON_SHA256_BEFORE=$pyBefore"
    Add "SELFHEAL_SHA256_BEFORE=$shBefore"
    Add "PYTHON_PIN_MATCH=$($pyBefore -eq $ExpectedPythonSha)"
    Add "SELFHEAL_PIN_MATCH=$($shBefore -eq $ExpectedSelfHealSha)"

    if ($pyBefore -ne $ExpectedPythonSha) { throw 'SAFE_ABORT: Python source pin mismatch.' }
    if ($shBefore -ne $ExpectedSelfHealSha) { throw 'SAFE_ABORT: Self-Heal source pin mismatch.' }

    $preParse = Parse-PowerShell $SelfHealSource
    Add "SELFHEAL_PARSE_ERRORS_BEFORE=$($preParse.Errors.Count)"
    if ($preParse.Errors.Count -ne 0) { throw 'SAFE_ABORT: current Self-Heal does not parse cleanly.' }

    $createdNew = $false
    $Mutex = New-Object System.Threading.Mutex($false,$MutexName,[ref]$createdNew)
    try { $MutexOwned = $Mutex.WaitOne(0) }
    catch [System.Threading.AbandonedMutexException] { $MutexOwned = $true; Add 'CYCLE_MUTEX_ABANDONED_ACQUIRED=True' }
    Add "CYCLE_MUTEX_FENCE_OWNED=$MutexOwned"
    if (-not $MutexOwned) { throw 'SAFE_ABORT: synchronized-cycle mutex is busy.' }

    $pipeline = Get-ScheduledTask -TaskName $PipelineTask -ErrorAction Stop
    $pipelineInfo = Get-ScheduledTaskInfo -TaskName $PipelineTask -ErrorAction Stop
    $selfHeal = Get-ScheduledTask -TaskName $SelfHealTask -ErrorAction Stop
    $selfHealInfo = Get-ScheduledTaskInfo -TaskName $SelfHealTask -ErrorAction Stop

    if ([string]$pipeline.State -eq 'Running') { throw 'SAFE_ABORT: pipeline is running.' }
    if ([string]$selfHeal.State -eq 'Running') { throw 'SAFE_ABORT: Self-Heal is running.' }

    $now = Get-Date
    $pipelineLead = ($pipelineInfo.NextRunTime - $now).TotalSeconds
    $selfHealLead = ($selfHealInfo.NextRunTime - $now).TotalSeconds
    Add ("PIPELINE_NEXT_RUN_LEAD_SECONDS={0:N1}" -f $pipelineLead)
    Add ("SELFHEAL_NEXT_RUN_LEAD_SECONDS={0:N1}" -f $selfHealLead)
    if ($pipelineLead -ge 0 -and $pipelineLead -lt 120) { throw 'SAFE_ABORT: pipeline run is less than 120 seconds away.' }
    if ($selfHealLead -ge 0 -and $selfHealLead -lt 120) { throw 'SAFE_ABORT: Self-Heal run is less than 120 seconds away.' }

    $active = @(Get-ReiProcesses)
    Add "ACTIVE_REI_PROCESS_COUNT=$($active.Count)"
    if ($active.Count -ne 0) { throw 'SAFE_ABORT: active REI production process detected.' }
    if (Test-Path -LiteralPath $RuntimeLock) { throw 'SAFE_ABORT: runtime.lock present; quiescent no-lock window required.' }

    New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
    Copy-Item -LiteralPath $SelfHealSource -Destination $BackupSelfHeal -Force
    $backupSha = Get-Sha $BackupSelfHeal
    Add "BACKUP_SELFHEAL=$BackupSelfHeal"
    Add "BACKUP_SELFHEAL_SHA256=$backupSha"
    if ($backupSha -ne $ExpectedSelfHealSha) { throw 'SAFE_ABORT: backup pin mismatch.' }

    $source = [System.IO.File]::ReadAllText($SelfHealSource)
    $nl = if ($source.Contains("`r`n")) { "`r`n" } else { "`n" }

    if ($source.Contains('function Invoke-OsByteLockProtectedRemoval([string]$LockPath) {')) {
        throw 'SAFE_ABORT: Phase II.5 helper already installed.'
    }

    $helperRaw = @'
function Invoke-OsByteLockProtectedRemoval([string]$LockPath) {
  $result = [ordered]@{
    removed=$false
    authority_acquired=$false
    probe_ok=$false
    cleanup_ok=$true
    stage='precheck'
    reason='atomic_remove_not_run'
    win32_error=$null
    error=''
  }

  if (-not (Test-Path -LiteralPath $LockPath)) {
    $result.reason = 'lock_missing_before_atomic_remove'
    return [pscustomobject]$result
  }

  $stream = $null
  $locked = $false
  try {
    $result.stage = 'open'
    try {
      $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
      $stream = New-Object System.IO.FileStream(
        $LockPath,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::ReadWrite,
        $share
      )
    }
    catch [System.IO.IOException] {
      $result.win32_error = ([int]$_.Exception.HResult -band 0xFFFF)
      $result.reason = 'atomic_remove_open_unavailable'
      return [pscustomobject]$result
    }
    catch {
      $result.reason = 'atomic_remove_open_error'
      $result.error = $_.Exception.Message
      return [pscustomobject]$result
    }

    $result.stage = 'lock'
    try {
      $stream.Lock(0,1)
      $locked = $true
      $result.authority_acquired = $true
      $result.probe_ok = $true
    }
    catch [System.IO.IOException] {
      $result.win32_error = ([int]$_.Exception.HResult -band 0xFFFF)
      $result.reason = 'atomic_remove_authority_unavailable'
      return [pscustomobject]$result
    }
    catch {
      $result.reason = 'atomic_remove_authority_error'
      $result.error = $_.Exception.Message
      return [pscustomobject]$result
    }

    $result.stage = 'remove'
    try {
      Remove-Item -LiteralPath $LockPath -Force -ErrorAction Stop
      $result.removed = $true
      $result.reason = 'atomic_remove_completed'
    }
    catch {
      $result.reason = 'atomic_remove_failed'
      $result.error = $_.Exception.Message
    }
  }
  finally {
    if ($locked -and $null -ne $stream) {
      try { $stream.Unlock(0,1) }
      catch {
        $result.cleanup_ok = $false
        if ($result.reason -eq 'atomic_remove_completed') { $result.reason = 'atomic_remove_completed_unlock_error' }
        if ([string]::IsNullOrWhiteSpace([string]$result.error)) { $result.error = $_.Exception.Message }
      }
    }
    if ($null -ne $stream) {
      try { $stream.Dispose() }
      catch {
        $result.cleanup_ok = $false
        if ($result.reason -eq 'atomic_remove_completed') { $result.reason = 'atomic_remove_completed_dispose_error' }
        if ([string]::IsNullOrWhiteSpace([string]$result.error)) { $result.error = $_.Exception.Message }
      }
    }
  }
  return [pscustomobject]$result
}
'@
    $helper = (($helperRaw -split '\r?\n') -join $nl).TrimEnd([char[]]"`r`n")

    $functionAnchor = 'function Get-HeartbeatFailClosedDecision([string]$LockPath) {'
    $source = Replace-ExactlyOnce -Text $source -Old $functionAnchor -New ($helper + $nl + $nl + $functionAnchor) -Label 'insert protected removal helper'

    $clearOldRaw = @'
                Remove-Item -LiteralPath $lock -Force -ErrorAction Stop
                $actions.Add("removed_orphan_shadow_lock:$lock") | Out-Null
'@
    $clearOld = (($clearOldRaw -split '\r?\n') -join $nl).TrimEnd([char[]]"`r`n")
    $clearNewRaw = @'
                $atomicRemoval = Invoke-OsByteLockProtectedRemoval -LockPath $lock
                if (-not $atomicRemoval.removed) {
                    $warnings.Add(("atomic_remove_preserved:site=Clear-OrphanLocks:{0}:decision={1}:stage={2}:win32={3}:error={4}" -f $lock,$atomicRemoval.reason,$atomicRemoval.stage,$atomicRemoval.win32_error,$atomicRemoval.error)) | Out-Null
                    continue
                }
                if (-not $atomicRemoval.cleanup_ok) {
                    $warnings.Add(("atomic_remove_cleanup_warning:site=Clear-OrphanLocks:{0}:decision={1}:error={2}" -f $lock,$atomicRemoval.reason,$atomicRemoval.error)) | Out-Null
                }
                $actions.Add("removed_orphan_shadow_lock:$lock") | Out-Null
'@
    $clearNew = (($clearNewRaw -split '\r?\n') -join $nl).TrimEnd([char[]]"`r`n")
    $source = Replace-ExactlyOnce -Text $source -Old $clearOld -New $clearNew -Label 'Clear-OrphanLocks atomic removal'

    $repairOldRaw = @'
        Remove-Item -LiteralPath $lockPath -Force -ErrorAction Stop

        $actions.Add(
            ('removed_orphan_runtime_lock:age_minutes={0:N1};backup={1}' -f $ageMinutes,$lockBackup)
        ) | Out-Null
'@
    $repairOld = (($repairOldRaw -split '\r?\n') -join $nl).TrimEnd([char[]]"`r`n")
    $repairNewRaw = @'
        $atomicRemoval = Invoke-OsByteLockProtectedRemoval -LockPath $lockPath
        if (-not $atomicRemoval.removed) {
            $warnings.Add(("atomic_remove_preserved:site=Repair-OrphanRuntimeLock:{0}:decision={1}:stage={2}:win32={3}:error={4}" -f $lockPath,$atomicRemoval.reason,$atomicRemoval.stage,$atomicRemoval.win32_error,$atomicRemoval.error)) | Out-Null
            return
        }
        if (-not $atomicRemoval.cleanup_ok) {
            $warnings.Add(("atomic_remove_cleanup_warning:site=Repair-OrphanRuntimeLock:{0}:decision={1}:error={2}" -f $lockPath,$atomicRemoval.reason,$atomicRemoval.error)) | Out-Null
        }

        $actions.Add(
            ('removed_orphan_runtime_lock:age_minutes={0:N1};backup={1}' -f $ageMinutes,$lockBackup)
        ) | Out-Null
'@
    $repairNew = (($repairNewRaw -split '\r?\n') -join $nl).TrimEnd([char[]]"`r`n")
    $source = Replace-ExactlyOnce -Text $source -Old $repairOld -New $repairNew -Label 'Repair-OrphanRuntimeLock atomic removal'

    Write-SourceSafely -Path $SelfHealSource -Content $source
    $PatchWritten = $true

    $postParse = Parse-PowerShell $SelfHealSource
    Add "SELFHEAL_PARSE_ERRORS_AFTER=$($postParse.Errors.Count)"
    if ($postParse.Errors.Count -ne 0) { throw 'POST_VERIFY_FAIL: patched Self-Heal has parser errors.' }

    $postText = [System.IO.File]::ReadAllText($SelfHealSource)
    $checks = [ordered]@{
        ATOMIC_HELPER_PRESENT = $postText.Contains('function Invoke-OsByteLockProtectedRemoval([string]$LockPath) {')
        FILESHARE_DELETE_PRESENT = $postText.Contains('[System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete')
        HELD_REMOVE_PRESENT = $postText.Contains('Remove-Item -LiteralPath $LockPath -Force -ErrorAction Stop')
        CLEAR_ATOMIC_CALL_PRESENT = $postText.Contains('                $atomicRemoval = Invoke-OsByteLockProtectedRemoval -LockPath $lock')
        REPAIR_ATOMIC_CALL_PRESENT = $postText.Contains('        $atomicRemoval = Invoke-OsByteLockProtectedRemoval -LockPath $lockPath')
        OLD_CLEAR_BARE_REMOVE_ABSENT = -not $postText.Contains('                Remove-Item -LiteralPath $lock -Force -ErrorAction Stop')
        OLD_REPAIR_BARE_REMOVE_ABSENT = -not $postText.Contains('        Remove-Item -LiteralPath $lockPath -Force -ErrorAction Stop')
        PHASEII4_OS_HELPER_PRESERVED = $postText.Contains('function Get-OsByteLockDecision([string]$LockPath) {')
        HEARTBEAT_ADVISORY_PRESERVED = $postText.Contains('heartbeat_advisory_ignored_os_lock_free')
    }
    foreach ($kv in $checks.GetEnumerator()) {
        Add ("{0}={1}" -f $kv.Key,$kv.Value)
        if (-not $kv.Value) { throw "POST_VERIFY_FAIL: structural check failed: $($kv.Key)" }
    }

    $pyAfter = Get-Sha $PythonSource
    $shAfter = Get-Sha $SelfHealSource
    Add "PYTHON_SHA256_AFTER=$pyAfter"
    Add "SELFHEAL_SHA256_AFTER=$shAfter"
    Add "PYTHON_UNCHANGED=$($pyAfter -eq $ExpectedPythonSha)"
    Add "SELFHEAL_CHANGED=$($shAfter -ne $ExpectedSelfHealSha)"
    if ($pyAfter -ne $ExpectedPythonSha) { throw 'POST_VERIFY_FAIL: Python source changed unexpectedly.' }
    if ($shAfter -eq $ExpectedSelfHealSha) { throw 'POST_VERIFY_FAIL: Self-Heal hash did not change.' }

    $Final = 'PASS_PHASEII5_ATOMIC_OWNERSHIP_PATCH_INSTALLED_CANDIDATE'
    Add 'NEXT_REQUIRED_STEP=RUN_0045A_0045B_0045C_0045D_UNDER_ONE_PINNED_NEW_SELFHEAL_HASH'
    Add 'REALITY_VALIDATED=False'
    Add 'PROMOTION=NO'
}
catch {
    Add "ERROR=$($_.Exception.Message)"
    if ($PatchWritten -and (Test-Path -LiteralPath $BackupSelfHeal -PathType Leaf)) {
        try {
            Copy-Item -LiteralPath $BackupSelfHeal -Destination $SelfHealSource -Force
            $rollbackSha = Get-Sha $SelfHealSource
            Add 'ROLLBACK_ATTEMPTED=True'
            Add "ROLLBACK_SHA256=$rollbackSha"
            Add "ROLLBACK_MATCHES_PHASEII4_PIN=$($rollbackSha -eq $ExpectedSelfHealSha)"
            if ($rollbackSha -eq $ExpectedSelfHealSha) { $Final = 'SAFE_ABORT_PHASEII5_PATCH_ROLLED_BACK' }
        }
        catch {
            Add "ROLLBACK_ERROR=$($_.Exception.Message)"
            $Final = 'FAIL_PHASEII5_PATCH_ROLLBACK_UNCERTAIN'
        }
    }
    elseif ($Final -eq 'FAIL_PHASEII5_ATOMIC_OWNERSHIP_PATCH_V1') {
        $Final = 'SAFE_ABORT_PHASEII5_PATCH_NO_MUTATION_CONFIRMED'
    }
}
finally {
    if ($MutexOwned -and $null -ne $Mutex) {
        try { $Mutex.ReleaseMutex(); Add 'CYCLE_MUTEX_RELEASED=True' }
        catch { Add "CYCLE_MUTEX_RELEASE_ERROR=$($_.Exception.Message)" }
    }
    if ($null -ne $Mutex) { try { $Mutex.Dispose() } catch {} }
    Add "FINAL_STATUS=$Final"
    Add "EVIDENCE=$Evidence"
    $Lines | Set-Content -LiteralPath $Evidence -Encoding UTF8
    Write-Host "FINAL_STATUS=$Final"
    Write-Host "EVIDENCE=$Evidence"
}
