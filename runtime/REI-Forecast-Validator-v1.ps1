function ConvertTo-ReiUtcCanonical {
    param([string]$Value)
    if ($Value -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?(?:Z|[+-]\d{2}:\d{2})$') {
        throw "FORECAST_TIME_FORMAT_INVALID: timestamp must include timezone and at most 7 fractional-second digits"
    }
    $dt = [DateTimeOffset]::Parse($Value, [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind)
    return $dt.ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss.fffffff'Z'", [System.Globalization.CultureInfo]::InvariantCulture)
}

function ConvertTo-ReiForecastCanonicalJson {
    param([System.Collections.IDictionary]$Payload)
    $requiredFields = @("forecast_id","schema_version","created_at_utc","cutoff_at_utc","resolve_at_utc","question","target_type","probability","abstain","evidence_bundle_hash","model_id")
    
    foreach ($field in $requiredFields) {
        if (-not $Payload.Contains($field)) { throw "FORECAST_REQUIRED_FIELD_MISSING: $field" }
    }

    $probability = $Payload["probability"]
    if ($null -eq $probability) { throw "FORECAST_PROBABILITY_TYPE_INVALID: probability must be a numeric scalar" }

    $allowedProbabilityTypes = @([System.TypeCode]::Byte, [System.TypeCode]::SByte, [System.TypeCode]::Int16, [System.TypeCode]::UInt16, [System.TypeCode]::Int32, [System.TypeCode]::UInt32, [System.TypeCode]::Int64, [System.TypeCode]::UInt64, [System.TypeCode]::Single, [System.TypeCode]::Double, [System.TypeCode]::Decimal)
    if ($allowedProbabilityTypes -notcontains [System.Type]::GetTypeCode($probability.GetType())) {
        throw "FORECAST_PROBABILITY_TYPE_INVALID: probability must be numeric, not $($probability.GetType().Name)"
    }

    $probAsDouble = [double]$probability
    if ([double]::IsNaN($probAsDouble) -or [double]::IsInfinity($probAsDouble)) { throw "FORECAST_PROBABILITY_NON_FINITE: probability must be finite" }
    if ($probability -lt 0.0 -or $probability -gt 1.0) { throw "FORECAST_PROBABILITY_OUT_OF_RANGE: probability must be between 0.0 and 1.0" }

    $canonical = [ordered]@{
        forecast_id          = $Payload["forecast_id"]
        schema_version       = $Payload["schema_version"]
        created_at_utc       = ConvertTo-ReiUtcCanonical $Payload["created_at_utc"]
        cutoff_at_utc        = ConvertTo-ReiUtcCanonical $Payload["cutoff_at_utc"]
        resolve_at_utc       = ConvertTo-ReiUtcCanonical $Payload["resolve_at_utc"]
        question             = $Payload["question"]
        target_type          = $Payload["target_type"]
        probability          = $Payload["probability"]
        abstain              = $Payload["abstain"]
        evidence_bundle_hash = $Payload["evidence_bundle_hash"]
        model_id             = $Payload["model_id"]
    }
    return ($canonical | ConvertTo-Json -Compress)
}

function Get-ReiSha256Hex {
    param([string]$Text)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return (($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString("x2") }) -join "") }
    finally { $sha.Dispose() }
}

function Assert-ReiForecastImmutability {
    param(
        [System.Collections.IDictionary]$PreviousState,
        [System.Collections.IDictionary]$NewState,
        [string]$ContractPath = ".\runtime\forecast-contract-v1.json"
    )
    $contract = Get-Content -Raw $ContractPath | ConvertFrom-Json
    
    if ($PreviousState["status"] -eq "COMMITTED") {
        foreach ($field in $contract.immutable_after_commit) {
            # 将值转换为字符串比对，规避类型差异带来的误判
            if ([string]$PreviousState[$field] -ne [string]$NewState[$field]) {
                throw "IMMUTABILITY_VIOLATION: Committed forecast field '$field' cannot be modified."
            }
        }
    }
    return $true
}
