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
    └── DashboardStatus.test.jsx
```

`App.jsx` hiện render `HomePage`; `RoomsPage`, `ReservationPage` và
`CheckinPage` là placeholder.

Quy ước khi bổ sung: component React viết PascalCase (ví dụ `RoomCard.jsx`);
custom hook bắt đầu bằng `use` (ví dụ `useOccupancy.js`). Component dùng chung
được yêu cầu cho các màn gồm `RoomCard`, `OccupancyBadge`, `StaleWarning`,
`BookingForm`, `TimeSlotPicker`, `QRCodeView` và `DashboardChart`; các component
này chưa được triển khai.

## Cài đặt và chạy

Cần Node.js và npm. Tại thư mục `frontend/`:

```sh
npm ci
npm run dev -- --port 3000
```

Vite proxy `/api` tới `http://localhost:8000`; đổi địa chỉ bằng
`VITE_BACKEND_PROXY_TARGET`. API base mặc định là `/api/v1` và có thể đổi bằng
`VITE_API_BASE_URL`.

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
npm run build
```
