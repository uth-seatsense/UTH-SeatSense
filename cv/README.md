# CV — Đếm người bằng camera

## Mục đích và trách nhiệm

Module CV phụ trách xử lý hình ảnh để đếm số người vào và ra khỏi phòng đọc.
Hướng triển khai là dùng YOLO để phát hiện người và theo dõi chuyển động qua
cửa. Số liệu được gửi cho Backend để cập nhật tình trạng chỗ trống, đồng thời
dùng để so sánh với phương án cảm biến và kết quả đếm tay.

## Cấu trúc thư mục dự kiến

```text
cv/
├── main.py          # Khởi động dịch vụ
├── config/          # Cấu hình xử lý hình ảnh
├── app/
│   ├── api/         # API của dịch vụ
│   ├── detection/   # Phát hiện và theo dõi người
│   ├── counting/    # Đếm lượt vào/ra
│   ├── services/    # Điều phối xử lý video
│   ├── schemas/     # Định dạng kết quả
│   └── utils/       # Các hàm hỗ trợ
├── models/          # Model dùng để nhận diện người
├── videos/          # Video thử nghiệm
└── tests/           # Kiểm thử phần CV
```

## Chuẩn bị trước khi chạy

Cần môi trường Python và các thư viện trong `requirements.txt`. Chuẩn bị
model phù hợp, camera hoặc video được phép sử dụng và cấu hình khu vực đếm.
Khi kết nối với hệ thống, thống nhất định dạng số liệu gửi sang Backend.

Có thể khởi động dịch vụ bằng Docker Compose từ thư mục gốc dự án:

```sh
docker compose up --build -d cv
```

## Quản lý model, video và dữ liệu nhạy cảm

- Lưu model trong `models/`, video thử nghiệm trong `videos/`; không đưa các
  file này lên Git. Ghi lại nguồn và phiên bản model để nhóm dễ dùng chung.
- Chỉ quay và dùng video khi được cho phép. Camera tại thư viện cần có sự
  đồng ý và biển thông báo.
- Xử lý hình ảnh tại chỗ, không nhận diện khuôn mặt và chỉ gửi số đếm lên server.
- Không lưu video khi chạy trực tiếp. Video đánh giá chỉ lưu tạm trong nhóm
  và xóa sau khi sử dụng xong.
- Không đưa ảnh người dùng, mật khẩu hay thông tin đăng nhập camera vào mã
  nguồn, log hoặc tài liệu chia sẻ.
