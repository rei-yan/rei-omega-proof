# REI Forecast Pipeline Integration Test (Full Chain)
$ErrorActionPreference = "Stop"

Write-Host "[1/5] 引入验证、账本与证据提取引擎..." -ForegroundColor Cyan
. .\runtime\REI-Forecast-Validator-v1.ps1
. .\runtime\REI-Forecast-Ledger-v1.ps1
. .\runtime\REI-Evidence-Extractor-v1.ps1

Write-Host "[2/5] 提取真实证据束 (Evidence Bundle)..." -ForegroundColor Cyan
$evidence = Get-ReiEvidenceBundleHash
Write-Host "-> 当前现实锚点: $($evidence.Hash)" -ForegroundColor DarkGray

# 使用动态时间戳后缀，确保重复运行不会发生主键冲突
$runId = Get-Date -Format "yyyyMMddHHmmssfff"
$testForecastId = "FC-AUTO-TEST-$runId"

Write-Host "[3/5] 测试 DRAFT 状态预测的规范化与 SQL 生成 (ID: $testForecastId)..." -ForegroundColor Cyan
$testForecast = [ordered]@{
    forecast_id          = $testForecastId
    schema_version       = 1
    created_at_utc       = "2026-09-15T20:00:00Z"
    cutoff_at_utc        = "2026-09-15T23:59:59Z"
    resolve_at_utc       = "2026-09-16T12:00:00Z"
    question             = "Automated pipeline sanity check active?"
    target_type          = "binary"
    probability          = 0.50
    abstain              = $false
    evidence_bundle_hash = $evidence.Hash  # <--- 动态注入刚才提取的真实哈希！
    model_id             = "rei-local-node-vnext"
    status               = "DRAFT"
}

$sqlOutput = Write-ReiForecastLedger -Forecast $testForecast
if ([string]::IsNullOrWhiteSpace($sqlOutput)) { throw "PIPELINE_ERROR: Failed to generate SQL." }

Write-Host "[4/5] 测试 SQLite 数据库落盘..." -ForegroundColor Cyan
$DbPath = "C:\REI-Shadow\state\forecast_ledger.db"
Get-Content -Raw .\runtime\forecast-ledger-schema-v1.sql | .\runtime\sqlite3.exe $DbPath
$sqlOutput | .\runtime\sqlite3.exe $DbPath

Write-Host "[5/5] 测试 COMMITTED 状态的不可变性拦截..." -ForegroundColor Cyan
$committedState = [ordered]@{}
foreach ($key in $testForecast.Keys) { $committedState[$key] = $testForecast[$key] }
$committedState["status"] = "COMMITTED"

$tamperedState = [ordered]@{}
foreach ($key in $committedState.Keys) { $tamperedState[$key] = $committedState[$key] }
$tamperedState["probability"] = 0.99

try {
    Assert-ReiForecastImmutability -PreviousState $committedState -NewState $tamperedState
    throw "PIPELINE_ERROR: Immutability check failed to catch tampering."
} catch {
    if ($_.Exception.Message -match "IMMUTABILITY_VIOLATION") {
        Write-Host "【流水线通过】全链路测试（含物理证据绑定）执行完毕！契约防御有效！" -ForegroundColor Green
    } else {
        throw $_
    }
}
