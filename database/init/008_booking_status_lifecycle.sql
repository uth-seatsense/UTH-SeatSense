-- SEAT-Booking: align persisted booking states with the canonical lifecycle.
-- Safe to reapply on existing databases; preserves booking/check-in rows.
BEGIN;
SELECT pg_advisory_xact_lock(240037);
CREATE EXTENSION IF NOT EXISTS btree_gist;

DO $$
BEGIN
    IF to_regclass('bookings') IS NULL THEN
        RAISE EXCEPTION 'bookings table is missing; apply 006_create_booking_system.sql first';
    END IF;
    IF to_regclass('check_ins') IS NULL THEN
        RAISE EXCEPTION 'check_ins table is missing; apply 006_create_booking_system.sql first';
    END IF;
    IF EXISTS (
        SELECT 1 FROM bookings
        WHERE status IS NULL OR status NOT IN (
            'pending', 'confirmed', 'expired',
            'booked', 'checked_in', 'completed', 'cancelled', 'no_show'
        )
    ) THEN
        RAISE EXCEPTION 'bookings contains an unrecognized status; review rows before migrating';
    END IF;
END $$;

LOCK TABLE bookings IN ACCESS EXCLUSIVE MODE;
ALTER TABLE bookings DROP CONSTRAINT IF EXISTS no_overlapping_bookings;

-- Drop only checks that constrain the status column, including generated names.
DO $$
DECLARE
    status_constraint RECORD;
BEGIN
    FOR status_constraint IN
        SELECT conname FROM pg_constraint
        WHERE conrelid = to_regclass('bookings')
          AND contype = 'c'
          AND pg_get_constraintdef(oid) ILIKE '%status%'
    LOOP
        EXECUTE format('ALTER TABLE bookings DROP CONSTRAINT %I', status_constraint.conname);
    END LOOP;
END $$;

UPDATE bookings
SET status = CASE status
    WHEN 'pending' THEN 'booked'
    WHEN 'confirmed' THEN CASE
        WHEN EXISTS (
            SELECT 1 FROM check_ins ci
            WHERE ci.booking_id = bookings.booking_id AND ci.status = 'success'
        ) THEN 'checked_in'
        ELSE 'booked'
    END
    WHEN 'expired' THEN 'no_show'
    ELSE status
END
WHERE status IN ('pending', 'confirmed', 'expired');

ALTER TABLE bookings ALTER COLUMN status SET DEFAULT 'booked';
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS checkin_at TIMESTAMPTZ;
UPDATE bookings b
SET checkin_at = ci.checkin_time
FROM check_ins ci
WHERE ci.booking_id = b.booking_id
  AND ci.status = 'success'
  AND b.status IN ('checked_in', 'completed')
  AND b.checkin_at IS NULL;

ALTER TABLE bookings
    ADD CONSTRAINT ck_bookings_status
    CHECK (status IN ('booked', 'checked_in', 'completed', 'cancelled', 'no_show'));
ALTER TABLE bookings
    ADD CONSTRAINT no_overlapping_bookings
    EXCLUDE USING gist (
        room_id WITH =,
        tstzrange(start_time, end_time) WITH &&
    ) WHERE (status IN ('booked', 'checked_in'));
DROP INDEX IF EXISTS idx_bookings_status;
CREATE INDEX idx_bookings_status
    ON bookings(status) WHERE status IN ('booked', 'checked_in');
COMMENT ON CONSTRAINT no_overlapping_bookings ON bookings IS
    'TC-07: Prevents overlap while a booking is booked or checked_in.';

-- Normalize the older reservations table when present; it is retained for
-- legacy compatibility and uses the same lifecycle vocabulary.
DO $$
DECLARE
    status_constraint RECORD;
BEGIN
    IF to_regclass('reservations') IS NOT NULL THEN
        LOCK TABLE reservations IN ACCESS EXCLUSIVE MODE;
        IF EXISTS (
            SELECT 1 FROM reservations
            WHERE status IS NULL OR status NOT IN (
                'pending', 'confirmed', 'expired',
                'booked', 'checked_in', 'completed', 'cancelled', 'no_show'
            )
        ) THEN
            RAISE EXCEPTION 'reservations contains an unrecognized status; review rows before migrating';
        END IF;

        FOR status_constraint IN
            SELECT conname FROM pg_constraint
            WHERE conrelid = to_regclass('reservations')
              AND contype = 'c'
              AND pg_get_constraintdef(oid) ILIKE '%status%'
        LOOP
            EXECUTE format('ALTER TABLE reservations DROP CONSTRAINT %I', status_constraint.conname);
        END LOOP;

        UPDATE reservations
        SET status = CASE status
            WHEN 'pending' THEN 'booked'
            WHEN 'confirmed' THEN 'booked'
            WHEN 'expired' THEN 'no_show'
            ELSE status
        END
        WHERE status IN ('pending', 'confirmed', 'expired');
        ALTER TABLE reservations ALTER COLUMN status SET DEFAULT 'booked';
        ALTER TABLE reservations
            ADD CONSTRAINT ck_reservations_status
            CHECK (status IN ('booked', 'checked_in', 'completed', 'cancelled', 'no_show'));
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(100) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO schema_migrations(version)
VALUES ('008_booking_status_lifecycle')
ON CONFLICT (version) DO NOTHING;

COMMIT;
