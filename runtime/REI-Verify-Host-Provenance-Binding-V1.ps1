# REI-Ω Host Provenance Binding Verifier v1
# Verifies a fresh host provenance receipt against an explicit repository binding map.
# This verifier is intentionally fail-closed. It grants no promotion or reality authority.

param(
    [string]$ReceiptPath = 'C:\REI-Shadow\state\provenance\host-provenance-latest.json',
    [string]$BindingPath = (Join-Path $PSScriptRoot 'host-executable-binding-v1.json')
)

$ErrorActionPreference = 'Stop'

function Fail([string]$Reason, [int]$Code = 2) {
    Write-Host 'REI_HOST_PROVENANCE_BINDING=FAIL'
    Write-Host ("Reason: {0}" -f $Reason)
    Write-Host 'RealityValidated=FALSE'
    Write-Host 'IndependentReplication=FALSE'
    Write-Host 'ASCENSION_GRANTED=NO'
    Write-Host 'CanonicalPromotion=NO'
    exit $Code
}

if (-not (Test-Path -LiteralPath $ReceiptPath -PathType Leaf)) {
    Fail "Host provenance receipt missing: $ReceiptPath"
}
if (-not (Test-Path -LiteralPath $BindingPath -PathType Leaf)) {
    Fail "Binding map missing: $BindingPath"
}

try {
    $receipt = Get-Content -LiteralPath $ReceiptPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $binding = Get-Content -LiteralPath $BindingPath -Raw -Encoding UTF8 | ConvertFrom-Json
}
catch {
    Fail ("Invalid JSON input: " + $_.Exception.Message)
}

if ([int]$receipt.schema_version -ne 1 -or [string]$receipt.receipt_type -ne 'HOST_PROVENANCE_SNAPSHOT') {
    Fail 'Unexpected host provenance receipt schema/type'
}
if ([int]$binding.schema_version -ne 1 -or [string]$binding.binding_id -ne 'REI_HOST_EXECUTABLE_BINDING_V1') {
    Fail 'Unexpected host provenance binding schema/type'
}

$receiptById = @{}
foreach ($component in @($receipt.components)) {
    $id = [string]$component.id
    if ([string]::IsNullOrWhiteSpace($id)) { Fail 'Receipt contains component with empty id' }
    if ($receiptById.ContainsKey($id)) { Fail "Duplicate receipt component id: $id" }
    $receiptById[$id] = $component
}

$bindingById = @{}
foreach ($entry in @($binding.bindings)) {
    $id = [string]$entry.id
    if ([string]::IsNullOrWhiteSpace($id)) { Fail 'Binding map contains component with empty id' }
    if ($bindingById.ContainsKey($id)) { Fail "Duplicate binding component id: $id" }
    $bindingById[$id] = $entry
}

$requiredIds = @('shadow','context-sync','local-model','wheel-pull','observer','bridge','git-sync')
$failures = New-Object System.Collections.Generic.List[string]
$matched = 0

foreach ($id in $requiredIds) {
    if (-not $receiptById.ContainsKey($id)) {
        $failures.Add("receipt_missing:$id") | Out-Null
        continue
    }
    if (-not $bindingById.ContainsKey($id)) {
        $failures.Add("binding_missing:$id") | Out-Null
        continue
    }

    $component = $receiptById[$id]
    $entry = $bindingById[$id]

    if (-not [bool]$component.exists) {
        $failures.Add("host_file_missing:$id") | Out-Null
        continue
    }

    $hostSha = ([string]$component.sha256).ToLowerInvariant()
    $expectedSha = ([string]$entry.expected_sha256).ToLowerInvariant()
    $repoPath = [string]$entry.repository_path
    $commitSha = [string]$entry.repository_commit_sha
    $status = [string]$entry.status

    if ($status -ne 'BOUND') {
        $failures.Add("binding_not_bound:$id:$status") | Out-Null
        continue
    }
    if ([string]::IsNullOrWhiteSpace($repoPath)) {
        $failures.Add("repository_path_missing:$id") | Out-Null
        continue
    }
    if ([string]::IsNullOrWhiteSpace($commitSha) -or $commitSha -notmatch '^[0-9a-fA-F]{40}$') {
        $failures.Add("repository_commit_invalid:$id") | Out-Null
        continue
    }
    if ([string]::IsNullOrWhiteSpace($expectedSha) -or $expectedSha -notmatch '^[0-9a-f]{64}$') {
        $failures.Add("expected_sha256_invalid:$id") | Out-Null
        continue
    }
    if ($hostSha -ne $expectedSha) {
        $failures.Add("sha256_mismatch:$id:host=$hostSha:expected=$expectedSha") | Out-Null
        continue
    }

    $matched += 1
}

if ($failures.Count -gt 0) {
    Write-Host 'REI_HOST_PROVENANCE_BINDING=FAIL'
    Write-Host ("Matched: {0}/{1}" -f $matched, $requiredIds.Count)
    foreach ($failure in $failures) { Write-Host ("FAILURE: {0}" -f $failure) }
    Write-Host 'RealityValidated=FALSE'
    Write-Host 'IndependentReplication=FALSE'
    Write-Host 'ASCENSION_GRANTED=NO'
    Write-Host 'CanonicalPromotion=NO'
    exit 2
}

Write-Host 'REI_HOST_PROVENANCE_BINDING=PASS'
Write-Host ("Matched: {0}/{1}" -f $matched, $requiredIds.Count)
Write-Host 'EvidenceGrade=HOST_VERSION_BINDING_ONLY'
Write-Host 'RealityValidated=FALSE'
Write-Host 'IndependentReplication=FALSE'
Write-Host 'ASCENSION_GRANTED=NO'
Write-Host 'CanonicalPromotion=NO'
exit 0
