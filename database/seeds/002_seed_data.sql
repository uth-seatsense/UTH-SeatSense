-- SEAT-37: Seed data for two facilities
-- Provides realistic test data for development and testing
BEGIN;

-- Seed users
INSERT INTO users (display_name, email, password_hash, role) VALUES
-- Admin users
('Nguyễn Văn Admin', 'admin@uth.edu.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQm1o.K6K', 'admin'), -- password: admin123
('Trần Thị Quản Lý', 'manager@uth.edu.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQm1o.K6K', 'librarian'),

-- Librarian users
('Lê Văn Thủ Thư', 'librarian1@uth.edu.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQm1o.K6K', 'librarian'),
('Phạm Thị Hỗ Trợ', 'librarian2@uth.edu.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQm1o.K6K', 'librarian'),

-- Student users
('Nguyễn Văn Học', 'student1@uth.edu.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQm1o.K6K', 'student'),
('Trần Thị Minh', 'student2@uth.edu.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQm1o.K6K', 'student'),
('Lê Hoàng Nam', 'student3@uth.edu.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQm1o.K6K', 'student'),
('Phạm Thị Hương', 'student4@uth.edu.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQm1o.K6K', 'student'),
('Hoàng Văn Bình', 'student5@uth.edu.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQm1o.K6K', 'student'),
('Võ Thị Lan', 'student6@uth.edu.vn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIQm1o.K6K', 'student')
ON CONFLICT (email) DO NOTHING;

-- Seed rooms for two facilities
INSERT INTO rooms (code, name, room_type, building, capacity, location, status) VALUES
-- Cơ sở chính (Main Campus)
('A101', 'Phòng đọc A101', 'reading_room', 'Cơ sở chính', 50, 'Tầng 1, Khu A', 'active'),
('A102', 'Phòng đọc A102', 'reading_room', 'Cơ sở chính', 60, 'Tầng 1, Khu A', 'active'),
('A201', 'Phòng học nhóm A201', 'group_study_room', 'Cơ sở chính', 10, 'Tầng 2, Khu A', 'active'),
('A202', 'Phòng học nhóm A202', 'group_study_room', 'Cơ sở chính', 8, 'Tầng 2, Khu A', 'active'),
('A203', 'Phòng học nhóm A203', 'group_study_room', 'Cơ sở chính', 12, 'Tầng 2, Khu A', 'active'),
('B101', 'Phòng đọc B101', 'reading_room', 'Cơ sở chính', 80, 'Tầng 1, Khu B', 'active'),
('B102', 'Phòng đọc B102', 'reading_room', 'Cơ sở chính', 70, 'Tầng 1, Khu B', 'active'),
('B201', 'Phòng học nhóm B201', 'group_study_room', 'Cơ sở chính', 15, 'Tầng 2, Khu B', 'active'),
('B202', 'Phòng đọc B202', 'reading_room', 'Cơ sở chính', 40, 'Tầng 2, Khu B', 'active'),
('B301', 'Phòng học nhóm B301', 'group_study_room', 'Cơ sở chính', 10, 'Tầng 3, Khu B', 'maintenance'),

-- Cơ sở 2 (Campus 2)
('C101', 'Phòng đọc C101', 'reading_room', 'Cơ sở 2', 45, 'Tầng 1, Toà C', 'active'),
('C102', 'Phòng đọc C102', 'reading_room', 'Cơ sở 2', 55, 'Tầng 1, Toà C', 'active'),
('C201', 'Phòng học nhóm C201', 'group_study_room', 'Cơ sở 2', 12, 'Tầng 2, Toà C', 'active'),
('C202', 'Phòng học nhóm C202', 'group_study_room', 'Cơ sở 2', 8, 'Tầng 2, Toà C', 'active'),
('D101', 'Phòng đọc D101', 'reading_room', 'Cơ sở 2', 65, 'Tầng 1, Toà D', 'active'),
('D102', 'Phòng đọc D102', 'reading_room', 'Cơ sở 2', 50, 'Tầng 1, Toà D', 'active'),
('D201', 'Phòng học nhóm D201', 'group_study_room', 'Cơ sở 2', 10, 'Tầng 2, Toà D', 'active'),
('D202', 'Phòng học nhóm D202', 'group_study_room', 'Cơ sở 2', 6, 'Tầng 2, Toà D', 'active'),
('D301', 'Phòng đọc D301', 'reading_room', 'Cơ sở 2', 40, 'Tầng 3, Toà D', 'active')
ON CONFLICT (code) DO NOTHING;

