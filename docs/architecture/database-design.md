# Database Design - UTH SeatSense

Tài liệu này mô tả schema cơ sở dữ liệu PostgreSQL cho hệ thống đặt phòng và theo dõi mật độ UTH SeatSense, bao gồm ERD (Entity Relationship Diagram) và từ điển dữ liệu đầy đủ.

Các trường gắn nhãn **target Sprint 4** là thiết kế cần triển khai/đối chiếu
với migration; mô tả ở đây không khẳng định chúng đã tồn tại trong database
đang chạy. Migration đã áp dụng được nêu riêng trong ghi chú của bảng.

## Mục lục

1. [ERD - Sơ đồ quan hệ thực thể](#erd---sơ-đồ-quan-hệ-thực-thể)
2. [Từ điển dữ liệu](#từ-điển-dữ-liệu)
3. [Ràng buộc và quy tắc nghiệp vụ](#ràng-buộc-và-quy-tắc-nghiệp-vụ)
4. [Chỉ mục (Indexes)](#chỉ-mục-indexes)
5. [Bảo mật và quyền riêng tư](#bảo-mật-và-quyền-riêng-tư)
6. [Dữ liệu CV SEAT-24](#dữ-liệu-cv-seat-24)

---

## ERD - Sơ đồ quan hệ thực thể

```mermaid
erDiagram
    User ||--o{ Booking : creates
    User ||--o{ AuditLog : performs
    User ||--o{ OccupancyAdjustment : records
    Campus ||--o{ Room : contains
    Room ||--o{ Booking : has
    Room ||--o{ OccupancyRecord : tracks
    Room ||--o{ CVCountRecord : monitors
    Room ||--o{ CountSession : starts
    Room ||--o{ CountEvent : records
    Room ||--o{ DeviceStatus : reports
    CountSession ||--o{ CountEvent : contains
    CountSession ||--o{ OccupancyRecord : snapshots
    CountSession ||--o{ OccupancyAdjustment : adjusts
    Booking ||--o| CheckIn : "checked-in"
    Booking ||--o{ CheckInToken : issues

    User {
        int user_id PK
        string display_name
        string email UK
        string password_hash
        string role
        bool is_active
        timestamp created_at
        timestamp updated_at
    }

    Campus {
        int campus_id PK
        string code UK
        string name
        bool is_active
    }

    Room {
        int id PK
        string code UK
        string name
        string room_type
        string building
        int campus_id FK "nullable until legacy mapping is confirmed"
        int capacity
        bool capacity_confirmed
        string location
        string status
        bool is_active
        timestamp created_at
    }

    Booking {
        int booking_id PK
        int user_id FK
        int room_id FK
        int participant_count "2..6 for new bookings; nullable for legacy rows"
        timestamp start_time
        timestamp end_time
        int buffer_minutes
        string status
        timestamp checkin_at
        timestamp no_show_at
        timestamp created_at
        timestamp updated_at
    }

    CheckInToken {
        int token_id PK
        int booking_id FK
        string token_hash UK
        timestamp expires_at
        timestamp used_at
        timestamp revoked_at
        timestamp created_at
    }

    CheckIn {
        int checkin_id PK
        int booking_id FK "UNIQUE"
        timestamp checkin_time
        string method
        string status
        timestamp created_at
    }

    OccupancyRecord {
        int id PK
        uuid observation_id UK
        int room_id FK
        uuid session_id FK
        int current_count "nullable until valid baseline"
        int available_seats "nullable until valid baseline"
        timestamp recorded_at
        string source
        string device_status
    }

    CountSession {
        uuid session_id PK
        int room_id FK
        int initial_occupancy
        int operator_id FK
        timestamp started_at
        timestamp ended_at
    }

    CVCountRecord {
        bigint id PK
        string schema_version
        uuid session_id
        string camera_id
        string room_code
        int room_id FK
        string source_type
        bigint frame_index
        double timestamp_ms
        timestamp recorded_at
        timestamp received_at
        int people_count
        int tracked_count
        bool line_enabled
        bigint in_count
        bigint out_count
        bigint initial_occupancy
        bigint estimated_occupancy
        bool occupancy_underflow
    }

    CountEvent {
        uuid event_id PK "idempotency key from CV"
        uuid session_id FK
        int room_id FK
        string device_id
        string direction
        timestamp event_time
        timestamp received_at
        string source
        timestamp created_at
    }

    DeviceStatus {
        string device_id PK
        int room_id FK
        string status
        timestamp last_seen_at
        timestamp updated_at
    }

    OccupancyAdjustment {
        int adjustment_id PK
        uuid session_id FK
        int room_id FK
        int previous_count
        int adjusted_count
        int actor_id FK
        string reason
        timestamp created_at
    }

    AuditLog {
        int log_id PK
        int actor_id FK
        string action
        string entity_type
        int entity_id
        json changes
        string ip_address
        timestamp created_at
        text detail
    }
```

**Giải thích quan hệ:**
- User → Booking: Một user có nhiều booking (1-nhiều)
- User → AuditLog: Một user thực hiện nhiều hành động audit (1-nhiều)
- Campus → Room: Một cơ sở có nhiều phòng; phòng cũ chưa xác minh cơ sở có `campus_id = NULL`.
- Room → Booking: Một phòng có nhiều booking (1-nhiều)
- Room → OccupancyRecord: Một phòng có nhiều bản ghi mật độ (1-nhiều)
- Room → CVCountRecord: Một phòng có nhiều bản ghi CV (1-nhiều)
- Room → CountSession: Một phòng có nhiều phiên đếm; mỗi phiên lưu N0 đã kiểm tra.
- CountSession → CountEvent: Sự kiện thuộc phiên đếm; `event_id` UUID duy nhất
  từ CV được giữ nguyên qua mọi lần retry.
- Room → DeviceStatus: Trạng thái mới nhất của mỗi thiết bị/nguồn.
- CountSession → OccupancyRecord: Snapshot occupancy có thể truy về phiên.
- CountSession → OccupancyAdjustment: Hiệu chỉnh gắn với phiên và được audit.
- User → OccupancyAdjustment: Mỗi N0/hiệu chỉnh ghi người thực hiện và lý do.
- Booking → CheckIn: Một booking có tối đa một check-in (1-0..1)
- Booking → CheckInToken: Một booking có lịch sử phát token; tối đa một token chưa dùng/chưa thu hồi tại một thời điểm.

---

## Từ điển dữ liệu

### Bảng: campuses

Danh mục hai cơ sở CS1/CS3 theo FR-SITE-01. Migration tạo danh mục nhưng không tự gán phòng hiện có vào cơ sở khi chưa có dữ liệu xác nhận.

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| campus_id | INTEGER | NOT NULL | PRIMARY KEY | auto-increment | — |
| code | VARCHAR(20) | NOT NULL | UNIQUE | — | CHECK: 'CS1', 'CS3' |
| name | VARCHAR(100) | NOT NULL | — | — | Tên hiển thị |
| is_active | BOOLEAN | NOT NULL | — | TRUE | — |

---

### Bảng: users

Xác thực và phân quyền người dùng.

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| user_id | INTEGER | NOT NULL | PRIMARY KEY | auto-increment | — |
| display_name | VARCHAR(100) | NOT NULL | — | — | Tên hiển thị |
| email | VARCHAR(255) | NOT NULL | UNIQUE | — | Định dạng email, dùng để đăng nhập |
| password_hash | VARCHAR(255) | NOT NULL | — | — | **Không lưu plain text**. Dùng bcrypt/argon2 |
| role | VARCHAR(20) | NOT NULL | — | 'student' | CHECK: 'student', 'librarian', 'admin' |
| is_active | BOOLEAN | NOT NULL | — | TRUE | Cờ soft delete |
| created_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm tạo tài khoản |
| updated_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm cập nhật cuối |

**Chỉ mục:**
- `idx_users_email` trên (email)
- `idx_users_role` trên (role) WHERE is_active = TRUE

---

### Bảng: rooms

Phòng học/đọc khả dụng để đặt chỗ.

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| id | INTEGER | NOT NULL | PRIMARY KEY | auto-increment | — |
| code | VARCHAR(50) | NOT NULL | UNIQUE | — | Mã phòng (vd: 'A101') |
| name | VARCHAR(150) | NOT NULL | — | — | Tên hiển thị |
| room_type | VARCHAR(50) | NOT NULL | — | — | Target Sprint 4: CHECK `free_area`, `topic_room` |
| building | VARCHAR(150) | NULL | — | — | Tên cơ sở (vd: 'Cơ sở chính', 'Cơ sở 2') |
| campus_id | INTEGER | NULL | FOREIGN KEY → campuses.campus_id | — | NULL chỉ dành cho phòng cũ chưa được xác minh; phải gán trước khi bật filter cơ sở |
| capacity | INTEGER | NOT NULL | — | — | **CHECK: capacity > 0** |
| capacity_confirmed | BOOLEAN | NOT NULL | — | FALSE | Chỉ TRUE sau khi sức chứa được xác nhận; nếu FALSE không công bố chỗ trống/mức đông chính thức |
| location | VARCHAR(255) | NULL | — | — | Vị trí cụ thể (vd: 'Tầng 1, Khu A') |
| status | VARCHAR(20) | NOT NULL | — | 'active' | CHECK: 'active', 'maintenance', 'closed' |
| is_active | BOOLEAN | NOT NULL | — | TRUE | Legacy soft delete |
| created_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm tạo |

**Chỉ mục:**
- Unique index trên `code`

**Ràng buộc:**
- `ck_rooms_capacity`: capacity > 0
- `ck_rooms_status`: status IN ('active', 'maintenance', 'closed')
- `ck_rooms_type`: room_type IN ('free_area', 'topic_room')

**Chuyển đổi dữ liệu:** schema/seed legacy hiện dùng `reading_room` và
`group_study_room`; migration Sprint 4 phải ánh xạ có chủ đích sang
`free_area`/`topic_room`. Không đổi nhãn bằng cách suy đoán ý nghĩa phòng.

---

### Bảng: bookings

Đặt phòng của người dùng, có cơ chế chống trùng lịch (TC-07).

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| booking_id | INTEGER | NOT NULL | PRIMARY KEY | auto-increment | — |
| user_id | INTEGER | NOT NULL | FOREIGN KEY → users.user_id | — | ON DELETE RESTRICT |
| room_id | INTEGER | NOT NULL | FOREIGN KEY → rooms.id | — | ON DELETE RESTRICT |
| participant_count | INTEGER | NULL | — | — | 2–6 với booking mới; NULL chỉ giữ dữ liệu lịch sử chưa có sĩ số |
| start_time | TIMESTAMPTZ | NOT NULL | — | — | Thời gian bắt đầu |
| end_time | TIMESTAMPTZ | NOT NULL | — | — | Thời gian kết thúc |
| buffer_minutes | INTEGER | NOT NULL | — | 15 | Khoảng đệm sau booking; lưu giá trị cấu hình tại thời điểm tạo |
| status | VARCHAR(20) | NOT NULL | — | 'booked' | CHECK: 'booked', 'checked_in', 'completed', 'cancelled', 'no_show' |
| checkin_at | TIMESTAMPTZ | NULL | — | — | Thời điểm check-in thành công; có giá trị khi status là 'checked_in' hoặc 'completed' |
| no_show_at | TIMESTAMPTZ | NULL | — | — | Thời điểm tác vụ định kỳ chuyển booking thành `no_show` |
| created_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm tạo |
| updated_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm cập nhật |

**Chỉ mục:**
- `idx_bookings_room_start` trên (room_id, start_time)
- `idx_bookings_user` trên (user_id)
- `idx_bookings_status` trên (status) WHERE status IN ('booked', 'checked_in')

**Ràng buộc:**
- `ck_bookings_time_order`: end_time > start_time
- `ck_bookings_participant_count`: participant_count IS NULL OR participant_count BETWEEN 2 AND 6
- `ck_bookings_buffer_minutes`: buffer_minutes >= 0
- **`no_overlapping_bookings` (TC-07):** EXCLUDE USING gist cho khoảng từ
  `start_time` đến `end_time + buffer_minutes`; giá trị `buffer_minutes` được
  nạp từ cấu hình khi tạo booking để kiểm tra overlap và buffer.

**State diagram và điều kiện chuyển:** xem [booking-lifecycle.md](booking-lifecycle.md).

> Migration `008_add_campus_and_booking_participants.sql` thêm danh mục campus, trường sĩ số, `checkin_at` và chuyển trạng thái booking cũ sang bộ chuẩn `booked`, `checked_in`, `completed`, `cancelled`, `no_show`. Phòng hiện có chưa được gán cơ sở tự động; cần xác minh mapping trước khi bật lọc campus.

### Bảng: checkin_tokens

Lưu hash của QR token dùng một lần. Không lưu chuỗi token thô; khi cấp token mới cho cùng booking, token chưa dùng trước đó phải được thu hồi.

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| token_id | INTEGER | NOT NULL | PRIMARY KEY | auto-increment | — |
| booking_id | INTEGER | NOT NULL | FOREIGN KEY → bookings.booking_id | — | ON DELETE CASCADE |
| token_hash | VARCHAR(64) | NOT NULL | UNIQUE | — | SHA-256 dạng hex; không lưu token gốc |
| expires_at | TIMESTAMPTZ | NOT NULL | — | — | Phải sau `created_at` |
| used_at | TIMESTAMPTZ | NULL | — | — | NULL khi chưa dùng |
| revoked_at | TIMESTAMPTZ | NULL | — | — | Thu hồi khi cấp token khác hoặc booking không còn hợp lệ |
| created_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm phát |

Index `idx_checkin_tokens_booking` phục vụ truy vấn theo booking và hạn dùng; unique partial index cho phép tối đa một token chưa dùng/chưa thu hồi trên mỗi booking. Token đã dùng hoặc thu hồi được giữ lại để truy vết.

---

### Bảng: check_ins

Ghi nhận check-in thành công. Mỗi booking chỉ check-in được một lần.

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| checkin_id | INTEGER | NOT NULL | PRIMARY KEY | auto-increment | — |
| booking_id | INTEGER | NOT NULL | FOREIGN KEY → bookings.booking_id, UNIQUE | — | ON DELETE CASCADE |
| checkin_time | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm check-in thực tế |
| method | VARCHAR(20) | NOT NULL | — | 'qr' | CHECK: 'qr', 'manual' |
| status | VARCHAR(20) | NOT NULL | — | 'success' | CHECK: 'success', 'failed', 'expired' |
| created_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm ghi nhận |

**Chỉ mục:**
- `idx_checkins_booking` trên (booking_id)
- `idx_checkins_time` trên (checkin_time)

---

### Bảng: occupancy_records

Quan sát mật độ phòng theo thời gian.

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| id | INTEGER | NOT NULL | PRIMARY KEY | auto-increment | — |
| observation_id | UUID | NOT NULL | UNIQUE | — | ID duy nhất cho quan sát |
| room_id | INTEGER | NOT NULL | FOREIGN KEY → rooms.id | — | ON DELETE RESTRICT |
| session_id | UUID | NULL | FOREIGN KEY → count_sessions.session_id | — | NULL chỉ cho dữ liệu legacy chưa ánh xạ phiên |
| current_count | INTEGER | NULL | — | — | CHECK: current_count >= 0; NULL khi chưa có N0 hợp lệ |
| available_seats | INTEGER | NULL | — | — | CHECK: available_seats >= 0 hoặc NULL |
| recorded_at | TIMESTAMPTZ | NOT NULL | — | — | Thời điểm ghi nhận |
| source | VARCHAR(30) | NOT NULL | — | 'cv' | Nguồn: 'cv' hoặc 'manual' |
| device_status | VARCHAR(20) | NULL | — | — | CHECK: 'online', 'offline', 'error', hoặc NULL |

**Chỉ mục:**
- `idx_occupancy_room_recorded` trên (room_id, recorded_at DESC)
- Unique index trên `observation_id`

---

### Bảng: count_events

Sự kiện rời rạc (discrete events) vào/ra. Khác với cv_count_records (frame aggregates).

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| event_id | UUID | NOT NULL | PRIMARY KEY | CV cấp | Idempotency key; giữ nguyên qua retry |
| session_id | UUID | NOT NULL | FOREIGN KEY → count_sessions.session_id | — | Phiên đếm sở hữu sự kiện |
| room_id | INTEGER | NOT NULL | FOREIGN KEY → rooms.id | — | ON DELETE RESTRICT |
| device_id | VARCHAR(100) | NOT NULL | — | — | Mã thiết bị, không phải ID theo dõi cá nhân |
| direction | VARCHAR(10) | NOT NULL | — | — | **CHECK: direction IN ('in', 'out')** |
| event_time | TIMESTAMPTZ | NOT NULL | — | — | Thời điểm sự kiện xảy ra |
| received_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm backend nhận được |
| source | VARCHAR(20) | NOT NULL | — | 'cv' | CHECK: 'cv', 'manual' |
| created_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm tạo bản ghi |

**Chỉ mục:**
- `idx_count_events_room` trên (room_id, event_time DESC)
- `idx_count_events_received` trên (received_at DESC)
- Primary key UUID trên `event_id` bảo đảm tính duy nhất và hỗ trợ retry idempotent

---

### Bảng: count_sessions (target Sprint 4)

Mỗi phiên đếm có N0 được người vận hành kiểm tra; không suy ra N0 bằng 0.

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| session_id | UUID | NOT NULL | PRIMARY KEY | do backend tạo | ID phiên |
| room_id | INTEGER | NOT NULL | FOREIGN KEY → rooms.id | — | ON DELETE RESTRICT |
| initial_occupancy | INTEGER | NOT NULL | — | — | CHECK >= 0; giá trị người vận hành xác nhận |
| operator_id | INTEGER | NOT NULL | FOREIGN KEY → users.user_id | — | Người kiểm tra/nhập N0 |
| started_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm bắt đầu |
| ended_at | TIMESTAMPTZ | NULL | — | — | NULL khi phiên còn mở |

Mỗi phiên mới cần N0 mới theo FR-OCC-06/BR-21/24. Nếu chưa xác định được N0,
không mở phiên occupancy chính thức; trạng thái UI phải là insufficient-data.
Giá trị capacity mẫu trong seed không đồng nghĩa `capacity_confirmed = TRUE`.

---

### Bảng: device_statuses (target Sprint 4)

Lưu trạng thái nguồn mới nhất; heartbeat không phải sự kiện IN/OUT và không
được cộng vào occupancy.

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| device_id | VARCHAR(100) | NOT NULL | PRIMARY KEY | — | Mã nguồn không chứa ID track |
| room_id | INTEGER | NOT NULL | FOREIGN KEY → rooms.id | — | ON DELETE RESTRICT |
| status | VARCHAR(20) | NOT NULL | — | — | CHECK: `online`, `offline`, `error` |
| last_seen_at | TIMESTAMPTZ | NOT NULL | — | — | Thời điểm heartbeat cuối |
| updated_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Lần cập nhật trạng thái cuối |

Ngưỡng stale/offline lấy từ cấu hình; migration/seed không đặt các ngưỡng này
thành hằng số trong logic.

---

### Bảng: occupancy_adjustments (target Sprint 4)

Lưu N0 và mọi hiệu chỉnh sau đó để truy vết; không cập nhật/xóa sự kiện CV thô.

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| adjustment_id | INTEGER | NOT NULL | PRIMARY KEY | auto-increment | — |
| session_id | UUID | NOT NULL | FOREIGN KEY → count_sessions.session_id | — | Phiên được hiệu chỉnh |
| room_id | INTEGER | NOT NULL | FOREIGN KEY → rooms.id | — | ON DELETE RESTRICT |
| previous_count | INTEGER | NULL | — | — | NULL cho bản ghi N0 ban đầu |
| adjusted_count | INTEGER | NOT NULL | — | — | CHECK >= 0 |
| actor_id | INTEGER | NOT NULL | FOREIGN KEY → users.user_id | — | Người thực hiện |
| reason | TEXT | NOT NULL | — | — | Không rỗng |
| created_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm ghi |

Index `idx_adjustments_session_time` trên `(session_id, created_at DESC)` phục
vụ truy vết N0 và hiệu chỉnh theo phiên.

---

### Bảng: audit_logs

Nhật ký kiểm toán hệ thống cho bảo mật và tuân thủ.

| Trường | Kiểu dữ liệu | Null | Khóa | Mặc định | Ràng buộc |
|---|---|---|---|---|---|
| log_id | INTEGER | NOT NULL | PRIMARY KEY | auto-increment | — |
| actor_id | INTEGER | NULL | FOREIGN KEY → users.user_id | — | ON DELETE SET NULL. NULL = hệ thống |
| action | VARCHAR(100) | NOT NULL | — | — | Hành động (vd: 'create_booking', 'login') |
| entity_type | VARCHAR(50) | NULL | — | — | Loại thực thể (vd: 'booking', 'room') |
| entity_id | INTEGER | NULL | — | — | ID của thực thể bị tác động |
| changes | JSONB | NULL | — | — | Giá trị cũ/mới cho update |
| ip_address | VARCHAR(45) | NULL | — | — | IP client (hỗ trợ IPv6) |
| created_at | TIMESTAMPTZ | NOT NULL | — | NOW() | Thời điểm ghi log |
| detail | TEXT | NULL | — | — | Chi tiết bổ sung |

**Chỉ mục:**
- `idx_audit_actor_time` trên (actor_id, created_at DESC)
- `idx_audit_entity` trên (entity_type, entity_id, created_at DESC)
- `idx_audit_action` trên (action, created_at DESC)

---

## Ràng buộc và quy tắc nghiệp vụ

### TC-07 / BR-04: Chống trùng lịch đặt phòng

**Yêu cầu:** Ngăn chặn các lượt đặt hợp lệ trên cùng phòng chồng lấn thời gian
hoặc vi phạm khoảng đệm sau booking. `buffer_minutes` được lấy từ cấu hình khi
tạo booking và lưu trên bản ghi để ràng buộc DB kiểm tra được.

**Triển khai mục tiêu:**
```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE bookings
ADD CONSTRAINT no_overlapping_bookings
EXCLUDE USING gist (
    room_id WITH =,
    tstzrange(
        start_time,
        end_time + buffer_minutes * INTERVAL '1 minute'
    ) WITH &&
) WHERE (status IN ('booked', 'checked_in'));
```

**Hành vi:**
- Ngăn chặn nguyên tử (atomic) các booking chồng lấn đồng thời
- Chỉ áp dụng cho trạng thái đang chiếm lịch (`booked`, `checked_in`)
- Booking đã cancelled hoặc completed không chặn lịch tương lai
- Sử dụng PostgreSQL range types và GiST index

### Các quy tắc nghiệp vụ khác

1. **Sức chứa phòng:** capacity > 0 (CHECK constraint)
2. **Thứ tự thời gian booking:** end_time > start_time (CHECK constraint)
3. **Hướng sự kiện đếm:** direction IN ('in', 'out') (CHECK constraint)
4. **Một check-in mỗi booking:** UNIQUE constraint trên check_ins.booking_id
5. **Logic CV line counter:** Khi line_enabled=true, in_count và out_count bắt buộc; khi false phải NULL
6. **Tính estimated_occupancy:** `max(0, N0 + tổng IN − tổng OUT)` trong một
   phiên; nếu N0 chưa được xác nhận, occupancy/chỗ trống/mức đông là NULL/
   insufficient-data, không phải 0.
7. **Idempotency sự kiện:** `event_id` UUID từ CV là khóa duy nhất; cùng ID và
   payload giống nhau trả receipt cũ, cùng ID nhưng payload khác bị từ chối.

---

## Chỉ mục (Indexes)

### Mục đích

| Bảng | Chỉ mục | Mục đích |
|---|---|---|
| users | idx_users_email | Tra cứu nhanh email khi đăng nhập |
| users | idx_users_role | Lọc user theo role |
| rooms | UNIQUE trên code | Đảm bảo mã phòng duy nhất |
| bookings | idx_bookings_room_start | Truy vấn booking theo phòng và thời gian |
| bookings | idx_bookings_user | Lịch sử booking của user |
| bookings | idx_bookings_status | Lọc booking đang hoạt động |
| check_ins | idx_checkins_booking | Tra cứu check-in của booking |
| check_ins | idx_checkins_time | Truy vấn theo thời gian |
| occupancy_records | idx_occupancy_room_recorded | Lịch sử mật độ phòng |
| occupancy_records | UNIQUE trên observation_id | Chống trùng quan sát |
| cv_count_records | idx_cv_camera_recorded | Truy vấn dữ liệu CV theo camera |
| cv_count_records | idx_cv_room_recorded | Truy vấn dữ liệu CV theo phòng |
| cv_count_records | UNIQUE trên (session_id, frame_index) | Idempotency |
| count_events | idx_count_events_room | Lịch sử sự kiện theo phòng |
| count_events | idx_count_events_received | Sự kiện gần đây |
| count_events | PRIMARY KEY event_id UUID | Khử trùng sự kiện qua retry |
| device_statuses | PRIMARY KEY device_id | Trạng thái mới nhất của nguồn |
| occupancy_adjustments | idx_adjustments_session_time | Truy vết N0 và hiệu chỉnh theo phiên |
| audit_logs | idx_audit_actor_time | Audit trail theo user |
| audit_logs | idx_audit_entity | Lịch sử thay đổi thực thể |
| audit_logs | idx_audit_action | Audit theo loại hành động |

---

## Bảo mật và quyền riêng tư

### Bảo mật mật khẩu

- **Không bao giờ lưu plain text password**
- Sử dụng **bcrypt** (khuyến nghị) hoặc **argon2**
- Bcrypt work factor: tối thiểu 12 rounds
- Không log password hoặc password hash

### Thu thập dữ liệu cá nhân tối thiểu

**Thông tin thu thập:**
- Email (xác thực)
- Tên hiển thị (nhận diện user)

**KHÔNG thu thập:**
- CMND/CCCD
- Địa chỉ nhà
- Số điện thoại
- Ngày sinh
- Ảnh (CV không lưu hình ảnh)

### Kế hoạch xóa dữ liệu sau dự án

1. Ẩn danh hóa hoặc xóa tài khoản user
2. Giữ lại số liệu thống kê tổng hợp (không có PII)
3. Xóa lịch sử booking chi tiết
4. Giữ audit log theo thời hạn tuân thủ (vd: 90 ngày), sau đó xóa

### Quyền riêng tư video/ảnh (NFR-PRI-02)

- **CV module xử lý frame real-time**
- **Không lưu trữ video hoặc ảnh lâu dài**
- Chỉ gửi số liệu tổng hợp lên backend
- Không nhận diện khuôn mặt hay cá nhân
- Không lưu bounding box hoặc dữ liệu ảnh vào database

---

## Dữ liệu CV SEAT-24

`cv_count_records` lưu một hàng cho mỗi frame đã xử lý, độc lập với bảng
occupancy_records phục vụ số người trong phòng. Chỉ lưu số liệu tổng hợp,
không lưu video, ảnh, bbox hay nhận diện cá nhân. Migration chuẩn:
`database/init/002_cv_count_records.sql`.

| Trường | Kiểu | Quy tắc |
| --- | --- | --- |
| id | BIGINT IDENTITY | PK tự sinh |
| schema_version | VARCHAR(10) | Bắt buộc, hiện là 1.0 |
| session_id | UUID | Phiên do CV cấp |
| camera_id | VARCHAR(100) | Không rỗng |
| room_code | VARCHAR(100), null | Giữ nguyên room_id chuỗi từ CV |
| room_id | BIGINT, null | FK rooms.id; ON DELETE RESTRICT |
| source_type | VARCHAR(10) | video hoặc webcam |
| frame_index | BIGINT | Không âm; thứ tự frame trong phiên |
| timestamp_ms | DOUBLE PRECISION | Không âm, hữu hạn; thời gian tương đối |
| recorded_at | TIMESTAMPTZ | Thời điểm xử lý do CV gửi, hữu hạn |
| received_at | TIMESTAMPTZ | Database cấp NOW() khi ghi mới |
| people_count | INTEGER | Số người hiện thấy, không âm |
| tracked_count | INTEGER | 0 đến people_count |
| line_enabled | BOOLEAN | Bật hoặc tắt đếm qua đường |
| in_count / out_count | BIGINT, null | Không âm; bắt buộc nếu bật line, null nếu tắt |
| initial_occupancy | BIGINT, null | Số ban đầu nếu biết, không âm |
| estimated_occupancy | BIGINT, null | max(0, initial + IN - OUT); null nếu initial null |
| occupancy_underflow | BOOLEAN | true nếu công thức trước clamp âm |

Unique `(session_id, frame_index)` chống ghi trùng và hỗ trợ truy vấn frame
theo phiên. Index `(camera_id, recorded_at DESC, id DESC)` và partial index
`(room_id, recorded_at DESC, id DESC)` khi room_id khác null hỗ trợ lịch sử.
schema_migrations ghi phiên bản SQL đã áp dụng và applied_at.

### Ánh xạ đầu ra CV

Nguồn lưu là `backend_counts.jsonl`; từng dòng được kiểm tra bằng
`CVCountInput` ở Backend. Không đưa dữ liệu debug results.jsonl có bbox vào
schema này. UUID, giới hạn số nguyên, timestamp có múi giờ và tính nhất quán
counters được kiểm tra trước khi ghi; database tiếp tục áp dụng ràng buộc.

room_id từ CV được giữ ở room_code. Backend tìm đúng rooms.code để gán FK;
mã chưa có hoặc null cho FK null, không ép chuỗi số thành rooms.id và không
tạo phòng giả. Retry không thay đổi ánh xạ đã lưu khi danh mục phòng thay đổi.
Giới hạn rooms.code là 50 ký tự; mã CV dài hơn vẫn được lưu nhưng không khớp
danh mục phòng hiện tại.

people_count không có nghĩa là tổng người trong phòng. Không tự chuyển nó
sang occupancy_records. IN/OUT là counters tích lũy trong phiên, không cộng
chúng giữa các frame. estimated_occupancy chỉ có khi biết số người ban đầu;
độ tin cậy vẫn phụ thuộc vị trí camera và tracking. Chưa lưu từng crossing
event hoặc hợp nhất số đếm giữa nhiều camera.

### Thời gian, ghi trùng và truy vấn

TIMESTAMPTZ giữ thời điểm tuyệt đối, không giữ nhãn múi giờ ban đầu. Backend
từ chối datetime thiếu múi giờ, dùng session DB UTC và xuất DTO theo UTC.
recorded_at là giờ xử lý, không phải giờ camera quay. timestamp_ms của video
là frame_index/FPS, webcam là monotonic từ đầu phiên; không đổi trường này
thành ngày giờ thật. received_at là giờ nhận tại DB, không đổi khi retry.

Repository INSERT ON CONFLICT DO NOTHING theo unique phiên/frame. Cùng nội
dung trả bản cũ; nội dung khác gây CVRecordConflict. Cả batch rollback nếu
có lỗi, không lưu một phần batch. Cơ chế này cũng được kiểm tra khi hai yêu
cầu trùng nội dung chạy đồng thời.

Lịch sử mặc định mới nhất trước theo recorded_at, rồi id. Khoảng thời gian
lọc là [start,end), limit tối đa 500. Offset pagination không bảo đảm snapshot
khi dữ liệu đang được ghi mới. latest trả None nếu chưa có dữ liệu, không
trả số 0 giả.

### Triển khai

Volume mới chạy init 001/002; volume cũ phải áp dụng 002 riêng. Không sửa
schema bằng ORM create_all hoặc xóa volume để nâng cấp. File SQL chạy trong
transaction và có advisory lock; migration mới cần file phiên bản mới.
Xem [hướng dẫn database](../../database/README.md) và
[API contract CV](api-contracts.md) để biết mapping dữ liệu CV.
