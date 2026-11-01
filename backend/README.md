# Backend — API và xử lý nghiệp vụ

## Mục đích và trách nhiệm

Backend kết nối giao diện web, thiết bị đếm người và cơ sở dữ liệu. Module này
phụ trách quản lý phòng, xử lý đặt phòng, kiểm tra trùng lịch, check-in và tự
nhả phòng khi quá hạn. Backend cũng nhận số liệu từ cảm biến hoặc CV để cung
cấp tình trạng chỗ trống và thống kê cho thủ thư.

## Cấu trúc thư mục dự kiến

```text
backend/
├── main.py          # Khởi động ứng dụng
├── app/
│   ├── api/         # Các API của hệ thống
│   ├── core/        # Cấu hình chung và bảo mật
│   ├── db/          # Kết nối cơ sở dữ liệu
│   ├── models/      # Mô tả các bảng dữ liệu
│   ├── schemas/     # Định dạng dữ liệu gửi và nhận
│   ├── repositories/ # Đọc, ghi dữ liệu
│   ├── services/    # Xử lý nghiệp vụ
│   └── utils/       # Các hàm hỗ trợ
├── migrations/      # Các bước cập nhật cấu trúc dữ liệu
└── tests/           # Kiểm thử Backend
```

## Chuẩn bị trước khi chạy

Cần môi trường Python, các thư viện trong `requirements.txt` và cơ sở dữ liệu
được cấu hình phù hợp. Dùng `.env.example` làm mẫu để chuẩn bị `.env`, giữ
thông tin tài khoản và địa chỉ kết nối cơ sở dữ liệu khớp nhau. Khi tích hợp,
thống nhất cách trao đổi dữ liệu với Frontend, CV và thiết bị cảm biến.

Có thể khởi động bằng Docker Compose từ thư mục gốc dự án:

```sh
docker compose up --build -d backend
```

## Quản lý thông tin nhạy cảm
- Backend chỉ nhận số liệu tổng hợp từ CV, không lưu model hay video camera.
- Giữ mật khẩu, token và cấu hình riêng trong biến môi trường hoặc `.env`;
  không đưa thông tin thật lên Git.
- Chỉ thu thập thông tin cần thiết cho việc đặt phòng và giới hạn người
  được phép truy cập.
- Dùng dữ liệu giả khi phát triển và kiểm thử. Không ghi thông tin cá nhân,
  mật khẩu hoặc mã QR còn hiệu lực vào log và tài liệu chia sẻ.
