<#
REI Local Sync for Windows + Ollama

This script keeps a local REI context bundle synchronized from GitHub.
It separates merged canonical material from open pull-request candidates.
Optionally, it rebuilds an Ollama context model when the bundle changes.

Examples:
  powershell -ExecutionPolicy Bypass -File .\REI-LocalSync.ps1 -Once
  powershell -ExecutionPolicy Bypass -File .\REI-LocalSync.ps1 -Once -BaseModel "MODEL_FROM_OLLAMA_LIST"
  powershell -ExecutionPolicy Bypass -File .\REI-LocalSync.ps1 -Install -BaseModel "MODEL_FROM_OLLAMA_LIST"
  powershell -ExecutionPolicy Bypass -File .\REI-LocalSync.ps1 -Uninstall
#>

[CmdletBinding()]
param(
    [string]$Repo = "rei-yan/rei-omega-proof",
    [int]$PullRequest = 25,
    [string]$OutputDir = "C:\REI-Shadow\context",
    [string]$BaseModel = $(if ($env:REI_OLLAMA_BASE_MODEL) { $env:REI_OLLAMA_BASE_MODEL } else { "qwen3:8b" }),
    [string]$LocalModelName = "rei-local-node",
    [ValidateRange(30, 3600)]
    [int]$PollSeconds = 60,
    [switch]$Once,
    [switch]$Install,
    [switch]$Uninstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$TaskName = "REI Local Context Sync"

function Write-Log {
    param([string]$Message)
    $line = "[$((Get-Date).ToString('s'))] $Message"
    Write-Host $line
    if (Test-Path -LiteralPath $OutputDir) {
        Add-Content -LiteralPath (Join-Path $OutputDir "sync.log") -Value $line -Encoding UTF8
    }
}

function Write-AtomicUtf8 {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Content
    )
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
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Update-OllamaContextModel {
    param(
        [string]$ContextBundle,
        [string]$ModelBase,
        [string]$ModelName
    )

    if ([string]::IsNullOrWhiteSpace($ModelBase)) {
        Write-Log "Context updated. Ollama refresh skipped because -BaseModel was not supplied."
        return $false
    }

    if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) {
        Write-Log "Context updated, but Ollama was not found in PATH."
        return $false
    }

    $availableModels = (& ollama list 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Context updated, but 'ollama list' failed."
        return $false
    }

    $escapedModel = [Regex]::Escape($ModelBase)
    if ($availableModels -notmatch "(?m)^$escapedModel\s") {
        Write-Log "Base model '$ModelBase' is not installed. Run 'ollama list' and pass an exact installed name."
        return $false
    }

    $safeBundle = $ContextBundle.Replace('"""', "'''")
    $modelFilePath = Join-Path $OutputDir "Modelfile.rei-local"
    $modelFile = @"
FROM $ModelBase
PARAMETER temperature 0.2
PARAMETER num_ctx 32768
SYSTEM """
You are the local REI research assistant.

The synchronized material contains two explicitly different states:
1. CANONICAL: merged GitHub main content.
2. CANDIDATE: open pull-request content.

Never describe candidate material as canonical unless it is merged into main.
Never treat internal CI or synthetic tests as independent external validation.
Keep open evidence gates, failures, UNKNOWN states, rollback requirements, and complexity debt visible.
The permanent core name is 无相神核.

$safeBundle
"""
"@
    Write-AtomicUtf8 -Path $modelFilePath -Content $modelFile

    Write-Log "Refreshing Ollama model '$ModelName' from '$ModelBase'..."
    & ollama create $ModelName -f $modelFilePath
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Ollama refresh failed. The synchronized context files remain valid."
        return $false
    }

    Write-Log "Ollama model '$ModelName' refreshed successfully."
    return $true
}

