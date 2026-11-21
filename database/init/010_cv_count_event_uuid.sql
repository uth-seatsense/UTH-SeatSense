-- SEAT-53: upgrade the SEAT-37 integer event key to the CV-provided UUID contract.
BEGIN;
SELECT pg_advisory_xact_lock(240053);

CREATE TABLE IF NOT EXISTS count_events (
    event_id UUID PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
    session_id UUID NOT NULL,
    device_id VARCHAR(100) NOT NULL,
    device_status VARCHAR(20) NOT NULL DEFAULT 'online',
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('in', 'out')),
    event_time TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source VARCHAR(20) NOT NULL DEFAULT 'cv',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE count_events ADD COLUMN IF NOT EXISTS session_id UUID;
ALTER TABLE count_events ADD COLUMN IF NOT EXISTS device_id VARCHAR(100);
ALTER TABLE count_events ADD COLUMN IF NOT EXISTS device_status VARCHAR(20) NOT NULL DEFAULT 'online';

DO $$
DECLARE
    event_id_type TEXT;
BEGIN
    SELECT data_type
    INTO event_id_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'count_events'
      AND column_name = 'event_id';

    IF event_id_type IN ('integer', 'bigint', 'smallint') THEN
        UPDATE count_events
        SET session_id = md5('legacy-session-' || event_id::text)::uuid
        WHERE session_id IS NULL;
        ALTER TABLE count_events ALTER COLUMN session_id SET NOT NULL;
        UPDATE count_events SET device_id = 'legacy-device' WHERE device_id IS NULL;
        ALTER TABLE count_events ALTER COLUMN device_id SET NOT NULL;
        ALTER TABLE count_events DROP CONSTRAINT IF EXISTS count_events_pkey;
        ALTER TABLE count_events ALTER COLUMN event_id DROP IDENTITY IF EXISTS;
        ALTER TABLE count_events
            ALTER COLUMN event_id TYPE UUID
            USING md5('legacy-event-' || event_id::text)::uuid;
        ALTER TABLE count_events
            ADD CONSTRAINT count_events_pkey PRIMARY KEY (event_id);
    ELSE
        ALTER TABLE count_events ALTER COLUMN session_id SET NOT NULL;
        ALTER TABLE count_events ALTER COLUMN device_id SET NOT NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_count_events_room
    ON count_events(room_id, event_time DESC);
CREATE INDEX IF NOT EXISTS idx_count_events_received
    ON count_events(received_at DESC);

COMMENT ON TABLE count_events IS
    'Discrete entrance/exit events. Distinct from cv_count_records.';
COMMENT ON COLUMN count_events.event_id IS
    'UUID idempotency key supplied by CV (SEAT-53).';

INSERT INTO schema_migrations (version)
VALUES ('010_cv_count_event_uuid')
ON CONFLICT (version) DO NOTHING;

COMMIT;
