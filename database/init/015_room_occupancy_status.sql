-- SEAT-59: one authoritative room-occupancy view for the web dashboard.
BEGIN;

DROP VIEW IF EXISTS room_occupancy_status;

CREATE VIEW room_occupancy_status AS
WITH latest_cv AS (
    SELECT DISTINCT ON (room_id)
        room_id,
        people_count,
        received_at,
        estimated_occupancy
    FROM cv_count_records
    WHERE room_id IS NOT NULL
    ORDER BY room_id, received_at DESC, id DESC
),
latest_manual AS (
    SELECT DISTINCT ON (room_id)
        room_id,
        current_count,
        recorded_at
    FROM occupancy_records
    WHERE room_id IS NOT NULL
    ORDER BY room_id, recorded_at DESC, id DESC
)
SELECT
    room.id AS room_id,
    room.code AS room_code,
    room.name AS room_name,
    campus.code AS campus_code,
    campus.name AS campus_name,
    room.capacity,
    room.capacity_confirmed,
    COALESCE(cv.estimated_occupancy, cv.people_count,
             manual.current_count) AS current_count,
    GREATEST(
        room.capacity - COALESCE(cv.estimated_occupancy, cv.people_count,
                                 manual.current_count, 0),
        0
    ) AS available_seats,
    GREATEST(cv.received_at, manual.recorded_at) AS updated_at
FROM rooms room
LEFT JOIN latest_cv cv ON cv.room_id = room.id
LEFT JOIN latest_manual manual ON manual.room_id = room.id
LEFT JOIN campuses campus ON campus.campus_id = room.campus_id
WHERE room.is_active IS TRUE;

COMMENT ON VIEW room_occupancy_status IS
    'SEAT-59: latest people count per active room. Prefer CV estimated occupancy, then visible CV people_count, then occupancy_records.';

COMMIT;
