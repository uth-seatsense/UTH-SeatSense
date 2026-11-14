# Frontend — UTH-SeatSense

Frontend React/Vite cung cấp giao diện để xem tình trạng chỗ ngồi, đặt phòng
học nhóm và check-in; dashboard thủ thư là một luồng nghiệp vụ trong SRS.
Bảng ánh xạ màn hình, API, quyền và trạng thái xem
[tại đây](../docs/ui/screen-api-mapping.md).

## Cấu trúc hiện tại

```text
frontend/src/
├── App.jsx
├── main.jsx
├── assets/
│   └── .gitkeep
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
├── mocks/          
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
│   └── api.js
├── styles/
│   └── main.css
└── tests/
    ├── App.test.jsx
    ├── DashboardStatus.test.jsx
    ├── Health.test.js
    └── Routes.test.jsx
```

`main.jsx` khởi tạo `BrowserRouter`; `App.jsx` định nghĩa các route:
`/`, `/login`, `/rooms`, `/reservation`, `/my-bookings`, `/checkin`,
`/dashboard`, `/health` và trang 404.
Home dùng trực tiếp Dashboard, không thêm header trùng phía sau sidebar.
`RoomsPage`, `ReservationPage`, `CheckinPage`, `LoginPage` và `MyBookingsPage`
là placeholder; chưa triển khai nghiệp vụ.

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
Image dùng `npm ci` và chạy Vite dev server cho skeleton, không phải cấu hình
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

`src/services/api.js` hiện có `getApiHealth()` và `getCurrentOccupancy()`.
Dashboard gọi `GET /api/v1/occupancy/current`, làm mới mỗi 30 giây, chấp nhận
số nguyên không âm trong `current_count`, `people_count`, `occupancy_count`
hoặc `count`. Số 0 hợp lệ; trường count null/thiếu được hiển thị như chưa có
dữ liệu. Lỗi HTTP, mạng hoặc JSON sai được hiển thị thành lỗi.

Backend hiện trả tổng số người trong các phòng hoạt động, không nhận lọc cơ sở.
Endpoint `GET /api/v1/occupancy/rooms/{room_id}/latest` có `is_stale`, nhưng
Dashboard hiện chưa gọi endpoint này. Xem [API Contract](../docs/architecture/api-contracts.md)
và [bảng ánh xạ màn hình](../docs/ui/screen-api-mapping.md) để biết các route
đã có, route mới chỉ được mô tả và route nghiệp vụ còn cần thống nhất.

## Mock và service layer — trạng thái

Thư mục `src/mocks/` hiện còn rỗng. Chưa có mock API client, fixture, xử lý token chung hoặc điều
hướng về đăng nhập khi gặp HTTP 401. Frontend vì vậy chưa thể chạy các luồng
phòng/đặt chỗ/check-in khi Backend chưa sẵn sàng; các màn này vẫn là placeholder.
Không có biến `VITE_USE_MOCK_API` được hỗ trợ hiện tại.

Khi triển khai lớp services, dùng một API client chung cho base URL, JSON,
token và lỗi HTTP; xử lý 401 bằng xóa token phiên và điều hướng tới đăng nhập.
Mock nên bật/tắt bằng biến môi trường (ví dụ `VITE_USE_MOCK_API`) và trả đúng
shape API Contract; chỉ bật mock khi có fixture/route tương ứng, không thay lỗi
thật bằng response thành công giả.

Không đặt mật khẩu/token bí mật trong mã nguồn hoặc biến `VITE_*`; các biến này
được đóng gói công khai phía trình duyệt. Không đưa dữ liệu cá nhân hoặc QR
thật vào fixture.

## Kiểm tra

```sh
npm test
npm run lint
npm run format:check
npm run build
```

`npm run format` định dạng JS/JSX; Dashboard kế thừa được loại tạm khỏi
Prettier để giữ nguyên code ngoài phạm vi task. ESLint vẫn kiểm tra Dashboard;
các cảnh báo props hiện có không chặn build.
Test route dùng `StaticRouter` trong môi trường Node, còn trình duyệt dùng
`BrowserRouter`. Khi nghiệm thu, kiểm tra mở trực tiếp/reload từng route,
navigation ở desktop/mobile và trang Home không bị sidebar che chữ.
