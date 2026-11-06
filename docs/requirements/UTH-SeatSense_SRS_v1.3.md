UTH-SeatSense

TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM
SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

Hệ thống theo dõi mật độ sử dụng phòng đọc
và đặt phòng học nhóm tại Thư viện UTH

| Thông tin | Nội dung |
| --- | --- |
| Mã đề tài | D6 – Đặt chỗ và theo dõi mật độ sử dụng phòng đọc |
| Phiên bản | 1.3 – Dự thảo theo Project Charter v1.2 |
| Ngày cập nhật | 30/10/2026 |
| Đơn vị hưởng lợi | Trung tâm Thông tin Thư viện UTH |
| Quản lý dự án | Vũ Nguyễn Nhã Uyên |
| Giáo viên hướng dẫn | TS. Đặng Nhân Cánh |
| Nhóm phát triển | Nhóm dự án UTH-SeatSense |
| Thời gian dự án | 26/10/2026 – 26/12/2026 |
| Trạng thái | Dự thảo – chờ rà soát và phê duyệt |

Tài liệu làm cơ sở thống nhất yêu cầu, thiết kế, phát triển, kiểm thử và đánh giá sản phẩm.

# Lịch sử phiên bản

| Phiên bản | Ngày | Mô tả | Trạng thái |
| --- | --- | --- | --- |
| 1.0 | 26/10/2026 | Bản SRS rút gọn ban đầu | Dự thảo |
| 1.1 | 28/10/2026 | Cập nhật camera AI và Docker Compose | Dự thảo |
| 1.2 | 28/10/2026 | Chuẩn hóa theo Project Charter v1.2; bỏ IoT/cảm biến khỏi phạm vi | Đã thay thế bởi 1.3 |
| 1.3 | 30/10/2026 | Rà soát đối chiếu Charter v1.2: chốt ByteTrack và PostgreSQL; bổ sung yêu cầu CV trực tiếp, quyền riêng tư, chi phí, rủi ro; sửa phạm vi. | Chờ rà soát |

# Mục lục nội dung

- 1. Giới thiệu

- 2. Mô tả tổng quan

- 3. Yêu cầu giao diện ngoài

- 4. Yêu cầu chức năng

- 5. Yêu cầu phi chức năng

- 6. Mô hình dữ liệu và quy tắc nghiệp vụ

- 7. Trường hợp sử dụng

- 8. Kiểm thử và tiêu chí nghiệm thu

- 9. Ưu tiên và ma trận truy vết

- 10. Giới hạn, giả định và rủi ro

- 11. Các vấn đề cần xác nhận

- 12. Phê duyệt

# 1. Giới thiệu

## 1.1. Mục đích tài liệu

Tài liệu SRS mô tả các yêu cầu chức năng, phi chức năng, giao diện, dữ liệu, quy tắc nghiệp vụ và tiêu chí kiểm thử của UTH-SeatSense. Đây là cơ sở thống nhất yêu cầu giữa nhóm phát triển, người dùng và đơn vị quản lý thư viện; hỗ trợ thiết kế, phát triển, kiểm thử và đánh giá sản phẩm.

## 1.2. Phạm vi sản phẩm

UTH-SeatSense là hệ thống web responsive hỗ trợ người dùng xem tình trạng sử dụng phòng đọc và đặt phòng học nhóm tại Thư viện UTH. Camera kết hợp YOLOv8n (phiên bản nhẹ) và ByteTrack (Phương án B, đã chốt trong Charter v1.2) để phát hiện/theo dõi người, đếm lượt vào/ra khi người cắt đường ảo. Mô-đun AI gửi số liệu đếm lên backend, không gửi danh tính người.

- Phạm vi thử nghiệm: Thư viện cơ sở 1 và cơ sở 2.

- Website responsive: xem chỗ trống/mức độ đông, đặt phòng theo khung giờ, check-in QR và dashboard thủ thư.

- Backend dùng FastAPI; cơ sở dữ liệu PostgreSQL; các dịch vụ chạy bằng Docker Compose.

- Thực nghiệm đối chiếu đếm tay, đánh giá trải nghiệm bằng SUS, báo cáo kết quả và kế hoạch kinh doanh.

- Tùy chọn (Could): dự báo mật độ 1–2 giờ tới và thông báo khi có chỗ trống, chỉ làm khi các yêu cầu Must/Should đã ổn định.

## 1.3. Ngoài phạm vi

- Phương án A (ESP32 + cảm biến khoảng cách) và mọi phần cứng IoT.

- Nhận diện khuôn mặt, nhận dạng danh tính hoặc theo dõi cá nhân.

- Lưu trữ video/hình ảnh lâu dài; video nghiên cứu nếu được phép chỉ lưu tạm và xóa sau đánh giá.

