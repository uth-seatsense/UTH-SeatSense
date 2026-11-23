# SEAT-59 — Báo cáo kiểm thử tích hợp và cổng Go/No-go

**Ngày:** 2026-11-23
**Commit:** `9e26516`
**Jira:** [SEAT-59](https://nhauyen70205.atlassian.net/browse/SEAT-59)
**Trạng thái Jira quan sát:** In Progress
**Người phụ trách:** Khiêm Nguyễn Đình
**Kết quả tổng:** CONDITIONAL GO / BLOCKED đối với video-ground-truth thực

## Kết luận

Phần tích hợp kỹ thuật đã đạt vòng kiểm thử thứ hai: luồng
CV API → `CountEvent` → `OccupancyRecord` → API occupancy đã chạy,
20/20 phép đo end-to-end đạt, retry idempotent, stale và database outage đều
được kiểm chứng. Kết quả vẫn còn BLOCKED đối với việc nghiệm thu bằng video
và ground truth thật, và Jira không tự chuyển sang Done.

## Bằng chứng thực tế

| Hạng mục | Kết quả | Bằng chứng |
|---|---|---|
| Backend/CV/DB/Frontend chạy Docker | Đạt | Container backend, cv, db và frontend đang chạy; health HTTP 200 |
| Frontend build | Đạt | 87/87 test đạt; build Vite thành công |
| Backend/occupancy/CV suite | Đạt | 31 test đạt, 6 test PostgreSQL/container bị bỏ qua do chưa bật flag chạy DB |
| Gửi CV event thực tế | Đạt | HTTP thành công với room_id 5; lần đầu `duplicate=false` |
| Gửi lại CV event thực tế | Đạt | Payload giống nhau trả `duplicate=true` |
| Jira SEAT-59 | Đang thực hiện | Jira mở: In Progress, Task, Medium, assignee Khiêm Nguyễn Đình |
| 20 phép đo end-to-end | Đạt kỹ thuật | 20/20 HTTP 200; p95 21.33 ms |
| Idempotency database | Đạt | 21 → 22 occupancy rows sau lần đầu; 22 → 22 sau retry |
| Stale | Đạt | Dừng CV 35 giây; `room5.is_stale=true` |
| Database outage 60 giây | Đạt | POST trả `database_unavailable`; DB khôi phục và health HTTP 200 |

Ảnh:

- [Màn hình Jira SEAT-59](test-reports/seat59-jira.png)
- [Màn hình Frontend Tổng quan](test-reports/seat59-frontend.png)

Log và dữ liệu:

- [Backend test](test-reports/seat59-backend-test.log)
- [Frontend test](test-reports/seat59-frontend-test.log)
- [Frontend build](test-reports/seat59-frontend-build.log)
- [Compose status](test-reports/seat59-compose-status.txt)
- [Runtime log](test-reports/seat59-runtime-log.txt)
- [20 mẫu latency](test-reports/seat59-latency.csv)
- [20 mẫu end-to-end mới](test-reports/seat59-e2e-20.csv)
- [Tóm tắt 20 mẫu end-to-end](test-reports/seat59-e2e-summary.json)
- [Kết quả idempotency](test-reports/seat59-idempotency.json)
- [Kết quả stale](test-reports/seat59-stale.json)
- [Kết quả database outage](test-reports/seat59-db-outage.json)
- [Dashboard cuối](test-reports/seat59-final-dashboard.png)
- [Jira cuối](test-reports/seat59-final-jira.png)

## Số đo độ trễ

20 lượt end-to-end CV API → `CountEvent` → `OccupancyRecord` → API occupancy:
- HTTP 200: **20/20**
- p95: **21.33 ms**
- Ngưỡng: **≤5 giây**
- Kết luận: **Đạt** cho phép đo kỹ thuật API/database hiện tại.

20 lượt gọi `/health/db` trước đó cho p95 **21.05 ms**; phép đo đó không thay
thế phép đo end-to-end vừa chạy.

## Số người theo phòng và phiên đăng nhập Web

Tại lần xác nhận ngày 2026-11-23 đã có view tổng hợp
`room_occupancy_status` và API `GET /api/v1/occupancy/rooms/status`.

Sức chứa được xác nhận theo cơ sở:

| Mã phòng | Cơ sở | Loại | Sức chứa |
|---|---|---|---:|
| DEMO-CS1-FREE-01 | CS1 | Khu tự học | 50 |
| DEMO-CS1-TOPIC-01 | CS1 | Phòng chuyên đề | 12 |
| DEMO-CS3-FREE-01 | CS3 | Khu tự học/tổng CS3 | 120 |

Tổng sức chứa phải được tính theo cơ sở đang chọn:
- CS1: **62 chỗ** (50 khu tự học + 12 phòng chuyên đề).
- CS3: **120 chỗ**.
- Không cộng sức chứa CS1 và CS3 vào cùng một tổng.
Các mã legacy `A101=40` và `B201=60` đã bị vô hiệu hóa, không dùng để
tính sức chứa chính trong Dashboard.

| Phòng | Sức chứa | Người hiện tại | Chỗ trống | Dữ liệu |
|---|---:|---:|---:|---|
| DEMO-CS1-FREE-01 | 50 | 0 | 50 | Fixture sức chứa CS1 |
| DEMO-CS1-TOPIC-01 | 12 | 0 | 12 | Fixture sức chứa CS1 |
| DEMO-CS3-FREE-01 | 120 | 0 | 120 | Fixture sức chứa CS3 |

- Tổng người trong cơ sở đang chọn: **0**
- CS1 — sức chứa/chỗ trống: **62/62**
- CS3 — sức chứa/chỗ trống: **120/120**
- Phiên đăng nhập Web còn hiệu lực: **0**

Trạng thái ban đầu được tạo bởi
`database/init/013_reset_live_counts_to_zero.sql`. Đây là snapshot demo,
không phải kết quả từ seed `002_seed_data.sql`.

Khi chạy webcam hoặc tải video tại CV Testing Lab:
1. Chọn mã phòng `DEMO-CS1-FREE-01`, `DEMO-CS1-TOPIC-01` hoặc `DEMO-CS3-FREE-01`.
2. Giữ số người ban đầu mặc định là `0`.
3. CV gửi từng khung hình tới
   `POST /api/v1/cv/count-records`.
4. Dashboard làm mới mỗi 30 giây và lấy bản ghi mới nhất từng phòng.

Ảnh Dashboard xác nhận:
[seat59-room-web-count.png](test-reports/seat59-room-web-count.png)
- [Dashboard CS1](test-reports/seat59-campus-CS1.png)
- [Dashboard CS3](test-reports/seat59-campus-CS3.png)

## Lỗ hổng đã phát hiện và đã sửa

1. Backend import `RoomNotFoundError` sai lớp; đã bổ sung exception
   `RoomNotFoundError` và kiểm tra room tồn tại trong
   `app/services/occupancy_service.py`.
2. Backend container nhận `CV_INGEST_API_KEY` rỗng trong khi CV dùng
   `CV_API_KEY`; đã đồng bộ Compose fallback theo `CV_API_KEY`.
3. Frontend Docker không khởi động do lockfile thiếu native binding;
   đã cập nhật `frontend/package-lock.json`, chạy lại 87 test và build.

## Điểm còn chặn

- Chưa có video thử được phép sử dụng và ground truth đếm tay.
- Chưa chạy 6 test PostgreSQL/container trong report cuối vì flag
  `SEAT24_RUN_DB_TESTS` chưa bật.
- Frontend hiện hiển thị “Chưa có dữ liệu” vì chưa có occupancy record live
  trên môi trường chạy.

## Điều kiện chuyển sang Go

- Chạy ít nhất 20 measurement end-to-end bằng cùng commit/config.
- Tính p95 theo công thức AT-02; p95 phải không quá 5 giây.
- Lưu ảnh, log, CSV, video/ground truth được phép và ngày/giờ thực chạy.
- Xác nhận stale/offline theo ngưỡng cấu hình.
- Cập nhật Jira SEAT-59 sang Done khi có bằng chứng phê duyệt.
