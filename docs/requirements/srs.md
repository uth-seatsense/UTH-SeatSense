

# UTH-SeatSense

TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM<br>SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

Hệ thống theo dõi mật độ sử dụng phòng đọc<br>và đặt phòng học nhóm tại Thư viện UTH

| Thông tin | Nội dung |
| --- | --- |
| Mã đề tài | D6 – Đặt chỗ và theo dõi mật độ sử dụng phòng đọc |
| Phiên bản | 1.8 – Duyệt nội bộ; chờ xác nhận thư viện trước triển khai |
| Ngày cập nhật | 10/11/2026 |
| Đơn vị hưởng lợi | Trung tâm Thông tin Thư viện UTH |
| Quản lý dự án | Vũ Nguyễn Nhã Uyên |
| Giáo viên hướng dẫn | TS. Đặng Nhân Cánh |
| Nhóm phát triển | Nhóm dự án UTH-SeatSense |
| Thời gian dự án | 26/10/2026 – 26/12/2026 |
| Trạng thái | Uyên duyệt nội bộ ngày 10/11/2026; 5 email thư viện hoãn đến trước triển khai tại thư viện |

Tài liệu làm cơ sở thống nhất yêu cầu, thiết kế, phát triển, kiểm thử và đánh giá sản phẩm.

## Lịch sử phiên bản

| Phiên bản | Ngày | Mô tả | Trạng thái |
| --- | --- | --- | --- |
| 1.0 | 26/10/2026 | Bản SRS rút gọn ban đầu | Dự thảo |
| 1.1 | 28/10/2026 | Cập nhật camera AI và Docker Compose | Dự thảo |
| 1.2 | 28/10/2026 | Chuẩn hóa theo Project Charter v1.2; bỏ IoT/cảm biến khỏi phạm vi | Chờ rà soát |
| 1.3 | 07/11/2026 | Chuyển sang kiểm thử bằng webcam laptop; bỏ lắp đặt camera tại thư viện; chốt React + Vite; chạy CV/AI ngoài Docker; cập nhật theo Project Charter v1.3 | Chờ rà soát |
| 1.4 | 07/11/2026 | Chia hai loại không gian; PWA thay app native; đăng nhập OTP qua email, bỏ đăng ký riêng; portal là tùy chọn | Chờ rà soát |
| 1.5 | 07/11/2026 | Thêm ứng dụng Android native; hỗ trợ hai cơ sở CS1 và CS3; triển khai thử nghiệm tại thư viện khi đủ điều kiện; cập nhật camera, quyền riêng tư, rủi ro | Chờ rà soát |
| 1.6 | 07/11/2026 | Chốt dùng webcam của máy tính cho cả kiểm thử và triển khai; bỏ chi phí mua camera; cập nhật mô tả camera, giả định, rủi ro | Chờ rà soát |
| 1.7 | 10/11/2026 | Chuẩn hóa quyết định, cập nhật FR/BR/KPI và ghi nhận Uyên duyệt nội bộ; email thư viện hoãn đến trước triển khai tại thư viện | Duyệt nội bộ |
| 1.8 | 10/11/2026 | Đối chiếu lại với Charter; chốt ByteTrack, quy trình ghi nhận số người ban đầu, hiệu chỉnh có truy vết và truy cập thử nghiệm qua Wi-Fi; đổi tên bản SRS cho khớp phiên bản | Duyệt nội bộ |

## Mục lục nội dung

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

## 1. Giới thiệu

### 1.1. Mục đích tài liệu

Tài liệu SRS mô tả các yêu cầu chức năng, phi chức năng, giao diện, dữ liệu, quy tắc nghiệp vụ và tiêu chí kiểm thử của UTH-SeatSense. Đây là cơ sở thống nhất yêu cầu giữa nhóm phát triển, người dùng và đơn vị quản lý thư viện; hỗ trợ thiết kế, phát triển, kiểm thử và đánh giá sản phẩm.

### 1.2. Phạm vi sản phẩm

UTH-SeatSense là hệ thống gồm web responsive và ứng dụng Android native hỗ trợ người dùng xem mật độ khu tự học tự do (chỉ xem, không đặt chỗ) và đặt phòng chuyên đề theo khung giờ tại Thư viện UTH; hệ thống triển khai thử nghiệm tại hai thư viện CS1 và CS3; sinh viên dùng ứng dụng Android hoặc web, thủ thư dùng web. Webcam của máy tính kết hợp YOLOv8 phiên bản nhẹ và ByteTrack để phát hiện/theo dõi người, đếm lượt vào/ra khi người cắt đường ảo. Mô-đun AI gửi số liệu đếm lên backend, không gửi danh tính người.

Phạm vi thử nghiệm: triển khai thử nghiệm tại hai thư viện CS1 và CS3, mỗi cơ sở có 01 khu tự học tự do và các phòng chuyên đề; trước khi đủ điều kiện triển khai, kiểm thử trong môi trường của nhóm bằng webcam laptop.

Website responsive: xem chỗ trống/mức độ đông của khu tự học tự do, đặt phòng chuyên đề theo khung giờ, check-in QR, đăng nhập bằng mã OTP qua email và dashboard thủ thư.

Ứng dụng Android native cho sinh viên: đăng nhập OTP, xem chỗ trống khu tự học tự do, đặt phòng chuyên đề, check-in QR (quét bằng camera điện thoại); dùng chung API với web.

Backend dự kiến dùng FastAPI; cơ sở dữ liệu PostgreSQL; các dịch vụ chạy bằng Docker Compose.

Thực nghiệm đối chiếu đếm tay, đánh giá trải nghiệm bằng SUS, báo cáo kết quả và kế hoạch kinh doanh.

### 1.3. Ngoài phạm vi

ESP32, cảm biến khoảng cách và phần cứng IoT dùng để đếm người.

Nhận diện khuôn mặt, nhận dạng danh tính hoặc theo dõi cá nhân.

Thay đổi hạ tầng của thư viện (cửa, điện, mạng) ngoài việc đặt máy tính có webcam.

Đặt chỗ cho khu tự học tự do (chỉ xem mật độ và chỗ trống).

Lưu trữ video/hình ảnh lâu dài; video nghiên cứu nếu được phép chỉ lưu tạm và xóa sau đánh giá.

Dự báo mật độ và thông báo chỗ trống là tính năng tùy chọn, không bắt buộc trong bản đầu; đăng nhập qua portal của trường chỉ làm nếu trường cấp quyền; web cài được (PWA).

Tích hợp hệ thống đào tạo/đăng nhập portal chính thức của trường (chỉ làm nếu trường cấp văn bản đồng ý và cách kết nối chính thức).

### 1.4. Thuật ngữ

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

### 1.5. Tài liệu tham chiếu

Project Charter: UTH-SeatSense, đề tài D6, phiên bản 1.7, cập nhật 10/11/2026.

IEEE 29148 – Systems and Software Engineering: Requirements Engineering (tham khảo).

Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân và quy định liên quan áp dụng tại thời điểm triển khai.

Tài liệu kỹ thuật FastAPI, PostgreSQL, Docker Compose, YOLOv8 và ByteTrack.

## 2. Mô tả tổng quan

### 2.1. Bối cảnh và vấn đề

Sinh viên có thể phải đến thư viện mới biết phòng đọc còn chỗ hay không; phòng học nhóm có thể được đặt nhưng không sử dụng; thủ thư thiếu dữ liệu mật độ theo giờ/ngày. Các vấn đề và mức độ ảnh hưởng cần được xác minh qua khảo sát sinh viên và phỏng vấn thủ thư, không xem giả định ban đầu là kết quả khảo sát.

### 2.2. Mục tiêu hệ thống

Hiển thị số người ước tính, số chỗ trống và mức độ đông của khu tự học tự do gần thời gian thực.

Cho phép sinh viên tìm phòng chuyên đề khả dụng, đặt phòng theo khung giờ và nhận xác nhận.

Hỗ trợ check-in QR và xử lý no-show theo quy tắc được thư viện phê duyệt.

Cung cấp dashboard thống kê mật độ, tỷ lệ sử dụng phòng và tỷ lệ no-show cho thủ thư.

Đánh giá sai số, tốc độ xử lý và độ trễ cập nhật của phương pháp camera AI.

Chuẩn hóa môi trường bằng Docker Compose; lập báo cáo thực nghiệm và kế hoạch kinh doanh.

### 2.3. Nhóm người dùng

| Vai trò | Nhu cầu và quyền chính |
| --- | --- |
| Sinh viên/người dùng | Dùng app Android hoặc web: xem tình trạng khu tự học tự do, đăng nhập bằng OTP qua email sinh viên, đặt phòng chuyên đề, xem lịch đặt và check-in QR cho lượt đặt hợp lệ của mình. |
| Thủ thư/quản lý | Xem dashboard; quản lý thông tin phòng, sức chứa và quy tắc vận hành theo quyền được cấp. |
| Nhóm phát triển/vận hành | Cấu hình camera AI/đường ảo; theo dõi lỗi; kiểm thử, đo FPS và sai số. |

### 2.4. Kiến trúc khái quát

