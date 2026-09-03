<#
REI-Ω / 无相神核 unattended bidirectional Shadow loop for Windows.

Order per cycle:
  cloud wheel receipts -> local Shadow V2.3 -> safe bridge -> GitHub shadow-node

The task never writes canonical/main and restarts after sign-in following reboot.
#>

[CmdletBinding()]
param(
    [string]$ReiHome = "C:\REI-Shadow",
    [string]$PythonExe = "C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe",
    [string]$ShadowScript = "C:\REI\rei_shadow_closed_loop_v2.py",
    [string]$WheelPullScript = "C:\REI-Shadow\sync_wheel_to_local.py",
    [string]$BridgeScript = "C:\REI-Shadow\bridge_to_wheel.py",
    [string]$GitHubPushScript = "C:\REI-Shadow\sync_shadow_to_github.py",
    [string]$ContextSyncScript = "C:\REI-Shadow\REI-LocalSync.ps1",
    [ValidateRange(300, 86400)]
    [int]$IntervalSeconds = 3600,
    [switch]$Once,
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$TaskName = "REI Unattended Closed Loop"
$LogDir = Join-Path $ReiHome "logs"
$LogPath = Join-Path $LogDir "unattended_loop.log"
$HeartbeatPath = Join-Path $ReiHome "state\unattended_heartbeat.json"

function Write-ReiLog {
    param([string]$Message)
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    if ((Test-Path -LiteralPath $LogPath) -and (Get-Item -LiteralPath $LogPath).Length -gt 10MB) {
        Move-Item -LiteralPath $LogPath -Destination ($LogPath + ".1") -Force
    }
    $line = "[$((Get-Date).ToUniversalTime().ToString('o'))] $Message"
    Write-Host $line
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

function Write-AtomicJson {
    param([string]$Path, [System.Collections.IDictionary]$Value)
    $directory = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    $temporary = Join-Path $directory ([System.IO.Path]::GetRandomFileName())
    $Value | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Resolve-Python {
    if (Test-Path -LiteralPath $PythonExe) { return $PythonExe }
    foreach ($candidate in @("python.exe", "python", "py.exe", "py")) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    throw "Python not found. Install Python or pass -PythonExe with the full path."
}

function Test-OllamaReady {
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5 | Out-Null
        return $true
    }
    catch { return $false }
}

function Ensure-Ollama {
    if (Test-OllamaReady) { return $true }
    $ollama = Get-Command "ollama" -ErrorAction SilentlyContinue
    if (-not $ollama) {
        Write-ReiLog "Ollama not found in PATH; this cycle will fail closed."
        return $false
    }
    Write-ReiLog "Ollama API is offline; starting ollama serve."
    Start-Process -FilePath $ollama.Source -ArgumentList "serve" -WindowStyle Hidden | Out-Null
    for ($attempt = 0; $attempt -lt 15; $attempt++) {
        Start-Sleep -Seconds 2
        if (Test-OllamaReady) { return $true }
    }
    Write-ReiLog "Ollama did not become ready within 30 seconds."
    return $false
}

function Invoke-PythonStep {
    param(
        [string]$Name,
        [string]$Script,
        [string[]]$Arguments = @()
    )
    if (-not (Test-Path -LiteralPath $Script)) {
        Write-ReiLog "$Name missing: $Script"
        return 127
    }
    Write-ReiLog "$Name starting."
    & $script:ResolvedPython $Script @Arguments 2>&1 | ForEach-Object { Write-ReiLog "${Name}: $_" }
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = 0 }
    Write-ReiLog "$Name exit code: $code"
    return [int]$code
}

function Invoke-OneCycle {
    $started = (Get-Date).ToUniversalTime()
    $status = "STARTING"
    $shadowCode = -1
    $bridgeCode = -1
    $pushCode = -1
    try {
        Write-ReiLog "REI unattended cycle starting; canonical writes remain forbidden."

        if (Test-Path -LiteralPath $ContextSyncScript) {
            try {
                & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ContextSyncScript -Once 2>&1 |
                    ForEach-Object { Write-ReiLog "ContextSync: $_" }
            }
            catch { Write-ReiLog "ContextSync retryable error: $($_.Exception.Message)" }
        }

        [void](Invoke-PythonStep -Name "WheelPull" -Script $WheelPullScript -Arguments @("--home", $ReiHome))

        if (-not (Ensure-Ollama)) {
            $status = "FAILED_CLOSED_OLLAMA"
            return
        }

        $shadowCode = Invoke-PythonStep -Name "Shadow" -Script $ShadowScript -Arguments @("--once", "--home", $ReiHome)
        if ($shadowCode -ne 0) {
            $status = "FAILED_CLOSED_SHADOW"
            return
        }

        $bridgeCode = Invoke-PythonStep -Name "Bridge" -Script $BridgeScript -Arguments @("--home", $ReiHome)
        if ($bridgeCode -ne 0) {
            $status = "FAILED_CLOSED_BRIDGE"
            return
        }

        $pushCode = Invoke-PythonStep -Name "GitHubPush" -Script $GitHubPushScript
        if ($pushCode -ne 0) {
            $status = "RETRYABLE_GITHUB_PUSH"
            return
        }

        $status = "SUCCESS"
    }
    catch {
        $status = "FAILED_CLOSED_UNHANDLED"
        Write-ReiLog "Cycle error: $($_.Exception.GetType().Name): $($_.Exception.Message)"
    }
    finally {
        $finished = (Get-Date).ToUniversalTime()
        Write-AtomicJson -Path $HeartbeatPath -Value ([ordered]@{
            schema_version = 1
            core_name = "无相神核"
            started_at_utc = $started.ToString("o")
            finished_at_utc = $finished.ToString("o")
            next_due_at_utc = $finished.AddSeconds($IntervalSeconds).ToString("o")
            status = $status
            shadow_exit_code = $shadowCode
            bridge_exit_code = $bridgeCode
            github_push_exit_code = $pushCode
            canonical_mainline_touched = $false
        })
        Write-ReiLog "Cycle finished: $status; canonical mainline touched: FALSE"
    }
}

function Install-ReiTask {
    if (-not (Test-Path -LiteralPath $PSCommandPath)) { throw "Save this script before -Install." }
    [void](Resolve-Python)
    foreach ($required in @($ShadowScript, $WheelPullScript, $BridgeScript, $GitHubPushScript)) {
        if (-not (Test-Path -LiteralPath $required)) { throw "Required file missing: $required" }
    }

    $arguments = @(
        "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass",
        "-File", ('"' + $PSCommandPath + '"'),
        "-ReiHome", ('"' + $ReiHome + '"'),
        "-PythonExe", ('"' + (Resolve-Python) + '"'),
        "-ShadowScript", ('"' + $ShadowScript + '"'),
        "-WheelPullScript", ('"' + $WheelPullScript + '"'),
        "-BridgeScript", ('"' + $BridgeScript + '"'),
        "-GitHubPushScript", ('"' + $GitHubPushScript + '"'),
        "-ContextSyncScript", ('"' + $ContextSyncScript + '"'),
        "-IntervalSeconds", $IntervalSeconds
    ) -join " "

    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arguments
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $settings = New-ScheduledTaskSettingsSet `
        -StartWhenAvailable `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit ([TimeSpan]::Zero) `
        -RestartCount 999 `
        -RestartInterval (New-TimeSpan -Minutes 1) `
        -MultipleInstances IgnoreNew

    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
        -Settings $settings -Description "REI Shadow bidirectional unattended loop; never writes canonical/main." `
        -RunLevel Highest -Force | Out-Null
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Installed and started: $TaskName"
}

function Uninstall-ReiTask {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $task) { Write-Host "Task not found: $TaskName"; return }
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed scheduled task: $TaskName"
}

