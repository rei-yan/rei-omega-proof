-- REI Forecast Ledger Schema v1
-- Immutable after COMMITTED. Target type constraints enforced.

CREATE TABLE IF NOT EXISTS forecast_ledger (
    forecast_id TEXT PRIMARY KEY,
    schema_version INTEGER NOT NULL,
    created_at_utc TEXT NOT NULL,
    cutoff_at_utc TEXT NOT NULL,
    resolve_at_utc TEXT NOT NULL,
    question TEXT NOT NULL,
    target_type TEXT NOT NULL,
    probability REAL,
    abstain INTEGER NOT NULL,
    evidence_bundle_hash TEXT,
    model_id TEXT NOT NULL,
    status TEXT NOT NULL,
    canonical_hash TEXT NOT NULL UNIQUE,
    
    -- Contract Level Constraints
    CHECK (status IN ('DRAFT', 'COMMITTED')),
    CHECK (probability >= 0.0 AND probability <= 1.0),
    CHECK (abstain IN (0, 1))
);

-- Index for temporal queries (Continuous Reality Loop Guard checks)
CREATE INDEX IF NOT EXISTS idx_forecast_cutoff ON forecast_ledger(cutoff_at_utc);
CREATE INDEX IF NOT EXISTS idx_forecast_status ON forecast_ledger(status);