Luồng dữ liệu dự kiến: Webcam máy tính → mô-đun CV/AI (YOLOv8n + ByteTrack + đếm qua đường ảo) → dữ liệu số lượng vào/ra → Backend FastAPI → PostgreSQL → website responsive/dashboard.

| Thành phần | Công nghệ dự kiến | Trách nhiệm |
| --- | --- | --- |
| CV/AI | Webcam của máy tính, YOLOv8n, ByteTrack | Phát hiện/theo dõi người, đếm qua đường ảo; chỉ gửi số liệu đếm. |
| Backend/API | FastAPI | Xác thực OTP, đặt phòng chuyên đề, check-in, no-show, tiếp nhận dữ liệu và cung cấp API. |
| Cơ sở dữ liệu | PostgreSQL | Lưu tài khoản, phòng, đặt chỗ, check-in, mật độ và sự kiện. |
| Frontend | Web responsive; React + Vite (JavaScript) | Hiển thị chỗ trống, đặt phòng, QR và dashboard. |
| Ứng dụng Android | Android native bằng Kotlin; thử nghiệm bằng APK trực tiếp | Giao diện sinh viên: xem chỗ trống, đặt phòng chuyên đề, check-in QR; gọi cùng API với web. |
| Dịch vụ email | SMTP (thử nghiệm dùng bộ bắt email giả trong Docker Compose) | Gửi mã OTP đăng nhập tới email sinh viên. |
| Đóng gói | Docker Compose | Khởi chạy dịch vụ nhất quán; quản lý cấu hình và volume dữ liệu. |

Quyết định: Docker Desktop trên Windows/macOS có thể hạn chế truy cập webcam từ container, nên mô-đun CV/AI chạy ngoài Docker và đọc trực tiếp webcam của máy tính; backend, cơ sở dữ liệu và frontend chạy bằng Docker Compose. Khả năng chạy trực tiếp phải được xác minh trên laptop của nhóm; nếu không đạt, đánh giá offline trên video quay thử của nhóm.

### 2.5. Môi trường vận hành

Trình duyệt hiện đại trên máy tính, máy tính bảng và điện thoại.

Khi kiểm thử: laptop chạy CV/AI có webcam tích hợp (hoặc webcam rời mượn) hoặc video quay thử của nhóm. Kiểm thử với người ngoài nhóm ưu tiên cùng Wi-Fi; chỉ dùng đường hầm hoặc hosting khi Uyên phê duyệt, có xác thực và giới hạn truy cập. Khi triển khai: máy tính có webcam đặt tại mỗi khu tự học của CS1 và CS3 sau khi được phép.

Backend, cơ sở dữ liệu và frontend chạy bằng Docker Compose; cấu hình nhạy cảm đặt trong biến môi trường.

Cấu hình phần cứng và thời gian chạy liên tục sẽ được xác nhận sau thử nghiệm.

### 2.6. Hai loại không gian

Mỗi phòng có thuộc tính loại (room_type) với hai giá trị:

Khu tự học tự do (free_area): chỉ xem số người ước tính, chỗ trống và mức độ đông từ camera đếm qua đường ảo; không đặt chỗ, không check-in.

Phòng chuyên đề (topic_room): xem lịch khung giờ, đặt cho nhóm, check-in QR, tự nhả phòng khi quá thời gian chờ.

API đặt phòng từ chối yêu cầu đặt cho khu tự học tự do; dữ liệu đếm chỉ gắn với khu tự học tự do.

### 2.7. Ứng dụng cho sinh viên và đăng nhập

Ứng dụng cho sinh viên là ứng dụng Android native viết bằng Kotlin, phát hành thử nghiệm bằng APK trực tiếp và dùng chung API với web; web responsive vẫn dùng cho thủ thư và sinh viên dùng trình duyệt; không làm ứng dụng iOS. Đăng nhập và đăng ký là một luồng:

Sinh viên nhập email trong danh sách cho phép, nhận OTP 6 số (tạm hết hạn sau 5 phút; tối đa 5 lần nhập sai; gửi lại sau 60 giây), nhập mã để vào; lần đầu hệ thống tự tạo hồ sơ, không có mật khẩu. Các ngưỡng tạm chờ nhóm rà soát bảo mật.

Giai đoạn thử nghiệm dùng danh sách email được phép và tài khoản demo do nhóm tạo; thủ thư do nhóm gán vai trò.

Chỉ khi trường cấp văn bản đồng ý và cách kết nối chính thức mới thêm đăng nhập qua portal, qua một lớp đăng nhập thay thế được. Nhóm không nhận hoặc lưu mật khẩu portal của sinh viên.

### 2.8. Hai cơ sở thư viện (CS1 và CS3)

Hệ thống hỗ trợ nhiều cơ sở thư viện; giai đoạn này gồm CS1 và CS3 của trường.

Mỗi phòng thuộc một cơ sở; mỗi cơ sở có camera đếm, khu tự học tự do và phòng chuyên đề riêng.

Sinh viên chọn cơ sở khi xem tình trạng hoặc đặt phòng; thủ thư xem dashboard theo từng cơ sở và tổng hợp.

Số đếm, sức chứa và đường ảo được cấu hình riêng cho từng khu của từng cơ sở; các cơ sở dùng chung một backend và một cơ sở dữ liệu.

## 3. Yêu cầu giao diện ngoài

### 3.1. Giao diện người dùng

| Mã | Giao diện | Yêu cầu |
| --- | --- | --- |
| UI-01 | Đăng nhập bằng mã OTP | Nhập email sinh viên rồi nhập mã 6 số; thông báo lỗi chung, không tiết lộ email đã có tài khoản hay chưa. |
| UI-02 | Trang tình trạng khu tự học tự do | Tên phòng, sức chứa, số người ước tính, chỗ trống, mức độ đông và thời điểm cập nhật. |
| UI-03 | Đặt phòng chuyên đề | Chọn ngày/giờ/phòng chuyên đề; xem khả dụng; xác nhận kết quả và báo trùng lịch. |
| UI-04 | Lịch đặt/QR | Hiển thị lượt đặt của người dùng và QR/mã check-in hợp lệ. |
| UI-05 | Dashboard | Bộ lọc thời gian/phòng; biểu đồ mật độ, tỷ lệ sử dụng và no-show nếu có dữ liệu. |
| UI-06 | Trạng thái dữ liệu | Cảnh báo dữ liệu lỗi thời/mất kết nối; không hiển thị dữ liệu cũ như mới. |
| UI-07 | Responsive | Tự điều chỉnh theo màn hình; luồng chính không cần cuộn ngang trên điện thoại. |
| UI-08 | Ứng dụng Android | Bố cục phù hợp màn hình điện thoại; luồng xem chỗ trống, đặt phòng, check-in QR dùng được; dùng chung API với web. |

### 3.2. Giao diện phần mềm

Frontend trao đổi với backend qua API.

Mô-đun CV/AI gửi sự kiện/số lượng vào-ra kèm mã phòng, thời điểm và trạng thái nguồn dữ liệu.

PostgreSQL lưu dữ liệu có cấu trúc; thông tin kết nối quản lý qua biến môi trường.

Docker Compose định nghĩa dịch vụ, mạng, cấu hình và volume dữ liệu.

Backend gửi email mã OTP qua dịch vụ SMTP; thông tin kết nối đặt trong biến môi trường.

### 3.3. Giao diện camera/phần cứng

Khi kiểm thử, hệ thống dùng webcam tích hợp (hoặc webcam rời) của laptop chạy CV/AI. Việc đặt máy/webcam tại CS1 hoặc CS3 chỉ được thực hiện sau khi có văn bản đồng ý của đơn vị quản lý và thống nhất vị trí, góc nhìn, mạng, điện, cấu hình máy. Đề xuất hướng máy vào lối đi, hạn chế thu hình nhận diện, cố định vùng quan sát và cấu hình đường ảo. CV/AI chạy ngoài Docker và đọc trực tiếp webcam; đánh giá offline trên video thử là phương án bắt buộc/dự phòng. Không quay tại thư viện trước khi được phép.

### 3.4. Giao diện truyền thông

Hợp đồng bản ghi CV cục bộ hiện là schema v1.0; dùng `event_id` hoặc `(session_id, frame_index)` để chống ghi trùng và timestamp UTC có múi giờ theo hợp đồng dữ liệu. Backend chưa có endpoint CV qua mạng, xác thực hoặc retry được chốt trong hợp đồng này; nhóm Backend/CV phải thống nhất các phần đó trước tích hợp. Không tự cộng các counter tích lũy qua từng frame.

## 4. Yêu cầu chức năng

Mỗi yêu cầu được đánh mã để truy vết sang thiết kế và kiểm thử. Ưu tiên: Must (bắt buộc), Should (nên có), Could (có thể bổ sung).