- Tích hợp hệ thống đào tạo/tài khoản chính thức của trường.

- Ứng dụng native iOS/Android; triển khai toàn bộ thư viện/nhiều tòa nhà.

## 1.4. Thuật ngữ

| Thuật ngữ | Giải thích |
| --- | --- |
| SRS | Software Requirements Specification – đặc tả yêu cầu phần mềm |
| YOLOv8n | Phiên bản nhẹ của YOLO để phát hiện người |
| ByteTrack | Bộ theo dõi đối tượng qua các khung hình |
| Đường ảo | Đường cấu hình trong vùng quan sát để xác định hướng vào/ra |
| No-show | Người đặt không check-in trong thời gian chờ |
| SUS | System Usability Scale – thang đo khả dụng |
| FPS | Số khung hình xử lý trong một giây |
| Docker Compose | Công cụ định nghĩa và chạy nhiều dịch vụ |

## 1.5. Tài liệu tham chiếu

- Project Charter: UTH-SeatSense, đề tài D6, phiên bản 1.2, cập nhật 28/10/2026.

- IEEE 29148 – Systems and Software Engineering: Requirements Engineering (tham khảo).

- Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân và quy định liên quan áp dụng tại thời điểm triển khai.

- Tài liệu kỹ thuật FastAPI, PostgreSQL, Docker Compose, YOLOv8 và ByteTrack.

# 2. Mô tả tổng quan

## 2.1. Bối cảnh và vấn đề

Sinh viên có thể phải đến thư viện mới biết phòng đọc còn chỗ hay không; phòng học nhóm có thể được đặt nhưng không sử dụng; thủ thư thiếu dữ liệu mật độ theo giờ/ngày. Các vấn đề và mức độ ảnh hưởng cần được xác minh qua khảo sát sinh viên và phỏng vấn thủ thư, không xem giả định ban đầu là kết quả khảo sát.

## 2.2. Mục tiêu hệ thống

1. Hiển thị số người ước tính, số chỗ trống và mức độ đông gần thời gian thực.

1. Cho phép sinh viên tìm phòng học nhóm khả dụng, đặt phòng theo khung giờ và nhận xác nhận.

1. Hỗ trợ check-in QR và xử lý no-show theo quy tắc được thư viện phê duyệt.

1. Cung cấp dashboard thống kê mật độ, tỷ lệ sử dụng phòng và tỷ lệ no-show cho thủ thư.

1. Đánh giá sai số, tốc độ xử lý và độ trễ cập nhật của phương pháp camera AI.

1. Chuẩn hóa môi trường bằng Docker Compose; lập báo cáo thực nghiệm và kế hoạch kinh doanh.

## 2.3. Nhóm người dùng

| Vai trò | Nhu cầu và quyền chính |
| --- | --- |
| Sinh viên/người dùng | Xem tình trạng phòng, đăng ký/đăng nhập, đặt phòng, xem lịch đặt và check-in QR cho lượt đặt hợp lệ của mình. |
| Thủ thư/quản lý | Xem dashboard; quản lý thông tin phòng, sức chứa và quy tắc vận hành theo quyền được cấp. |
| Nhóm phát triển/vận hành | Cấu hình camera AI/đường ảo; theo dõi lỗi; kiểm thử, đo FPS và sai số. |

## 2.4. Kiến trúc khái quát

Luồng dữ liệu dự kiến: Camera → mô-đun CV/AI (YOLOv8n + ByteTrack + đếm qua đường ảo) → dữ liệu số lượng vào/ra → Backend FastAPI → PostgreSQL → website responsive/dashboard.

| Thành phần | Công nghệ | Trách nhiệm |
| --- | --- | --- |
| CV/AI | Camera, YOLOv8n, ByteTrack | Phát hiện/theo dõi người, đếm qua đường ảo; chỉ gửi số liệu đếm. |
| Backend/API | FastAPI | Xác thực, đặt phòng, check-in, no-show, tiếp nhận dữ liệu và cung cấp API. |
| Cơ sở dữ liệu | PostgreSQL | Lưu tài khoản, phòng, đặt chỗ, check-in, mật độ và sự kiện. |
| Frontend | Web responsive, đã chốt: React + Vite (JavaScript) | Hiển thị chỗ trống, đặt phòng, QR và dashboard. |
| Đóng gói | Docker Compose | Khởi chạy dịch vụ nhất quán; quản lý cấu hình và volume dữ liệu. |

Lưu ý: Docker Desktop trên Windows/macOS có thể hạn chế truy cập webcam USB từ container. Nhóm cần chốt chạy CV/AI ngoài Docker hay xử lý video mẫu trong container. Khả năng chạy trực tiếp phải được xác minh trên phần cứng thực tế; nếu không đạt, có thể đánh giá offline trên video được phép sử dụng.

