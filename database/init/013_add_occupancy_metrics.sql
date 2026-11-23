-- SEAT-56: Add occupancy metrics fields (over_capacity, occupancy_level)
-- These fields support the occupancy calculation logic from SEAT-54
BEGIN;
SELECT pg_advisory_xact_lock(240058);

-- Add over_capacity column (boolean, default false)
ALTER TABLE occupancy_records
    ADD COLUMN IF NOT EXISTS over_capacity BOOLEAN DEFAULT FALSE NOT NULL;

-- Add occupancy_level column (vang/vua/dong from SEAT-54)
-- Will be mapped to low/medium/high in API responses
ALTER TABLE occupancy_records
    ADD COLUMN IF NOT EXISTS occupancy_level VARCHAR(10);

-- Add check constraint for occupancy_level
ALTER TABLE occupancy_records
    DROP CONSTRAINT IF EXISTS ck_occupancy_level;

ALTER TABLE occupancy_records
    ADD CONSTRAINT ck_occupancy_level
    CHECK (occupancy_level IS NULL OR occupancy_level IN ('vang', 'vua', 'dong'));

-- Add comments
COMMENT ON COLUMN occupancy_records.over_capacity IS 'True if current_count exceeds room capacity.';
COMMENT ON COLUMN occupancy_records.occupancy_level IS 'Density level: vang (low ≤30%), vua (medium 30-70%), dong (high >70%). Mapped to low/medium/high in API.';

INSERT INTO schema_migrations (version)
VALUES ('013_add_occupancy_metrics')
ON CONFLICT (version) DO NOTHING;

COMMIT;