| Mã | Tên | Mô tả | Ưu tiên |
| --- | --- | --- | --- |
| FR-AUTH-01 | Tự tạo hồ sơ lần đầu | Tự tạo hồ sơ ở lần đầu xác minh OTP thành công với email thuộc danh sách được phép; không có màn hình đăng ký riêng và không dùng mật khẩu. | Must |
| FR-AUTH-02 | Đăng nhập OTP/đăng xuất | Gửi mã OTP 6 số qua email sinh viên trong danh sách cho phép; mã dùng một lần, hết hạn sau 5 phút; cấp phiên đăng nhập và cho phép kết thúc phiên. | Must |
| FR-AUTH-03 | Phân quyền | Phân biệt người dùng và thủ thư/quản lý; chặn thao tác trái quyền. | Must |
| FR-AUTH-04 | Bảo vệ mã OTP | Mã OTP chỉ lưu dạng băm, dùng một lần, hết hạn sau 5 phút; hủy mã sau 5 lần nhập sai; giới hạn gửi lại một lần mỗi 60 giây; thông báo lỗi chung. Các ngưỡng là tạm thời đến khi nhóm rà soát bảo mật. | Must |
| FR-AUTH-05 | Đăng nhập qua portal (tùy chọn) | Mặc định dùng OTP email. Chỉ bổ sung SSO/API portal sau khi có văn bản đồng ý, đầu mối kỹ thuật và phương thức tích hợp chính thức; không nhận hoặc lưu mật khẩu portal. | Could |
| FR-OCC-01 | Nhận dữ liệu đếm | Tiếp nhận số lượng/sự kiện vào-ra kèm mã phòng và thời điểm. | Must |
| FR-OCC-02 | Cập nhật số người | Cập nhật số người hiện tại từ số ban đầu của phiên và từng sự kiện vào/ra hợp lệ đúng một lần; không cộng lại counter tích lũy của mỗi frame. | Must |
| FR-OCC-03 | Tính chỗ trống | Khi sức chứa và số người ban đầu đã được xác nhận/cấu hình, tính max(0, sức chứa − số người ước tính); nếu cấu hình chưa được xác nhận, không hiển thị số chỗ trống như dữ liệu chính thức. | Must |
| FR-OCC-04 | Hiển thị mật độ | Hiển thị số người ước tính, sức chứa, chỗ trống, mức độ đông và thời điểm cập nhật; khi sức chứa chưa được xác nhận, báo rõ dữ liệu đang chờ cấu hình. | Must |
| FR-OCC-05 | Trạng thái nguồn | Cảnh báo dữ liệu lỗi thời hoặc nguồn đếm mất kết nối. | Must |
| FR-OCC-06 | Khởi tạo số người | Khi bắt đầu mỗi phiên đếm, người vận hành ghi số người đang có mặt sau khi kiểm tra khu vực; nếu không xác định được số ban đầu thì không công bố số chỗ trống/mức đông chính thức cho đến khi được hiệu chỉnh. | Must |
| FR-ROOM-01 | Loại không gian | Mỗi phòng có loại free_area (khu tự học tự do) hoặc topic_room (phòng chuyên đề). Khu tự học tự do chỉ xem, không đặt chỗ; hệ thống từ chối yêu cầu đặt chỗ cho free_area. | Must |
| FR-SITE-01 | Nhiều cơ sở | Mỗi phòng thuộc một cơ sở (CS1 hoặc CS3); giao diện và API lọc theo cơ sở; dashboard xem theo từng cơ sở và tổng hợp. | Must |
| FR-SITE-02 | Triển khai tại hai cơ sở | Cấu hình riêng cho từng cơ sở (camera, đường ảo, sức chứa, nguồn dữ liệu); mỗi cơ sở có máy xử lý CV/AI gửi dữ liệu về backend chung. | Should |
| FR-CV-01 | Phát hiện người | Dùng YOLOv8 phiên bản nhẹ phát hiện người trong vùng quan sát. | Must |
| FR-CV-02 | Theo dõi đối tượng | Dùng ByteTrack để theo dõi tạm thời qua khung hình theo phương án đã chốt trong Charter. | Must |
| FR-CV-03 | Đếm qua đường ảo | Ghi nhận hướng vào/ra khi đối tượng cắt đường ảo; hạn chế đếm lặp. | Must |
| FR-CV-04 | Đánh giá offline | Cho phép chạy trên video quay thử của nhóm nếu demo trực tiếp không đạt. | Must |
| FR-BOOK-01 | Xem phòng khả dụng | Xem phòng chuyên đề và khung giờ còn khả dụng. | Must |
| FR-BOOK-02 | Tạo đặt phòng | Chọn phòng, ngày, giờ bắt đầu/kết thúc và số thành viên để tạo lượt đặt. | Must |
| FR-BOOK-03 | Kiểm tra hợp lệ | Kiểm tra phòng chuyên đề, quyền đặt, thời lượng 30–120 phút, thời điểm đặt trước không quá 7 ngày, nhóm 2–6 người và tối đa một lượt/người/ngày theo giới hạn tạm; từ chối nếu không hợp lệ. | Must |
| FR-BOOK-04 | Ngăn trùng lịch | Từ chối lượt đặt chồng lấn trên cùng phòng kể cả yêu cầu đồng thời; tạm yêu cầu cách hai lượt ít nhất 15 phút. | Must |
| FR-BOOK-05 | Xác nhận đặt | Lưu lượt đặt thành công và hiển thị xác nhận. | Must |
| FR-BOOK-06 | Xem/hủy lượt đặt | Cho xem lượt đặt cá nhân; tạm cho hủy đến 30 phút trước giờ bắt đầu, sau đó yêu cầu thủ thư xử lý. | Should |
| FR-CHK-01 | Tạo QR | Tạo/hiển thị QR hoặc mã check-in gắn với lượt đặt hợp lệ. | Should |
| FR-CHK-02 | Xác minh QR | Xác minh mã, trạng thái và thời gian lượt đặt. | Should |
| FR-CHK-03 | Ghi nhận check-in | Lưu thời điểm và cập nhật trạng thái sau check-in hợp lệ. | Should |
| FR-BOOK-07 | Xử lý no-show | Tạm đánh dấu no-show và giải phóng khung giờ khi đã đủ 15 phút sau giờ bắt đầu mà chưa check-in; khoảng chờ phải cấu hình được để thay đổi theo quyết định thư viện. | Should |
| FR-DASH-01 | Dashboard mật độ | Thủ thư xem thống kê mật độ theo thời gian và phòng. | Should |
| FR-DASH-02 | Thống kê vận hành | Hiển thị tỷ lệ sử dụng, số lượt đặt, no-show nếu có dữ liệu. | Should |
| FR-ADMIN-01 | Quản lý phòng | Chỉ tài khoản quản trị được nhóm cấp quyền mới sửa cấu hình trong môi trường thử nghiệm; danh mục/sức chứa dùng tại thư viện phải do đại diện thư viện xác nhận. Lưu nhật ký người sửa, thời điểm và nội dung thay đổi; không xóa cứng phòng đã có giao dịch. | Should |
| FR-APP-01 | Ứng dụng Android | Nếu thực hiện, làm ứng dụng Android native (tạm chọn Kotlin), cài thử bằng APK trực tiếp; hỗ trợ đăng nhập OTP, xem tình trạng khu tự học tự do, đặt phòng chuyên đề, check-in QR và dùng chung API với web. iOS ngoài phạm vi. | Should |
| FR-PWA-01 | Web cài được (PWA) | Web có manifest và service worker để cài lên màn hình điện thoại; không thay thế quyết định về phạm vi ứng dụng Android native. | Could |
| FR-OPS-01 | Docker Compose | Khởi chạy các dịch vụ chính bằng Docker Compose theo README. | Must |
| FR-OPS-02 | Dữ liệu bền vững | Dùng volume để dữ liệu PostgreSQL không mất khi container restart. | Must |
| FR-EXP-01 | Đối chiếu đếm tay | Đối chiếu dữ liệu camera với đếm tay trong các phiên thử nghiệm. | Must |
| FR-EXP-02 | Đánh giá SUS | Khảo sát SUS và tổng hợp kết quả thử nghiệm người dùng. | Should |
| FR-EXP-03 | Báo cáo/kinh doanh | Lập báo cáo thực nghiệm và kế hoạch kinh doanh về doanh thu, chi phí, điểm hòa vốn. | Must |
| FR-OPT-01 | Dự báo/thông báo | Có thể bổ sung dự báo 1–2 giờ hoặc thông báo chỗ trống sau khi Must/Should ổn định. | Could |

## 5. Yêu cầu phi chức năng

