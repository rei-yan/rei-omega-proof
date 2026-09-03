<#
REI-Ω unattended lockstep closed loop vNext for Windows.
Order per cycle:
  context sync -> cloud receipts -> Ollama -> local-model overlay -> Shadow V2.3
  -> vNext observer -> vNext bridge -> GitHub shadow-node
No step may write canonical/main.
#>
[CmdletBinding()]
param(
    [string]$ReiHome = "C:\REI-Shadow",
    [string]$PythonExe = "C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe",
    [string]$ShadowScript = "C:\REI\rei_shadow_closed_loop_v2.py",
    [string]$WheelPullScript = "C:\REI-Shadow\sync_wheel_to_local.py",
    [string]$ObserverScript = "C:\REI-Shadow\vnext_observer.py",
    [string]$BridgeScript = "C:\REI-Shadow\bridge_to_wheel_vnext.py",
    [string]$GitHubPushScript = "C:\REI-Shadow\sync_shadow_to_github.py",
    [string]$ContextSyncScript = "C:\REI-Shadow\REI-LocalSync.ps1",
    [string]$LocalModelScript = "C:\REI-Shadow\REI-LocalModel-VNext.ps1",
    [ValidateRange(300, 86400)][int]$IntervalSeconds = 3600,
    [switch]$Once,
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProtocolVersion = "REI-CLP/3.0-observer"
$TaskName = "REI Unattended Closed Loop"
$LogDir = Join-Path $ReiHome "logs"
$LogPath = Join-Path $LogDir "unattended_loop_vnext.log"
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
    $temporary = Join-Path $directory ([IO.Path]::GetRandomFileName())
    $Value | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Resolve-Python {
    if (Test-Path -LiteralPath $PythonExe) { return $PythonExe }
    foreach ($candidate in @("python.exe", "python", "py.exe", "py")) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    throw "Python not found."
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
        Write-ReiLog "Ollama missing; fail closed."
        return $false
    }
    Start-Process -FilePath $ollama.Source -ArgumentList "serve" -WindowStyle Hidden | Out-Null
    for ($attempt = 0; $attempt -lt 15; $attempt++) {
        Start-Sleep -Seconds 2
        if (Test-OllamaReady) { return $true }
    }
    Write-ReiLog "Ollama did not become ready within 30 seconds."
    return $false
}

