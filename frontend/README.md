# Frontend — UTH-SeatSense

Frontend React/Vite hiện có Dashboard, Health Check và service layer cho một số
API. Các trang đăng nhập, danh sách phòng, đặt phòng, lịch đặt và check-in vẫn
là skeleton/placeholder; dashboard thủ thư là một luồng nghiệp vụ trong SRS.
Bảng ánh xạ màn hình, API, quyền và trạng thái xem
[tại đây](../docs/ui/screen-api-mapping.md).

## Cấu trúc hiện tại

```text
frontend/
├── mocks/
│   ├── occupancy.fresh.json
│   ├── occupancy.offline.json
│   ├── occupancy.stale.json
│   └── rooms.json
└── src/
    ├── App.jsx
    ├── main.jsx
    ├── assets/
    │   └── .gitkeep
    ├── auth/
    │   ├── AuthContext.jsx
    │   └── RequireAuth.jsx
    ├── components/
    │   ├── checkin/
    │   ├── common/
    │   │   └── .gitkeep
    │   ├── dashboard/
    │   │   └── .gitkeep
    │   ├── occupancy/
    │   │   └── .gitkeep
    │   ├── reservations/
    │   │   └── .gitkeep
    │   └── rooms/
    │       └── .gitkeep
    ├── hooks/
    │   └── .gitkeep
    ├── pages/
    │   ├── CheckinPage.jsx
    │   ├── DashboardPage.jsx
    │   ├── HomePage.jsx
    │   ├── HealthPage.jsx
    │   ├── LoginPage.jsx
    │   ├── MyBookingsPage.jsx
    │   ├── ReservationPage.jsx
    │   └── RoomsPage.jsx
    ├── routes/
    │   └── .gitkeep
    ├── services/
    │   ├── api.js
    │   └── checkin.js
    ├── styles/
    │   └── main.css
    └── tests/
        ├── App.test.jsx
        ├── ApiBookings.test.js
        ├── DashboardStatus.test.jsx
        ├── Health.test.js
        └── Routes.test.jsx
```

`main.jsx` khởi tạo `BrowserRouter`; `App.jsx` định nghĩa các route:
`/`, `/login`, `/rooms`, `/reservation`, `/my-bookings`, `/checkin`,
`/dashboard`, `/health` và trang 404.
Home dùng trực tiếp Dashboard, không thêm header trùng phía sau sidebar.
Các luồng đăng nhập OTP, xem phòng/chỗ trống, đặt/hủy booking và check-in QR
gọi chung Backend API với Android. Các trang phòng, booking và check-in yêu cầu
đăng nhập; token Bearer chỉ lưu trong `sessionStorage` của tab hiện tại.
QR được tạo trong trình duyệt; quét camera dùng `BarcodeDetector` khi trình
duyệt hỗ trợ, nếu không có thể dán nội dung QR SeatSense.

Quy ước khi bổ sung: component React viết PascalCase (ví dụ `RoomCard.jsx`);
custom hook bắt đầu bằng `use` (ví dụ `useOccupancy.js`). Component dùng chung
được yêu cầu cho các màn gồm `RoomCard`, `OccupancyBadge`, `StaleWarning`,
`BookingForm`, `TimeSlotPicker`, `QRCodeView` và `DashboardChart`; các component
này chưa được triển khai.

## Cài đặt và chạy

Cần Node.js 22.12+ hoặc 24 LTS và npm. Tại thư mục `frontend/`:

```sh
npm ci
npm run dev -- --port 3000
```

Vite proxy `/api` tới `http://localhost:8000`; đổi địa chỉ bằng
`VITE_BACKEND_PROXY_TARGET`. API base mặc định là `/api/v1` và có thể đổi bằng
`VITE_API_BASE_URL`.

Trên PowerShell nếu `npm.ps1` bị chặn, dùng `npm.cmd` thay cho `npm`.
Đặt `VITE_API_BASE_URL` trong `frontend/.env.local` rồi restart dev server.
Với `VITE_BACKEND_PROXY_TARGET`, truyền qua environment của terminal vì cấu hình
Vite đọc trực tiếp `process.env`.

## Docker — chỉ build frontend (SEAT-50)

Service frontend và các biến môi trường đã có trong Compose.
Từ thư mục gốc, sau khi cấu hình `.env` theo `.env.example`:

```sh
docker compose build frontend
docker compose up --no-build --no-deps -d frontend
```

Hai lệnh này không build hoặc khởi động CV/backend. Mở
`http://localhost:3000` (hoặc cổng `FRONTEND_PORT` đã cấu hình).
Image dùng `npm ci` và chạy Vite dev server cho giao diện phát triển, không phải cấu hình
production.

`VITE_API_BASE_URL` là biến API base của frontend (tương ứng `API_BASE_URL`
trong mô tả task), mặc định `/api/v1`. Compose cấu hình proxy nội bộ bằng
`VITE_BACKEND_PROXY_TARGET=http://backend:8000`. Không đặt hostname Docker
`backend` vào URL gọi trực tiếp từ trình duyệt.

