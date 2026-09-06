<#
REI-Ω canonical mainline observation v1.

Purpose:
- snapshot origin/main from the local repository;
- compare two observed SHAs around a mutating runtime action;
- fail closed if canonical main changes during that action.

This script does not claim which actor authored a changed commit. It only proves
whether the observed main ref remained unchanged across the guarded interval.
#>
[CmdletBinding()]
param(
  [ValidateSet('Snapshot','Compare')][string]$Mode = 'Snapshot',
  [string]$Repo = 'C:\REI-Shadow\repo',
  [string]$BeforeSha = '',
  [string]$AfterSha = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-GitExe {
  $cmd = Get-Command git.exe -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $cmd = Get-Command git -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  foreach ($p in @('C:\Program Files\Git\cmd\git.exe','C:\Program Files\Git\bin\git.exe','C:\Program Files (x86)\Git\cmd\git.exe')) {
    if (Test-Path -LiteralPath $p) { return $p }
  }
  throw 'git executable not found'
}

function Assert-Sha([string]$Value,[string]$Name) {
  if ($Value -notmatch '^[0-9a-fA-F]{40}$') { throw "$Name is not a 40-character git SHA" }
}

if ($Mode -eq 'Compare') {
  Assert-Sha $BeforeSha 'BeforeSha'
  Assert-Sha $AfterSha 'AfterSha'
  if ($BeforeSha.ToLowerInvariant() -ne $AfterSha.ToLowerInvariant()) {
    Write-Error "CANONICAL_MAINLINE_TOUCHED_BY_RUNTIME before=$BeforeSha after=$AfterSha"
    exit 2
  }
  Write-Host "CANONICAL_MAINLINE_UNTOUCHED_BY_RUNTIME sha=$BeforeSha"
  exit 0
}

if (-not (Test-Path -LiteralPath $Repo -PathType Container)) { throw "Repo missing: $Repo" }
$git = Resolve-GitExe
& $git -C $Repo fetch origin main --quiet
if ($LASTEXITCODE -ne 0) { throw 'git fetch origin main failed' }
$sha = (& $git -C $Repo rev-parse origin/main).Trim()
if ($LASTEXITCODE -ne 0) { throw 'cannot resolve origin/main' }
Assert-Sha $sha 'origin/main'
Write-Output $sha
