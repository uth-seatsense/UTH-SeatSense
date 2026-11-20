# Database — Cơ sở dữ liệu

## Mục đích và trách nhiệm

Module Database lưu cấu trúc cơ sở dữ liệu và dữ liệu mẫu của dự án.
Các nhóm dữ liệu chính gồm thông tin phòng, lịch đặt phòng và số người sử
dụng phòng theo thời gian. Backend đọc, ghi dữ liệu để phục vụ các chức năng
trên web và thống kê sử dụng phòng.

## Cấu trúc thư mục dự kiến

```text
database/
├── init/            # Các file SQL tạo bảng ban đầu
├── seeds/           # Dữ liệu mẫu để phát triển và kiểm thử
└── README.md
```

Các migration PostgreSQL được đặt trong `init/` và chạy theo thứ tự tên file
khi volume mới được khởi tạo. Seed hai cơ sở và phòng mẫu cũng được nạp sau
migration; các tệp trong `seeds/` là fixture bổ sung, không tự nạp.
## Chuẩn bị và chạy

Cần PostgreSQL hoặc Docker Desktop có Docker Compose. Dùng `.env.example`
làm mẫu để chuẩn bị `.env`, sau đó kiểm tra tên cơ sở dữ liệu, tài khoản,
mật khẩu và thông tin kết nối dùng chung với Backend.

Để khởi động bằng Docker Compose, chạy tại thư mục gốc dự án:

```sh
docker compose up -d db
```

Các file trong `init/` tạo schema, chuẩn hóa loại phòng và thêm hai cơ sở cùng
bốn phòng mẫu (`free_area`, `topic_room`) trên volume mới. `docker compose
down` rồi `up` giữ volume và dữ liệu; không dùng `down -v` nếu cần giữ dữ liệu.

### Nâng cấp PostgreSQL volume đã tồn tại

PostgreSQL không chạy lại các file init trên volume đã có dữ liệu. Sao lưu
database trước, sau đó áp dụng lần lượt các migration/seed mới từ PowerShell ở
thư mục gốc:

```powershell
Get-Content -Raw database\init\010_cv_count_event_uuid.sql |
  docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
Get-Content -Raw database\init\011_normalize_room_types.sql |
  docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
Get-Content -Raw database\init\012_seed_campuses_and_rooms.sql |
  docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Migration ánh xạ rõ `reading_room` → `free_area` và `group_study_room` →
`topic_room`. Nếu dữ liệu có loại phòng khác, migration dừng để rà soát thay vì
tự suy đoán hoặc đổi nhãn.

### Áp dụng migration OTP cho PostgreSQL volume đã tồn tại

PostgreSQL chỉ chạy các file `init/` khi khởi tạo volume rỗng. Trước khi bật
đăng nhập OTP trên môi trường dùng dữ liệu hiện có, hãy sao lưu database rồi
áp migration mới bằng PowerShell từ thư mục gốc repository:

```powershell
Get-Content -Raw database\init\009_add_email_otp_auth.sql |
  docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Kiểm tra phiên bản migration và hai bảng `email_otp_challenges`,
`auth_sessions` trước khi sử dụng API auth. Không dùng `docker compose down -v`
trên database cần giữ dữ liệu.

## Quản lý model, video và dữ liệu nhạy cảm

- Chỉ lưu số liệu tổng hợp và thông tin đặt phòng cần thiết; không lưu model,
  video hay ảnh camera trong cơ sở dữ liệu.
- Dữ liệu mẫu phải là dữ liệu giả, không chứa thông tin sinh viên thật.
- Không đưa mật khẩu, `.env` hay bản sao cơ sở dữ liệu thật lên Git.
- Giới hạn quyền truy cập dữ liệu thật, lưu bản sao ở nơi riêng và thống nhất
  thời hạn giữ hoặc xóa sau khi kết thúc dự án.