Trang `/health` hiển thị đang kiểm tra, kết nối thành công kèm JSON, hoặc lỗi
thật từ backend; timeout sau 10 giây. Khi chạy riêng frontend và backend chưa
sẵn sàng, trạng thái lỗi là bình thường, không được thay bằng dữ liệu giả.
Để nghiệm thu kết nối thành công, cần backend hoạt động và kiểm tra lại
`/api/v1/health` qua frontend.

## API và trạng thái hiện có

`src/services/api.js` dùng chung base URL, JSON, Bearer token và xử lý lỗi
cho các endpoint `auth/*`, `rooms`, `occupancy/rooms/{id}/latest`,
`bookings` và `check-in`. OTP đăng nhập lấy access token opaque từ Backend;
401 trên endpoint được bảo vệ xóa token phiên và yêu cầu đăng nhập lại.
Dashboard gọi `GET /api/v1/occupancy/current`, làm mới mỗi 30 giây, chấp nhận
số nguyên không âm trong `current_count`, `people_count`, `occupancy_count`
hoặc `count`. Số 0 hợp lệ; trường count null/thiếu được hiển thị như chưa có
dữ liệu. Lỗi HTTP, mạng hoặc JSON sai được hiển thị thành lỗi.

Backend hiện trả tổng số người trong các phòng hoạt động, không nhận lọc cơ sở.
Endpoint `GET /api/v1/occupancy/rooms/{room_id}/latest` được gọi tại trang
phòng và có `is_stale`. Xem [API Contract](../docs/architecture/api-contracts.md)
và [bảng ánh xạ màn hình](../docs/ui/screen-api-mapping.md).

## Mock và service layer

Thư mục `frontend/mocks/` chứa dữ liệu mẫu cho ba trạng thái:

- `occupancy.fresh.json`: Dữ liệu mới (is_stale: false)
- `occupancy.stale.json`: Dữ liệu cũ hơn 30 giây (is_stale: true)
- `occupancy.offline.json`: Mất kết nối camera (device_status: offline)
- `rooms.json`: Danh sách phòng mẫu

### Bật/tắt mock bằng biến môi trường

Mock được bật bằng biến `VITE_USE_MOCK=true`. Khi bật, `getRooms()` và
`getCurrentOccupancy()` dùng fixture trong `frontend/mocks/`; `getApiHealth()`
trả về `{ status: "ok", service: "backend" }` mà không gọi backend. Khi tắt
hoặc không đặt biến này, các hàm trên gọi API thật. Auth, booking, check-in và
occupancy theo từng phòng vẫn dùng Backend API. Sau khi đổi biến, khởi động lại
Vite.

**Bash/Git Bash:**
```sh
VITE_USE_MOCK=true npm run dev
```

**PowerShell:**
```powershell
$env:VITE_USE_MOCK='true'; npm run dev
```

**Command Prompt (cmd.exe):**
```cmd
set VITE_USE_MOCK=true && npm run dev
```

**Cách dễ nhất — đặt trong `frontend/.env.local`:**
```env
VITE_USE_MOCK=true
```

Rồi chạy `npm run dev` bình thường. Để chọn trạng thái occupancy khi đang dùng
mock, có thể đặt thêm `VITE_MOCK_OCCUPANCY_STATE=fresh`, `stale` hoặc `offline`;
mặc định là `fresh`. Với trạng thái `fresh`, API client cập nhật timestamp
theo thời điểm gọi; `stale` và `offline` giữ timestamp cố định của fixture.

### Cấu trúc dữ liệu mock

Mock data khớp API Contract (SEAT-39, SEAT-56):

- Danh sách phòng với campus_id, campus_code, capacity, building, is_active
- Occupancy với room_type, current_count, available_seats, occupancy_level, is_stale, device_status
- Ba trạng thái: dữ liệu mới, cũ, mất kết nối

Không đặt mật khẩu/token bí mật trong mã nguồn hoặc biến `VITE_*`; các biến này
được đóng gói công khai phía trình duyệt. Dữ liệu cá nhân hoặc QR thật không được
đưa vào fixture.

## Kiểm tra

```sh
npm test                  # Chạy test suite
npm run lint              # Kiểm tra ESLint
npm run format:check      # Kiểm tra định dạng Prettier
npm run build             # Build production
```

Vitest chạy trong môi trường `jsdom`; `tests/setup.ts` cấu hình cleanup cho
React Testing Library. `tests/apiClient.mock.test.js` kiểm tra fixture phòng,
ba trạng thái occupancy và mock health; `tests/HealthPage.test.jsx` kiểm tra
trang health. `src/tests/DashboardStatus.test.jsx` kiểm tra trạng thái
occupancy trên Dashboard.

`npm run format` định dạng JS/JSX và sửa file tại chỗ; `npm run format:check`
chỉ kiểm tra định dạng. Dashboard kế thừa được loại tạm khỏi Prettier để giữ
nguyên code ngoài phạm vi task. ESLint vẫn kiểm tra Dashboard; các cảnh báo
props hiện có không chặn build.
Test route dùng `StaticRouter` trong môi trường Node, còn trình duyệt dùng
`BrowserRouter`. Khi nghiệm thu, kiểm tra mở trực tiếp/reload từng route,
navigation ở desktop/mobile và trang Home không bị sidebar che chữ.
