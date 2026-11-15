# Test case UI

Các ca dưới đây phục vụ kế hoạch trong [test-plan.md](test-plan.md). Mỗi màn có
ít nhất hai ca: hiển thị/thao tác chính và lỗi/empty/stale. Cột cuối dùng mã TC
chuẩn trong [SRS](requirements/srs.md).

| Màn hình | Ca 1 — hiển thị và thao tác chính | Ca 2 — lỗi / trạng thái cần chạy | Mã TC SRS |
| --- | --- | --- | --- |
| Trang chủ / điều hướng sinh viên | Mở trang, chọn xem chỗ trống và mở đặt phòng; các lựa chọn điều hướng phải còn thấy và thao tác được ở mọi viewport. | API lỗi hoặc mất mạng: hiện thông báo/trạng thái lỗi, có đường quay lại/thử lại; nội dung không tràn ngang trên điện thoại. | TC-11, TC-03 |
| Đăng nhập OTP (UI-01) | Nhập email hợp lệ, yêu cầu OTP, nhập mã hợp lệ và tiếp tục luồng đặt phòng. | Email không được phép, OTP sai/hết hạn hoặc gửi lại quá sớm: hiển thị lỗi, cho sửa/nhập lại; không làm mất nút xác nhận. | TC-15, TC-11 |
| Danh sách phòng / tình trạng khu tự học (UI-02, UI-06) | Hiển thị phòng, sức chứa, số người, chỗ trống và thời điểm cập nhật; chọn phòng/cơ sở hoặc làm mới. | Rỗng, chưa đủ dữ liệu, dữ liệu cũ hoặc mất mạng: hiện đúng empty/stale/error; không hiển thị số chỗ trống âm hay số liệu chính thức giả. | TC-01, TC-02, TC-03, TC-20, TC-23, TC-11 |
| Đặt phòng chuyên đề (UI-03) | Chọn phòng, ngày/giờ và số người hợp lệ; gửi đặt phòng và xác nhận kết quả. | Thời gian/đầu vào sai, phòng bảo trì hoặc trùng lịch: chỉ rõ lỗi và giữ form có thể sửa; booking không hợp lệ không được tạo. | TC-05, TC-06, TC-07, TC-16, TC-11 |
| Lịch đặt / xem QR (UI-04) | Mở danh sách có booking, xem chi tiết và QR; kiểm tra empty state khi chưa có lượt đặt. | API lỗi, booking đã hủy/hết hạn hoặc QR không còn hợp lệ: hiển thị lỗi/trạng thái, không cho thao tác check-in sai. | TC-08, TC-09, TC-11 |
| Check-in QR (UI-04, UI-08) | Quét QR hợp lệ bằng luồng Android; xác nhận kết quả check-in. | QR sai, hết hạn, đã dùng hoặc không có quyền: hiện lỗi; trạng thái booking không bị chuyển thành check-in. | TC-08, TC-17, TC-11 |
| Dashboard / báo cáo thủ thư (UI-05, UI-06) | Người có quyền chọn bộ lọc thời gian/phòng và xem dashboard/báo cáo có dữ liệu. | Không đủ quyền, dữ liệu rỗng/cũ hoặc API lỗi: hiện trạng thái tương ứng và thao tác thử lại/đổi bộ lọc. | TC-10, TC-03, TC-11 |
| Quản lý phòng / khởi tạo phiên đếm | Vai trò được cấp quyền xem/sửa cấu hình thử nghiệm; nhập số ban đầu hợp lệ để bắt đầu phiên. | Người không đủ quyền hoặc thiếu số ban đầu/sức chứa đã xác nhận: chặn thao tác và không công bố số chỗ trống/mức đông chính thức. | TC-10, TC-19, TC-20, TC-23, TC-11 |
| Ứng dụng native (nếu triển khai) | Trên Android, thử đăng nhập OTP, xem chỗ trống, đặt phòng và check-in theo phạm vi SRS. | Thử OTP/API lỗi và quyền camera bị từ chối; thông báo có thể khôi phục, không mất dữ liệu/booking. | TC-15, TC-17 |