## 2.5. Môi trường vận hành

- Trình duyệt hiện đại trên máy tính, máy tính bảng và điện thoại.

- Máy chạy CV/AI có camera được cấp phép hoặc video mẫu được phép sử dụng.

- Backend, cơ sở dữ liệu và frontend chạy bằng Docker Compose; cấu hình nhạy cảm đặt trong biến môi trường.

- Cấu hình phần cứng và thời gian chạy liên tục sẽ được xác nhận sau thử nghiệm.

# 3. Yêu cầu giao diện ngoài

## 3.1. Giao diện người dùng

| Mã | Giao diện | Yêu cầu |
| --- | --- | --- |
| UI-01 | Đăng ký/đăng nhập | Biểu mẫu rõ ràng, kiểm tra dữ liệu và thông báo lỗi phù hợp. |
| UI-02 | Trang tình trạng phòng | Tên phòng, sức chứa, số người ước tính, chỗ trống, mức độ đông và thời điểm cập nhật. |
| UI-03 | Đặt phòng | Chọn ngày/giờ/phòng; xem khả dụng; xác nhận kết quả và báo trùng lịch. |
| UI-04 | Lịch đặt/QR | Hiển thị lượt đặt của người dùng và QR/mã check-in hợp lệ. |
| UI-05 | Dashboard | Bộ lọc thời gian/phòng; biểu đồ mật độ, tỷ lệ sử dụng và no-show nếu có dữ liệu. |
| UI-06 | Trạng thái dữ liệu | Cảnh báo dữ liệu lỗi thời/mất kết nối; không hiển thị dữ liệu cũ như mới. |
| UI-07 | Responsive | Tự điều chỉnh theo màn hình; luồng chính không cần cuộn ngang trên điện thoại. |

## 3.2. Giao diện phần mềm

- Frontend trao đổi với backend qua API.

- Mô-đun CV/AI gửi sự kiện/số lượng vào-ra kèm mã phòng, thời điểm và trạng thái nguồn dữ liệu.

- PostgreSQL lưu dữ liệu có cấu trúc; thông tin kết nối quản lý qua biến môi trường.

- Docker Compose định nghĩa dịch vụ, mạng, cấu hình và volume dữ liệu.

## 3.3. Giao diện camera/phần cứng

Camera được đặt trên cao, nhìn từ trên xuống, theo hướng và vùng quan sát được thư viện phê duyệt; có biển thông báo tại khu vực. Vị trí cần giảm che khuất và cho phép cấu hình đường ảo tại lối vào/ra. Cách kết nối camera trực tiếp hay xử lý video offline là quyết định kỹ thuật cần xác minh.

## 3.4. Giao diện truyền thông

Mô-đun CV/AI giao tiếp với backend qua API HTTP/HTTPS hoặc giao thức nội bộ phù hợp. Cấu trúc payload, xác thực, định dạng thời gian và xử lý gửi lặp cần được thống nhất trong thiết kế API.

# 4. Yêu cầu chức năng

Mỗi yêu cầu được đánh mã để truy vết sang thiết kế và kiểm thử. Ưu tiên: Must (bắt buộc), Should (nên có), Could (có thể bổ sung).

