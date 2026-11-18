# Ánh xạ màn hình ↔ API

Tài liệu này đối chiếu giao diện hiện có với API Contract và các yêu cầu trong
SRS 1.9 và backlog Sprint 4. API base path là `/api/v1`. “Đã có” chỉ các handler Backend thực thi được;
“Contract/chưa triển khai” nghĩa là shape/endpoint được mô tả nhưng chưa có
handler; “đề xuất” là path cần thống nhất với Backend, không phải API đang chạy.
Contract mục tiêu là [api-contracts.md](../architecture/api-contracts.md);
OpenAPI runtime hiện chưa có đầy đủ các route dưới đây.

## Màn hình và luồng dữ liệu

| Màn hình | API gọi | Quyền | Trạng thái cần xử lý | Component dùng |
|---|---|---|---|---|
| Tổng quan sinh viên (`HomePage` → `DashboardPage`, hiện có) | `GET /api/v1/occupancy/current` — đã có; tổng số toàn hệ thống, chưa lọc cơ sở | Công khai xem; Backend hiện không gắn quyền cho endpoint | Đang tải; lỗi HTTP/mạng/JSON; chưa có dữ liệu (`current_count` null/thiếu); số 0 hợp lệ; đang làm mới mỗi 30 giây. Endpoint này không có `is_stale` | Hiện: `MetricCard`, `AreaRow` và `Icon` nội bộ. Dự kiến: `OccupancyBadge`, `StaleWarning`, `DashboardChart` |
| Danh sách phòng/khu tự học (`RoomsPage`, hiện placeholder) | Target: `GET /api/v1/rooms?campus_code=CS1|CS3`; occupancy qua `GET /api/v1/occupancy/rooms/{room_id}/latest`. Rooms chưa có handler; latest hiện có legacy response, chưa tổng hợp CountEvent/N0 | Contract chưa chốt quyền xem; runtime hiện không có middleware occupancy | Loading; lỗi; rỗng; chưa đủ N0/capacity; stale/offline; phòng đóng/bảo trì | `RoomCard`, `OccupancyBadge`, `StaleWarning` là component mục tiêu |
| Chi tiết phòng/mật độ | Target: `GET /api/v1/rooms/{room_id}` và `GET /api/v1/occupancy/rooms/{room_id}/latest`; lịch sử `GET /api/v1/rooms/{room_id}/occupancy/history` (chưa có handler) | Quyền xem theo contract, chưa triển khai xác thực | Loading; 404 `room_not_found`; 503 `occupancy_unavailable` hoặc `service_unavailable`; stale/offline có nhãn riêng; không đổi thiếu dữ liệu thành 0 | `OccupancyBadge`, `StaleWarning`, `DashboardChart` là component mục tiêu |
| Đặt phòng học nhóm và lịch của tôi (`ReservationPage`, hiện placeholder) | Contract: `GET /api/v1/rooms?room_type=topic_room`, `GET/POST /api/v1/bookings`, `DELETE /api/v1/bookings/{booking_id}`; chưa có handler | Sinh viên đăng nhập; chủ lượt đặt được hủy theo SRS; Backend chưa thực thi | Loading; empty; xung đột/giờ sai; phòng hết chỗ; success/error; phiên hết hạn | `BookingForm`, `TimeSlotPicker`, `QRCodeView` là component mục tiêu |
| Check-in QR (`CheckinPage`, hiện placeholder) | Contract: `POST /api/v1/bookings/{booking_id}/check-in-token` và `POST /api/v1/check-in`; chưa có handler | Chủ booking đã đăng nhập; Backend chưa thực thi quyền | Đang gửi; QR sai/hết hạn/đã dùng; ngoài thời gian; mạng/API lỗi; 401; thành công | `QRCodeView` và form check-in là component mục tiêu |
| Đăng nhập OTP (chưa có màn hình) | Contract: `POST /api/v1/auth/register` gửi OTP, `POST /api/v1/auth/login` xác minh, `POST /api/v1/auth/logout`; chưa có handler | Gửi OTP công khai; xác minh email được phép; backend auth chưa có | Đang gửi; OTP sai/hết hạn; gửi lại; lỗi; xác minh thành công | Form đăng nhập chưa có |
| Dashboard thủ thư (chưa tách thành màn; SRS yêu cầu) | Target: `GET /api/v1/dashboard/summary`; chưa có handler. Contract hiện mới mô tả tổng occupancy/booking, chưa chốt utilization/no-show theo cơ sở | Thủ thư/quản lý theo SRS; Backend hiện chưa có kiểm soát quyền được xác nhận | Đang tải; lỗi/401; thiếu dữ liệu; trạng thái stale; chỉ hiển thị metric có trong response | `DashboardChart`, `OccupancyBadge`, `StaleWarning` (mục tiêu, chưa có) |

