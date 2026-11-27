# Sprint 4 — Bảng Go/No-go SEAT-59

**Ngày kiểm tra:** 2026-11-23
**Commit:** `9e26516`
**Jira:** [SEAT-59](https://nhauyen70205.atlassian.net/browse/SEAT-59)

## Quyết định

**CONDITIONAL GO — BLOCKED đối với video/ground-truth**

Các thành phần kỹ thuật đã đạt vòng kiểm thử thứ hai. Quy trình vẫn còn chờ
video thử/ground truth thật theo TC-04/TC-13 trước khi chuyển Jira sang Done.

## Bằng chứng đã chạy

| Ca / tiêu chí | Trạng thái | Kết quả thực tế |
|---|---|---|
| TC-12 Docker/DB/health | Pass | Backend, CV, DB, Frontend và Adminer khởi động; Backend/CV/DB health đạt |
| TC-04 CV event + idempotency | Pass cục bộ | Gửi lần đầu và gửi lại cùng `event_id` trên room_id 5; lần đầu `duplicate=false`, retry `duplicate=true` |
| TC-22 Tích hợp/CV count | Partial | 31 test backend đạt, 6 test PostgreSQL/container bị skip |
| TC-03 dữ liệu cũ/stale/offline | Blocked | Chưa chạy đủ fixture thời gian thực và UI stale/offline |
| AT-02 p95 CV→Web | Pass kỹ thuật | 20/20 HTTP 200; p95 end-to-end API/database = 21.33 ms |
| TC-04 CountEvent idempotency | Pass | Lần đầu duplicate=false; retry duplicate=true; occupancy rows 22 → 22 |
| Stale/offline | Pass kỹ thuật | Dừng CV 35 giây; room5 is_stale=true |
| Database outage/recovery | Pass | Dừng DB 60 giây; POST trả database_unavailable; restart health HTTP 200 |
| Frontend runtime/UI | Partial | HTTP 200, build đạt và 87 test đạt; UI đang hiển thị “Chưa có dữ liệu” |
| Số người theo phòng + phiên Web | Pass cục bộ | CS1 hiển thị 62 chỗ (50 + 12); CS3 hiển thị 120 chỗ; khi đổi cơ sở Dashboard cập nhật đúng danh sách/sức chứa |

## Mẫu độ trễ

20 lần đo end-to-end CV API → CountEvent → OccupancyRecord → occupancy API:

- p95: **21.33 ms**
- Tất cả 20 mẫu trả HTTP 200
- Cấu trúc chi tiết:
  [seat59-e2e-20.csv](seat59-e2e-20.csv)
  [seat59-e2e-summary.json](seat59-e2e-summary.json)

Kết quả này chứng minh p95 kỹ thuật API/database; chưa thay ground truth
hoặc độ trễ webcam/video đầu vào thực tế.

## Ảnh bằng chứng

- [Jira SEAT-59](seat59-jira.png)
- [Frontend Tổng quan](seat59-frontend.png)
- [Jira SEAT-59 cuối](seat59-final-jira.png)
- [Frontend Tổng quan cuối](seat59-final-dashboard.png)

## Điều kiện chuyển sang GO

1. Có video thử và ground truth được phép sử dụng.
2. Ghi ít nhất 20 timestamp CV–Backend–Web có cùng `event_id`.
3. Tính p95 theo công thức AT-02; p95 <= 5 giây.
4. Chạy stale/offline và ghi log, ảnh chụp.
5. Chạy đầy đủ PostgreSQL/container tests theo flag môi trường.
6. Cập nhật Jira từ In Progress sang Done sau phê duyệt bằng chứng.

Báo cáo chi tiết:
[docs/SEAT-59.md](../SEAT-59.md)
