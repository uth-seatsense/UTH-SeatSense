# Kết quả kiểm thử SEAT-17 giai đoạn 2

Ngày 30/10/2026, CPU, môi trường và model như báo cáo giai đoạn 1.

## Kiểm thử tự động

14 kiểm thử unittest đạt, gồm:

- Qua line hai chiều, cooldown, đảo chiều IN, rung trong deadband.
- Đi qua phần kéo dài ngoài đoạn thẳng không được tính.
- ID mất dấu quá hạn, ID mới và bbox chưa có ID không tạo lượt giả.
- Cấu hình line sai bị từ chối.
- Schema từ chối số âm, tracked_count lớn hơn people_count, NaN,
  thời gian thiếu múi giờ, camera rỗng, trường lạ và counters không nhất quán.
- Ước tính âm được clamp và phải có cờ underflow.
- Pipeline video với quỹ đạo giả lập tạo đúng IN ở 500 ms, OUT ở 1500 ms,
  event_id riêng và ước tính cuối phiên đúng. Test này kiểm tra điều phối,
  không đánh giá độ chính xác detector.
- Pipeline model thật vẫn đạt kiểm tra bbox/ID, số 0, CSV, MP4 và hai phiên
  độc lập; bản ghi Backend và events được validate bằng schema.

## Chạy video mẫu thật

Video people-walking.mp4, line (0.5,0) → (0.5,1), IN âm sang dương,
initial_occupancy=0, confidence=0.32:

- Xử lý 50 frame, nguồn 10 FPS, số người hiện thấy cao nhất 6.
- Xuất 50 bản ghi backend_counts.jsonl, CSV và dữ liệu debug.
- Ghi nhận 0 IN, 1 OUT; event ở frame 27, timestamp_ms=2700.
- estimated_occupancy=0, occupancy_underflow=true đúng quy tắc cấu hình.
- Video chú thích đọc được, có đường kẻ và bộ đếm.

Đường kẻ chỉ để kiểm tra chức năng, video không phải camera cửa thư viện.
Chưa có ground truth nên chưa công bố độ chính xác IN/OUT. Các giới hạn
FPS cố định, ID switch, che khuất và Docker/GPU chưa kiểm chứng vẫn còn.
Không triển khai truyền HTTP, PostgreSQL hoặc giao diện ở giai đoạn này.
Link tải model được ghi trong `cv/README.md`.