| Mã | Tên | Mô tả | Ưu tiên |
| --- | --- | --- | --- |
| FR-AUTH-01 | Đăng ký | Cho phép tạo tài khoản với trường thông tin tối thiểu đã thống nhất. | Must |
| FR-AUTH-02 | Đăng nhập/đăng xuất | Xác thực người dùng và cho phép kết thúc phiên. | Must |
| FR-AUTH-03 | Phân quyền | Phân biệt người dùng và thủ thư/quản lý; chặn thao tác trái quyền. | Must |
| FR-OCC-01 | Nhận dữ liệu đếm | Tiếp nhận số lượng/sự kiện vào-ra kèm mã phòng và thời điểm. | Must |
| FR-OCC-02 | Cập nhật số người | Cập nhật số người hiện tại theo sự kiện vào/ra hợp lệ. | Must |
| FR-OCC-03 | Tính chỗ trống | Tính sức chứa cấu hình trừ số người hiện tại; không hiển thị giá trị âm. | Must |
| FR-OCC-04 | Hiển thị mật độ | Hiển thị số người ước tính, sức chứa, chỗ trống, mức độ đông và thời điểm cập nhật. | Must |
| FR-OCC-05 | Trạng thái nguồn | Cảnh báo dữ liệu lỗi thời hoặc nguồn đếm mất kết nối. | Must |
| FR-CV-01 | Phát hiện người | Dùng YOLOv8n (YOLOv8 phiên bản nhẹ) phát hiện người trong vùng quan sát. | Must |
| FR-CV-02 | Theo dõi đối tượng | Dùng ByteTrack để theo dõi tạm thời qua khung hình; ID chỉ phục vụ đếm, không dùng để định danh. | Must |
| FR-CV-03 | Đếm qua đường ảo | Ghi nhận hướng vào/ra khi đối tượng cắt đường ảo; hạn chế đếm lặp. | Must |
| FR-CV-04 | Đánh giá offline | Cho phép chạy trên video mẫu được phép sử dụng nếu demo trực tiếp không đạt. | Must |
| FR-CV-05 | Chạy trực tiếp với camera | Chạy CV/AI với camera thật để demo thời gian thực, tốc độ theo NFR-PER-02; nếu phần cứng không đáp ứng thì dùng FR-CV-04. | Should |
| FR-BOOK-01 | Xem phòng khả dụng | Xem phòng học nhóm và khung giờ còn khả dụng. | Must |
| FR-BOOK-02 | Tạo đặt phòng | Chọn phòng, ngày, giờ bắt đầu và kết thúc để tạo lượt đặt. | Must |
| FR-BOOK-03 | Kiểm tra hợp lệ | Kiểm tra thời gian và quyền đặt trước khi lưu. | Must |
| FR-BOOK-04 | Ngăn trùng lịch | Từ chối lượt đặt chồng lấn trên cùng phòng kể cả yêu cầu đồng thời. | Must |
| FR-BOOK-05 | Xác nhận đặt | Lưu lượt đặt thành công và hiển thị xác nhận. | Must |
| FR-BOOK-06 | Xem/hủy lượt đặt | Cho xem lượt đặt cá nhân; hủy theo chính sách đã duyệt. | Should |
| FR-CHK-01 | Tạo QR | Tạo/hiển thị QR hoặc mã check-in gắn với lượt đặt hợp lệ. | Should |
| FR-CHK-02 | Xác minh QR | Xác minh mã, trạng thái và thời gian lượt đặt. | Should |
| FR-CHK-03 | Ghi nhận check-in | Lưu thời điểm và cập nhật trạng thái sau check-in hợp lệ. | Should |
| FR-BOOK-07 | Xử lý no-show | Tự động xác định lượt quá thời gian chờ chưa check-in (dự kiến 10–15 phút, cần chốt) và giải phóng khung giờ theo cấu hình. | Should |
| FR-DASH-01 | Dashboard mật độ | Thủ thư xem thống kê mật độ theo giờ/ngày và theo phòng. | Should |
| FR-DASH-02 | Thống kê vận hành | Hiển thị tỷ lệ sử dụng phòng, số lượt đặt, tỷ lệ no-show nếu có dữ liệu. | Should |
| FR-ADMIN-01 | Quản lý phòng | Người có quyền cấu hình tên, loại, sức chứa, vị trí và trạng thái phòng. | Should |
| FR-OPS-01 | Docker Compose | Khởi chạy các dịch vụ chính bằng Docker Compose theo README. | Must |
| FR-OPS-02 | Dữ liệu bền vững | Dùng volume để dữ liệu PostgreSQL không mất khi container restart. | Must |
| FR-EXP-01 | Đối chiếu đếm tay | Đối chiếu dữ liệu camera với đếm tay trong các phiên thử nghiệm. | Must |
| FR-EXP-02 | Đánh giá SUS | Khảo sát SUS và tổng hợp kết quả thử nghiệm người dùng. | Should |
| FR-EXP-03 | Báo cáo/kinh doanh | Lập báo cáo thực nghiệm và kế hoạch kinh doanh về doanh thu, chi phí, điểm hòa vốn. | Must |
| FR-OPT-01 | Dự báo/thông báo | Có thể bổ sung dự báo 1–2 giờ hoặc thông báo chỗ trống sau khi Must/Should ổn định. | Could |

# 5. Yêu cầu phi chức năng

