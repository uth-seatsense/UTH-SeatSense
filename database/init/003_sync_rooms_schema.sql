
BEGIN;

-- Bổ sung các cột còn thiếu, không ảnh hưởng dữ liệu hiện tại.
ALTER TABLE rooms
    ADD COLUMN IF NOT EXISTS code VARCHAR(50);

ALTER TABLE rooms
    ADD COLUMN IF NOT EXISTS building VARCHAR(150);

ALTER TABLE rooms
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- Gán mã kỹ thuật cho hai tầng hiện có.
UPDATE rooms
SET code = CASE
    WHEN id = 1 THEN 'FLOOR_1'
    WHEN id = 2 THEN 'FLOOR_2'
    ELSE code
END
WHERE code IS NULL;

-- Gán cơ sở cho các khu vực hiện tại.
UPDATE rooms
SET building = 'Cơ sở 1'
WHERE building IS NULL;

-- Không cho phép hoàn tất migration nếu còn phòng chưa có mã.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM rooms WHERE code IS NULL) THEN
        RAISE EXCEPTION
            'Migration stopped: some rooms have no code. Please review room data.';
    END IF;
END $$;

ALTER TABLE rooms
    ALTER COLUMN code SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_rooms_code
    ON rooms (code);

COMMIT;