-- Seed some bookings (using room IDs from the inserted rooms)
WITH room_ids AS (
    SELECT id, code FROM rooms WHERE code IN ('A101', 'A201', 'B101', 'C101', 'D201')
),
user_ids AS (
    SELECT user_id, email FROM users WHERE email LIKE 'student%@uth.edu.vn' LIMIT 5
)
INSERT INTO bookings (user_id, room_id, start_time, end_time, status) VALUES
-- Past bookings (completed)
((SELECT user_id FROM user_ids WHERE email = 'student1@uth.edu.vn'),
 (SELECT id FROM room_ids WHERE code = 'A101'),
 NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '2 hours', 'completed'),

-- Current/recent bookings (confirmed)
((SELECT user_id FROM user_ids WHERE email = 'student2@uth.edu.vn'),
 (SELECT id FROM room_ids WHERE code = 'A201'),
 NOW() - INTERVAL '1 hour', NOW() + INTERVAL '1 hour', 'confirmed'),

((SELECT user_id FROM user_ids WHERE email = 'student3@uth.edu.vn'),
 (SELECT id FROM room_ids WHERE code = 'B101'),
 NOW() + INTERVAL '30 minutes', NOW() + INTERVAL '2.5 hours', 'confirmed'),

-- Future bookings (pending)
((SELECT user_id FROM user_ids WHERE email = 'student4@uth.edu.vn'),
 (SELECT id FROM room_ids WHERE code = 'C101'),
 NOW() + INTERVAL '1 day', NOW() + INTERVAL '1 day' + INTERVAL '3 hours', 'pending'),

((SELECT user_id FROM user_ids WHERE email = 'student5@uth.edu.vn'),
 (SELECT id FROM room_ids WHERE code = 'D201'),
 NOW() + INTERVAL '2 days', NOW() + INTERVAL '2 days' + INTERVAL '2 hours', 'pending'),

-- Cancelled booking
((SELECT user_id FROM user_ids WHERE email = 'student1@uth.edu.vn'),
 (SELECT id FROM room_ids WHERE code = 'A101'),
 NOW() + INTERVAL '3 days', NOW() + INTERVAL '3 days' + INTERVAL '1 hour', 'cancelled');

-- Seed check-ins for confirmed bookings
WITH confirmed_bookings AS (
    SELECT booking_id FROM bookings WHERE status = 'confirmed' LIMIT 2
)
INSERT INTO check_ins (booking_id, checkin_time, method, status)
SELECT booking_id, NOW() - INTERVAL '30 minutes', 'qr', 'success'
FROM confirmed_bookings;

-- Seed occupancy records
WITH active_rooms AS (
    SELECT id FROM rooms WHERE status = 'active' LIMIT 10
)
INSERT INTO occupancy_records (room_id, current_count, available_seats, source, recorded_at, device_status)
SELECT
    id,
    FLOOR(RANDOM() * 30)::INTEGER as current_count,
    FLOOR(RANDOM() * 20)::INTEGER as available_seats,
    'cv',
    NOW() - (RANDOM() * INTERVAL '1 hour'),
    CASE WHEN RANDOM() < 0.9 THEN 'online' ELSE 'offline' END
FROM active_rooms;

-- Seed some count events
WITH active_rooms AS (
    SELECT id FROM rooms WHERE status = 'active' LIMIT 5
)
INSERT INTO count_events (room_id, direction, event_time, source)
SELECT
    id,
    CASE WHEN RANDOM() < 0.5 THEN 'in' ELSE 'out' END,
    NOW() - (RANDOM() * INTERVAL '2 hours'),
    'cv'
FROM active_rooms, generate_series(1, 3);

-- Seed audit log entries
WITH admin_user AS (
    SELECT user_id FROM users WHERE role = 'admin' LIMIT 1
)
INSERT INTO audit_logs (actor_id, action, entity_type, entity_id, detail)
VALUES
((SELECT user_id FROM admin_user), 'create_room', 'room', 1, 'Created room A101'),
((SELECT user_id FROM admin_user), 'update_room', 'room', 2, 'Updated room capacity'),
(NULL, 'system_startup', NULL, NULL, 'System initialized with seed data');

COMMIT;