| Mã | Thuộc tính | Yêu cầu/tiêu chí | Trạng thái |
| --- | --- | --- | --- |
| NFR-PER-01 | Độ trễ | Mục tiêu tạm: phân vị 95 (p95) từ lúc ghi nhận sự kiện đến lúc hiển thị trên web ≤ 5 giây trong môi trường thử nghiệm. | Chờ thầy hướng dẫn xác nhận |
| NFR-PER-02 | Tốc độ AI | Mục tiêu tạm: trung vị ≥ 5 FPS ở khoảng 416 px, đo ít nhất 60 giây; nếu không đạt, đánh giá offline và ghi rõ môi trường. | Chờ thầy hướng dẫn xác nhận |
| NFR-ACC-01 | Độ chính xác | Mục tiêu tạm: sai số tổng hợp = tổng \|đếm camera − đếm tay\| / tổng đếm tay × 100% ≤ 10%; phiên có tổng đếm tay bằng 0 báo riêng bằng sai số tuyệt đối, không chia cho 0. | Chờ thầy hướng dẫn xác nhận |
| NFR-REL-01 | Độ ổn định | Mục tiêu tạm: chạy liên tục ít nhất 4 giờ trong một phiên kiểm thử; ghi nhật ký lỗi/mất kết nối. Đây không phải cam kết SLA khi triển khai. | Chờ thầy hướng dẫn xác nhận |
| NFR-USA-01 | Khả dụng | Nhãn, thông báo và luồng thao tác rõ ràng cho sinh viên/thủ thư. |  |
| NFR-USA-02 | Responsive | Các luồng xem phòng, đặt phòng, check-in thích ứng desktop/tablet/mobile. |  |
| NFR-USA-03 | SUS | Mục tiêu SUS ≥ 70 với khoảng 15–30 sinh viên thử nghiệm; chưa phải kết quả đạt được. | Cần đo |
| NFR-SEC-01 | Xác thực | API/trang quản lý kiểm tra phiên và quyền; hệ thống không lưu mật khẩu, mã OTP chỉ lưu dạng băm, dùng một lần và có hạn. |  |
| NFR-SEC-02 | Bí mật | Khóa và thông tin kết nối đặt trong biến môi trường, không commit vào kho mã nguồn. |  |
| NFR-PRI-01 | Không định danh | Không nhận diện khuôn mặt/danh tính; ID tracker chỉ phục vụ theo dõi tạm thời. |  |
| NFR-PRI-02 | Giảm thiểu ảnh | Ưu tiên xử lý tại chỗ, chỉ truyền số liệu đếm lên server; không lưu video lâu dài. |  |
| NFR-PRI-03 | Video nghiên cứu | Không lưu video sau xử lý. Chỉ quay thử người đã đồng ý. Tạm giữ bản ghi số đếm tổng hợp tối đa 90 ngày sau đánh giá; dữ liệu đặt phòng gắn người dùng được xóa/ẩn danh trong 30 ngày sau khi kết thúc dự án. Khi triển khai cần văn bản đồng ý, biển thông báo và phân quyền; thời hạn lưu chờ nhà trường/thư viện duyệt. | Chờ xác nhận |
| NFR-MNT-01 | Bảo trì | Mã nguồn chia module, có README và hướng dẫn cấu hình/chạy. |  |
| NFR-DEP-01 | Triển khai | Docker Compose mô tả dịch vụ và cung cấp tệp .env.example. |  |
| NFR-DAT-01 | Nhất quán | Kiểm tra dữ liệu đặt phòng và ngăn trùng ở backend/cơ sở dữ liệu. |  |

## 6. Mô hình dữ liệu và quy tắc nghiệp vụ

### 6.1. Thực thể dữ liệu dự kiến

| Thực thể | Trường tiêu biểu | Mục đích |
| --- | --- | --- |
| User | user_id, display_name, email, student_code, role, created_at | Tài khoản và quyền. |
| LoginCode | code_id, email, code_hash, expires_at, attempts, used_at | Mã OTP đăng nhập (chỉ lưu dạng băm). |
| Room | room_id, room_name, room_type, capacity, campus (CS1/CS3), location, status | Phòng, sức chứa, cơ sở và loại không gian (free_area hoặc topic_room). |
| OccupancyRecord | record_id, room_id, current_count, available_seats, source, recorded_at, device_status | Dữ liệu mật độ theo thời gian. |
| OccupancyAdjustment | adjustment_id, room_id, session_id, previous_count, adjusted_count, reason, actor_id, created_at | Số đếm ban đầu/hiệu chỉnh có truy vết, không sửa sự kiện CV thô. |
| Booking | booking_id, user_id, room_id, start_time, end_time, participant_count, status, created_at, checkin_at | Lượt đặt phòng; participant_count kiểm tra giới hạn nhóm tạm thời. |
| CheckIn | checkin_id, booking_id, checkin_time, method, status | Kết quả check-in. |
| CountEvent | event_id, room_id, direction, event_time, received_at, source | Sự kiện vào/ra. |
| AuditLog | log_id, actor_id, action, created_at, detail | Nhật ký thao tác quản trị nếu cần. |

### 6.2. Quy tắc nghiệp vụ

| Mã | Quy tắc |
| --- | --- |
| BR-01 | Khi bắt đầu phiên, người vận hành ghi số người thực tế đang có mặt làm số ban đầu; số người ước tính = max(0, số ban đầu + tổng IN − tổng OUT hợp lệ trong phiên); số chỗ trống = max(0, sức chứa đã xác nhận − số người ước tính). Không hiển thị chỗ trống/mức đông chính thức nếu thiếu số ban đầu hoặc sức chứa đã xác nhận. |
| BR-02 | Số chỗ trống không được âm; số người vượt sức chứa cần được đánh dấu. |
| BR-03 | Lượt đặt tạm dài 30–120 phút, phải bắt đầu trong vòng 7 ngày tiếp theo và có thời gian kết thúc sau thời gian bắt đầu. |
| BR-04 | Các lượt đặt hợp lệ trên cùng phòng không được chồng lấn; tạm yêu cầu cách nhau ít nhất 15 phút để chuẩn bị phòng. |
| BR-05 | Chỉ lượt đặt hợp lệ, chưa hủy và trước thời điểm giờ bắt đầu + 15 phút mới được check-in; tại hoặc sau thời điểm đó, lượt chưa check-in được xử lý no-show. |
| BR-06 | Lượt đã check-in không được xử lý lại thành no-show. |
| BR-07 | Tạm đánh dấu no-show nếu lượt đặt chưa check-in sau 15 phút kể từ giờ bắt đầu; thời gian chờ phải cấu hình được và chờ thư viện xác nhận. |
| BR-08 | Khi no-show, cập nhật trạng thái và giải phóng phần thời gian còn lại theo cấu hình; ghi nhận thời điểm xử lý để kiểm tra. |
| BR-09 | Người dùng chỉ xem/thao tác lượt đặt của mình, trừ vai trò có quyền. |
| BR-10 | Chỉ người được phân quyền truy cập dashboard quản lý. |
| BR-11 | Camera không được nhận diện khuôn mặt hoặc định danh cá nhân. |
| BR-12 | Khi dữ liệu lỗi thời/mất kết nối, giao diện phải hiển thị cảnh báo. |
| BR-13 | Mỗi bản ghi đếm có phòng, thời điểm và nguồn; sự kiện trùng phải được khử theo event_id hoặc (session_id, frame_index). Không cộng counter tích lũy qua các frame. |
| BR-14 | Chỉ phòng chuyên đề được đặt chỗ; khu tự học tự do không nhận đặt chỗ. |
| BR-15 | Mã OTP 6 số tạm có hiệu lực 5 phút, chỉ dùng một lần, chỉ lưu dạng băm; mã bị hủy sau 5 lần nhập sai và chỉ cho gửi lại sau 60 giây. |
| BR-16 | Mặc định dùng OTP email; không nhận/lưu mật khẩu portal. Chỉ tích hợp SSO/API chính thức sau khi có văn bản đồng ý và đầu mối kỹ thuật của trường. |
| BR-17 | Mỗi phòng thuộc đúng một cơ sở; số đếm và đặt chỗ được tính riêng theo từng phòng và cơ sở. |
| BR-18 | Tạm giới hạn nhóm 2–6 người và một lượt đặt/người/ngày; thư viện phải xác nhận sức chứa nhóm và giới hạn vận hành trước khi dùng thật. |
| BR-19 | Tạm cho người đặt hủy trước giờ bắt đầu ít nhất 30 phút; sau thời hạn này, thủ thư xử lý ngoại lệ. |
| BR-20 | Chỉ tài khoản được cấp quyền quản trị mới sửa danh mục phòng; các thay đổi ghi người thực hiện, thời gian và nội dung. Phòng có lịch sử đặt không bị xóa cứng. |
| BR-21 | Số người ban đầu/hiệu chỉnh phải lưu thành bản ghi riêng có phiên, người thực hiện, thời gian, giá trị trước/sau và lý do; không sửa/xóa sự kiện CV thô hoặc lịch sử đã ghi. Mỗi phiên mới cần số ban đầu mới. |
| BR-22 | Không lưu video. Thời hạn tạm: số đếm tổng hợp tối đa 90 ngày sau đánh giá; dữ liệu đặt phòng có thể nhận diện người dùng xóa/ẩn danh trong 30 ngày sau khi kết thúc dự án; chỉ vai trò được cấp quyền mới truy cập. Chờ phê duyệt quyền riêng tư. |
| BR-23 | Mức đông tạm tính theo tỷ lệ số người ước tính/sức chứa: thấp ≤50%, trung bình >50% và <80%, đông ≥80%; nếu thiếu sức chứa đã xác nhận hoặc số đếm ban đầu hợp lệ thì hiển thị chưa đủ dữ liệu. |
| BR-24 | Mỗi phiên đếm bắt đầu bằng số người do người vận hành kiểm tra và nhập. Khi không thể xác định số ban đầu, không trình bày số chỗ trống/mức đông như giá trị chính thức; mọi hiệu chỉnh sau đó phải truy vết được và không thay đổi dữ liệu CV thô. |

