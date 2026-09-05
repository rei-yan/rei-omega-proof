<#
REI Local Sync for Windows + Ollama
Reconciled candidate contract: PR #28 / rei-v193-reconcile.
This copy mirrors the active shadow-node context synchronizer semantics.
#>
[CmdletBinding()]
param(
    [string]$Repo = "rei-yan/rei-omega-proof",
    [int]$PullRequest = 28,
    [string]$OutputDir = "C:\REI-Shadow\context",
    [string]$BaseModel = $(if ($env:REI_OLLAMA_BASE_MODEL) { $env:REI_OLLAMA_BASE_MODEL } else { "qwen3:8b" }),
    [string]$LocalModelName = "rei-local-node",
    [ValidateRange(30, 3600)][int]$PollSeconds = 60,
    [switch]$ContextOnly,
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
    if (Test-Path -LiteralPath $OutputDir) { Add-Content -LiteralPath (Join-Path $OutputDir "sync.log") -Value $line -Encoding UTF8 }
}

function Write-AtomicUtf8 {
    param([string]$Path,[AllowEmptyString()][string]$Content)
    $directory = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    $temporary = Join-Path $directory ([IO.Path]::GetRandomFileName())
    $utf8NoBom = New-Object Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($temporary,$Content,$utf8NoBom)
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Get-Sha256Text([string]$Text) {
    $bytes = [Text.Encoding]::UTF8.GetBytes($Text)
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-','').ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function Update-OllamaContextModel([string]$ContextBundle,[string]$ModelBase,[string]$ModelName) {
    if ([string]::IsNullOrWhiteSpace($ModelBase)) { Write-Log "Context updated; Ollama refresh skipped."; return $false }
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { Write-Log "Ollama not found."; return $false }
    $available = (& ollama list 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) { Write-Log "ollama list failed."; return $false }
    $escaped = [Regex]::Escape($ModelBase)
    if ($available -notmatch "(?m)^$escaped\s") { Write-Log "Base model '$ModelBase' missing."; return $false }
    $safeBundle = $ContextBundle.Replace('"""',"'''")
    $modelFilePath = Join-Path $OutputDir "Modelfile.rei-local"
    $modelFile = @"
FROM $ModelBase
PARAMETER temperature 0.2
PARAMETER num_ctx 32768
SYSTEM """
You are the local REI research assistant.
CANONICAL is merged main only. CANDIDATE is PR #28 / rei-v193-reconcile until merged.
Never treat internal CI or synthetic tests as independent external validation.
Preserve failures, UNKNOWN, rollback requirements, lineage dependence, and complexity debt.
The permanent core name is 无相神核.
$safeBundle
"""
"@
    Write-AtomicUtf8 $modelFilePath $modelFile
    & ollama create $ModelName -f $modelFilePath
    if ($LASTEXITCODE -ne 0) { Write-Log "Ollama refresh failed."; return $false }
    return $true
}

function Invoke-ReiSync {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    $headers = @{ 'User-Agent'='REI-Local-Sync'; 'Accept'='application/vnd.github+json' }
    $pr = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/pulls/$PullRequest" -Headers $headers -Method Get
    $baseRef=[string]$pr.base.ref; $headRef=[string]$pr.head.ref; $headSha=[string]$pr.head.sha
    $merged=[bool]$pr.merged; $prState=[string]$pr.state
    if ($PullRequest -eq 28 -and $headRef -ne 'rei-v193-reconcile') { throw "PR #28 head mismatch: $headRef" }

    $canonical=(Invoke-WebRequest -Uri "https://raw.githubusercontent.com/$Repo/$baseRef/CURRENT_REI_CHAT_HANDOFF.md" -Headers $headers -UseBasicParsing).Content
    $candidate=(Invoke-WebRequest -Uri "https://raw.githubusercontent.com/$Repo/$headRef/CURRENT_REI_STRENGTH.md" -Headers $headers -UseBasicParsing).Content
    $stableBundle=@"
# REI LOCAL SYNCHRONIZED CONTEXT
Repository: $Repo
Pull request: #$PullRequest
PR state: $prState
PR merged: $merged
Candidate head: $headSha

## STATUS CONTRACT
CANONICAL comes only from merged GitHub main.
CANDIDATE comes from PR #$PullRequest / $headRef.
CandidatePR != CanonicalMain
GreenCI != IndependentReplication
RealityVeto > REI

## CANONICAL — $baseRef
$canonical

## CANDIDATE — PR #$PullRequest / $headRef / $headSha
$candidate
"@
    $bundlePath=Join-Path $OutputDir 'REI_LOCAL_CONTEXT.md'
    $newHash=Get-Sha256Text $stableBundle
    $hashPath=Join-Path $OutputDir 'context.sha256'
    $oldHash=if(Test-Path $hashPath){(Get-Content $hashPath -Raw).Trim()}else{''}
    if($newHash -eq $oldHash){ Write-Log 'No substantive GitHub context change.'; return }

    $syncedAt=[DateTime]::UtcNow.ToString('o')
    $bundle=$stableBundle.Replace('# REI LOCAL SYNCHRONIZED CONTEXT',"# REI LOCAL SYNCHRONIZED CONTEXT`r`n`r`nSynced at UTC: $syncedAt")
    Write-AtomicUtf8 (Join-Path $OutputDir 'CANONICAL_MAIN.md') $canonical
    Write-AtomicUtf8 (Join-Path $OutputDir ("CANDIDATE_PR{0}.md" -f $PullRequest)) $candidate
    Write-AtomicUtf8 $bundlePath $bundle
    Write-AtomicUtf8 $hashPath $newHash

    if($ContextOnly){$ollamaRefreshed=$false; Write-Log 'Context-only sync complete; vNext model builder owns Ollama refresh.'}
    else{$ollamaRefreshed=Update-OllamaContextModel $bundle $BaseModel $LocalModelName}

    $state=[ordered]@{
      synced_at_utc=$syncedAt; repository=$Repo; pull_request=$PullRequest; pull_request_state=$prState;
      merged=$merged; base_ref=$baseRef; head_ref=$headRef; head_sha=$headSha; context_sha256=$newHash;
      context_only=[bool]$ContextOnly; ollama_base_model=$BaseModel; ollama_model_name=$LocalModelName;
      ollama_refreshed=$ollamaRefreshed; canonical_rule='Only merged base-branch content is canonical.'
    } | ConvertTo-Json -Depth 4
    Write-AtomicUtf8 (Join-Path $OutputDir 'sync_state.json') $state
    Write-Log "REI local context synchronized from PR #$PullRequest at head $headSha."
}

function Install-ReiSyncTask {
    $scriptPath=$PSCommandPath
    if(-not(Test-Path $scriptPath)){throw 'Save this script locally before -Install.'}
    $arguments="-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`" -PullRequest $PullRequest -PollSeconds $PollSeconds -LocalModelName `"$LocalModelName`""
    if($ContextOnly){$arguments+=' -ContextOnly'}
    if(-not[string]::IsNullOrWhiteSpace($BaseModel)){$arguments+=" -BaseModel `"$BaseModel`""}
    $action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arguments
    $trigger=New-ScheduledTaskTrigger -AtLogOn
    $settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero)
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description 'Keeps REI PR #28 reconciled context synchronized.' -Force | Out-Null
    Start-ScheduledTask -TaskName $TaskName
}

function Uninstall-ReiSyncTask {
    $existing=Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if($existing){Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue; Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false}
}

if($Uninstall){Uninstall-ReiSyncTask;exit 0}
if($Install){Install-ReiSyncTask;exit 0}
$createdNew=$false
$mutex=New-Object Threading.Mutex($true,'Local\REI_Local_Context_Sync',[ref]$createdNew)
if(-not$createdNew){Write-Host 'REI Local Sync is already running.';exit 0}
try{do{try{Invoke-ReiSync}catch{Write-Log ('Sync error: '+$_.Exception.Message)};if(-not$Once){Start-Sleep -Seconds $PollSeconds}}while(-not$Once)}
finally{try{$mutex.ReleaseMutex()}catch{};$mutex.Dispose()}