function Show-ReiStatus {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        $info = Get-ScheduledTaskInfo -TaskName $TaskName
        Write-Host "Task: $($task.State); Last result: $($info.LastTaskResult); Last run: $($info.LastRunTime)"
    }
    else { Write-Host "Task: NOT_INSTALLED" }
    if (Test-Path -LiteralPath $HeartbeatPath) { Get-Content -LiteralPath $HeartbeatPath -Raw }
    else { Write-Host "Heartbeat: NOT_FOUND" }
}

if ($Install) { Install-ReiTask; exit 0 }
if ($Uninstall) { Uninstall-ReiTask; exit 0 }
if ($Status) { Show-ReiStatus; exit 0 }

$script:ResolvedPython = Resolve-Python
$createdNew = $false
$mutex = New-Object System.Threading.Mutex($true, "Local\REI_Unattended_Closed_Loop", [ref]$createdNew)
if (-not $createdNew) { Write-Host "REI unattended loop is already running."; exit 0 }

try {
    do {
        $cycleStart = Get-Date
        Invoke-OneCycle
        if ($Once) { break }
        $elapsed = [int]((Get-Date) - $cycleStart).TotalSeconds
        $wait = [Math]::Max(60, $IntervalSeconds - $elapsed)
        Write-ReiLog "Next cycle in $wait seconds."
        Start-Sleep -Seconds $wait
    } while ($true)
}
finally {
    try { $mutex.ReleaseMutex() } catch { }
    $mutex.Dispose()
}