| Mã | Thuộc tính | Yêu cầu/tiêu chí | Trạng thái |
| --- | --- | --- | --- |
| NFR-PER-01 | Độ trễ | Mục tiêu: sự kiện hiển thị trên web trong ≤ 5 giây trong môi trường thử nghiệm. | Cần đo |
| NFR-PER-02 | Tốc độ AI | Mục tiêu ≥ 5 FPS ở khoảng 416 px; nếu không đạt, đánh giá offline và ghi rõ môi trường. | Cần đo |
| NFR-ACC-01 | Độ chính xác | Mục tiêu sai số đếm ≤ 10% so với đếm tay; thống nhất công thức trước khi đo. | Cần đo |
| NFR-REL-01 | Độ ổn định | Ghi nhật ký lỗi/mất kết nối; chốt thời lượng chạy liên tục trước nghiệm thu. | Cần xác nhận |
| NFR-USA-01 | Khả dụng | Nhãn, thông báo và luồng thao tác rõ ràng cho sinh viên/thủ thư. | Cần kiểm thử |
| NFR-USA-02 | Responsive | Các luồng xem phòng, đặt phòng, check-in thích ứng desktop/tablet/mobile. | Cần kiểm thử |
| NFR-USA-03 | SUS | Mục tiêu SUS ≥ 70 với khoảng 15–30 sinh viên thử nghiệm; chưa phải kết quả đạt được. | Cần đo |
| NFR-SEC-01 | Xác thực | API/trang quản lý kiểm tra phiên và quyền; mật khẩu không lưu dạng văn bản thuần. | Cần rà soát |
| NFR-SEC-02 | Bí mật | Khóa và thông tin kết nối đặt trong biến môi trường, không commit vào kho mã nguồn. | Cần rà soát |
| NFR-PRI-01 | Không định danh | Không nhận diện khuôn mặt/danh tính; ID tracker chỉ phục vụ theo dõi tạm thời. | Cần rà soát |
| NFR-PRI-02 | Giảm thiểu ảnh | Camera đặt trên cao nhìn xuống; xử lý ngay tại chỗ, chỉ truyền số liệu đếm lên server; không lưu video lâu dài. | Cần rà soát |
| NFR-PRI-03 | Video nghiên cứu | Chỉ thu thập khi được phép; chỉ lưu tạm, hạn chế truy cập trong nhóm, xóa sau khi tính xong; không đưa lên Git. | Cần rà soát |
| NFR-PRI-04 | Đồng ý và thông báo | Có văn bản/email đồng ý của thư viện trước khi lắp camera và có biển thông báo tại khu vực. | Cần xác nhận |
| NFR-PRI-05 | Dữ liệu đặt phòng | Dữ liệu đặt phòng gắn mã sinh viên chỉ thu thập tối thiểu, bảo mật, xóa sau dự án nếu không cần; chỉ lưu số liệu đếm tổng hợp ẩn danh. | Cần rà soát |
| NFR-PRI-06 | Tuân thủ pháp lý | Đối chiếu Nghị định 13/2023/NĐ-CP và nêu rõ trong báo cáo, cùng các hạn chế (đếm sai khi đông, che khuất, ánh sáng yếu). | Cần rà soát |
| NFR-MNT-01 | Bảo trì | Mã nguồn chia module, có README và hướng dẫn cấu hình/chạy. | Cần rà soát |
| NFR-DEP-01 | Triển khai | Docker Compose mô tả dịch vụ và cung cấp tệp .env.example. | Cần rà soát |
| NFR-DAT-01 | Nhất quán | Kiểm tra dữ liệu đặt phòng và ngăn trùng ở backend/cơ sở dữ liệu. | Cần kiểm thử |

# 6. Mô hình dữ liệu và quy tắc nghiệp vụ

## 6.1. Thực thể dữ liệu dự kiến

| Thực thể | Trường tiêu biểu | Mục đích |
| --- | --- | --- |
| User | user_id, display_name, email, password_hash, role, created_at | Tài khoản và quyền. |
| Room | room_id, room_name, room_type, capacity, location, status | Phòng và sức chứa. |
| OccupancyRecord | record_id, room_id, current_count, available_seats, source, recorded_at, device_status | Dữ liệu mật độ theo thời gian. |
| Booking | booking_id, user_id, room_id, start_time, end_time, status, created_at, checkin_at | Lượt đặt phòng. |
| CheckIn | checkin_id, booking_id, checkin_time, method, status | Kết quả check-in. |
| CountEvent | event_id, room_id, direction, event_time, received_at, source | Sự kiện vào/ra. |
| AuditLog | log_id, actor_id, action, created_at, detail | Nhật ký thao tác quản trị nếu cần. |

## 6.2. Quy tắc nghiệp vụ

| Mã | Quy tắc |
| --- | --- |
| BR-01 | Số chỗ trống = sức chứa cấu hình − số người hiện tại ước tính. |
| BR-02 | Số chỗ trống không được âm; số người vượt sức chứa cần được đánh dấu. |
| BR-03 | Thời gian kết thúc lượt đặt phải sau thời gian bắt đầu. |
| BR-04 | Các lượt đặt hợp lệ trên cùng phòng không được chồng lấn. |
| BR-05 | Chỉ lượt đặt hợp lệ, chưa hủy và trong khung giờ cho phép mới được check-in. |
| BR-06 | Lượt đã check-in không được xử lý lại thành no-show. |
| BR-07 | Lượt quá thời gian chờ mà chưa check-in xử lý theo thời gian chờ được duyệt (dự kiến 10–15 phút; cần chốt). |
| BR-08 | Khung giờ no-show được giải phóng theo quy tắc cấu hình và cập nhật trạng thái. |
| BR-09 | Người dùng chỉ xem/thao tác lượt đặt của mình, trừ vai trò có quyền. |
| BR-10 | Chỉ người được phân quyền truy cập dashboard quản lý. |
| BR-11 | Camera không được nhận diện khuôn mặt hoặc định danh cá nhân. |
| BR-12 | Khi dữ liệu lỗi thời/mất kết nối, giao diện phải hiển thị cảnh báo. |
| BR-13 | Mỗi bản ghi đếm có phòng, thời điểm và nguồn; sự kiện trùng phải được xử lý. |

