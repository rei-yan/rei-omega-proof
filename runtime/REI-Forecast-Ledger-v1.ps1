# 引入基础验证器引擎
. .\runtime\REI-Forecast-Validator-v1.ps1

function Write-ReiForecastLedger {
    param(
        [System.Collections.IDictionary]$Forecast,
        [string]$DbPath = "C:\REI-Shadow\state\forecast_ledger.db"
    )

    # 1. 执行严格规范化与哈希绑定
    $canonicalJson = ConvertTo-ReiForecastCanonicalJson -Payload $Forecast
    $canonicalHash = Get-ReiSha256Hex -Text $canonicalJson

    # 2. 格式化数据以防 SQL 语法错误
    $q = $Forecast.question.Replace("'", "''")
    $prob = [double]$Forecast.probability
    $abstainInt = if ($Forecast.abstain) { 1 } else { 0 }
    
    $createdUtc = ConvertTo-ReiUtcCanonical $Forecast.created_at_utc
    $cutoffUtc = ConvertTo-ReiUtcCanonical $Forecast.cutoff_at_utc
    $resolveUtc = ConvertTo-ReiUtcCanonical $Forecast.resolve_at_utc

    # 3. 构造安全的 INSERT 语句
    $sql = @"
INSERT INTO forecast_ledger (
    forecast_id, schema_version, created_at_utc, cutoff_at_utc, resolve_at_utc,
    question, target_type, probability, abstain, evidence_bundle_hash,
    model_id, status, canonical_hash
) VALUES (
    '$($Forecast.forecast_id)', $($Forecast.schema_version), '$createdUtc', '$cutoffUtc', '$resolveUtc',
    '$q', '$($Forecast.target_type)', $prob, $abstainInt, '$($Forecast.evidence_bundle_hash)',
    '$($Forecast.model_id)', '$($Forecast.status)', '$canonicalHash'
);
"@

    Write-Host "【成功】预测记录已通过规范化校验！" -ForegroundColor Green
    Write-Host "Canonical JSON: $canonicalJson" -ForegroundColor DarkGray
    Write-Host "Canonical Hash: $canonicalHash" -ForegroundColor Cyan
    
    return $sql
}
