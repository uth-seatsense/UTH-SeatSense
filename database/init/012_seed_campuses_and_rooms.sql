-- Development fixtures for the two confirmed campuses; safe to reapply.
BEGIN;
SELECT pg_advisory_xact_lock(240058);

INSERT INTO campuses (code, name)
VALUES ('CS1', 'Cơ sở 1'), ('CS3', 'Cơ sở 3')
ON CONFLICT (code) DO NOTHING;

INSERT INTO rooms (
    code, name, room_type, building, capacity, is_active, location, status, campus_id
)
SELECT
    seed.code,
    seed.name,
    seed.room_type,
    seed.building,
    seed.capacity,
    TRUE,
    seed.location,
    'active',
    campus.campus_id
FROM (
    VALUES
        ('DEMO-CS1-FREE-01', 'Khu tự học CS1', 'free_area', 'CS1', 'Cơ sở 1', 50, 'Tầng 1, Khu A'),
        ('DEMO-CS1-TOPIC-01', 'Phòng chuyên đề CS1', 'topic_room', 'CS1', 'Cơ sở 1', 12, 'Tầng 2, Khu A'),
        ('DEMO-CS3-FREE-01', 'Khu tự học CS3', 'free_area', 'CS3', 'Cơ sở 3', 120, 'Tầng 1, Khu B')
) AS seed(code, name, room_type, campus_code, building, capacity, location)
JOIN campuses AS campus ON campus.code = seed.campus_code
ON CONFLICT (code) DO NOTHING;

INSERT INTO schema_migrations (version)
VALUES ('012_seed_campuses_and_rooms')
ON CONFLICT (version) DO NOTHING;

COMMIT;
