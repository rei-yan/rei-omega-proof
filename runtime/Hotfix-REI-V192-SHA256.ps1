# REI-Ω v1.9.2 Windows PowerShell SHA256 compatibility hotfix
# Replaces .NET 6+ static SHA256.HashData / Convert.ToHexString usage with
# Windows PowerShell 5.1 / .NET Framework compatible SHA256.Create().ComputeHash.

param(
  [switch]$NoStart
)

$ErrorActionPreference = 'Stop'
$CycleScript = 'C:\REI-Shadow\runtime-v191\rei_cycle_v191.ps1'
$TaskName = 'REI Full Pipeline v1.9.1'
$Backup = "$CycleScript.sha256-hotfix-backup"

if (-not (Test-Path $CycleScript)) {
  throw "Cycle script not found: $CycleScript"
}

Copy-Item $CycleScript $Backup -Force
$src = Get-Content $CycleScript -Raw
$old = '$compatHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($compatSeed))).ToLower()'
$new = @'
$sha256 = [System.Security.Cryptography.SHA256]::Create()
try {
  $hashBytes = $sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($compatSeed))
  $compatHash = ([System.BitConverter]::ToString($hashBytes) -replace '-', '').ToLowerInvariant()
}
finally {
  $sha256.Dispose()
}
'@

if ($src.Contains($old)) {
  $src = $src.Replace($old, $new.TrimEnd())
  Set-Content -Encoding UTF8 $CycleScript $src
  Write-Host "Patched SHA256 compatibility in: $CycleScript" -ForegroundColor Green
} elseif ($src -match 'SHA256\]::Create\(') {
  Write-Host 'Compatible SHA256 implementation already present. No patch needed.' -ForegroundColor Yellow
} else {
  throw 'Expected SHA256.HashData expression was not found; refusing an unsafe blind edit.'
}

# Validate that the incompatible APIs are gone.
$verify = Get-Content $CycleScript -Raw
if ($verify -match 'SHA256\]::HashData' -or $verify -match 'Convert\]::ToHexString') {
  throw 'Hotfix validation failed: incompatible SHA256 API still present.'
}
if ($verify -notmatch 'SHA256\]::Create\(' -or $verify -notmatch 'ComputeHash') {
  throw 'Hotfix validation failed: compatible SHA256 implementation missing.'
}

Write-Host "Backup: $Backup" -ForegroundColor Cyan
Write-Host 'SHA256 hotfix validation: PASS' -ForegroundColor Green

if (-not (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue)) {
  throw "Scheduled task missing: $TaskName"
}

if (-not $NoStart) {
  Start-ScheduledTask -TaskName $TaskName
  Write-Host 'Restarted synchronized runtime task for immediate verification.' -ForegroundColor Cyan
}

Write-Host 'Next:' -ForegroundColor Cyan
Write-Host "  Get-ScheduledTaskInfo -TaskName '$TaskName' | Select LastRunTime,LastTaskResult,NextRunTime" -ForegroundColor Cyan
Write-Host '  Get-Content C:\REI-Shadow\runtime-v191\state\last-cycle.json' -ForegroundColor Cyan
