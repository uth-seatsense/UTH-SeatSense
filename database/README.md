# Database — Cơ sở dữ liệu

## Mục đích và trách nhiệm

Module Database lưu cấu trúc cơ sở dữ liệu và dữ liệu mẫu của dự án.
Các nhóm dữ liệu chính gồm thông tin phòng, lịch đặt phòng và số người sử
dụng phòng theo thời gian. Backend đọc, ghi dữ liệu để phục vụ các chức năng
trên web và thống kê sử dụng phòng.

## Cấu trúc thư mục dự kiến

```text
database/
├── init/            # Các file SQL tạo bảng ban đầu
├── seeds/           # Dữ liệu mẫu để phát triển và kiểm thử
└── README.md
```

Các bước thay đổi cấu trúc cơ sở dữ liệu được quản lý cùng Backend trong
`backend/migrations/` để các thành viên dễ cập nhật thống nhất.
## Chuẩn bị và chạy

Cần PostgreSQL hoặc Docker Desktop có Docker Compose. Dùng `.env.example`
làm mẫu để chuẩn bị `.env`, sau đó kiểm tra tên cơ sở dữ liệu, tài khoản,
mật khẩu và thông tin kết nối dùng chung với Backend.

Để khởi động bằng Docker Compose, chạy tại thư mục gốc dự án:

```sh
docker compose up -d db
```

Các file trong `init/` dùng để tạo cơ sở dữ liệu ban đầu. Dữ liệu trong
`seeds/` được nạp riêng khi cần thử nghiệm. Khi đổi cấu trúc bảng, nhóm cần
thống nhất cách cập nhật và sao lưu dữ liệu cần giữ.

## Quản lý model, video và dữ liệu nhạy cảm

- Chỉ lưu số liệu tổng hợp và thông tin đặt phòng cần thiết; không lưu model,
  video hay ảnh camera trong cơ sở dữ liệu.
- Dữ liệu mẫu phải là dữ liệu giả, không chứa thông tin sinh viên thật.
- Không đưa mật khẩu, `.env` hay bản sao cơ sở dữ liệu thật lên Git.
- Giới hạn quyền truy cập dữ liệu thật, lưu bản sao ở nơi riêng và thống nhất
  thời hạn giữ hoặc xóa sau khi kết thúc dự án.
