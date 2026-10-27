INSERT INTO rooms (code, name, building, capacity)
VALUES
    ('A101', 'Phòng học A101', 'Cơ sở chính', 40),
    ('B201', 'Phòng học B201', 'Cơ sở chính', 60)
ON CONFLICT (code) DO NOTHING;
