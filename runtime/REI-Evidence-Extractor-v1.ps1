# 引入基础哈希验证器工具
. .\runtime\REI-Forecast-Validator-v1.ps1

function Get-ReiEvidenceBundleHash {
    param(
        [string]$ContextPath = "C:\REI-Shadow\context\model_vnext_state.json",
        [string]$LedgerStatePath = "C:\REI-Shadow\state\reality-feedback\latest.json"
    )

    $bundleData = ""

    # 1. 抓取模型上下文状态
    if (Test-Path $ContextPath) {
        $bundleData += "[CONTEXT:`n" + (Get-Content -Raw $ContextPath).Trim() + "`n]"
    } else {
        $bundleData += "[CONTEXT: MISSING`n]"
    }

    # 2. 抓取现实反馈层状态
    if (Test-Path $LedgerStatePath) {
        $bundleData += "[LEDGER:`n" + (Get-Content -Raw $LedgerStatePath).Trim() + "`n]"
    } else {
        $bundleData += "[LEDGER: MISSING`n]"
    }
    
    # 计算并返回 SHA256
    $hash = Get-ReiSha256Hex -Text $bundleData
    
    return [ordered]@{
        BundleData = $bundleData
        Hash = $hash
    }
}