## 6.3. Giới hạn diễn giải số chỗ trống

Camera đếm người trong vùng quan sát không trực tiếp xác định ghế nào đang trống. Vì vậy, số chỗ trống là giá trị ước tính từ sức chứa cấu hình trừ số người hiện tại. Độ tin cậy phụ thuộc vị trí camera, che khuất, sự kiện vào/ra bị bỏ sót và quy trình hiệu chỉnh số đếm; nội dung này phải được đánh giá thực nghiệm.

# 7. Trường hợp sử dụng

| Mã | Trường hợp | Tác nhân | Luồng chính | Ngoại lệ |
| --- | --- | --- | --- | --- |
| UC-01 | Xem chỗ trống | Sinh viên | Mở trang chủ → lấy dữ liệu mới nhất → tính chỗ trống → hiển thị số người, sức chứa, mức đông và thời điểm cập nhật. | Nếu dữ liệu lỗi thời/mất kết nối, hiện cảnh báo. |
| UC-02 | Đặt phòng | Sinh viên | Đăng nhập → chọn ngày/giờ → xem phòng khả dụng → gửi yêu cầu → kiểm tra hợp lệ/trùng lịch → lưu và xác nhận. | Từ chối nếu trùng lịch, thời gian sai hoặc lưu lỗi. |
| UC-03 | Check-in QR | Sinh viên | Mở QR → gửi mã → backend xác minh lượt đặt → lưu check-in → hiển thị kết quả. | Từ chối mã sai/hết hạn, lượt bị hủy hoặc check-in lặp. |
| UC-04 | No-show | Bộ xử lý tự động | Kiểm tra lượt chưa check-in/chưa hủy → so thời gian chờ → cập nhật no-show và giải phóng khung giờ. | Không xử lý lượt đã check-in; ghi log lỗi. |
| UC-05 | Dashboard | Thủ thư | Đăng nhập → chọn phòng/khoảng thời gian → xem biểu đồ mật độ và thống kê. | Từ chối người thiếu quyền; báo khi thiếu dữ liệu. |
| UC-06 | Đếm qua đường ảo | CV/AI | Khung hình → YOLOv8n → ByteTrack → phát hiện cắt đường ảo → sự kiện vào/ra → gửi backend. | Ghi log/báo trạng thái nếu camera hoặc xử lý lỗi. |
| UC-07 | Khởi chạy hệ thống | Nhóm vận hành | Chuẩn bị biến môi trường → chạy Docker Compose → kiểm tra dịch vụ → mở website. | Log hỗ trợ chẩn đoán; dữ liệu volume còn sau restart. |

# 8. Kiểm thử và tiêu chí nghiệm thu

| Mã | Nội dung | Kết quả mong đợi |
| --- | --- | --- |
| TC-01 | Danh sách phòng | Hiển thị đúng phòng đã cấu hình và trạng thái. |
| TC-02 | Tính chỗ trống | Sức chứa trừ số người ước tính; giá trị không âm. |
| TC-03 | Mất kết nối/dữ liệu cũ | Hiện cảnh báo và thời điểm cập nhật cuối. |
| TC-04 | Đếm đường ảo | Đếm đúng hướng vào/ra, hạn chế đếm lặp. |
| TC-05 | Đặt phòng hợp lệ | Lưu lượt đặt và trả xác nhận. |
| TC-06 | Đặt trùng giờ | Từ chối lượt chồng lấn cùng phòng. |
| TC-07 | Đặt đồng thời | Không tạo hai lượt đặt hợp lệ chồng lấn. |
| TC-08 | QR hợp lệ/không hợp lệ | QR hợp lệ check-in; mã sai/hết hạn bị từ chối. |
| TC-09 | No-show | Xử lý đúng cấu hình; lượt đã check-in không thành no-show. |
| TC-10 | Dashboard/phân quyền | Thống kê đúng; người không đủ quyền bị chặn. |
| TC-11 | Responsive | Luồng chính dùng được trên desktop/tablet/mobile. |
| TC-12 | Docker Compose | Khởi chạy theo README; dữ liệu PostgreSQL còn sau restart. |
| TC-13 | Đối chiếu đếm tay | Có dữ liệu tay/camera, công thức sai số và kết quả. |
| TC-14 | SUS | Có kết quả khảo sát và phương pháp tính điểm. |
| TC-15 | Chạy camera trực tiếp | CV/AI nhận hình từ camera thật, đếm và gửi số liệu lên backend; ghi lại FPS và độ trễ. |