### 6.3. Giới hạn diễn giải số chỗ trống

Camera đếm người trong vùng quan sát không trực tiếp xác định ghế nào đang trống. Vì vậy, số chỗ trống là giá trị ước tính từ sức chứa cấu hình trừ số người hiện tại. Độ tin cậy phụ thuộc vị trí camera, che khuất, sự kiện vào/ra bị bỏ sót và quy trình hiệu chỉnh số đếm; nội dung này phải được đánh giá thực nghiệm.

## 7. Trường hợp sử dụng

| Mã | Trường hợp | Tác nhân | Luồng chính | Ngoại lệ |
| --- | --- | --- | --- | --- |
| UC-01 | Xem chỗ trống | Sinh viên | Mở trang chủ → lấy dữ liệu mới nhất → tính chỗ trống → hiển thị số người, sức chứa, mức đông và thời điểm cập nhật. | Nếu dữ liệu lỗi thời/mất kết nối, hiện cảnh báo. |
| UC-02 | Đặt phòng | Sinh viên | Đăng nhập bằng OTP → chọn ngày/giờ → xem phòng chuyên đề khả dụng → gửi yêu cầu → kiểm tra hợp lệ/trùng lịch → lưu và xác nhận. | Từ chối nếu trùng lịch, thời gian sai hoặc lưu lỗi. |
| UC-03 | Check-in QR | Sinh viên | Mở QR → gửi mã → backend xác minh lượt đặt → lưu check-in → hiển thị kết quả. | Từ chối mã sai/hết hạn, lượt bị hủy hoặc check-in lặp. |
| UC-04 | No-show | Bộ xử lý tự động | Kiểm tra lượt chưa check-in/chưa hủy → so thời gian chờ → cập nhật no-show và giải phóng khung giờ. | Không xử lý lượt đã check-in; ghi log lỗi. |
| UC-05 | Dashboard | Thủ thư | Đăng nhập → chọn phòng/khoảng thời gian → xem biểu đồ mật độ và thống kê. | Từ chối người thiếu quyền; báo khi thiếu dữ liệu. |
| UC-06 | Đếm qua đường ảo | CV/AI | Khung hình → YOLOv8n → ByteTrack → phát hiện cắt đường ảo → sự kiện vào/ra → gửi backend. | Ghi log/báo trạng thái nếu camera hoặc xử lý lỗi. |
| UC-07 | Khởi chạy hệ thống | Nhóm vận hành | Chuẩn bị biến môi trường → chạy Docker Compose → kiểm tra dịch vụ → mở website. | Log hỗ trợ chẩn đoán; dữ liệu volume còn sau restart. |
| UC-08 | Đăng nhập bằng OTP | Sinh viên/Thủ thư | Nhập email → kiểm tra email được phép → gửi mã 6 số → nhập mã → xác minh → tạo hồ sơ nếu lần đầu → cấp phiên. | Email không được phép, mã sai hoặc hết hạn, quá số lần thử, xin mã quá thường xuyên: từ chối với thông báo chung. |
| UC-09 | Khởi tạo phiên đếm | Người vận hành | Kiểm tra khu vực → nhập số người đang có mặt → bắt đầu phiên → hệ thống tính tiếp từ số ban đầu và sự kiện vào/ra hợp lệ. | Nếu không có số ban đầu đáng tin cậy, hệ thống báo chưa đủ dữ liệu và không công bố chỗ trống/mức đông chính thức. |

## 8. Kiểm thử và tiêu chí nghiệm thu

| Mã | Nội dung | Kết quả mong đợi |
| --- | --- | --- |
| TC-01 | Danh sách phòng | Hiển thị đúng phòng đã cấu hình và trạng thái. |
| TC-02 | Tính chỗ trống | Sức chứa trừ số người ước tính; giá trị không âm; thiếu số người ban đầu hoặc sức chứa đã xác nhận thì không hiển thị giá trị chính thức. |
| TC-03 | Mất kết nối/dữ liệu cũ | Hiện cảnh báo và thời điểm cập nhật cuối. |
| TC-04 | Đếm đường ảo | Đếm đúng hướng vào/ra, hạn chế đếm lặp. |
| TC-05 | Đặt phòng hợp lệ | Lưu lượt đặt trong thời lượng, khoảng đặt trước, số thành viên và giới hạn tạm; ngoài giới hạn bị từ chối. |
| TC-06 | Đặt trùng giờ | Từ chối lượt chồng lấn cùng phòng. |
| TC-07 | Đặt đồng thời | Không tạo hai lượt đặt hợp lệ chồng lấn. |
| TC-08 | QR hợp lệ/không hợp lệ | Quét QR trên Android; chỉ mã đúng trong khoảng từ giờ bắt đầu đến 15 phút sau giờ bắt đầu check-in được; mã sai, hết hạn hoặc dùng lại bị từ chối. |
| TC-09 | No-show | Lượt chưa check-in được đánh dấu no-show sau 15 phút và phần thời gian còn lại được giải phóng; lượt đã check-in không thành no-show. |
| TC-10 | Dashboard/phân quyền | Thống kê đúng; người không đủ quyền bị chặn; thay đổi phòng có nhật ký tác giả/thời điểm/nội dung. |
| TC-11 | Responsive | Luồng chính dùng được trên desktop/tablet/mobile. |
| TC-12 | Docker Compose | Khởi chạy theo README; dữ liệu PostgreSQL còn sau restart. |
| TC-13 | Đối chiếu đếm tay | Có dữ liệu tay/camera, công thức sai số và kết quả. |
| TC-14 | SUS | Có kết quả khảo sát và phương pháp tính điểm. |
| TC-15 | Đăng nhập OTP | Mã đúng vào được và tự tạo hồ sơ lần đầu; OTP tạm hết hạn sau 5 phút, tối đa 5 lần nhập sai, gửi lại sau 60 giây; mã sai/hết hạn/dùng lại bị từ chối. |
| TC-16 | Loại không gian | Đặt chỗ cho free_area bị từ chối; giao diện khu tự học không có nút đặt. |
| TC-17 | Ứng dụng Android | Nếu triển khai Should: cài APK trên thiết bị Android thử nghiệm, đăng nhập OTP, xem chỗ trống, đặt phòng chuyên đề và check-in QR; iOS ngoài phạm vi. |
| TC-18 | Hai cơ sở | Dữ liệu và đặt chỗ của CS1 và CS3 tách biệt; lọc theo cơ sở đúng. |
| TC-19 | Hiệu chỉnh số đếm | Chỉ vai trò được cấp quyền hiệu chỉnh được; phải có lý do và nhật ký; dữ liệu sự kiện CV thô không bị sửa/xóa. |
| TC-20 | Chỗ trống và mức đông chưa cấu hình | Không có sức chứa/số ban đầu đã xác nhận thì UI báo chưa đủ dữ liệu, không hiển thị giá trị giả. |
| TC-21 | Thời hạn lưu | Kiểm tra video không được lưu; số đếm và dữ liệu định danh bị xóa/ẩn danh theo thời hạn tạm sau khi có phê duyệt. |
| TC-22 | Hợp đồng CV | Schema v1.0 được kiểm tra; bản ghi trùng bị khử; không cộng counter tích lũy từng frame; kiểm thử UTC có múi giờ. |
| TC-23 | Khởi tạo phiên đếm | Người vận hành ghi số người thực tế sau khi kiểm tra; phiên mới yêu cầu số ban đầu mới; thiếu số ban đầu thì UI báo chưa đủ dữ liệu và không công bố chỗ trống/mức đông chính thức. |
| TC-24 | Truy cập thử nghiệm | Người thử ngoài nhóm truy cập trước qua cùng Wi-Fi; chỉ mở đường hầm/hosting sau khi Uyên phê duyệt, có xác thực và giới hạn truy cập. |

### 8.1. Chỉ tiêu đánh giá thực nghiệm

| Mã | Mục tiêu | Cách đánh giá |
| --- | --- | --- |
| AT-01 | Sai số đếm ≤ 10% | Tạm tính sai số tổng hợp = tổng giá trị tuyệt đối(camera − đếm tay) / tổng đếm tay × 100% trong 5–10 phiên, nhiều mức đông; phiên mẫu số bằng 0 báo sai số tuyệt đối riêng, không dùng phép chia. |
| AT-02 | p95 độ trễ ≤ 5 giây | Đo từ lúc ghi nhận sự kiện đến lúc website hiển thị, báo phân vị 95 trên dữ liệu thử. |
| AT-03 | Trung vị ≥ 5 FPS ở khoảng 416 px | Đo tối thiểu 60 giây trên laptop nhóm và tại CS1/CS3 nếu được phép; nếu không đạt hoặc không có quyền truy cập, đánh giá offline và ghi cấu hình. |
| AT-04 | SUS ≥ 70 | Khảo sát khoảng 15–30 sinh viên dùng thử. |
| AT-05 | Độ ổn định | Tạm chạy liên tục ít nhất 4 giờ trong một phiên; thống kê lỗi/mất kết nối từ nhật ký, không diễn giải là SLA. |
| AT-06 | Xử lý no-show (kịch bản thử) | Đo tỷ lệ no-show tại CS1 và CS3 nếu triển khai được; nếu không, kiểm thử bằng kịch bản thử (TC-09) và nêu rõ giới hạn. |

