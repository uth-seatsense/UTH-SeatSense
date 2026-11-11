-- SEAT-37: Update occupancy_records to match SRS 6.1 specification
-- Adds available_seats and device_status fields
BEGIN;

-- Add new columns to match SRS 6.1 OccupancyRecord spec
ALTER TABLE occupancy_records
    ADD COLUMN IF NOT EXISTS available_seats INTEGER;

ALTER TABLE occupancy_records
    ADD COLUMN IF NOT EXISTS device_status VARCHAR(20);

-- Rename occupied_count to current_count for consistency with SRS
ALTER TABLE occupancy_records
    RENAME COLUMN occupied_count TO current_count;

-- Add check constraints
ALTER TABLE occupancy_records
    DROP CONSTRAINT IF EXISTS ck_occupancy_current_count;

ALTER TABLE occupancy_records
    ADD CONSTRAINT ck_occupancy_current_count
    CHECK (current_count >= 0);

ALTER TABLE occupancy_records
    DROP CONSTRAINT IF EXISTS ck_occupancy_available_seats;

ALTER TABLE occupancy_records
    ADD CONSTRAINT ck_occupancy_available_seats
    CHECK (available_seats IS NULL OR available_seats >= 0);

ALTER TABLE occupancy_records
    DROP CONSTRAINT IF EXISTS ck_occupancy_device_status;

ALTER TABLE occupancy_records
    ADD CONSTRAINT ck_occupancy_device_status
    CHECK (device_status IS NULL OR device_status IN ('online', 'offline', 'error'));

-- Rename observed_at to recorded_at for consistency
ALTER TABLE occupancy_records
    RENAME COLUMN observed_at TO recorded_at;

-- Update index name to match new column name
DROP INDEX IF EXISTS idx_occupancy_room_observed;
CREATE INDEX IF NOT EXISTS idx_occupancy_room_recorded
    ON occupancy_records(room_id, recorded_at DESC);

COMMENT ON COLUMN occupancy_records.current_count IS 'Number of people currently in the room.';
COMMENT ON COLUMN occupancy_records.available_seats IS 'Number of available seats. NULL if not calculated.';
COMMENT ON COLUMN occupancy_records.device_status IS 'Status of the counting device: online, offline, or error.';
COMMENT ON COLUMN occupancy_records.recorded_at IS 'Timestamp when the occupancy was recorded.';

COMMIT;
