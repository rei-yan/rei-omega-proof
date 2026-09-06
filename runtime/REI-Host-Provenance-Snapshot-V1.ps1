# REI-Ω Host Provenance Snapshot v1
# Read-only inventory of the host-side executables invoked by rei_cycle_v193.ps1.
# This script does NOT deploy, mutate runtime state, touch canonical state, or grant promotion.

param(
    [string]$ManifestPath = (Join-Path $PSScriptRoot 'host-executable-manifest-v1.json'),
    [string]$RepoPath = 'C:\REI-Shadow\repo',
    [string]$OutputPath = 'C:\REI-Shadow\state\provenance\host-provenance-latest.json',
    [string]$ExpectedHeadRef = 'rei-v193-reconcile',
    [string]$ExpectedHeadSha = ''
)

$ErrorActionPreference = 'Stop'

function Get-UtcNow {
    return [DateTime]::UtcNow.ToString('o')
}

function Write-JsonAtomic([string]$Path, $Object) {
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    $temp = Join-Path $dir ('.' + [IO.Path]::GetFileName($Path) + '.' + $PID + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    try {
        $Object | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $temp -Encoding UTF8
        Move-Item -LiteralPath $temp -Destination $Path -Force
    }
    finally {
        if (Test-Path -LiteralPath $temp) {
            Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
        }
    }
}

function Get-GitValue([string[]]$Args) {
    try {
        $value = (& git.exe -C $RepoPath @Args 2>$null | Out-String).Trim()
        if ($LASTEXITCODE -ne 0) { return $null }
        return $value
    }
    catch { return $null }
}

if (-not (Test-Path -LiteralPath $ManifestPath)) {
    throw "Host executable manifest missing: $ManifestPath"
}

$manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ([int]$manifest.schema_version -ne 1) {
    throw "Unsupported host executable manifest schema: $($manifest.schema_version)"
}

$components = @()
foreach ($entry in @($manifest.components)) {
    $path = [string]$entry.host_path
    $exists = Test-Path -LiteralPath $path -PathType Leaf
    $sha256 = $null
    $bytes = $null
    $lastWriteUtc = $null
    if ($exists) {
        $item = Get-Item -LiteralPath $path
        $sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        $bytes = [int64]$item.Length
        $lastWriteUtc = $item.LastWriteTimeUtc.ToString('o')
    }
    $components += [ordered]@{
        id = [string]$entry.id
        host_path = $path
        required = [bool]$entry.required
        exists = [bool]$exists
        sha256 = $sha256
        bytes = $bytes
        last_write_utc = $lastWriteUtc
        repository_binding = 'UNESTABLISHED'
        repository_path = $null
        repository_blob_sha = $null
        repository_commit_sha = $null
    }
}

$required = @($components | Where-Object { $_.required })
$allRequiredPresent = (@($required | Where-Object { -not $_.exists }).Count -eq 0)
$allRequiredHashed = (@($required | Where-Object { [string]::IsNullOrWhiteSpace([string]$_.sha256) }).Count -eq 0)

$repoPresent = Test-Path -LiteralPath $RepoPath -PathType Container
$repoBranch = $null
$repoHeadSha = $null
$repoDirty = $null
if ($repoPresent -and (Get-Command git.exe -ErrorAction SilentlyContinue)) {
    $repoBranch = Get-GitValue @('rev-parse','--abbrev-ref','HEAD')
    $repoHeadSha = Get-GitValue @('rev-parse','HEAD')
    $status = Get-GitValue @('status','--porcelain')
    if ($null -ne $status) { $repoDirty = -not [string]::IsNullOrWhiteSpace($status) }
}

$refMatches = ($repoBranch -eq $ExpectedHeadRef)
$shaCheckRequested = -not [string]::IsNullOrWhiteSpace($ExpectedHeadSha)
$shaMatches = if ($shaCheckRequested) { $repoHeadSha -eq $ExpectedHeadSha } else { $null }

$receipt = [ordered]@{
    schema_version = 1
    receipt_type = 'HOST_PROVENANCE_SNAPSHOT'
    generated_at_utc = Get-UtcNow
    host = $env:COMPUTERNAME
    candidate_pull_request = 28
    expected_head_ref = $ExpectedHeadRef
    expected_head_sha = if ($shaCheckRequested) { $ExpectedHeadSha } else { $null }
    manifest_id = [string]$manifest.manifest_id
    manifest_path = $ManifestPath
    repo = [ordered]@{
        path = $RepoPath
        present = [bool]$repoPresent
        branch = $repoBranch
        head_sha = $repoHeadSha
        dirty = $repoDirty
        expected_ref_match = [bool]$refMatches
        expected_sha_check_requested = [bool]$shaCheckRequested
        expected_sha_match = $shaMatches
    }
    components = $components
    summary = [ordered]@{
        required_component_count = $required.Count
        required_present_count = @($required | Where-Object { $_.exists }).Count
        required_hashed_count = @($required | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_.sha256) }).Count
        all_required_files_present = [bool]$allRequiredPresent
        all_required_files_hashed = [bool]$allRequiredHashed
        repository_binding_complete = $false
        status = if ($allRequiredPresent -and $allRequiredHashed) { 'HOST_HASHES_CAPTURED_REPO_BINDING_NOT_YET_ESTABLISHED' } else { 'HOST_PROVENANCE_INCOMPLETE' }
    }
    authority_boundary = [ordered]@{
        evidence_grade = 'HOST_INTERNAL_PROVENANCE_ONLY'
        reality_validated = $false
        independent_replication = $false
        ascension_granted = $false
        canonical_write_permission = $false
        promotion_permission = $false
    }
}

Write-JsonAtomic -Path $OutputPath -Object $receipt

Write-Host 'REI_HOST_PROVENANCE_SNAPSHOT_COMPLETE'
Write-Host ("Receipt: {0}" -f $OutputPath)
Write-Host ("Required present: {0}/{1}" -f $receipt.summary.required_present_count, $receipt.summary.required_component_count)
Write-Host ("Required hashed: {0}/{1}" -f $receipt.summary.required_hashed_count, $receipt.summary.required_component_count)
Write-Host ("Repo branch: {0}" -f $repoBranch)
Write-Host ("Repo head: {0}" -f $repoHeadSha)
Write-Host ("Status: {0}" -f $receipt.summary.status)
Write-Host 'RealityValidated=FALSE'
Write-Host 'IndependentReplication=FALSE'
Write-Host 'ASCENSION_GRANTED=NO'
Write-Host 'CanonicalPromotion=NO'
