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

Cần Node.js và npm. Chuẩn bị địa chỉ API của Backend để giao diện lấy dữ liệu.
Mở terminal tại `frontend/` và chạy:

```sh
npm ci
npm run dev -- --port 3000
```

Mở <http://localhost:3000> để xem giao diện.

## Quản lý model, video và dữ liệu nhạy cảm

- Không đưa model hoặc video camera vào giao diện; sử dụng số liệu do Backend trả về.
- Dùng dữ liệu giả và ảnh minh họa được phép sử dụng khi thiết kế, kiểm thử.
- Không đặt mật khẩu hay token bí mật trong mã giao diện, `public/` hoặc biến
  `VITE_*`, vì người dùng có thể xem được chúng trên trình duyệt.
- Không chia sẻ ảnh chụp chứa mã sinh viên, thông tin đặt phòng hoặc QR thật.
- Không đưa thư viện đã cài (`node_modules/`) và bản build (`dist/`) lên Git.