function Invoke-NativePowerShellStep {
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
    $previousPreference = $ErrorActionPreference
    try {
        # Windows PowerShell can surface native stderr as NativeCommandError when
        # redirected through a pipeline. Ollama writes harmless progress to stderr,
        # so temporarily keep those records non-terminating and judge the child by
        # its actual exit code instead.
        $ErrorActionPreference = "Continue"
        $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Script @Arguments 2>&1
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    foreach ($line in @($output)) { Write-ReiLog "${Name}: $line" }
    if ($null -eq $code) { $code = 0 }
    Write-ReiLog "$Name exit code: $code"
    return [int]$code
}

function Invoke-PythonStep {
    param([string]$Name, [string]$Script, [string[]]$Arguments = @())
    if (-not (Test-Path -LiteralPath $Script)) {
        Write-ReiLog "$Name missing: $Script"
        return 127
    }
    Write-ReiLog "$Name starting."
    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = & $script:ResolvedPython $Script @Arguments 2>&1
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    foreach ($line in @($output)) { Write-ReiLog "${Name}: $line" }
    if ($null -eq $code) { $code = 0 }
    Write-ReiLog "$Name exit code: $code"
    return [int]$code
}

function Invoke-OneCycle {
    $started = (Get-Date).ToUniversalTime()
    $status = "STARTING"
    $codes = [ordered]@{ context_sync = -1; local_model = -1; wheel_pull = -1; shadow = -1; observer = -1; bridge = -1; github_push = -1 }
    try {
        Write-ReiLog "vNext lockstep cycle starting; protocol=$ProtocolVersion; canonical writes forbidden."

        if (Test-Path -LiteralPath $ContextSyncScript) {
            $codes.context_sync = Invoke-NativePowerShellStep -Name "ContextSync" -Script $ContextSyncScript -Arguments @("-Once")
            if ($codes.context_sync -ne 0) { Write-ReiLog "ContextSync failed; prior atomically stored context may still be used." }
        }
        else {
            Write-ReiLog "ContextSync missing; local-model overlay will fail closed if no prior bundle exists."
            $codes.context_sync = 127
        }

        $codes.wheel_pull = Invoke-PythonStep -Name "WheelPull" -Script $WheelPullScript -Arguments @("--home", $ReiHome)
        if ($codes.wheel_pull -ne 0) { Write-ReiLog "WheelPull failed; continuing only with already-local valid receipts." }

        if (-not (Ensure-Ollama)) { $status = "FAILED_CLOSED_OLLAMA"; return }

        $codes.local_model = Invoke-NativePowerShellStep -Name "LocalModel" -Script $LocalModelScript -Arguments @("-ContextDir", (Join-Path $ReiHome "context"))
        if ($codes.local_model -ne 0) { $status = "FAILED_CLOSED_LOCAL_MODEL"; return }

        $env:REI_MODEL = "rei-local-node-vnext"
        $env:REI_VALIDATOR_MODEL = "rei-local-node-vnext"
        $env:REI_CLOSED_LOOP_PROTOCOL = $ProtocolVersion
        $env:REI_OBSERVER_MODE = "true"

        $codes.shadow = Invoke-PythonStep -Name "Shadow" -Script $ShadowScript -Arguments @("--once", "--home", $ReiHome)
        if ($codes.shadow -ne 0) { $status = "FAILED_CLOSED_SHADOW"; return }

        $codes.observer = Invoke-PythonStep -Name "VNextObserver" -Script $ObserverScript -Arguments @("--home", $ReiHome)
        if ($codes.observer -ne 0) { $status = "FAILED_CLOSED_OBSERVER"; return }

        $codes.bridge = Invoke-PythonStep -Name "VNextBridge" -Script $BridgeScript -Arguments @("--home", $ReiHome)
        if ($codes.bridge -ne 0) { $status = "FAILED_CLOSED_BRIDGE"; return }

        $codes.github_push = Invoke-PythonStep -Name "GitHubPush" -Script $GitHubPushScript -Arguments @("--home", $ReiHome, "--repo", (Join-Path $ReiHome "repo"))
        if ($codes.github_push -ne 0) { $status = "RETRYABLE_GITHUB_PUSH"; return }

        $status = "SUCCESS"
    }
    catch {
        $status = "FAILED_CLOSED_UNHANDLED"
        Write-ReiLog "Cycle error: $($_.Exception.GetType().Name): $($_.Exception.Message)"
    }
    finally {
        $finished = (Get-Date).ToUniversalTime()
        Write-AtomicJson -Path $HeartbeatPath -Value ([ordered]@{
            schema_version = 2
            protocol_version = $ProtocolVersion
            observer_mode = $true
            local_model = "rei-local-node-vnext"
            core_name = "无相神核"
            started_at_utc = $started.ToString("o")
            finished_at_utc = $finished.ToString("o")
            next_due_at_utc = $finished.AddSeconds($IntervalSeconds).ToString("o")
            status = $status
            step_exit_codes = $codes
            canonical_mainline_touched = $false
            canonical_write_permission = $false
        })
        Write-ReiLog "Cycle finished: $status; observer_mode=TRUE; canonical mainline touched: FALSE"
    }
}

function Install-ReiTask {
    if (-not (Test-Path -LiteralPath $PSCommandPath)) { throw "Save this script before -Install." }
    [void](Resolve-Python)
    foreach ($required in @($ShadowScript, $WheelPullScript, $ObserverScript, $BridgeScript, $GitHubPushScript, $LocalModelScript)) {
        if (-not (Test-Path -LiteralPath $required)) { throw "Required file missing: $required" }
    }

    $arguments = @(
        "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass",
        "-File", ('"' + $PSCommandPath + '"'),
        "-ReiHome", ('"' + $ReiHome + '"'),
        "-PythonExe", ('"' + (Resolve-Python) + '"'),
        "-IntervalSeconds", $IntervalSeconds
    ) -join " "

    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) { Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue }

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

    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
        -Description "REI lockstep vNext observer closed loop; never writes canonical/main." `
        -RunLevel Highest -Force | Out-Null
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Installed and started: $TaskName"
    Write-Host "Protocol: $ProtocolVersion"
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
