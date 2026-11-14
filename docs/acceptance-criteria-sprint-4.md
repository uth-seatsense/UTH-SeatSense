# Tiêu chí nghiệm thu Sprint 4

Tài liệu này tập hợp tiêu chí nghiệm thu Given/When/Then cho các nhóm story
Sprint 4, để đối chiếu với backlog và cập nhật mô tả Jira.

## Story SPRINT-04-01 — Xem trạng thái phòng và đặt phòng

- FR-04-01: Người dùng xem danh sách phòng và trạng thái từng phòng.
- BR-04-01: Chỗ trống không được hiển thị âm; nếu số người hiện tại >= sức chứa
  thì hiển thị 0 và trạng thái đầy.
- TC-04-01: Màn hình trạng thái phòng load trong ≤ 5 giây sau khi truy cập.

Given phòng có sức chứa 40 và đã ghi 45 sự kiện vào, When mở trang tình trạng
phòng, Then số chỗ trống hiển thị 0 và phòng được đánh dấu vượt sức chứa
(BR-04-01).

Given người dùng đã chọn phòng A201 và thời gian còn trống, When nhấn đặt phòng,
Then hệ thống tạo booking mới với trạng thái pending và hiển thị trên lịch đặt
của người dùng (FR-04-01).

Given một phòng đã có booking trùng khung giờ, When người dùng đặt chồng lịch,
Then hệ thống từ chối và thông báo rõ rằng khung giờ đã được đặt (TC-04-01).

## Story SPRINT-04-02 — Check-in QR và xác nhận đến phòng

- FR-04-02: Người dùng có thể check-in bằng QR trong khung thời gian booking hợp lệ.
- BR-04-02: Một booking chỉ được check-in khi trạng thái hợp lệ và thời gian còn
  hiệu lực.
- TC-04-02: Check-in thất bại cho QR hết hạn hoặc không thuộc booking hiện tại,
  đồng thời không tạo trạng thái sai.

Given booking hợp lệ còn trong thời gian đặt, When người dùng quét mã QR, Then
hệ thống chuyển booking sang trạng thái checked-in và hiển thị xác nhận thành
công (FR-04-02).

Given QR không thuộc booking đang hoạt động hoặc đã quá hạn, When người dùng
quét, Then hệ thống không cập nhật trạng thái và hiển thị lỗi "QR không hợp lệ"
(BR-04-02).

Given người dùng quét QR trong lúc hệ thống đang tải dữ liệu, When thực hiện
thao tác, Then thời gian phản hồi không vượt quá 5 giây và không làm sai tiền
đề dữ liệu (TC-04-02).

## Story SPRINT-04-03 — Tự nhả phòng khi quá hạn

- FR-04-03: Booking hết thời gian sẽ được cập nhật sang trạng thái expired hoặc
  released.
- BR-04-03: Sau khi quá hạn, mã QR đặt phòng không còn hiệu lực và phòng được
  giải phóng cho việc đặt mới.
- TC-04-03: Hệ thống lưu log/audit sự kiện nhả phòng kèm thời điểm chính xác.

Given booking đã hết thời gian đặt, When hệ thống chạy kiểm tra trạng thái,
Then booking chuyển sang expired/released và không còn được check-in tiếp
(FR-04-03).

Given phòng đã được giải phóng sau khi hết hạn, When người dùng quét mã QR cũ,
Then hệ thống từ chối vì QR không còn hiệu lực (BR-04-03).

Given trường hợp thời gian kết thúc đã trôi qua, When kiểm tra audit log, Then
thời gian nhả phòng phải khớp với thời điểm hết hạn và không có sai lệch > 1
phút (TC-04-03).

## Story SPRINT-04-04 — App Android đặt phòng và check-in

- FR-04-04: App Android cho phép sinh viên xem phòng, đặt phòng và check-in bằng QR.
- BR-04-04: Mỗi thao tác phải được xác thực theo tài khoản người dùng; không cho
  đặt phòng khi người dùng chưa đăng nhập hoặc mã OTP không hợp lệ.
- TC-04-04: Giao diện app không bị cắt nội dung ở màn hình 390x844 và nút chính
  không chồng lên nhau.

Given sinh viên đã đăng nhập bằng OTP, When mở app và chọn phòng, Then hệ thống
hiển thị danh sách phòng còn trống và cho phép đặt theo khung giờ (FR-04-04).

Given người dùng chưa đăng nhập hoặc token hết hạn, When thực hiện đặt
phòng/check-in, Then hệ thống yêu cầu đăng nhập lại và không tạo booking mới
(BR-04-04).

Given app chạy trên điện thoại Android kích thước nhỏ, When thao tác đặt phòng
và quét QR, Then giao diện phải còn hiển thị nút chính và không có lỗi layout
trong 5 giây đầu (TC-04-04).

## Story SPRINT-04-05 — Camera CV chạy thực nghiệm tại CS1/CS3 (nếu được phép)

- FR-04-05: Hệ thống CV có thể đọc dữ liệu từ webcam local và truyền số liệu
  đếm lên backend.
- BR-04-05: Nếu camera không truy cập được, hệ thống báo lỗi rõ và không giả
  định số liệu không đáng tin cậy.
- TC-04-05: Dữ liệu đếm được gửi lên server theo cấu trúc hợp đồng và không lưu
  video nhận diện cá nhân.

Given máy tính có webcam hoạt động và đã được cấp phép triển khai, When chạy CV
tại CS1/CS3, Then dữ liệu đếm được gửi lên backend và hiển thị trên dashboard
(FR-04-05).

Given webcam không khả dụng hoặc không được phép cấp quyền, When CV khởi động,
Then hệ thống hiển thị cảnh báo và không ghi nhận dữ liệu giả mạo (BR-04-05).

Given dữ liệu đếm được gửi lên backend, When kiểm tra payload, Then payload phù
hợp contract và không chứa dữ liệu nhạy cảm như video/nhận diện cá nhân
(TC-04-05).

## Cập nhật Jira

- Gắn nhãn `AC-ready` cho từng story sau khi tiêu chí được dán vào đúng issue.
- Mỗi tiêu chí cần có test case tương ứng và dùng điều kiện kiểm thử cụ thể,
  tránh các từ mơ hồ như "nhanh", "đẹp", "dễ dùng".
- Mẫu comment xác nhận của dev: `Confirmed: Acceptance criteria reviewed for
  [story ID]`.
- Các tên SPRINT-04-01 đến SPRINT-04-05 trong tài liệu là nhóm nội dung; cần
  đối chiếu và thay bằng issue key thực tế từ backlog khi cập nhật Jira.

## Điều kiện hoàn tất

- 100% story Sprint 4 trong backlog có tiêu chí nghiệm thu.
- Mỗi story có tối thiểu ba tiêu chí Given/When/Then bao gồm luồng chính, luồng
  lỗi và ràng buộc phi chức năng.
- Mỗi tiêu chí có ít nhất một test case kiểm thử được.
- Đã gắn nhãn `AC-ready` và dev của story đã xác nhận bằng comment trên Jira.


