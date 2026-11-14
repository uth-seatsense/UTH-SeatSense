# Kế hoạch kiểm thử responsive

Tài liệu kế hoạch cho SEAT-49. Mục tiêu là kiểm tra các luồng chính trên điện
thoại, máy tính bảng và laptop theo `UI-07`, `NFR-USA-02` và `TC-11` trong
[SRS](requirements/srs.md). Danh sách ca kiểm thử giao diện được tách riêng tại
[ui-test-plan.md](ui-test-plan.md). Tiêu chí nghiệm thu Sprint 4 của SEAT-30 ở
[acceptance-criteria-sprint-4.md](acceptance-criteria-sprint-4.md).

## 1. Ma trận thiết bị, kích thước và trình duyệt

| Viewport CSS | Loại thiết bị / cấu hình kiểm thử | Trình duyệt | Kiểm tra chính |
| --- | --- | --- | --- |
| 360 × 800 | Điện thoại, portrait | Chrome Android; Safari iOS nếu thiết bị hỗ trợ viewport này | Luồng xem phòng, đặt phòng và check-in; không cuộn ngang trang |
| 390 × 844 | Điện thoại, portrait | Safari iOS trên iPhone; Chrome Android | Luồng chính, bàn phím ảo, form và nút thao tác |
| 768 × 1024 | Tablet, portrait | Safari trên iPad; Chrome Android | Điều hướng, danh sách/phòng, form và dialog |
| 1024 × 768 | Tablet, landscape hoặc laptop nhỏ | Edge; Chrome | Đổi hướng/chiều rộng, không chồng nội dung |
| 1440 × 900 | Laptop/desktop | Chrome; Edge | Toàn bộ luồng sinh viên và thủ thư |

Ghi phiên bản hệ điều hành, trình duyệt, thiết bị, viewport CSS, hướng màn hình
và zoom 100% trong kết quả chạy. Dùng bản stable đang cài tại ngày kiểm thử.
Các lỗi cản luồng được kiểm tra lại trên đúng trình duyệt phát sinh và ít nhất
một trình duyệt khác trong ma trận.

## 2. Cách chạy và tiêu chí responsive

- Chạy từng ca trong [ui-test-plan.md](ui-test-plan.md) tại các viewport 360,
  390, 768, 1024 và 1440 px, trên các trình duyệt được chỉ định trong ma trận.
- Ở 360 và 390 px, trang không được có cuộn ngang:
  `scrollWidth <= clientWidth`. Các nút chính không bị che bởi bàn phím, dialog
  hoặc thanh điều hướng.
- Mỗi màn có ít nhất hai ca: hiển thị/thao tác chính và trạng thái lỗi,
  empty hoặc stale.
- Với màn có bảng/biểu đồ, chỉ cho phép cuộn nội bộ nếu cần; không cuộn ngang
  toàn trang hoặc chặn thao tác chính.
- Kiểm tra zoom 100% và 125% trên laptop, touch trên điện thoại/tablet và
  keyboard focus trên web.
- Các luồng chính phải chạy được ở cả portrait và landscape khi thiết bị hỗ trợ
  xoay màn hình.

## 3. Checklist trạng thái theo screen-flow SEAT-45

- [ ] Trạng thái dùng chung: Loading; Success; Empty; API Error; No Connection;
  404; Stale Data; Unauthorized/Forbidden.
- [ ] Tình trạng phòng: Loading; Loaded Fresh; Loaded Stale; No Data; Empty
  (số 0 hợp lệ); API Error; No Connection.
- [ ] Đặt phòng: Idle; Validation Error; Submitting; Success; Conflict; Daily
  Limit; Invalid Participant; Room Not Found/Unavailable; API Error.
- [ ] Check-in QR: Ready Scan; Scanning; QR Invalid; Submitting; Success; No
  Permission; Booking Not Found; Overdue; Duplicate; QR Expired.
- [ ] Lịch đặt/QR: Loading; Loaded; Empty; Detail; QR Display; Cancel
  Confirmation; API Error.
- [ ] Dashboard/báo cáo: Loading; Loaded; Empty/Insufficient Data; Stale; No
  Permission; Exporting; Export Success; Export Error.
- [ ] OTP: email không hợp lệ/không được phép; OTP sai/hết hạn; hết lượt thử;
  gửi lại bị giới hạn; gửi/xác minh thành công.
- [ ] Với mỗi trạng thái lỗi, kiểm tra thông báo, hành động tiếp theo, khả năng
  quay lại/thử lại và việc không hiển thị dữ liệu cũ như dữ liệu mới.

## 4. Khả năng đọc khi khó phân biệt màu

- [ ] Trạng thái phòng/booking không chỉ phân biệt bằng màu: có nhãn chữ và/hoặc
  biểu tượng/hình dạng đi kèm.
- [ ] Dùng chế độ thang xám hoặc bộ lọc mô phỏng mù màu; vẫn phân biệt được
  phòng trống/đầy/bảo trì và booking thành công/lỗi bằng nhãn hoặc biểu tượng.
- [ ] Cảnh báo lỗi không chỉ dùng viền/nền màu; nội dung nêu nguyên nhân và
  hành động kế tiếp.

## 5. Native, SUS và ghi nhận kết quả

- **Native:** SRS Q-17 chốt Android/Kotlin, iOS ngoài phạm vi; phiên bản Android
  tối thiểu và thiết bị kiểm thử vẫn chờ xác nhận. Ghi rõ TBD cho đến khi Q-17
  được cập nhật. Nếu triển khai Android, chạy TC-17 trên thiết bị/OS được chốt
  và ghi model máy, phiên bản OS, APK cùng kết quả luồng OTP, xem phòng, đặt
  phòng và check-in.
- **SUS:** sau khi người tham gia hoàn tất luồng chính, thu khảo sát theo TC-14
  và AT-04 trong [SRS](requirements/srs.md): mục tiêu tạm SUS ≥ 70 với khoảng
  15–30 người. SUS là phép đo riêng, không thay thế kết quả TC-11/TC-17.
- **Mẫu ghi mỗi lần chạy:** ngày/giờ; người kiểm thử; mã TC SRS; màn hình;
  thiết bị/model; OS và phiên bản; trình duyệt và phiên bản; viewport/orientation;
  zoom; dữ liệu đầu vào; bước chạy; kết quả mong đợi/thực tế; Pass/Fail/Blocked;
  liên kết ảnh chụp màn hình; mã lỗi/issue; ghi chú.
- Ảnh chụp phải thể hiện viewport và trạng thái liên quan, được lưu trong hồ sơ
  kiểm thử nội bộ, không chứa email/OTP hoặc dữ liệu cá nhân thật.
- Đây là kế hoạch, chưa phải bằng chứng đã chạy. Chỉ đánh dấu TC đạt khi có kết
  quả và ảnh minh chứng; native ghi Blocked/TBD cho đến khi Q-17 được chốt.

## 6. Kiểm thử phần mềm tổng thể

- Unit tests: kiểm tra quy tắc miền, schema và logic đếm CV.
- API tests: kiểm tra contract request/response và xử lý lỗi.
- Integration tests: kiểm tra tương tác backend/database và backend/CV.
- End-to-end tests: kiểm tra các luồng xem phòng, đặt phòng và check-in.

## 7. Báo cáo kiểm thử

Ghi ngày, commit, lệnh chạy, kết quả và các giới hạn đã biết trong
[test-report.md](test-report.md).