## 8.1. Chỉ tiêu đánh giá thực nghiệm

| Mã | Mục tiêu | Cách đánh giá |
| --- | --- | --- |
| AT-01 | Sai số đếm ≤ 10% | Đối chiếu đếm tay trong 5–10 phiên, mỗi phiên 30–60 phút, nhiều mức đông. |
| AT-02 | Độ trễ ≤ 5 giây | Đo từ lúc ghi nhận sự kiện đến lúc website hiển thị. |
| AT-03 | ≥ 5 FPS ở khoảng 416 px | Đo trên phần cứng thực tế; nếu không đạt, đánh giá offline và ghi môi trường. |
| AT-04 | SUS ≥ 70 | Khảo sát khoảng 15–30 sinh viên dùng thử. |
| AT-05 | Độ ổn định | Chốt thời gian chạy liên tục; thống kê lỗi/mất kết nối từ nhật ký. |
| AT-06 | Tỷ lệ no-show | So sánh trước/sau nếu có dữ liệu phù hợp và được phép. |
| AT-07 | Chi phí không vượt ngân sách trần | Đối chiếu bảng chi tiêu thực tế với ngân sách trần (hiện chưa thống kê). |

Các chỉ tiêu là mục tiêu, không phải kết quả đã đạt; các mục tiêu số sẽ được rà soát lại sau khảo sát thực địa. Nếu số đếm tham chiếu bằng 0, nhóm phải quy định cách tính sai số để tránh phép chia không xác định.

## 8.2. Điều kiện nghiệm thu tổng quát

- Các yêu cầu Must đã triển khai và vượt qua kiểm thử tương ứng.

- Không còn lỗi nghiêm trọng về đặt trùng, phân quyền và tính nhất quán dữ liệu.

- Khởi chạy bằng Docker Compose theo README; có .env.example và hướng dẫn cập nhật.

- Có báo cáo thực nghiệm nêu môi trường, dữ liệu, công thức, kết quả và giới hạn.

- Có chấp thuận của thư viện và quy trình camera đáp ứng nguyên tắc quyền riêng tư.

- Không tuyên bố KPI đạt được khi chưa đo.

# 9. Ưu tiên và ma trận truy vết

| Mức ưu tiên | Phạm vi |
| --- | --- |
| Must | Xem chỗ trống; đặt phòng/ngăn trùng; đếm camera + YOLOv8n + ByteTrack qua đường ảo (ít nhất đánh giá offline); Docker Compose; đối chiếu đếm tay; báo cáo và kế hoạch kinh doanh. |
| Should | Check-in QR, no-show, dashboard thủ thư, SUS; demo AI trực tiếp nếu phần cứng cho phép. |
| Could | Dự báo mật độ 1–2 giờ tới; thông báo khi có chỗ trống. |
| Won’t | ESP32/cảm biến IoT, nhận diện khuôn mặt, app native, tích hợp tài khoản chính thức, triển khai toàn thư viện. |

## 9.1. Ma trận truy vết mẫu

| Yêu cầu | Thành phần | Kiểm thử |
| --- | --- | --- |
| FR-OCC-03 | Backend + Frontend | TC-02 |
| FR-CV-03 | CV/AI + Backend | TC-04, AT-01 |
| FR-CV-05 | CV/AI + Backend | TC-15, AT-03 |
| FR-BOOK-04 | Backend + PostgreSQL | TC-06, TC-07 |
| FR-CHK-02/03 | Backend + Frontend | TC-08 |
| FR-DASH-01/02 | Backend + Frontend | TC-10 |
| NFR-PER-01 | CV/AI + Backend + Frontend | AT-02 |
| NFR-ACC-01 | CV/AI | AT-01 |
| NFR-USA-03 | Frontend + nhóm kiểm thử | AT-04 |
| NFR-PRI-01/02 | CV/AI + quy trình vận hành | Rà soát xử lý hình ảnh |
| FR-OPS-01/02 | Docker Compose + PostgreSQL | TC-12 |

# 10. Giới hạn, giả định và rủi ro

## 10.1. Giả định và ràng buộc

- Thư viện cho phép thử nghiệm camera tại khu vực được thống nhất; phải có văn bản/email chấp thuận trước lắp đặt.

- Có nguồn điện và mạng tại vị trí triển khai.

- Mỗi thành viên dành tối thiểu [x] giờ/tuần cho dự án (cần chốt).

- Máy tính có thể không có GPU chuyên dụng; hiệu năng AI phải được đo.

- Thời gian dự án theo Charter: 26/10/2026–26/12/2026; ngân sách trần chưa thống kê.