## API đã có và giới hạn

| Method + path | Trạng thái đã kiểm tra | Response/giới hạn liên quan |
|---|---|---|
| `GET /api/v1/health` | Có handler | Health check |
| `GET /api/v1/occupancy/current` | Có handler | `{current_count, updated_at, location}`; tổng occupancy mới nhất của mỗi phòng hoạt động; hiện không lọc campus |
| `GET /api/v1/occupancy/rooms/{room_id}/latest` | Có handler | Occupancy live một phòng, gồm `estimated_occupancy`, `recorded_at`, `received_at`, `is_stale`; trả lỗi nếu không tìm thấy phòng/dữ liệu |
| `GET /api/v1/rooms`, `GET /api/v1/rooms/{room_id}` | API contract mục tiêu; router hiện chưa định nghĩa handler | Chưa dùng được từ frontend |
| `GET /api/v1/occupancy/rooms/{room_id}/latest` | Có legacy handler; runtime missing-data response khác target. Target dùng occupancy từ event/N0, `device_status`, `occupancy_status` và phân biệt `404 room_not_found` với `503 occupancy_unavailable` | Cần SEAT-54/56/57 và contract update |
| `GET /api/v1/rooms/{room_id}/occupancy/history` | API contract mục tiêu; chưa có response/handler runtime | Chưa dùng được từ frontend |
| Bookings, check-in, OTP/auth, dashboard analytics | API contract đề xuất; router/handler chưa hoàn chỉnh | Không giả định đã tích hợp |

Không thêm `campus_code=CS1`/`CS3` vào `GET /occupancy/current` để trình bày dữ liệu
như đã lọc: schema hiện tại chưa ánh xạ phòng với cơ sở. Khi lọc cơ sở được
triển khai, cần cập nhật contract và test cùng Backend.

## Chuẩn cấu trúc frontend

Đây là quy ước cho phần triển khai tiếp theo; không mô tả thành phần chưa tồn tại
như thể đã chạy:

- Tên component React viết PascalCase: `RoomCard`, `OccupancyBadge`,
  `StaleWarning`, `BookingForm`, `TimeSlotPicker`, `QRCodeView`,
  `DashboardChart`.
- Custom hook bắt đầu bằng `use`; ví dụ `useOccupancy`.
- API client/service chung phụ trách base URL, JSON, access token và chuẩn hóa
  lỗi. Với 401: xóa token phiên rồi chuyển tới màn đăng nhập; Backend hiện chưa
  có auth contract.
- Mock đặt tại `frontend/mocks/` theo backlog SEAT-62, bật/tắt bằng cấu hình môi trường tách
  khỏi service gọi mạng. Fixture phải khớp API Contract hoặc contract đã được
  thống nhất; route mock chưa khai báo phải báo lỗi rõ ràng, không trả response
  thành công giả.

## Khoảng trống so với tiêu chí hoàn thành

Trong workspace hiện tại chỉ dashboard occupancy có request thật. `RoomsPage`,
`ReservationPage` và `CheckinPage` là placeholder; chưa có mock, token handler
chung, luồng 401 về đăng nhập hoặc các component dùng chung nêu trên. Do vậy
tiêu chí “mọi màn có API tương ứng; mock chạy được khi backend chưa sẵn sàng”
chưa đạt. README frontend ghi nhận trạng thái này; cần thống nhất contract còn
thiếu với Backend trước khi đánh dấu hoàn thành tích hợp.


