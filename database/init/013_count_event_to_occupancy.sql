BEGIN;

ALTER TABLE occupancy_records
    ADD COLUMN IF NOT EXISTS observation_id UUID;

UPDATE occupancy_records
SET observation_id = md5('legacy-occupancy-' || id::text)::uuid
WHERE observation_id IS NULL;

ALTER TABLE occupancy_records
    ALTER COLUMN observation_id SET NOT NULL;

ALTER TABLE occupancy_records
    ADD COLUMN IF NOT EXISTS over_capacity BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE occupancy_records
    ADD COLUMN IF NOT EXISTS occupancy_level VARCHAR(10);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'uq_occupancy_records_observation_id'
    ) THEN
        ALTER TABLE occupancy_records
            ADD CONSTRAINT uq_occupancy_records_observation_id
            UNIQUE (observation_id);
    END IF;
END $$;

COMMIT;
