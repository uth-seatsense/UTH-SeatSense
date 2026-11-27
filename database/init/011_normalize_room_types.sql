-- Align legacy room types with the Sprint 4 room contract.
BEGIN;
SELECT pg_advisory_xact_lock(240058);

ALTER TABLE rooms
    DROP CONSTRAINT IF EXISTS ck_rooms_type;

UPDATE rooms
SET room_type = CASE room_type
    WHEN 'reading_room' THEN 'free_area'
    WHEN 'group_study_room' THEN 'topic_room'
    ELSE room_type
END
WHERE room_type IN ('reading_room', 'group_study_room');

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM rooms
        WHERE room_type IS NULL OR room_type NOT IN ('free_area', 'topic_room')
    ) THEN
        RAISE EXCEPTION
            'Migration stopped: rooms contain unsupported room_type values; review them before migrating.';
    END IF;
END $$;

ALTER TABLE rooms
    ALTER COLUMN room_type SET DEFAULT 'free_area';

ALTER TABLE rooms
    ADD CONSTRAINT ck_rooms_type
    CHECK (room_type IN ('free_area', 'topic_room'));

CREATE INDEX IF NOT EXISTS idx_occupancy_room_recorded
    ON occupancy_records (room_id, recorded_at DESC);

INSERT INTO schema_migrations (version)
VALUES ('011_normalize_room_types')
ON CONFLICT (version) DO NOTHING;

COMMIT;
