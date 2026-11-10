-- SEAT-37: Update rooms table to match SRS 6.1 specification
-- Adds room_type, location, and status fields
BEGIN;

-- Add new columns if they don't exist
ALTER TABLE rooms
    ADD COLUMN IF NOT EXISTS room_type VARCHAR(50);

ALTER TABLE rooms
    ADD COLUMN IF NOT EXISTS location VARCHAR(255);

ALTER TABLE rooms
    ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';

-- Update existing rooms with default values
UPDATE rooms
SET room_type = 'reading_room'
WHERE room_type IS NULL;

UPDATE rooms
SET status = 'active'
WHERE status IS NULL;

-- Make room_type NOT NULL after populating
ALTER TABLE rooms
    ALTER COLUMN room_type SET NOT NULL;

ALTER TABLE rooms
    ALTER COLUMN status SET NOT NULL;

-- Add check constraints
ALTER TABLE rooms
    DROP CONSTRAINT IF EXISTS ck_rooms_capacity;

ALTER TABLE rooms
    ADD CONSTRAINT ck_rooms_capacity
    CHECK (capacity > 0);

ALTER TABLE rooms
    DROP CONSTRAINT IF EXISTS ck_rooms_status;

ALTER TABLE rooms
    ADD CONSTRAINT ck_rooms_status
    CHECK (status IN ('active', 'maintenance', 'closed'));

ALTER TABLE rooms
    DROP CONSTRAINT IF EXISTS ck_rooms_type;

ALTER TABLE rooms
    ADD CONSTRAINT ck_rooms_type
    CHECK (room_type IN ('reading_room', 'group_study_room'));

COMMENT ON COLUMN rooms.room_type IS 'Type of room: reading_room for general study, group_study_room for collaborative work.';
COMMENT ON COLUMN rooms.location IS 'Physical location description (e.g., "Tầng 1, Khu A").';
COMMENT ON COLUMN rooms.status IS 'Operational status: active (available), maintenance (temporarily closed), closed (permanently unavailable).';

COMMIT;
