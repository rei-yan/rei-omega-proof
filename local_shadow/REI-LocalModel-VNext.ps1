<#
REI local-model vNext overlay.
Builds an observer-governed Ollama model on top of the already synchronized
rei-local-node context. It does not write REI canonical state.
#>
[CmdletBinding()]
param(
    [string]$ContextDir = "C:\REI-Shadow\context",
    [string]$BaseModel = "rei-local-node",
    [string]$ModelName = "rei-local-node-vnext",
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProtocolVersion = "REI-CLP/3.0-observer"
$StatePath = Join-Path $ContextDir "model_vnext_state.json"
$ModelFilePath = Join-Path $ContextDir "Modelfile.rei-local-vnext"
$ContextHashPath = Join-Path $ContextDir "context.sha256"

function Write-AtomicUtf8 {
    param([string]$Path, [string]$Content)
    $directory = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    $temporary = Join-Path $directory ([System.IO.Path]::GetRandomFileName())
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($temporary, $Content, $utf8NoBom)
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Get-Sha256Text {
    param([string]$Text)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant() }
    finally { $sha.Dispose() }
}

if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) { Write-Host "VNEXT_LOCAL_MODEL_FAILED_CLOSED: ollama not found"; exit 2 }
New-Item -ItemType Directory -Path $ContextDir -Force | Out-Null
$contextHash = if (Test-Path -LiteralPath $ContextHashPath) { (Get-Content -LiteralPath $ContextHashPath -Raw).Trim() } else { "NO_CONTEXT_HASH" }
$contract = @"
Protocol: $ProtocolVersion
Mode: OBSERVER_ONLY
Canonical write permission: FALSE

You are the local REI candidate-generation model operating under an observer-governed closed-loop protocol.
Preserve multiple live hypotheses when evidence is insufficient. Do not force premature collapse to one answer.
For every substantive claim, distinguish evidence from model inference; preserve provenance and source dependence.
Search for the strongest counterexample, OOD failure, causal confounder, duplicate evidence, contamination risk, and rollback trigger.
Confidence is not authority. High confidence, high review score, or repeated evidence never grants canonical promotion.
When inputs contain a numeric time series, spectral reasoning may be proposed as an observer feature; otherwise mark spectral analysis not applicable.
Hypothesis mixtures are ordinary epistemic alternatives, not quantum superposition and not quantum-computing capability.
Never claim independent replication, reality validation, externally witnessed prediction, ascension, or world-best status without external evidence.
Never perform external actions or write canonical/main. Output remains proposal-only for Shadow and Divine Wheel review.
"@
$fingerprint = Get-Sha256Text -Text ($ProtocolVersion + "|" + $contextHash + "|" + $contract)
$previousFingerprint = ""
if (Test-Path -LiteralPath $StatePath) { try { $previousFingerprint = [string]((Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json).fingerprint) } catch { $previousFingerprint = "" } }
$available = (& ollama list 2>&1 | Out-String)
if ($LASTEXITCODE -ne 0) { Write-Host "VNEXT_LOCAL_MODEL_FAILED_CLOSED: ollama list failed"; exit 2 }
$escapedBase = [Regex]::Escape($BaseModel)
if ($available -notmatch "(?m)^$escapedBase\s") { Write-Host "VNEXT_LOCAL_MODEL_FAILED_CLOSED: base model '$BaseModel' missing"; exit 2 }
$escapedTarget = [Regex]::Escape($ModelName); $targetExists = $available -match "(?m)^$escapedTarget\s"
if (-not $Force -and $targetExists -and $fingerprint -eq $previousFingerprint) {
    Write-Host "VNEXT_LOCAL_MODEL_NO_CHANGE"; Write-Host "Model: $ModelName"; Write-Host "Protocol: $ProtocolVersion"; exit 0
}
$safeContract = $contract.Replace('"""', "'''")
$modelFile = @"
FROM $BaseModel
PARAMETER temperature 0.15
PARAMETER num_ctx 32768
SYSTEM """
$safeContract
"""
"@
Write-AtomicUtf8 -Path $ModelFilePath -Content $modelFile
& ollama create $ModelName -f $ModelFilePath
if ($LASTEXITCODE -ne 0) { Write-Host "VNEXT_LOCAL_MODEL_FAILED_CLOSED: ollama create failed"; exit 2 }
$state = [ordered]@{ schema_version = 1; protocol_version = $ProtocolVersion; observer_mode = $true; base_model = $BaseModel;
    model_name = $ModelName; context_sha256 = $contextHash; fingerprint = $fingerprint;
    refreshed_at_utc = (Get-Date).ToUniversalTime().ToString("o"); canonical_write_permission = $false } | ConvertTo-Json -Depth 5
Write-AtomicUtf8 -Path $StatePath -Content $state
Write-Host "VNEXT_LOCAL_MODEL_SUCCESS"; Write-Host "Model: $ModelName"; Write-Host "Protocol: $ProtocolVersion"; Write-Host "Canonical write permission: FALSE"
