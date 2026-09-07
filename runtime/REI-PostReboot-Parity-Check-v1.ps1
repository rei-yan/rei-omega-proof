# REI-Ω read-only post-reboot parity check v1
# No mutation. No task start/stop. No file writes.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ParityPath = 'C:\REI-Shadow\repo\shadow\local_runtime_parity.json'
$PythonSource = 'C:\REI\rei_shadow_closed_loop_v2.py'
$SelfHealSource = 'C:\REI-Shadow\runtime-v191\REI-Local-SelfHeal-V1.ps1'
$ExpectedBaselineSha = 'cc85cb647188eefe182cfc5ab6364d9f146ef96a'
$ExpectedPythonSha = '6752672711E1FF7BA5F7035221E88403EAAEE716E444573D82477A62D51EC3DB'
$ExpectedSelfHealSha = '11CECB2192E7555029804A8A75BB3FB6394302F11F09FF1E5CF2DA1D69CF4323'

function Sha([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return '' }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToUpperInvariant()
}

$boot = (Get-CimInstance Win32_OperatingSystem -ErrorAction Stop).LastBootUpTime.ToUniversalTime()
$now = [DateTime]::UtcNow

Write-Host '=== REI POST-REBOOT PARITY CHECK v1 ==='
Write-Host ("NOW_UTC={0:o}" -f $now)
Write-Host ("LAST_BOOT_UTC={0:o}" -f $boot)

$pySha = Sha $PythonSource
$shSha = Sha $SelfHealSource
Write-Host "PYTHON_SHA_MATCH=$($pySha -eq $ExpectedPythonSha)"
Write-Host "SELFHEAL_PHASEII4_SHA_MATCH=$($shSha -eq $ExpectedSelfHealSha)"
Write-Host "PYTHON_SHA256=$pySha"
Write-Host "SELFHEAL_SHA256=$shSha"

$pipelineInfo = Get-ScheduledTaskInfo -TaskName 'REI Full Pipeline v1.9.1' -ErrorAction Stop
$selfHealInfo = Get-ScheduledTaskInfo -TaskName 'REI Local Self Heal v1' -ErrorAction Stop
Write-Host "PIPELINE_LAST_RESULT=$($pipelineInfo.LastTaskResult)"
Write-Host ("PIPELINE_LAST_RUN={0:o}" -f $pipelineInfo.LastRunTime)
Write-Host "SELFHEAL_LAST_RESULT=$($selfHealInfo.LastTaskResult)"
Write-Host ("SELFHEAL_LAST_RUN={0:o}" -f $selfHealInfo.LastRunTime)

if (-not (Test-Path -LiteralPath $ParityPath -PathType Leaf)) {
    Write-Host 'PARITY_PRESENT=False'
    Write-Host 'POST_REBOOT_PARITY_PASS=False'
    exit 2
}

$item = Get-Item -LiteralPath $ParityPath -ErrorAction Stop
$parity = Get-Content -LiteralPath $ParityPath -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
$freshAfterBoot = $item.LastWriteTimeUtc -gt $boot
$headMatch = [string]$parity.candidate_head_sha -eq $ExpectedBaselineSha
$prMatch = [int]$parity.candidate_pull_request -eq 28
$completed = [string]$parity.runtime_status -eq 'COMPLETED'
$errorsZero = [int]$parity.runtime_errors_count -eq 0
$canonicalUntouched = -not [bool]$parity.canonical_mainline_touched
$canonicalWriteFalse = -not [bool]$parity.canonical_write_permission
$coreCommittedFalse = -not [bool]$parity.core_committed
$realityFalse = -not [bool]$parity.reality_validated
$ascensionFalse = -not [bool]$parity.ascension_granted
$pipelineOk = $pipelineInfo.LastTaskResult -eq 0
$selfHealOk = $selfHealInfo.LastTaskResult -eq 0
$pythonOk = $pySha -eq $ExpectedPythonSha
$selfHealPinOk = $shSha -eq $ExpectedSelfHealSha

Write-Host 'PARITY_PRESENT=True'
Write-Host ("PARITY_LASTWRITE_UTC={0:o}" -f $item.LastWriteTimeUtc)
Write-Host "PARITY_FRESH_AFTER_BOOT=$freshAfterBoot"
Write-Host "PARITY_PR28_MATCH=$prMatch"
Write-Host "PARITY_HEAD_SHA_MATCH=$headMatch"
Write-Host "PARITY_RUNTIME_COMPLETED=$completed"
Write-Host "PARITY_RUNTIME_ERRORS_ZERO=$errorsZero"
Write-Host "PARITY_CANONICAL_UNTOUCHED=$canonicalUntouched"
Write-Host "PARITY_CANONICAL_WRITE_FALSE=$canonicalWriteFalse"
Write-Host "PARITY_CORE_COMMITTED_FALSE=$coreCommittedFalse"
Write-Host "PARITY_REALITY_VALIDATED_FALSE=$realityFalse"
Write-Host "PARITY_ASCENSION_FALSE=$ascensionFalse"
Write-Host "PARITY_SOURCE_CYCLE_ID=$($parity.source_cycle_id)"
Write-Host "PARITY_OBSERVED_AT_UTC=$($parity.observed_at_utc)"

$pass = (
    $freshAfterBoot -and
    $prMatch -and
    $headMatch -and
    $completed -and
    $errorsZero -and
    $canonicalUntouched -and
    $canonicalWriteFalse -and
    $coreCommittedFalse -and
    $realityFalse -and
    $ascensionFalse -and
    $pipelineOk -and
    $selfHealOk -and
    $pythonOk -and
    $selfHealPinOk
)

Write-Host "POST_REBOOT_PARITY_PASS=$pass"
if ($pass) { exit 0 }
exit 1
