# SEAT-58 — Báo cáo hoàn tất

**Ngày nghiệm thu:** 2026-11-20  
**Trạng thái:** Hoàn tất

## Phạm vi đã thực hiện

- Sửa migration `010_cv_count_event_uuid.sql` để chuyển `event_id` từ cột identity integer sang UUID an toàn và ghi nhận migration.
- Thêm migration `011_normalize_room_types.sql` để chuẩn hóa loại phòng cũ và tạo index cho truy vấn occupancy.
- Thêm `012_seed_campuses_and_rooms.sql` với dữ liệu idempotent cho 2 campus và 4 phòng mẫu.
- Truyền cấu hình CV và ngưỡng occupancy qua Docker Compose, Backend và `.env.example`.
- Xóa cấu hình Docker test dư thừa; kiểm thử Backend chạy trực tiếp bằng pytest.
- Cập nhật hướng dẫn database và báo cáo kiểm thử.

## Kết quả nghiệm thu

- Khởi tạo trên volume PostgreSQL cô lập, mới bằng `docker compose up -d --build`: thành công. DB, CV và Backend báo healthy; Frontend và Adminer khởi động.
- Dữ liệu seed: 2 campus, 4 phòng — 2 `free_area`, 2 `topic_room`.
- Kiểm tra schema: `count_events.event_id` có kiểu UUID và khóa unique; index occupancy tồn tại.
- TC-12: trước và sau `docker compose down` rồi `up`, số lượng vẫn là `2 campus | 4 rooms | 2 free_area | 2 topic_room | 1 occupancy probe`.
- Bằng chứng Adminer gồm 4 phòng `DEMO-CS1-*` và `DEMO-CS3-*`, cùng sức chứa và loại phòng.
- `.env` không được Git theo dõi và được ignore; `CV_API_KEY` và `CV_INGEST_API_KEY` trong `.env.example` để trống. Không đưa khóa thật vào Git.

Lượt nghiệm thu Docker dùng project, volume và file override cổng riêng để không đụng dữ liệu của project đang chạy. Stack nghiệm thu và volume tạm đã được dọn sau khi thu bằng chứng.

## Kiểm thử

| Lệnh | Kết quả |
|---|---|
| `$env:SEAT24_RUN_COMPOSE_TESTS='1'; .\.venv\Scripts\python.exe -m unittest discover -s database\tests -p test_compose_persistence.py -v` | Đạt: 2/2; bao gồm bootstrap sạch và giữ occupancy qua down/up. |
| `.\.venv\Scripts\python.exe -m pytest backend\tests -q` | Đạt: 35 passed, 6 skipped; có 1 cảnh báo deprecation Starlette/httpx. |
| `docker compose config --quiet` | Đạt. |
| `git diff --check` | Đạt. |

## Ghi chú container tại thời điểm ghi báo cáo

- Project `uth-seatsense` đang có `db` và `adminer`; Backend, CV và Frontend của project này chưa chạy.
- Project `seatsense-evidence-clean` đang có đủ `db`, `backend`, `cv`, `frontend` và `adminer`. Đây là project evidence riêng, không bị dọn trong quá trình nghiệm thu SEAT-58.
- Với ứng dụng đầy đủ, cần `db`, `backend`, `frontend`; cần `cv` khi bật nhận diện/đếm occupancy. `adminer` chỉ là giao diện quản trị DB để phát triển/kiểm tra, không bắt buộc để ứng dụng chạy.