function Invoke-ReiSync {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    $headers = @{ "User-Agent" = "REI-Local-Sync"; "Accept" = "application/vnd.github+json" }

    $pr = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/pulls/$PullRequest" -Headers $headers -Method Get
    $baseRef = [string]$pr.base.ref
    $headRef = [string]$pr.head.ref
    $headSha = [string]$pr.head.sha
    $merged = [bool]$pr.merged
    $prState = [string]$pr.state

    $canonical = (Invoke-WebRequest -Uri "https://raw.githubusercontent.com/$Repo/$baseRef/CURRENT_REI_CHAT_HANDOFF.md" -Headers $headers -UseBasicParsing).Content
    $candidate = (Invoke-WebRequest -Uri "https://raw.githubusercontent.com/$Repo/$headRef/CURRENT_REI_STRENGTH.md" -Headers $headers -UseBasicParsing).Content
    $stableBundle = @"
# REI LOCAL SYNCHRONIZED CONTEXT

Repository: $Repo
Pull request: #$PullRequest
PR state: $prState
PR merged: $merged
Candidate head: $headSha

## STATUS CONTRACT

CANONICAL comes only from the merged GitHub base branch.
CANDIDATE comes from the open pull-request head.
CandidatePR != CanonicalMain
GreenCI != IndependentReplication
RealityVeto > REI

## CANONICAL — $baseRef

$canonical

## CANDIDATE — PR #$PullRequest / $headRef / $headSha

$candidate
"@

    $bundlePath = Join-Path $OutputDir "REI_LOCAL_CONTEXT.md"
    # Hash only source-derived content. A sync timestamp must not trigger a rebuild
    # on every polling interval when GitHub itself has not changed.
    $newHash = Get-Sha256Text -Text $stableBundle
    $hashPath = Join-Path $OutputDir "context.sha256"
    $oldHash = if (Test-Path -LiteralPath $hashPath) { (Get-Content -LiteralPath $hashPath -Raw).Trim() } else { "" }

    if ($newHash -eq $oldHash) {
        Write-Log "No substantive GitHub context change."
        return
    }

    $syncedAt = (Get-Date).ToUniversalTime().ToString("o")
    $bundle = $stableBundle.Replace(
        "# REI LOCAL SYNCHRONIZED CONTEXT",
        "# REI LOCAL SYNCHRONIZED CONTEXT`r`n`r`nSynced at UTC: $syncedAt"
    )

    Write-AtomicUtf8 -Path (Join-Path $OutputDir "CANONICAL_MAIN.md") -Content $canonical
    Write-AtomicUtf8 -Path (Join-Path $OutputDir "CANDIDATE_PR25.md") -Content $candidate
    Write-AtomicUtf8 -Path $bundlePath -Content $bundle
    Write-AtomicUtf8 -Path $hashPath -Content $newHash

    $ollamaRefreshed = Update-OllamaContextModel -ContextBundle $bundle -ModelBase $BaseModel -ModelName $LocalModelName
    $state = [ordered]@{
        synced_at_utc = $syncedAt
        repository = $Repo
        pull_request = $PullRequest
        pull_request_state = $prState
        merged = $merged
        base_ref = $baseRef
        head_ref = $headRef
        head_sha = $headSha
        context_sha256 = $newHash
        ollama_base_model = $BaseModel
        ollama_model_name = $LocalModelName
        ollama_refreshed = $ollamaRefreshed
        canonical_rule = "Only merged base-branch content is canonical."
    } | ConvertTo-Json -Depth 4
    Write-AtomicUtf8 -Path (Join-Path $OutputDir "sync_state.json") -Content $state
    Write-Log "REI local context synchronized at head $headSha."
}

function Install-ReiSyncTask {
    $scriptPath = $PSCommandPath
    if (-not (Test-Path -LiteralPath $scriptPath)) { throw "Save this script locally before using -Install." }

    $arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`" -PollSeconds $PollSeconds -LocalModelName `"$LocalModelName`""
    if (-not [string]::IsNullOrWhiteSpace($BaseModel)) { $arguments += " -BaseModel `"$BaseModel`"" }

    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arguments
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero)
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "Keeps REI GitHub context synchronized with local Ollama." -Force | Out-Null
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Installed and started scheduled task: $TaskName"
}

function Uninstall-ReiSyncTask {
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Removed scheduled task: $TaskName"
    }
    else {
        Write-Host "Scheduled task not found: $TaskName"
    }
}

if ($Uninstall) { Uninstall-ReiSyncTask; exit 0 }
if ($Install) { Install-ReiSyncTask; exit 0 }

$createdNew = $false
$mutex = New-Object System.Threading.Mutex($true, "Local\REI_Local_Context_Sync", [ref]$createdNew)
if (-not $createdNew) { Write-Host "REI Local Sync is already running."; exit 0 }

try {
    do {
        try { Invoke-ReiSync }
        catch { Write-Log ("Sync error: " + $_.Exception.Message) }
        if (-not $Once) { Start-Sleep -Seconds $PollSeconds }
    } while (-not $Once)
}
finally {
    try { $mutex.ReleaseMutex() } catch { }
    $mutex.Dispose()
}
