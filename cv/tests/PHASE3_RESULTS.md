# Kết quả kiểm thử SEAT-17 giai đoạn 3
Hoàn tất
## Xác minh

- 18 bài kiểm thử Python đạt, gồm bộ kiểm thử giai đoạn 2 và API giao diện.
- Kiểm thử webcam bằng JPEG từ video mẫu và model thật: 2 frame có người,
  source_type webcam, trạng thái tracking trong phiên, stop lặp an toàn,
  frame sau stop bị từ chối và xuất được 2 bản ghi JSONL. Không mở camera vật lý.
- Upload video mẫu với model thật chạy đủ 50 frame. Snapshot có JPEG và
  record tương ứng, xuất được CSV, JSONL số đếm/debug/sự kiện và summary.
- Xác minh dừng phiên, trạng thái cancelled, chặn video thứ hai khi đang chạy,
  chặn tải kết quả chưa hoàn tất, trả 404 cho phiên/file không hợp lệ.
- Model thiếu, cấu hình sai, định dạng file không hỗ trợ được trả lỗi rõ.
- Chặn POST từ Origin khác; summary HTTP không chứa output_dir cục bộ.
- Video upload được xóa sau xử lý hoặc dừng.
- 4 bài kiểm thử Node.js đạt: đếm tay tại frame đang thấy, mẫu số 0,
  hiển thị số 0 và null đúng, cảnh báo underflow và tải kết quả phiên dừng.
- 4 bài kiểm thử jsdom trên chính HTML mẫu đạt: script khởi tạo được,
  chọn webcam/khóa RTSP, thiếu camera được báo lỗi, snapshot/so sánh cần
  frame thật, render số đếm và so sánh đếm tay trên bố cục mẫu.

## Giới hạn xác minh

Chưa có trình duyệt khả dụng trong môi trường công cụ để kiểm tra trực quan
desktop/mobile hoặc thao tác bằng chuột. Kiểm thử JavaScript dùng DOM giả lập,
không thay thế kiểm tra layout trên trình duyệt. Cần mở ứng dụng local theo
README để kiểm tra bố cục trên thiết bị người dùng.

Chưa kiểm chứng camera vật lý, Docker/GPU, RTSP, PostgreSQL hoặc Backend hệ thống.
Chỉ giữ frame mới nhất và 100 sự kiện gần nhất trong UI; file kết quả lưu
toàn bộ các frame/sự kiện. Tạm dừng xem không tạm dừng xử lý. FPS là nghịch
đảo thời gian detector + tracker, không phải tốc độ tổng pipeline.
Phiên dừng có thể không có frame nếu dừng trong lúc model đang tải.
