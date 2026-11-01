# Tests — Kiểm thử hệ thống

## Mục đích và trách nhiệm

Thư mục Tests dùng để kiểm tra các phần của hệ thống có phối hợp đúng với
nhau hay không. Các tình huống gồm cập nhật số chỗ trống, đặt phòng, check-in
và xem thống kê. Mỗi thành viên kiểm tra phần mình phụ trách và cùng nhóm
kiểm tra những luồng sử dụng liên quan.

## Cấu trúc thư mục dự kiến

```text
tests/
├── integration/     # Kiểm tra kết nối và trao đổi dữ liệu giữa các module
├── e2e/             # Kiểm tra các bước sử dụng hoàn chỉnh trên web
└── README.md
```

Các bài kiểm tra riêng từng module đặt tại `backend/tests/`, `cv/tests/`
và `frontend/src/tests/` để dễ quản lý cùng mã nguồn.

## Chuẩn bị trước khi chạy

Cài môi trường và thư viện theo module cần kiểm tra: Python cho Backend/CV,
Node.js và npm cho Frontend. Với bài kiểm tra liên module, khởi động các dịch
vụ liên quan và dùng cơ sở dữ liệu thử nghiệm riêng.

Chuẩn bị dữ liệu đầu vào, các bước thực hiện và kết quả mong đợi cho từng
trường hợp. Ghi lại cách chạy và kết quả thực tế để các thành viên có thể
kiểm tra lại trên cùng điều kiện.

## Quản lý model, video và dữ liệu nhạy cảm

- Dùng thông tin sinh viên, lịch đặt phòng và QR giả để kiểm thử.
- Model và video thử nghiệm để ở `cv/models/`, `cv/videos/`, không chép vào
  thư mục test hoặc đưa lên Git. Chỉ dùng video được phép và xóa sau khi đánh giá.
- Không dùng cơ sở dữ liệu thật cho các bài kiểm tra có thao tác xóa hoặc đặt lại dữ liệu.
- Che thông tin cá nhân, mật khẩu, token và QR thật trong ảnh chụp, log và báo cáo lỗi.