- Phải tuân thủ quy định của thư viện và nhà trường.

- Framework frontend, cấu hình camera, thời gian chờ no-show và một số chính sách nghiệp vụ chưa chốt.

## 10.2. Rủi ro và ứng phó

| Rủi ro | Ảnh hưởng | Ứng phó |
| --- | --- | --- |
| Thư viện không cho lắp camera | Rất cao | Xin phép sớm; dùng video mẫu được phép hoặc khu vực thử nghiệm được chấp thuận. |
| Laptop không đủ mạnh | Trung bình | Dùng YOLOv8n, giảm độ phân giải/FPS, giới hạn vùng quan tâm, đánh giá offline. |
| Đếm sai do che khuất/đông | Trung bình | Điều chỉnh góc camera/đường ảo; phân tích lỗi và báo cáo giới hạn. |
| Container không truy cập webcam | Trung bình | Chạy CV/AI ngoài Docker hoặc xử lý video mẫu trong container. |
| Lo ngại quyền riêng tư | Cao | Xử lý tại chỗ, không nhận diện danh tính, không lưu video lâu dài, có biển báo/chấp thuận. |
| Trễ tiến độ | Cao | Ưu tiên Must; chỉ làm Should khi Must ổn định; loại Could trước. |
| Camera giao chậm hoặc hỏng | Cao | Đặt hàng ngay Tuần 2; chuẩn bị camera dự phòng. |
| Thành viên bận hoặc nghỉ | Cao | Phân công người dự phòng; tài liệu hóa công việc. |
| Số đếm bị lệch | Trung bình | Ghi thời điểm/nguồn, cảnh báo dữ liệu cũ, xác định quy trình hiệu chỉnh. |

# 11. Các vấn đề cần xác nhận

Các mục sau chưa được xem là yêu cầu nghiệp vụ đã phê duyệt; cần thống nhất với giảng viên và đại diện thư viện.

| STT | Vấn đề |
| --- | --- |
| 1 | Hình thức đăng ký/xác minh tài khoản: email cá nhân hay email sinh viên. |
| 2 | Ai được quyền thêm, sửa hoặc ngừng sử dụng phòng. |
| 3 | Sức chứa chính thức của phòng đọc và từng phòng học nhóm. |
| 4 | Thời lượng đặt tối thiểu/tối đa, thời gian đặt trước và khoảng cách giữa hai lượt. |
| 5 | Quy tắc hủy đặt phòng và thời hạn hủy. |
| 6 | Thời gian chờ check-in trước khi đánh dấu no-show (ví dụ 10–15 phút; cần chốt). |
| 7 | Quy trình check-in QR: camera điện thoại, máy quét riêng hay giao diện web. |
| 8 | Vị trí/góc lắp camera và phần cứng xử lý AI được thư viện phê duyệt. |
| 9 | Điều kiện để chạy camera AI trực tiếp hay chỉ đánh giá offline. |
| 10 | Phiên bản và cấu hình triển khai PostgreSQL (đã chốt là CSDL chính theo Charter v1.2). |
| 11 | Thời hạn lưu dữ liệu đặt phòng, dữ liệu đếm/video; ai được truy cập. |
| 12 | Ngưỡng phân loại mức độ đông của phòng. |
| 13 | Thời gian chạy liên tục mục tiêu. |
| 14 | Môi trường, tải thử nghiệm và công thức chính thức cho KPI. |
| 15 | Cách hiệu chỉnh khi camera bỏ sót sự kiện hoặc số đếm bị lệch. |
| 16 | Framework frontend và định dạng API/payload giữa CV/AI và backend. |

# 12. Phê duyệt

| Vai trò | Người phê duyệt | Ngày | Chữ ký |
| --- | --- | --- | --- |
| Đại diện nhóm dự án | Vũ Nguyễn Nhã Uyên |  |  |
| Giáo viên hướng dẫn | TS. Đặng Nhân Cánh |  |  |
| Đại diện Thư viện UTH | Chưa xác định |  |  |

Kết luận: SRS được xây dựng theo Project Charter UTH-SeatSense phiên bản 1.2 và phạm vi đã chốt. Cần cập nhật sau khảo sát, xác nhận nghiệp vụ với thư viện và thử nghiệm camera AI.

# Phụ lục A. Nguồn dự án

Kho mã nguồn: https://github.com/uth-seatsense/UTH-SeatSense

Bảng công việc: https://nhauyen70205.atlassian.net/jira/software/projects/SEAT/boards/2?filter=&groupBy=none

Hướng dẫn chạy: README.md trong kho mã nguồn.

Lưu ý: KPI là mục tiêu để đo lường, không phải kết quả đã xác minh. Các quy tắc còn mở cần được phê duyệt trước khi ban hành bản chính thức.
