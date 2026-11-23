-- SEAT-59: set the initial live view to zero for a clean demo/test start.
BEGIN;

INSERT INTO cv_count_records (
    schema_version, session_id, camera_id, room_code, room_id,
    source_type, frame_index, timestamp_ms, recorded_at, received_at,
    people_count, tracked_count, line_enabled,
    in_count, out_count, initial_occupancy,
    estimated_occupancy, occupancy_underflow
)
VALUES
    ('1.0', md5('SEAT-59-reset-A101')::uuid, 'reset-seat59', 'A101',
     (SELECT id FROM rooms WHERE code='A101'), 'webcam', 0, 0,
     NOW(), NOW(), 0, 0, TRUE, 0, 0, 0, 0, FALSE),
    ('1.0', md5('SEAT-59-reset-B201')::uuid, 'reset-seat59', 'B201',
     (SELECT id FROM rooms WHERE code='B201'), 'webcam', 0, 0,
     NOW(), NOW(), 0, 0, TRUE, 0, 0, 0, 0, FALSE)
ON CONFLICT (session_id, frame_index) DO UPDATE SET
    people_count = EXCLUDED.people_count,
    tracked_count = EXCLUDED.tracked_count,
    in_count = EXCLUDED.in_count,
    out_count = EXCLUDED.out_count,
    initial_occupancy = EXCLUDED.initial_occupancy,
    estimated_occupancy = EXCLUDED.estimated_occupancy,
    occupancy_underflow = EXCLUDED.occupancy_underflow,
    recorded_at = EXCLUDED.recorded_at,
    received_at = EXCLUDED.received_at;

COMMIT;
