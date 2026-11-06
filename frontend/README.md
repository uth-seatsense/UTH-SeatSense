# Frontend — Giao diện web

## Mục đích và trách nhiệm

Frontend cung cấp giao diện cho sinh viên xem chỗ trống, đặt phòng học nhóm
và check-in bằng QR. Thủ thư sử dụng giao diện để theo dõi tình trạng phòng
và xem thống kê. Web cần dễ sử dụng trên cả máy tính và điện thoại.

Dữ liệu được lấy qua API của Backend. Frontend phụ trách hiển thị thông tin,
nhận thao tác của người dùng và thông báo kết quả.

## Cấu trúc thư mục dự kiến

```text
frontend/
├── public/          # Tài nguyên công khai
├── src/
│   ├── main.jsx     # Khởi động giao diện
│   ├── App.jsx      # Thành phần giao diện chính
│   ├── pages/       # Các trang chức năng
│   ├── components/  # Các phần giao diện dùng lại
│   ├── routes/      # Điều hướng giữa các trang
│   ├── hooks/       # Xử lý giao diện dùng chung
│   ├── services/    # Gọi API Backend
│   ├── assets/      # Ảnh và biểu tượng
│   ├── styles/      # Định dạng giao diện
│   └── tests/       # Kiểm thử Frontend
└── package.json     # Thư viện và lệnh chạy
```

## Chuẩn bị và chạy

Cần Node.js và npm. Vite chạy tại <http://localhost:3000> khi dùng Docker
Compose; chạy riêng thường dùng cổng `5173`. Mở terminal tại `frontend/` và
chạy:

```sh
npm ci
npm run dev -- --port 3000
```

Vite proxy các yêu cầu `/api` tới `http://localhost:8000`; đổi địa chỉ backend
bằng biến `VITE_BACKEND_PROXY_TARGET` nếu cần.

## API số người hiện tại

Frontend gọi `GET /api/v1/occupancy/current` và tự làm mới mỗi 30 giây. Có thể
ghi đè URL bằng `VITE_OCCUPANCY_API_URL` trong file `.env.local` của frontend.
URL mặc định cũng có thể thay đổi bằng `VITE_API_BASE_URL` (mặc định
`/api/v1`).

Phản hồi thành công cần có số người nguyên không âm trong một trong các trường
`current_count`, `people_count`, `occupancy_count` hoặc `count`. Các trường
`updated_at` và `location` là tùy chọn. Giá trị đếm bằng `0` là hợp lệ; phản hồi
rỗng sẽ hiện thông báo chưa có dữ liệu. Lỗi HTTP, lỗi mạng hoặc JSON không hợp
lệ sẽ hiện thông báo lỗi. Không có dữ liệu mẫu được dùng thay cho phản hồi API.

Endpoint tổng hợp bản ghi mới nhất của mỗi phòng đang hoạt động từ bảng
`occupancy_records`. Hiện tại API trả tổng số toàn hệ thống; schema phòng chưa
có mã cơ sở để lọc riêng CS1/CS3. Dữ liệu chỉ xuất hiện khi CV hoặc nguồn ghi
nhận khác lưu bản ghi occupancy vào database.

## Quản lý model, video và dữ liệu nhạy cảm

- Không đưa model hoặc video camera vào giao diện; sử dụng số liệu do Backend trả về.
- Dùng dữ liệu giả và ảnh minh họa được phép sử dụng khi thiết kế, kiểm thử.
- Không đặt mật khẩu hay token bí mật trong mã giao diện, `public/` hoặc biến
  `VITE_*`, vì người dùng có thể xem được chúng trên trình duyệt.
- Không chia sẻ ảnh chụp chứa mã sinh viên, thông tin đặt phòng hoặc QR thật.
- Không đưa thư viện đã cài (`node_modules/`) và bản build (`dist/`) lên Git.

## Kiểm tra

```sh
npm test
npm run build
```