Các chỉ tiêu là mục tiêu, không phải kết quả đã đạt. Nếu số đếm tham chiếu bằng 0, nhóm phải quy định cách tính sai số để tránh phép chia không xác định.

### 8.2. Điều kiện nghiệm thu tổng quát

Các yêu cầu Must đã triển khai và vượt qua kiểm thử tương ứng.

Không còn lỗi nghiêm trọng về đặt trùng, phân quyền và tính nhất quán dữ liệu.

Khởi chạy bằng Docker Compose theo README; có .env.example và hướng dẫn cập nhật.

Có báo cáo thực nghiệm nêu môi trường, dữ liệu, công thức, kết quả và giới hạn.

Quy trình quay thử chỉ dùng người đã đồng ý; khi triển khai có chấp thuận của thư viện/nhà trường và biển thông báo, đáp ứng nguyên tắc quyền riêng tư.

Không tuyên bố KPI đạt được khi chưa đo.

## 9. Ưu tiên và ma trận truy vết

| Mức ưu tiên | Phạm vi |
| --- | --- |
| Must | Xem chỗ trống khu tự học tự do; đặt phòng chuyên đề/ngăn trùng; đăng nhập OTP qua email; đếm bằng webcam + YOLOv8n + ByteTrack qua đường ảo (ít nhất đánh giá offline); Docker Compose; đối chiếu đếm tay; báo cáo và kế hoạch kinh doanh. |
| Should | Check-in QR, no-show, dashboard thủ thư, SUS, ứng dụng Android, triển khai tại CS1 và CS3; demo AI trực tiếp nếu phần cứng cho phép. |
| Could | Dự báo mật độ 1–2 giờ tới; thông báo khi có chỗ trống. |
| Won’t | ESP32/cảm biến IoT, nhận diện khuôn mặt, ứng dụng iOS, tích hợp portal chính thức (trừ khi trường cấp quyền), đặt chỗ cho khu tự học tự do, triển khai ngoài CS1 và CS3. |

### 9.1. Ma trận truy vết mẫu

| Yêu cầu | Thành phần | Kiểm thử |
| --- | --- | --- |
| FR-OCC-03 | Backend + Frontend | TC-02 |
| FR-OCC-06 | Người vận hành + Backend + Frontend | TC-23 |
| FR-CV-03 | CV/AI + Backend | TC-04, AT-01 |
| FR-BOOK-04 | Backend + PostgreSQL | TC-06, TC-07 |
| FR-CHK-02/03 | Backend + Frontend | TC-08 |
| FR-DASH-01/02 | Backend + Frontend | TC-10 |
| NFR-PER-01 | CV/AI + Backend + Frontend | AT-02 |
| NFR-ACC-01 | CV/AI | AT-01 |
| NFR-USA-03 | Frontend + nhóm kiểm thử | AT-04 |
| NFR-PRI-01/02 | CV/AI + quy trình vận hành | Rà soát xử lý hình ảnh |
| FR-OPS-01/02 | Docker Compose + PostgreSQL | TC-12 |
| FR-AUTH-02/04 | Backend + Frontend + email | TC-15 |
| FR-SITE-01/02 | Backend + Frontend + Android | TC-18 |
| FR-APP-01 | Android | TC-17 |
| FR-ROOM-01 | Backend + Frontend | TC-16 |

## 10. Giới hạn, giả định và rủi ro

### 10.1. Giả định và ràng buộc

Mỗi thành viên có laptop với webcam hoạt động; có thể tổ chức phiên thử với người tham gia đã đồng ý.

Có nguồn điện và mạng tại nơi kiểm thử.

Việc dùng portal của trường phụ thuộc văn bản đồng ý và cách kết nối chính thức từ trường; nếu không có, hệ thống dùng đăng nhập OTP qua email sinh viên.

Cần dịch vụ gửi email (SMTP). Người thử, kể cả ngoài nhóm, ưu tiên truy cập qua cùng Wi-Fi; đường hầm tạm hoặc hosting chỉ được dùng khi Uyên phê duyệt và có xác thực cùng giới hạn truy cập.

Chưa có bằng chứng chấp thuận triển khai tại CS1/CS3 trong hồ sơ này. Chỉ đặt máy/webcam, thu hình hoặc xử lý dữ liệu tại thư viện sau khi có văn bản đồng ý, thống nhất vị trí và đáp ứng yêu cầu quyền riêng tư; trước đó chỉ kiểm thử webcam trong môi trường nhóm.

Máy tính có thể không có GPU chuyên dụng; hiệu năng AI phải được đo.

Thời gian dự án theo Charter: 26/10/2026–26/12/2026; không mua camera (dùng webcam của máy tính).

Các giá trị nêu trong mục 11 là mặc định tạm cho kiểm thử, không phải chính sách đã được thư viện/nhà trường/thầy hướng dẫn phê duyệt; cấu hình phải cho phép thay đổi.

### 10.2. Rủi ro và ứng phó

| Rủi ro | Ảnh hưởng | Ứng phó |
| --- | --- | --- |
| Thư viện hoặc nhà trường chậm hoặc không cho đặt máy tính/webcam tại CS1/CS3 | Cao | Xin văn bản đồng ý sớm; dự phòng bằng kiểm thử webcam laptop và video quay thử, ghi rõ giới hạn. |
| Laptop không đủ mạnh | Trung bình | Dùng YOLOv8n, giảm độ phân giải/FPS, giới hạn vùng quan tâm, đánh giá offline. |
| Đếm sai do che khuất/đông | Trung bình | Điều chỉnh góc camera/đường ảo; phân tích lỗi và báo cáo giới hạn. |
| Container không truy cập webcam | Trung bình | Đã chốt chạy CV/AI ngoài Docker, đọc webcam trực tiếp; video quay thử dùng để đánh giá offline. |
| Lo ngại quyền riêng tư | Trung bình | Xử lý tại chỗ, không nhận diện danh tính, không lưu video lâu dài; khi kiểm thử chỉ quay người đã đồng ý, khi triển khai có biển thông báo và văn bản đồng ý của thư viện. |
| Email OTP vào thư mục spam hoặc bị chặn | Trung bình | Thử sớm với 3–5 email sinh viên thật; dự phòng bằng mã mời và tài khoản demo. |
| Người thử ngoài nhóm không truy cập được hệ thống | Trung bình | Ưu tiên thử cùng Wi-Fi; chỉ dùng đường hầm/hosting khi Uyên phê duyệt, có xác thực và giới hạn truy cập. |
| Trường không cấp kết nối portal | Thấp | Dùng đăng nhập OTP và tài khoản demo; lớp đăng nhập thay thế được. |
| Phạm vi quá lớn so với thời gian (app Android, hai cơ sở, triển khai thật) | Cao | Ưu tiên web và API; app Android và triển khai là Should; thử một cơ sở trước; cắt từ dưới lên. |
| Điều kiện hai cơ sở khác nhau (số cửa, Wi-Fi, ánh sáng, nguồn điện) | Trung bình | Khảo sát tại chỗ từng cơ sở; cấu hình riêng cho mỗi cơ sở. |
| Trễ tiến độ | Cao | Ưu tiên Must; chỉ làm Should khi Must ổn định; loại Could trước. |
| Số đếm bị lệch | Trung bình | Ghi thời điểm/nguồn, cảnh báo dữ liệu cũ, xác định quy trình hiệu chỉnh. |

## 11. Các vấn đề cần xác nhận

Các quyết định dưới đây đã được chuẩn hóa thành 17 mục; danh sách cũ được gộp ở các mục OTP/portal, sức chứa/danh mục phòng và chính sách đặt chỗ/giới hạn nhóm. Ngày 10/11/2026 là ngày Uyên duyệt nội bộ, không mặc định là ngày phản hồi của bên liên quan. Mười hai mục ngoài các câu cần email thư viện được ghi nhận là đã xác nhận theo báo cáo của Uyên; người trả lời gốc/ngày trả lời chưa được cung cấp, nên không gán xác nhận trực tiếp cho nhà trường, thầy hướng dẫn hoặc thành viên cụ thể.

Ưu tiên P0: Q-01, Q-03, Q-04, Q-05, Q-06, Q-08 và Q-17. Theo chỉ đạo của Uyên, email Q-03, Q-04, Q-05, Q-06 và Q-08 được hoãn ở giai đoạn nội bộ; vẫn phải có xác nhận trước mọi hoạt động đặt webcam/thu thập dữ liệu tại thư viện. Kế hoạch ban đầu yêu cầu gửi câu hỏi ngày 06/11/2026; repo không lưu bằng chứng email. Đầu mối thư viện và CNTT nhà trường chưa được nêu tên.

Phân nhóm đầu mối cần trả lời/xác nhận (một số mục cần phối hợp nhiều bên):

