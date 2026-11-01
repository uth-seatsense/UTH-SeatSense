-- SEAT-24: additive migration; also executed on a fresh Compose volume.
-- Reapply this exact file to upgrade an existing database. No data is dropped.
BEGIN;
SELECT pg_advisory_xact_lock(240024);

CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(100) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cv_count_records (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schema_version VARCHAR(10) NOT NULL CHECK (schema_version = '1.0'),
    session_id UUID NOT NULL,
    camera_id VARCHAR(100) NOT NULL CHECK (length(btrim(camera_id)) > 0),
    -- Raw CV room_id is a code, not the numeric rooms.id.
    room_code VARCHAR(100) CHECK (room_code IS NULL OR length(btrim(room_code)) > 0),
    room_id BIGINT REFERENCES rooms(id) ON DELETE RESTRICT,
    source_type VARCHAR(10) NOT NULL CHECK (source_type IN ('video', 'webcam')),
    frame_index BIGINT NOT NULL CHECK (frame_index >= 0),
    timestamp_ms DOUBLE PRECISION NOT NULL
        CHECK (timestamp_ms >= 0 AND timestamp_ms < 'Infinity'::double precision),
    recorded_at TIMESTAMPTZ NOT NULL CHECK (isfinite(recorded_at)),
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    people_count INTEGER NOT NULL CHECK (people_count >= 0),
    tracked_count INTEGER NOT NULL CHECK (tracked_count >= 0 AND tracked_count <= people_count),
    line_enabled BOOLEAN NOT NULL,
    in_count BIGINT CHECK (in_count >= 0),
    out_count BIGINT CHECK (out_count >= 0),
    initial_occupancy BIGINT CHECK (initial_occupancy >= 0),
    estimated_occupancy BIGINT CHECK (estimated_occupancy >= 0),
    occupancy_underflow BOOLEAN NOT NULL,
    CONSTRAINT uq_cv_session_frame UNIQUE (session_id, frame_index),
    CONSTRAINT ck_cv_line_counters CHECK (
        (line_enabled AND in_count IS NOT NULL AND out_count IS NOT NULL)
        OR (NOT line_enabled AND in_count IS NULL AND out_count IS NULL
            AND initial_occupancy IS NULL)
    ),
    CONSTRAINT ck_cv_occupancy_estimate CHECK (
        (initial_occupancy IS NULL AND estimated_occupancy IS NULL AND NOT occupancy_underflow)
        OR (initial_occupancy IS NOT NULL AND estimated_occupancy IS NOT NULL
            AND estimated_occupancy = GREATEST(0::numeric,
                initial_occupancy::numeric + in_count::numeric - out_count::numeric)
            AND occupancy_underflow =
                (initial_occupancy::numeric + in_count::numeric - out_count::numeric < 0))
    )
);

CREATE INDEX IF NOT EXISTS idx_cv_camera_recorded
    ON cv_count_records (camera_id, recorded_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_cv_room_recorded
    ON cv_count_records (room_id, recorded_at DESC, id DESC)
    WHERE room_id IS NOT NULL;

COMMENT ON TABLE cv_count_records IS
    'CV frame aggregates; people_count is visible people, not room occupancy.';
COMMENT ON COLUMN cv_count_records.room_code IS
    'Original optional room_id string from CV schema 1.0; preserved even if unmapped.';
COMMENT ON COLUMN cv_count_records.room_id IS
    'Optional numeric rooms.id resolved by Backend; never cast raw CV room_id.';
COMMENT ON COLUMN cv_count_records.recorded_at IS
    'UTC processing instant supplied by CV, not original camera capture time.';
COMMENT ON COLUMN cv_count_records.timestamp_ms IS
    'Relative video time or monotonic webcam session time; not an absolute timestamp.';

INSERT INTO schema_migrations (version)
VALUES ('002_cv_count_records') ON CONFLICT (version) DO NOTHING;
COMMIT;
