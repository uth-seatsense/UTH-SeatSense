# Test case UI

Các test case dưới đây cung cấp chi tiết thực thi cho
[mục Kiểm thử giao diện responsive trong test-plan.md](test-plan.md#7-kiểm-thử-giao-diện-responsive).
Mã TC dùng theo SRS 1.9; không tạo mã TC mới. Mỗi UI-01–UI-08 có ít nhất hai
case (happy path và lỗi/empty/stale). Cả hai case phải được chạy trên ma trận
viewport tương ứng ở test plan, trừ UI-08 native có ma trận thiết bị riêng.

| Screen | Test case A — hiển thị/thao tác chính | Test case B — lỗi / trạng thái | Mã TC SRS |
| --- | --- | --- | --- |
| UI-01 — Đăng nhập OTP | Mở form, gửi email hợp lệ, nhập OTP hợp lệ và tiếp tục; form có label, focus và nút thao tác hiển thị. | Email không hợp lệ, OTP sai/hết hạn hoặc API lỗi; lỗi có hướng khắc phục, dữ liệu nhập còn sửa được và không lộ email tồn tại hay không. | TC-15, TC-11 |
| UI-02 — Khu tự học tự do | Hiển thị phòng, cơ sở, sức chứa, occupancy, chỗ trống và lần cập nhật; lọc CS1/CS3; không có nút đặt chỗ cho free_area. | Danh sách rỗng, occupancy chưa có N0, dữ liệu stale hoặc API lỗi; hiện đúng empty/insufficient/stale/error, không thay bằng số 0 giả. | TC-01, TC-02, TC-03, TC-16, TC-18, TC-20 |
| UI-03 — Đặt phòng chuyên đề | Chọn cơ sở, phòng, ngày/giờ và số người hợp lệ; gửi form mock và thấy kết quả xác nhận mock. | Thiếu/sai trường, thời lượng không hợp lệ, phòng bảo trì hoặc booking trùng; chỉ rõ lỗi và không tạo booking không hợp lệ. | TC-05, TC-06, TC-07, TC-11, TC-16 |
| UI-04 — Lịch đặt / QR | Mở lịch có booking, xem chi tiết và mã QR; kiểm tra trạng thái booking. | Chưa có booking, API lỗi hoặc QR sai/hết hạn/đã dùng; hiện trạng thái phù hợp và không xác nhận check-in sai. | TC-08, TC-09, TC-11 |
| UI-05 — Dashboard thủ thư | Người có quyền chọn bộ lọc thời gian/cơ sở/phòng và xem số liệu/biểu đồ khi có dữ liệu. | Không đủ quyền, dữ liệu rỗng/cũ hoặc API lỗi; cảnh báo rõ, không hiển thị dữ liệu lỗi như mới. | TC-03, TC-10, TC-11 |
| UI-06 — Trạng thái dữ liệu | Kiểm tra trạng thái fresh; hiện thời điểm cập nhật và số liệu chỉ khi đủ N0/sức chứa đã xác nhận. | Dùng fixture stale, offline, insufficient-data và lỗi API; thông báo đúng trạng thái, không công bố số chỗ trống/mức đông chính thức khi thiếu dữ liệu. | TC-02, TC-03, TC-20, TC-23 |
| UI-07 — Responsive xuyên màn | Chạy xem phòng/đặt phòng/check-in ở 360, 390, 768, 1024 và 1440 px; thao tác touch/keyboard còn dùng được. | Ở 360 và 390 px kiểm tra thông báo lỗi, empty/stale; không có cuộn ngang toàn trang, nút chính không che nội dung. | TC-11 |
| UI-08 — Android native | Sau khi có APK, đăng nhập OTP, xem chỗ trống, đặt phòng và check-in QR trên thiết bị đã chốt. | Từ chối camera/OTP/API lỗi; thông báo khôi phục được và không tạo booking/check-in sai. | TC-17 |

## Ghi kết quả

Với mỗi lượt chạy, ghi mã case, ngày, tester, commit, OS, thiết bị, viewport
CSS, tên/phiên bản trình duyệt hoặc Android API level, fixture, kết quả
Pass/Fail/Blocked và đường dẫn ảnh chụp màn hình. Ảnh phải thể hiện đúng
viewport và trạng thái đang kiểm tra; không chứa OTP, secret, email thật hay
hình ảnh nhận diện cá nhân.

Liên kết các tác vụ được usability test với TC-14/SUS, nhưng báo cáo SUS riêng
với kết quả chức năng/responsive. TC-17 giữ Blocked cho đến khi Q-17 được bổ
sung thiết bị Android và phiên bản/API level tối thiểu; không tự đoán phiên
bản hệ điều hành.
