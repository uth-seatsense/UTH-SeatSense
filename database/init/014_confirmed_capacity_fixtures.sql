BEGIN;

ALTER TABLE rooms
    ADD COLUMN IF NOT EXISTS capacity_confirmed BOOLEAN NOT NULL DEFAULT FALSE;

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
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name,
    room_type = EXCLUDED.room_type,
    building = EXCLUDED.building,
    capacity = EXCLUDED.capacity,
    is_active = TRUE,
    location = EXCLUDED.location,
    status = 'active',
    campus_id = EXCLUDED.campus_id;

UPDATE rooms
SET is_active = FALSE,
    capacity_confirmed = FALSE
WHERE code IN ('A101', 'B201');

UPDATE rooms
SET capacity_confirmed = TRUE
WHERE code IN (
    'DEMO-CS1-FREE-01',
    'DEMO-CS1-TOPIC-01',
    'DEMO-CS3-FREE-01'
);

UPDATE rooms
SET name = 'Khu tự học CS1',
    location = 'Tầng 1, Khu A'
WHERE code = 'DEMO-CS1-FREE-01';

UPDATE rooms
SET name = 'Phòng chuyên đề CS1',
    location = 'Tầng 2, Khu A'
WHERE code = 'DEMO-CS1-TOPIC-01';

UPDATE rooms
SET name = 'Khu tự học CS3',
    location = 'Tầng 1, Khu B'
WHERE code = 'DEMO-CS3-FREE-01';

COMMIT;
