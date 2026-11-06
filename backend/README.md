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

## Khởi động toàn bộ project và cổng sử dụng

Chạy các lệnh bên dưới trong PowerShell từ thư mục gốc `UTH-SeatSense` (cùng cấp với `docker-compose.yml`). Cần mở Docker Desktop trước.

1. Tạo file cấu hình `.env` từ mẫu nếu project chưa có file này, sau đó đặt mật khẩu PostgreSQL dùng riêng cho máy phát triển:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Khởi động PostgreSQL và dịch vụ CV trước. Nếu dùng nhận diện video, đặt model tại `cv/models/best.pt` trên máy; Compose sẽ mount file đó vào container CV.

   ```powershell
   docker compose up -d --build db cv
   docker compose ps
   ```

   Chờ `db` và `cv` báo `healthy` trước khi tiếp tục.

3. Khởi động Backend. Compose sẽ đợi PostgreSQL và CV khỏe mạnh trước khi chạy API.

   ```powershell
   docker compose up -d --build backend
   ```

4. Khởi động Frontend sau khi Backend báo `healthy`.

   ```powershell
   docker compose up -d --build frontend
   docker compose ps
   ```

Có thể khởi động tất cả dịch vụ theo thứ tự phụ thuộc đã cấu hình sẵn bằng một lệnh:

```powershell
docker compose up -d --build
```

| Thứ tự | Dịch vụ | Cổng trên máy | Địa chỉ |
|---|---|---:|---|
| 1 | PostgreSQL | `5432` | Kết nối DB, không mở bằng trình duyệt |
| 2 | CV/AI | `8001` | <http://localhost:8001> và <http://localhost:8001/docs> |
| 3 | Backend API | `8000` | <http://localhost:8000/docs> |
| 4 | Frontend | `3000` | <http://localhost:3000> |

Các cổng host có thể đổi trong `.env` bằng `POSTGRES_PORT`, `CV_PORT`, `BACKEND_PORT` và `FRONTEND_PORT`. Bên trong mạng Docker, Backend kết nối database ở `db:5432`, CV ở `cv:8001`; Frontend proxy API tới `backend:8000`.

Kiểm tra trạng thái dịch vụ bằng `docker compose ps`; xem log Backend bằng `docker compose logs -f backend`. Dừng project bằng `docker compose down` (không thêm `-v` nếu cần giữ dữ liệu PostgreSQL).

## Quản lý thông tin nhạy cảm
- Backend chỉ nhận số liệu tổng hợp từ CV, không lưu model hay video camera.
- Giữ mật khẩu, token và cấu hình riêng trong biến môi trường hoặc `.env`;
  không đưa thông tin thật lên Git.
- Chỉ thu thập thông tin cần thiết cho việc đặt phòng và giới hạn người
  được phép truy cập.
- Dùng dữ liệu giả khi phát triển và kiểm thử. Không ghi thông tin cá nhân,
  mật khẩu hoặc mã QR còn hiệu lực vào log và tài liệu chia sẻ.

## API số người hiện tại

`GET /api/v1/occupancy/current` trả tổng số người từ bản ghi mới nhất của mỗi
phòng đang hoạt động. Phản hồi gồm `current_count`, `updated_at` và `location`;
hai trường đầu có thể là `null` khi chưa có dữ liệu. Các nghiệp vụ đặt phòng,
check-in và xác thực vẫn đang được phát triển.
