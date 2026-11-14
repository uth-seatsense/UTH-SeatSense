# Ánh xạ màn hình ↔ API

Tài liệu này đối chiếu giao diện hiện có với API Contract và các yêu cầu trong
SRS. API base path là `/api/v1`. “Đã có” chỉ các handler Backend thực thi được;
“Contract/chưa triển khai” nghĩa là shape/endpoint được mô tả nhưng chưa có
handler; “đề xuất” là path cần thống nhất với Backend, không phải API đang chạy.

## Màn hình và luồng dữ liệu

| Màn hình | API gọi | Quyền | Trạng thái cần xử lý | Component dùng |
|---|---|---|---|---|
| Tổng quan sinh viên (`HomePage` → `DashboardPage`, hiện có) | `GET /api/v1/occupancy/current` — đã có; tổng số toàn hệ thống, chưa lọc cơ sở | Công khai xem; Backend hiện không gắn quyền cho endpoint | Đang tải; lỗi HTTP/mạng/JSON; chưa có dữ liệu (`current_count` null/thiếu); số 0 hợp lệ; đang làm mới mỗi 30 giây. Endpoint này không có `is_stale` | Hiện: `MetricCard`, `AreaRow` và `Icon` nội bộ. Dự kiến: `OccupancyBadge`, `StaleWarning`, `DashboardChart` |
| Danh sách phòng/khu tự học (`RoomsPage`, hiện placeholder) | `GET /api/v1/rooms?campus=...` — có trong API Contract, handler chưa triển khai; lấy số mới nhất qua `GET /api/v1/occupancy/rooms/{room_id}/latest` — đã có | Công khai xem phòng và mật độ; không có middleware phân quyền hiện tại | Đang tải; lỗi; danh sách rỗng; phòng không có occupancy (404); số đếm null khác 0; `is_stale`; phòng đóng/bảo trì | `RoomCard`, `OccupancyBadge`, `StaleWarning` (đều là component mục tiêu, chưa có) |
| Chi tiết phòng/mật độ | `GET /api/v1/rooms/{room_id}` — có trong contract, handler chưa triển khai; `GET /api/v1/rooms/{room_id}/occupancy/history` — mới có mô tả contract, chưa có handler; latest qua `/occupancy/rooms/{room_id}/latest` | Công khai xem; chưa có phân quyền endpoint | Đang tải; 404 phòng/dữ liệu; lỗi; dữ liệu cũ theo `is_stale`; chưa có dữ liệu | `OccupancyBadge`, `StaleWarning`, `DashboardChart` (mục tiêu, chưa có) |
| Đặt phòng học nhóm và lịch của tôi (`ReservationPage`, hiện placeholder) | Đề xuất: `GET /api/v1/rooms?room_type=topic_room`, `GET /api/v1/reservations/mine`, `POST /api/v1/reservations`, `DELETE /api/v1/reservations/{booking_id}`. Chưa có contract wire/handler | Sinh viên đăng nhập; chủ lượt đặt được hủy theo SRS; Backend chưa thực thi | Đang tải; không có phòng/lịch; xung đột hoặc giờ không hợp lệ; phòng hết chỗ; thành công/thất bại; phiên hết hạn | `BookingForm`, `TimeSlotPicker`, `QRCodeView` (mục tiêu, chưa có) |
| Check-in QR (`CheckinPage`, hiện placeholder) | Đề xuất: `POST /api/v1/checkin`. Router tồn tại nhưng chưa có handler hoặc request/response contract | Sinh viên có lượt đặt hợp lệ; Backend chưa thực thi quyền | Đang gửi; QR sai/hết hạn/đã dùng; ngoài thời gian check-in; mạng/API lỗi; 401; thành công | `QRCodeView` và form check-in (chưa có component) |
| Đăng nhập OTP (chưa có màn hình) | SRS yêu cầu OTP email; path chưa được quy định. Đề xuất cần thỏa thuận: gửi OTP, xác minh OTP, đăng xuất | Gửi OTP công khai; xác minh yêu cầu email được phép; chưa có endpoint/backend auth | Đang gửi; OTP sai/hết hạn; gửi lại; lỗi; xác minh thành công | Form đăng nhập (chưa có component) |
| Dashboard thủ thư (chưa tách thành màn; SRS yêu cầu) | `GET /api/v1/occupancy/current` chỉ cung cấp tổng hiện có. API thống kê theo cơ sở, tỷ lệ sử dụng/no-show chưa được định nghĩa; cần contract riêng | Thủ thư/quản lý theo SRS; Backend hiện chưa có kiểm soát quyền được xác nhận | Đang tải; lỗi/401; không có dữ liệu; dữ liệu cũ; thống kê tổng và theo cơ sở | `DashboardChart`, `OccupancyBadge`, `StaleWarning` (mục tiêu, chưa có) |

## API đã có và giới hạn

| Method + path | Trạng thái đã kiểm tra | Response/giới hạn liên quan |
|---|---|---|
| `GET /api/v1/health` | Có handler | Health check |
| `GET /api/v1/occupancy/current` | Có handler | `{current_count, updated_at, location}`; tổng occupancy mới nhất của mỗi phòng hoạt động; hiện không lọc campus |
| `GET /api/v1/occupancy/rooms/{room_id}/latest` | Có handler | Occupancy live một phòng, gồm `estimated_occupancy`, `recorded_at`, `received_at`, `is_stale`; trả lỗi nếu không tìm thấy phòng/dữ liệu |
| `GET /api/v1/rooms`, `GET /api/v1/rooms/{room_id}` | API Contract có response mẫu; router hiện chưa định nghĩa handler | Chưa dùng được từ frontend |
| `GET /api/v1/rooms/{room_id}/occupancy/history` | Chỉ có tiêu đề mô tả trong API Contract | Chưa có schema response/handler |
| Reservations, check-in, OTP/auth, dashboard analytics | Chưa có wire contract; một số router đã include nhưng không có handler | Cần Backend thống nhất path, payload, lỗi và quyền trước khi tích hợp |

Không thêm `campus=CS1`/`CS3` vào `GET /occupancy/current` để trình bày dữ liệu
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
- Mock đặt trong `frontend/src/mocks/`, bật/tắt bằng cấu hình môi trường tách
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


