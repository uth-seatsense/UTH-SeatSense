# Kết quả kiểm thử SEAT-17 giai đoạn 1
Hoàn tất
## Môi trường và dữ liệu

- Chạy CPU trong môi trường Python ảo.
- Ultralytics 8.4.191, Torch 2.11.0, Torchvision 0.26.0.
- OpenCV 4.14.0.94, NumPy 2.5.4, lap 0.5.13.
- Model: checkpoint YOLOv8n `best.pt`, lưu cục bộ ngoài Git.
- Video: `people-walking.mp4`, confidence 0.32, image size 640.

## Kết quả

- CLI xử lý đủ 50 frame, FPS nguồn 10, số người đồng thời cao nhất 6.
- Tạo JSONL, CSV, MP4 có chú thích và summary thành công.
- `unittest`: 4 test đạt, có inference bằng model thật.
- Kiểm thử ghép 16 frame mẫu + 4 frame đen xác nhận: có người được phát
  hiện và gán ID; frame đen xuất 0; 20 dòng kết quả mỗi phiên; thời gian
  từ 0 đến 1900 ms; CSV khớp JSONL; MP4 đọc lại đủ 20 frame.
- Hai lần xử lý có session ID riêng và số đếm theo frame khớp nhau.
- Thiếu model/video và video không hợp lệ được báo lỗi.

## Giới hạn

Chưa có ground truth trên camera thư viện nên chưa kết luận độ chính xác.
Chưa kiểm chứng GPU, Docker build hoặc cài mới trong môi trường sạch.
Pipeline xử lý tuần tự mọi frame giải mã được, không cam kết realtime.
Thời gian video tính theo FPS cố định; chưa hỗ trợ timestamp chính xác cho
video variable frame rate. Video hỏng giữa chừng có thể bị OpenCV coi là EOF.
Không có đếm IN/OUT, lưu PostgreSQL hoặc kết nối Backend trong giai đoạn này.
File kết quả có bbox và video chú thích chỉ giữ cục bộ trong thư mục đã ignore.