- Thư viện: Q-02–Q-06, Q-08 và Q-11; xác nhận danh mục/sức chứa, quy tắc đặt chỗ, vị trí webcam và yêu cầu vận hành/quyền riêng tư.
- Nhà trường/CNTT: Q-01, Q-11 và Q-17; xác nhận khả năng Portal/SSO, yêu cầu quản trị dữ liệu và các giới hạn nền tảng ứng dụng.
- Giáo viên hướng dẫn: Q-12–Q-14; xác nhận ngưỡng đánh giá, mục tiêu và công thức KPI.
- Nhóm dự án: Q-07, Q-09–Q-10 và Q-15–Q-17; chốt cách triển khai QR/demo, cấu hình kỹ thuật, hiệu chỉnh số đếm và hợp đồng framework/payload. Q-03 cần người vận hành của nhóm nhập số ban đầu; Q-17 gồm quyết định kỹ thuật của nhóm sau khi kiểm tra ràng buộc từ nhà trường.

| Câu hỏi | Đề xuất | Trả lời / trạng thái | Người xác nhận / người theo dõi | Ngày | FR/BR ảnh hưởng |
| --- | --- | --- | --- | --- | --- |
| Q-01 (P0). Trường có cấp Portal/SSO/API không; quy tắc OTP email nào dùng nếu chưa có? | MVP dùng OTP email; tạm: 6 chữ số, hạn 5 phút, tối đa 5 lần nhập sai, gửi lại sau 60 giây, chỉ email trong danh sách cho phép. Chỉ làm SSO/API khi có văn bản đồng ý và đầu mối kỹ thuật. Hệ quả: không lệ thuộc hệ thống trường, nhưng người dùng phải truy cập email. | UYÊN BÁO ĐÃ XÁC NHẬN — chưa có câu trả lời gốc/đầu mối CNTT nhà trường trong repo; không ghi nhận là trường đã xác nhận trực tiếp. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); đầu mối CNTT nhà trường chưa được nêu. | 10/11/2026 (Uyên xác nhận) | FR-AUTH-01–05; BR-15–16; NFR-SEC-01 |
| Q-02. Ai được thêm, sửa hoặc ngừng sử dụng phòng? | Thủ thư/đại diện thư viện xác nhận danh mục và sức chứa; chỉ tài khoản quản trị được Uyên phân quyền mới được cập nhật hệ thống thử nghiệm. Lưu nhật ký và ngừng sử dụng bằng trạng thái, không xóa cứng. Hệ quả: giảm sửa sai/trái quyền và giữ lịch sử đặt phòng. | UYÊN BÁO ĐÃ XÁC NHẬN — người có thẩm quyền phía thư viện chưa được nêu trong repo. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); đại diện thư viện chưa được chỉ định. | 10/11/2026 (Uyên xác nhận) | FR-ADMIN-01; BR-09–10, BR-20 |
| Q-03 (P0). Danh mục phòng, sức chứa, số cửa tại CS1/CS3 và số người ban đầu được xác định thế nào? | Thư viện xác nhận danh mục/sức chứa/số cửa trước triển khai. Mỗi phiên thử, người vận hành kiểm tra khu vực và nhập số người thực tế ban đầu; nếu không có số đáng tin cậy thì không công bố chỗ trống/mức đông chính thức. Hệ quả: số liệu có nguồn gốc rõ ràng, nhưng phải kiểm tra thủ công mỗi phiên; dữ liệu thư viện chỉ dùng sau khi được xác nhận. | UYÊN DUYỆT GIÁ TRỊ TẠM CHO NỘI BỘ — email thư viện hoãn đến trước triển khai tại thư viện; chưa có số liệu thật. | Vũ Nguyễn Nhã Uyên (duyệt nội bộ); người vận hành ghi số ban đầu; đại diện thư viện cần xác nhận sức chứa trước triển khai. | 10/11/2026 (duyệt nội bộ) | FR-OCC-03–06; FR-SITE-01–02; FR-ADMIN-01; BR-01–02, BR-17, BR-21, BR-23–24 |
| Q-04 (P0). Thời lượng, thời gian đặt trước, khoảng cách, sĩ số và giới hạn lượt đặt? | Tạm: mỗi lượt 30–120 phút, đặt trước tối đa 7 ngày, cách lượt kế tiếp 15 phút, nhóm 2–6 người, một lượt/người/ngày. Hệ quả: quy tắc dễ kiểm thử nhưng có thể không phù hợp quy trình vận hành hoặc sức chứa thực tế; cấu hình phải đổi được. | UYÊN DUYỆT GIÁ TRỊ TẠM CHO NỘI BỘ — email thư viện hoãn đến trước triển khai; chưa phải chính sách vận hành. | Vũ Nguyễn Nhã Uyên (duyệt nội bộ); đại diện thư viện cần xác nhận trước triển khai. | 10/11/2026 (duyệt nội bộ) | FR-BOOK-02–04; BR-03–04, BR-18 |
| Q-05 (P0). Hủy đặt phòng và thời hạn hủy? | Tạm cho người dùng hủy trước giờ bắt đầu ít nhất 30 phút; sau thời điểm đó chuyển thủ thư xử lý ngoại lệ. Hệ quả: giải phóng phòng sớm, nhưng có thể không phù hợp quy định thư viện. | UYÊN DUYỆT GIÁ TRỊ TẠM CHO NỘI BỘ — email thư viện hoãn đến trước triển khai; chỉ áp dụng cho kiểm thử. | Vũ Nguyễn Nhã Uyên (duyệt nội bộ); đại diện thư viện cần xác nhận trước triển khai. | 10/11/2026 (duyệt nội bộ) | FR-BOOK-06; BR-19 |
| Q-06 (P0). Chờ bao lâu trước khi đánh dấu no-show và nhả phòng? | Tạm chờ 15 phút sau giờ bắt đầu; sau đó đánh dấu no-show và giải phóng phần thời gian còn lại. Hệ quả: hạn chế giữ phòng không sử dụng nhưng có thể ảnh hưởng người đến trễ; thời gian phải cấu hình được. | UYÊN DUYỆT GIÁ TRỊ TẠM CHO NỘI BỘ — email thư viện hoãn đến trước triển khai; không tự nhả phòng tại thư viện trước xác nhận. | Vũ Nguyễn Nhã Uyên (duyệt nội bộ); đại diện thư viện cần xác nhận trước triển khai. | 10/11/2026 (duyệt nội bộ) | FR-BOOK-07; FR-CHK-02; BR-05–08 |
| Q-07. QR được quét bằng ứng dụng nào? | Tạm quét bằng camera trong ứng dụng Android; web hiển thị QR/mã. Dự phòng vận hành là thủ thư xác minh mã trên web, không cần máy quét riêng. Hệ quả: cần điện thoại Android; luồng web dự phòng vẫn cần phân quyền. | UYÊN BÁO ĐÃ XÁC NHẬN — chi tiết câu trả lời/người trả lời gốc chưa được cung cấp. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); đại diện thư viện chưa được chỉ định. | 10/11/2026 (Uyên xác nhận) | FR-CHK-01–03; FR-APP-01; BR-05 |
| Q-08 (P0). Vị trí/góc webcam và cấu hình máy tính ở CS1/CS3? | Chỉ khảo sát và lắp đặt sau văn bản đồng ý; đề xuất webcam hướng vào lối đi, giảm nhận diện khuôn mặt, máy tính chạy CV tại chỗ, cấu hình riêng theo cơ sở. Hệ quả: chất lượng góc nhìn ảnh hưởng độ chính xác; trước khi được phép chỉ thử ở môi trường nhóm. | UYÊN DUYỆT GIÁ TRỊ TẠM CHO NỘI BỘ — email thư viện hoãn đến trước triển khai; không ghi hình tại thư viện trước khi được phép. | Vũ Nguyễn Nhã Uyên (duyệt nội bộ); đại diện thư viện cần xác nhận trước triển khai; Lê Văn Trí hỗ trợ CV. | 10/11/2026 (duyệt nội bộ) | FR-CV-01–04; FR-SITE-02; NFR-PRI-01–03 |
| Q-09. Demo trực tiếp hay đánh giá offline; người ngoài nhóm truy cập thế nào? | Webcam trực tiếp trên máy nhóm là mục tiêu nếu chạy ổn; video thử có đồng ý là phương án dự phòng. Người thử, kể cả ngoài nhóm, ưu tiên cùng Wi-Fi; chỉ dùng đường hầm/hosting khi Uyên cho phép, có xác thực và giới hạn truy cập. Không lấy việc đặt webcam ở thư viện làm điều kiện kỹ thuật trước khi có phép. Hệ quả: vẫn hoàn tất đánh giá nội bộ mà không mở hệ thống công khai; kết quả không đại diện môi trường thư viện nếu chưa được phép thử tại đó. | UYÊN BÁO ĐÃ XÁC NHẬN — người xác nhận kỹ thuật/thầy hướng dẫn và ngày trả lời gốc chưa được cung cấp. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); Lê Văn Trí phụ trách kỹ thuật. | 10/11/2026 (Uyên xác nhận) | FR-CV-04; FR-EXP-02; NFR-PER-02; NFR-PRI-03; AT-03; TC-24 |
| Q-10. CSDL và cấu hình triển khai? | Dùng PostgreSQL 16.6 Alpine như cấu hình Docker Compose hiện có; không suy diễn cấu hình production từ cấu hình dev. Hệ quả: phù hợp schema/migrations hiện tại; cấu hình production cần được chốt riêng nếu triển khai. | UYÊN BÁO ĐÃ XÁC NHẬN — phiên bản dev đối chiếu được trong repo; cấu hình production chưa được cung cấp. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); nhóm Backend/Docker duy trì cấu hình; thầy hướng dẫn chưa có trả lời gốc trong repo. | 10/11/2026 (Uyên xác nhận; repo đối chiếu) | FR-OPS-01–02; NFR-DEP-01; BR-13 |
| Q-11. Lưu dữ liệu bao lâu, ai được truy cập? | Không lưu video; tạm giữ số đếm tổng hợp tối đa 90 ngày sau đánh giá và xóa/ẩn danh dữ liệu đặt phòng định danh trong 30 ngày sau khi kết thúc dự án; chỉ người được phân quyền truy cập. Hệ quả: cần quy trình xóa và phê duyệt quyền riêng tư trước triển khai. | UYÊN BÁO ĐÃ XÁC NHẬN — đây là giá trị nội bộ tạm; chưa có phê duyệt của đầu mối dữ liệu nhà trường/thư viện. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); đầu mối dữ liệu nhà trường/thư viện chưa được chỉ định. | 10/11/2026 (Uyên xác nhận) | FR-AUTH-03; FR-DASH-01–02; BR-09–10, BR-22; NFR-PRI-01–03 |
| Q-12. Ngưỡng phân loại mức độ đông? | Tạm: thấp ≤50%, trung bình >50% và <80%, đông ≥80% sức chứa. Hệ quả: cần sức chứa chính xác; nếu thiếu sức chứa hoặc số đếm hợp lệ, hiển thị “chưa đủ dữ liệu”. | UYÊN BÁO ĐÃ XÁC NHẬN — ngưỡng là giá trị nội bộ; tên người duyệt KPI gốc chưa được cung cấp. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); TS. Đặng Nhân Cánh là đầu mối xác nhận học thuật. | 10/11/2026 (Uyên xác nhận) | FR-OCC-03–04; BR-01–02, BR-23 |
| Q-13. Mục tiêu chạy liên tục? | Tạm đo một phiên 4 giờ liên tục, ghi thời gian gián đoạn và lỗi; đây là mục tiêu kiểm thử, không phải cam kết SLA. Hệ quả: đo được trong phạm vi đồ án mà không hàm ý vận hành 24/7. | UYÊN BÁO ĐÃ XÁC NHẬN — người duyệt mục tiêu chạy liên tục gốc chưa được cung cấp. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); TS. Đặng Nhân Cánh là đầu mối xác nhận học thuật. | 10/11/2026 (Uyên xác nhận) | NFR-REL-01; AT-05; FR-OPS-01 |
| Q-14. Môi trường, tải và công thức KPI? | Tạm dùng công thức sai số tổng hợp tại AT-01; 5–10 phiên ở nhiều mức đông; phiên tổng đếm tay bằng 0 báo sai số tuyệt đối; p95 độ trễ ≤5 giây; trung vị ≥5 FPS ở 416 px trong ít nhất 60 giây; SUS ≥70 với 15–30 người. Hệ quả: kết quả có thể so sánh, nhưng mẫu nhỏ phải nêu giới hạn. | UYÊN BÁO ĐÃ XÁC NHẬN — người duyệt KPI gốc/công thức chi tiết chưa được cung cấp; giữ các giới hạn đo trong báo cáo. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); TS. Đặng Nhân Cánh là đầu mối KPI; Lê Văn Trí đo CV. | 10/11/2026 (Uyên xác nhận) | FR-EXP-01–02; NFR-PER-01–02; NFR-ACC-01; NFR-USA-03; AT-01–04 |
| Q-15. Xử lý bỏ sót hoặc lệch số đếm? | Tạo bản ghi điều chỉnh riêng có lý do, người thực hiện và thời gian; cho phép cập nhật số hiện tại bởi vai trò được cấp quyền, nhưng không sửa/xóa sự kiện CV thô hoặc lịch sử đã lưu. Hệ quả: có truy vết và phân biệt đo tự động với hiệu chỉnh thủ công. | UYÊN BÁO ĐÃ XÁC NHẬN — người trả lời kỹ thuật gốc chưa được cung cấp; cơ chế còn cần tích hợp và kiểm thử. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); nhóm Backend/CV thực hiện. | 10/11/2026 (Uyên xác nhận) | FR-OCC-01–02, FR-ADMIN-01; BR-13, BR-21 |
| Q-16. Framework frontend và payload CV/backend? | Frontend React + Vite (JavaScript), theo Charter; dùng hợp đồng dữ liệu CV schema 1.0 hiện có. Endpoint mạng, xác thực, retry và mã phòng ánh xạ phải được chốt cùng trước tích hợp. Hệ quả: giữ tương thích hợp đồng hiện tại, tránh coi JSONL cục bộ là API đã triển khai. | UYÊN BÁO ĐÃ XÁC NHẬN — framework/schema đối chiếu được trong tài liệu; endpoint mạng và retry vẫn chưa có trong hợp đồng. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); nhóm Frontend/Backend/CV hoàn thiện endpoint. | 10/11/2026 (Uyên xác nhận; repo đối chiếu) | FR-CV-01–04; FR-OCC-01; NFR-DAT-01; hợp đồng dữ liệu CV v1.0 |
| Q-17 (P0). Nền tảng ứng dụng: Android hay iOS; công nghệ và phát hành? | Theo Charter: Android native cho sinh viên, iOS ngoài phạm vi; tạm chọn Kotlin, phát hành APK trực tiếp và kiểm thử trên thiết bị Android nhóm mượn. Hệ quả: giữ được camera quét QR, không phát sinh chi phí cửa hàng; nếu thiếu thời gian, ưu tiên web/API vì ứng dụng là Should. | UYÊN BÁO ĐÃ XÁC NHẬN — quy định nền tảng/phát hành của trường và người duyệt công nghệ Android gốc chưa được cung cấp. | Vũ Nguyễn Nhã Uyên (báo đã xác nhận); đầu mối CNTT nhà trường chưa được chỉ định; nhóm Android chưa phân công. | 10/11/2026 (Uyên xác nhận) | FR-APP-01; FR-PWA-01; FR-CHK-01–03; NFR-USA-02; TC-11, TC-17 |

### Trạng thái xác nhận

- Uyên đã duyệt nội bộ SRS 1.8 ngày 10/11/2026; 17/17 mục có trạng thái.
- Uyên báo 12 mục ngoài Q-03/04/05/06/08 đã được xác nhận; tên người trả lời gốc và ngày trả lời cụ thể chưa được cung cấp, nên hồ sơ không gán các câu trả lời trực tiếp cho nhà trường/thầy hướng dẫn/nhóm.
- Theo chỉ đạo của Uyên, email thư viện cho Q-03/04/05/06/08 được hoãn ở giai đoạn nội bộ. Chưa có email trong repo; phải lấy văn bản đồng ý và xác nhận quy tắc liên quan trước khi đặt webcam, thu thập dữ liệu hoặc vận hành tại thư viện.
- Các giá trị được Uyên duyệt chỉ dùng cho phát triển/kiểm thử nội bộ; không thay thế phê duyệt nghiệp vụ/quyền riêng tư của thư viện hoặc nhà trường.

## 12. Phê duyệt

| Vai trò | Người phê duyệt | Ngày | Chữ ký |
| --- | --- | --- | --- |
| Đại diện nhóm dự án | Vũ Nguyễn Nhã Uyên | 10/11/2026 | Đã duyệt nội bộ SRS 1.8 theo xác nhận trong phiên làm việc |
| Giáo viên hướng dẫn | TS. Đặng Nhân Cánh | Chưa ghi nhận chữ ký; Uyên báo các xác nhận ngoài nhóm email đã có | Chưa có chữ ký trong repo |
| Đại diện Thư viện UTH | Chưa được chỉ định | Hoãn xác nhận email cho giai đoạn nội bộ | Cần văn bản trước khi triển khai tại thư viện |

Kết luận: SRS 1.8 đã được Uyên duyệt cho giai đoạn phát triển/kiểm thử nội bộ theo Project Charter UTH-SeatSense phiên bản 1.7. Đây chưa phải phê duyệt triển khai tại thư viện; xác nhận/email thư viện cho Q-03/04/05/06/08 được hoãn theo chỉ đạo của Uyên và vẫn là điều kiện trước khi đặt webcam, thu thập dữ liệu hoặc áp dụng chính sách thật.

## Phụ lục A. Nguồn dự án

Kho mã nguồn: https://github.com/uth-seatsense/UTH-SeatSense

Bảng công việc: https://nhauyen70205.atlassian.net/jira/software/projects/SEAT/boards/2?filter=&groupBy=none

Hướng dẫn chạy: README.md trong kho mã nguồn.

Lưu ý: KPI là mục tiêu để đo lường, không phải kết quả đã xác minh. Các quy tắc mang nhãn tạm cần được phê duyệt trước khi ban hành bản chính thức. Tham khảo thêm [hợp đồng dữ liệu CV](../architecture/cv-data-contract.md) và [thiết kế cơ sở dữ liệu](../architecture/database-design.md).
