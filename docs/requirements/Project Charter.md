# Project Charter: UTH-SeatSense (Đề tài D6)



Hệ thống theo dõi mật độ sử dụng phòng đọc và đặt phòng học nhóm tại Thư viện UTH

Học kỳ doanh nghiệp · Phiên bản 1.7 (cập nhật: chốt các quyết định nội bộ về công nghệ, kiểm đếm và truy cập thử nghiệm) · Ngày lập: 26/10/2026 · Cập nhật: 10/11/2026

## 1. Thông tin chung

| Mục | Nội dung |
| --- | --- |
| Tên dự án | UTH-SeatSense (tên tạm, có thể đổi) |
| Mã đề tài | D6 – Đặt chỗ và theo dõi mật độ sử dụng phòng đọc |
| Đơn vị hưởng lợi | Trung tâm Thông tin Thư viện UTH |
| Nhóm trưởng / Project Manager | Vũ Nguyễn Nhã Uyên |
| Giáo viên hướng dẫn | TS.Đặng Nhân Cánh |
| Thời gian thực hiện | 2.5 tháng, từ [26/10/2026] đến [26/12/2026] |
| Ngân sách trần | Không mua camera (dùng webcam của máy tính); phần mềm dùng miễn phí/mã nguồn mở; chi phí máy chủ/hosting nếu cần xem mục 12 |
| Kho mã nguồn | https://github.com/uth-seatsense/UTH-SeatSense |
| Bảng công việc | https://nhauyen70205.atlassian.net/jira/software/projects/SEAT/boards/2?filter=&groupBy=none |
| Tài liệu hướng dẫn chạy dự án | README.md trong kho mã nguồn |

## 2. Bối cảnh và vấn đề

Sinh viên thường phải đến tận nơi mới biết phòng đọc còn chỗ hay không, mất thời gian tìm chỗ và đôi khi phải quay về. Phòng học nhóm có thể được đặt nhưng không sử dụng (no-show), gây lãng phí. Thủ thư chưa có số liệu mật độ theo giờ/ngày để bố trí không gian và nhân sự.

Các vấn đề này sẽ được xác nhận bằng số liệu khảo sát thật ở Tuần 1–2 (phỏng vấn thủ thư, khảo sát 50–100 sinh viên). Các con số trong mục KPI sẽ được hiệu chỉnh lại sau khảo sát.

## 3. Mục tiêu dự án

1. Hiển thị số chỗ trống và mức độ đông của khu tự học tự do (chỉ xem, không đặt chỗ) gần thời gian thực trên web.

2. Cho phép sinh viên đặt phòng chuyên đề cho nhóm theo khung giờ, check-in bằng QR, tự động nhả phòng khi quá hạn.

3. Cung cấp dashboard thống kê cho thủ thư (mật độ theo giờ/ngày, tỷ lệ sử dụng phòng, tỷ lệ no-show).

4. Đánh giá độ chính xác và tốc độ xử lý của phương pháp đếm người bằng camera + YOLO (webcam của máy tính, cả khi kiểm thử và khi triển khai tại CS1 và CS3), rút ra kết luận bằng số liệu thực nghiệm và nêu rõ giới hạn.

5. Đóng gói hệ thống bằng Docker để cả nhóm chạy cùng một môi trường.

6. Xây dựng kế hoạch kinh doanh cho sản phẩm (mô hình doanh thu, chi phí, điểm hòa vốn).

## 4. Câu hỏi nghiên cứu

• Camera dùng YOLO có đếm số người đủ chính xác (sai số ≤ 10% so với đếm tay), đủ nhanh trên laptop thường và bảo vệ được quyền riêng tư không?

• Hiển thị chỗ trống thời gian thực và đặt phòng online có giúp giảm thời gian tìm chỗ và tăng hiệu suất sử dụng phòng không?

## 5. Phạm vi

Trong phạm vi (In scope)

• Triển khai thử nghiệm tại hai thư viện CS1 và CS3 của trường: mỗi cơ sở có 1 khu tự học tự do (chỉ xem mật độ, không đặt chỗ) và các phòng chuyên đề (đặt theo khung giờ). Camera dùng là webcam của máy tính (không mua camera riêng). Trước khi đủ điều kiện triển khai (văn bản đồng ý, mạng, điện), nhóm kiểm thử bằng webcam laptop.

• Phương án B (đã chốt): webcam laptop + YOLOv8 (bản nhẹ) + tracker (ByteTrack), đếm khi người cắt đường ảo.

• Khi bắt đầu mỗi phiên đếm, người vận hành kiểm tra khu vực và nhập số người đang có mặt làm số ban đầu. Nếu không xác định được số ban đầu đáng tin cậy, hệ thống không công bố số chỗ trống/mức đông chính thức; mọi hiệu chỉnh được lưu riêng kèm người thực hiện, thời gian và lý do.

• Ứng dụng Android native cho sinh viên (Kotlin, thử nghiệm bằng APK trực tiếp; đăng nhập OTP, xem chỗ trống khu tự học, đặt phòng chuyên đề, check-in QR) và web responsive (dashboard thủ thư, dùng qua trình duyệt); cùng dùng một backend; hỗ trợ hai cơ sở CS1 và CS3.

• Kiểm thử với người ngoài nhóm ưu tiên cùng Wi-Fi. Chỉ dùng đường hầm hoặc hosting khi Uyên phê duyệt và có xác thực, giới hạn truy cập.

• Đóng gói và chạy các dịch vụ bằng Docker Compose.

• Thực nghiệm đối chiếu đếm tay, thử nghiệm người dùng (SUS), báo cáo và kế hoạch kinh doanh.

Ngoài phạm vi (Out of scope)

• Phương án A (ESP32 + cảm biến khoảng cách) và mọi phần cứng IoT.

• Nhận diện khuôn mặt hoặc định danh người trong ảnh.

• Lưu trữ video/hình ảnh lâu dài.

• Tích hợp đăng nhập portal/tài khoản chính thức của trường (chỉ làm nếu trường cấp văn bản đồng ý và cách kết nối chính thức; hệ thống thiết kế lớp đăng nhập thay thế được).

• Ứng dụng iOS (chỉ làm ứng dụng Android native).

• Thay đổi hạ tầng của thư viện (cửa, điện, mạng) ngoài việc đặt máy tính có webcam.

• Đặt chỗ cho khu tự học tự do (chỉ xem mật độ và chỗ trống).

• Triển khai ngoài hai cơ sở CS1 và CS3.

## 6. Giải pháp tổng quan

| Thành phần | Công nghệ | Vai trò |
| --- | --- | --- |
| CV/AI (cv/) | Webcam laptop + YOLOv8n + ByteTrack, đếm qua đường ảo | Đếm người vào/ra, chỉ gửi con số lên server |
| Backend (backend/) | FastAPI | Nhận dữ liệu đếm, API, đăng nhập OTP qua email, logic đặt phòng chuyên đề, check-in, tự nhả phòng |
| CSDL | PostgreSQL | Lưu dữ liệu hệ thống |
| Frontend (frontend/) | Web responsive, chốt: React + Vite (JavaScript) | Chỗ trống khu tự học, đặt phòng chuyên đề, dashboard |
| Ứng dụng Android (android/) | Android native (Kotlin; thử nghiệm bằng APK trực tiếp) | Xem chỗ trống, đặt phòng chuyên đề, check-in QR (quét bằng camera điện thoại) |
| Docker | Docker Compose | Đóng gói, chạy các dịch vụ bằng một lệnh |

[Webcam laptop + YOLOv8n + ByteTrack] -> (số lượng vào/ra) -> Server (FastAPI) -> PostgreSQL -> Web / Dashboard

Vai trò của Docker: chuẩn hóa môi trường để mọi thành viên chạy cùng một hệ thống; khởi động toàn bộ dịch vụ bằng docker compose up -d --build; giữ dữ liệu PostgreSQL trong volume; hỗ trợ demo và triển khai. Docker chỉ là lớp đóng gói và chạy, không tham gia xử lý nghiệp vụ hay nhận diện người.

Chốt về camera trong Docker: Docker Desktop trên Windows/macOS thường khó cho container dùng webcam. Nhóm chốt chạy mô-đun CV/AI ngoài Docker, đọc trực tiếp webcam của máy tính; backend, CSDL và frontend chạy bằng Docker Compose. Video quay thử (nếu có) chỉ dùng để đánh giá offline.

Hai loại không gian: mỗi phòng có trường loại (room_type). Khu tự học tự do (free_area): chỉ xem số người, chỗ trống và mức đông từ camera đếm qua đường ảo; không đặt chỗ, không check-in. Phòng chuyên đề (topic_room): xem lịch khung giờ, đặt cho nhóm, check-in QR, tự nhả phòng khi quá hạn. API đặt phòng từ chối yêu cầu đặt cho khu tự học tự do. Số người ban đầu được người vận hành ghi nhận sau khi kiểm tra khu vực ở đầu mỗi phiên; nếu chưa có số ban đầu đáng tin cậy hoặc sức chứa được xác nhận, không công bố chỗ trống/mức đông chính thức. Hiệu chỉnh là bản ghi riêng có người thực hiện, thời điểm và lý do, không sửa dữ liệu CV thô.

Ứng dụng cho sinh viên: ứng dụng Android native dùng chung API với web (đăng nhập OTP, xem chỗ trống, đặt phòng chuyên đề, check-in QR). Web responsive vẫn giữ cho thủ thư và sinh viên dùng trình duyệt. iOS không nằm trong phạm vi.

Hai cơ sở: hệ thống hỗ trợ hai thư viện CS1 và CS3; mỗi phòng thuộc một cơ sở. Mỗi cơ sở có camera đếm, khu tự học tự do và phòng chuyên đề riêng; sinh viên chọn cơ sở khi xem hoặc đặt; thủ thư xem dashboard theo từng cơ sở và tổng hợp. Triển khai thật phụ thuộc văn bản đồng ý của thư viện/nhà trường ; đến khi đủ điều kiện, kiểm thử bằng webcam laptop.

Đăng nhập: đăng nhập và đăng ký là một luồng: nhập email sinh viên, nhận mã OTP 6 số, nhập mã để vào; lần đầu tự tạo hồ sơ, không có mật khẩu. Giai đoạn thử nghiệm dùng danh sách email được phép và tài khoản demo do nhóm tạo; thủ thư do nhóm gán vai trò. Chỉ khi trường cấp văn bản đồng ý và cách kết nối chính thức mới thêm đăng nhập qua portal, qua một lớp đăng nhập thay thế được. Nhóm không nhận mật khẩu portal của sinh viên.

Nguyên tắc giảm tải cho CV/AI: dùng YOLOv8n, độ phân giải đầu vào 320–416 px, xử lý 3–5 khung hình/giây, cắt vùng quan tâm quanh cửa, có thể xuất sang ONNX/OpenVINO. Phần đánh giá nghiên cứu chạy offline trên video quay sẵn (Google Colab hoặc chạy qua đêm); phần demo trực tiếp chạy ở mức nhẹ.

## 7. Chỉ tiêu thành công (KPI)

| Chỉ số | Mục tiêu | Cách đo |
| --- | --- | --- |
| Sai số đếm | ≤ 10% | So với đếm tay trong 5–10 phiên thử, nhiều mức đông; dùng công thức sai số tổng hợp trong SRS và báo sai số tuyệt đối riêng nếu tổng đếm tay bằng 0 |
| Độ trễ cập nhật | p95 ≤ 5 giây | Từ lúc ghi nhận sự kiện đến lúc hiển thị trên web |
| Độ ổn định | Chạy liên tục ≥ 4 giờ trong một phiên kiểm thử | Nhật ký hệ thống; đây là mục tiêu thử nghiệm, không phải SLA |
| Tốc độ xử lý CV/AI | Trung vị ≥ 5 FPS ở khoảng 416 px (hoặc đánh giá offline nếu thấp hơn) | Đo tối thiểu 60 giây và ghi cấu hình môi trường |
| Trải nghiệm người dùng | Điểm SUS ≥ 70 | Khoảng 15–30 sinh viên dùng thử |
| Kiểm thử đặt phòng, check-in QR, tự nhả phòng | Chạy đúng các kịch bản kiểm thử (đặt, trùng lịch, check-in, quá hạn tự nhả) | Bộ test case; đo no-show thực tế nếu triển khai được tại thư viện |
| Triển khai thực tế | Chạy thử tại CS1 và CS3 sau khi được phép; thời lượng được nhóm và thư viện xác nhận trước khi triển khai | Nhật ký vận hành; số liệu đối chiếu đếm tay tại chỗ |
| Chi phí | Không vượt ngân sách trần | Bảng chi tiêu thực tế |

Các mục tiêu số sẽ được rà soát lại sau khảo sát thực địa.

## 8. Các bên liên quan

| Bên liên quan | Vai trò | Mối quan tâm chính |
| --- | --- | --- |
| Sinh viên | Người dùng cuối | Biết chỗ trống, đặt phòng dễ, không bị theo dõi cá nhân |
| Thủ thư / Ban quản lý thư viện | Khách hàng, người cấp phép đặt máy tính và webcam tại CS1 và CS3 | Số liệu quản lý, không ảnh hưởng hoạt động, an toàn dữ liệu |
| Giáo viên hướng dẫn | Đánh giá, cố vấn | Chất lượng nghiên cứu, tiến độ |
| Nhóm dự án | Thực hiện | Hoàn thành đúng hạn, học được kỹ năng |

## 9. Tổ chức nhóm và vai trò

| Vai trò | Người phụ trách | Người dự phòng | Trách nhiệm chính |
| --- | --- | --- | --- |
| Leader | Vũ Nguyễn Nhã Uyên |  | Kế hoạch, họp, làm việc với thư viện, kế hoạch kinh doanh, báo cáo |
| AI / CV Engineer | Lê Văn Trí |  | YOLO + tracking, đếm người, đo FPS, đánh giá độ chính xác |
| Backend Developer | Nguyễn Bình Khiêm và Nguyễn Lương Thắng |  | API, CSDL, đăng nhập OTP, logic đặt phòng chuyên đề, tự nhả phòng |
| Frontend / UI-UX DeveDevelop | Đỗ Lê Thùy Trâm và Lê Thị Ngọc Thi |  | Web chỗ trống, đặt phòng, dashboard, wireframe |
| Docker / tích hợp | Nguyễn Bình Khiêm |  | Docker Compose, .env.example, kiểm tra luồng dữ liệu giữa các dịch vụ |

## 10. Yêu cầu và thứ tự ưu tiên (MoSCoW)

| Ưu tiên | Yêu cầu |
| --- | --- |
| Must | Xem số chỗ trống, mật độ khu tự học tự do gần thời gian thực (không đặt chỗ) |
| Must | Đặt phòng chuyên đề cho nhóm theo khung giờ, kiểm tra trùng lịch |
| Must | Đăng nhập bằng mã OTP qua email sinh viên (đăng nhập và đăng ký chung một luồng, không mật khẩu) |
| Must | Đếm vào/ra bằng camera + YOLO + ByteTrack với sai số chấp nhận được (ít nhất chạy offline trên video) |
| Must | Chạy được toàn hệ thống bằng Docker Compose |
| Must | Thực nghiệm đối chiếu đếm tay |
| Should | Check-in QR và tự động nhả phòng sau 15 phút (giá trị tạm nội bộ; cần thư viện xác nhận trước vận hành thật) |
| Should | Ứng dụng Android native cho sinh viên (đăng nhập, xem chỗ trống, đặt phòng chuyên đề, check-in QR) |
| Should | Triển khai thử nghiệm tại hai thư viện CS1 và CS3 (phụ thuộc xin phép) |
| Could | Web cài được như ứng dụng (PWA) |
| Should | Dashboard thống kê cho thủ thư |
| Should | CV/AI chạy trực tiếp với camera (demo thời gian thực) |
| Could | Dự báo mật độ 1–2 giờ tới, thông báo khi có chỗ trống; đăng nhập qua portal trường nếu được cấp quyền |
| Won't (lần này) | Cảm biến/IoT, nhận diện khuôn mặt, ứng dụng iOS, đăng nhập qua portal của trường (trừ khi trường cấp quyền), đặt chỗ cho khu tự học tự do |

Quy tắc: chỉ làm Should khi Must đã xong; chỉ làm Could khi Should đã ổn định. Khi trễ tiến độ, cắt từ dưới lên.

## 11. Các mốc tiến độ

| Tuần | Sprint | Kết quả phải có |
| --- | --- | --- |
| 1–2 | Sprint 0 | Charter được duyệt, khảo sát xong, gửi đề nghị xin phép CS1 và CS3, chốt kiến trúc, kiểm tra webcam laptop và chuẩn bị môi trường Docker |
| 3 | Sprint 1 | YOLOv8n đếm được trên video mẫu; API và CSDL khung chạy được; docker compose up chạy được bộ khung |
| 4 | Sprint 2 | CV/AI gửi dữ liệu lên server; web hiển thị số người (bản thô) |
| 5 | Sprint 3 | Module đặt phòng chuyên đề và đăng nhập OTP hoàn chỉnh, giao diện theo wireframe; khởi tạo app Android (đăng nhập, xem chỗ trống) |
| 6 | Sprint 4 | Check-in QR và tự nhả phòng; app Android đặt phòng và check-in; đặt máy tính có webcam và chạy CV tại CS1/CS3 (nếu đã được phép), ghi dữ liệu thật |
| 7 | Sprint 5 | Thu thập số liệu đối chiếu đếm tay; dashboard thủ thư |
| 8 | Sprint 6 | Sửa lỗi, tối ưu, kiểm tra app Android trên điện thoại, thử nghiệm người dùng (SUS) |
| 9–10 | Sprint 7 | Đóng băng tính năng, báo cáo, slide, poster, video demo |

Cổng kiểm soát (Go/No-go): cuối Tuần 2 (đã có văn bản đồng ý của thư viện cho CS1 và CS3 chưa, webcam laptop chạy được YOLO chưa, kiến trúc đã chốt chưa?), cuối Tuần 4 (dữ liệu đã chảy từ CV/AI đến web chưa?), cuối Tuần 7 (đã đủ số liệu thực nghiệm chưa?).

## 12. Ngân sách và nguồn lực

| Hạng mục | Số lượng | Đơn giá | Thành tiền | Nguồn giá |
| --- | --- | --- | --- | --- |
| Webcam tích hợp sẵn trên máy tính (dùng thiết bị sẵn có, không mua camera) | 0 | 0 | 0 | Thiết bị sẵn có |
| Giá đỡ, dây, phụ kiện đặt webcam (không mua) | 0 | 0 | 0 | Không áp dụng |
| Máy tính chạy CV/AI tại mỗi cơ sở và máy chủ/hosting (khi triển khai thật; dùng máy sẵn có nếu được) | [ ] | [ ] | [ ] | [link] |
| In ấn (poster, biển thông báo) | [ ] | [ ] | [ ] | [ ] |
| Tổng |  |  | [ ] |  |

Nhóm đã chốt dùng webcam của máy tính nên không có ngân sách mua camera và phụ kiện; khi triển khai tại CS1 và CS3 chỉ cần xét máy tính chạy CV/AI và hosting. Email OTP dùng SMTP miễn phí. App Android cài trực tiếp bằng file APK khi thử nghiệm; nếu đưa lên cửa hàng ứng dụng có thể phát sinh phí tài khoản nhà phát triển (nhóm xét). Giá phải do nhóm tự tra tại thời điểm mua và ghi rõ nguồn. Phần mềm sử dụng ưu tiên miễn phí/mã nguồn mở (FastAPI, PostgreSQL, Docker, Ultralytics, Google Colab, GitHub, Jira).

## 13. Quản lý rủi ro

| Rủi ro | Xác suất | Ảnh hưởng | Phương án đối phó | Người theo dõi |
| --- | --- | --- | --- | --- |
| Thư viện hoặc nhà trường chậm hoặc không cho đặt máy tính/webcam tại CS1/CS3 | Trung bình | Rất cao | Xin văn bản đồng ý sớm (Tuần 1–2); đề xuất vị trí và quy trình; dự phòng kiểm thử bằng webcam laptop và video quay thử, ghi rõ giới hạn | LD |
| Laptop không đủ mạnh cho YOLO | Trung bình | Trung bình | YOLOv8n, giảm độ phân giải/FPS, ONNX/OpenVINO, đánh giá offline trên Colab | AI/CV |
| YOLO đếm sai khi đông hoặc bị che khuất | Cao | Trung bình | Coi là kết quả nghiên cứu, phân tích lỗi, điều chỉnh vị trí camera và đường ảo | AI/CV |
| CV/AI không truy cập được camera trong Docker | Thấp | Trung bình | Đã chốt: chạy CV/AI ngoài Docker, đọc webcam trực tiếp; các dịch vụ còn lại chạy bằng Docker Compose | AI/CV |
| Webcam máy tính hỏng hoặc chất lượng kém (góc thấp, độ phân giải thấp) | Thấp | Trung bình | Kiểm tra webcam sớm; mượn webcam rời của thành viên hoặc dùng video quay thử | AI/CV |
| Email OTP vào thư mục spam hoặc bị trường chặn | Trung bình | Trung bình | Thử sớm với 3–5 email sinh viên thật; dự phòng bằng mã mời và tài khoản demo | Backend |
| Người thử ngoài nhóm không truy cập được hệ thống (chạy Docker trên laptop) | Trung bình | Trung bình | Thử cùng Wi-Fi hoặc đường hầm tạm; xét hosting miễn phí; ghi rõ giới hạn | Docker |
| Trường không cấp kết nối portal | Cao | Thấp | Dùng đăng nhập OTP và tài khoản demo; lớp đăng nhập thay thế được; ghi portal là hướng phát triển | LD |
| Phạm vi quá lớn so với 10 tuần (app Android, hai cơ sở, triển khai thật) | Cao | Cao | App Android và triển khai thật là Should; ưu tiên web và API trước; thử một cơ sở trước; cắt từ dưới lên nếu trễ | LD |
| Điều kiện hai cơ sở khác nhau (số cửa, Wi-Fi, ánh sáng, nguồn điện) | Trung bình | Trung bình | Khảo sát tại chỗ từng cơ sở sớm; cấu hình riêng cho mỗi cơ sở | AI/CV |
| Thành viên bận hoặc nghỉ | Trung bình | Cao | Người dự phòng, tài liệu hóa công việc | LD |
| Lo ngại quyền riêng tư về camera tại thư viện | Trung bình | Cao | Camera nhìn từ trên xuống, xử lý tại chỗ, không lưu video; có biển thông báo và văn bản đồng ý | LD |
| Trễ tiến độ | Cao | Cao | Cắt tính năng Could/Should, không cắt Must | LD |

Rủi ro được rà soát lại trong buổi họp cuối mỗi tuần.

## 14. Giả định và ràng buộc

Giả định

• Mỗi thành viên có laptop với webcam hoạt động; có thể tổ chức phiên thử với người tham gia đã đồng ý. Người thử ngoài nhóm ưu tiên kết nối cùng Wi-Fi; đường hầm hoặc hosting cần Uyên phê duyệt và phải có xác thực, giới hạn truy cập.

• Thư viện và nhà trường đồng ý cho đặt máy tính có webcam tại CS1 và CS3 với điều kiện hợp lý; có nguồn điện và Wi-Fi tại vị trí đặt.

• Có nguồn điện và Wi-Fi tại nơi kiểm thử.

• Giai đoạn thử nghiệm dùng email sinh viên (OTP) hoặc tài khoản demo; việc dùng portal của trường phụ thuộc văn bản đồng ý và cách kết nối chính thức từ trường.

• Mỗi thành viên thống nhất và cập nhật thời lượng đóng góp hàng tuần trong kế hoạch sprint; chưa đặt một ngưỡng giờ chung.

Ràng buộc

• Thời gian 10 tuần, không mua camera (dùng webcam máy tính); chi phí khác theo mục 12.

• Cấu hình máy hạn chế (laptop cá nhân), không có GPU chuyên dụng.

• Phải tuân thủ quy định của thư viện và nhà trường.

## 15. Quyền riêng tư và đạo đức dữ liệu

• Khi triển khai tại CS1 và CS3: có văn bản/email đồng ý của thư viện và nhà trường trước khi đặt máy tính và webcam, và có biển thông báo tại khu vực. Khi kiểm thử: chỉ quay người trong nhóm hoặc tình nguyện viên đã đồng ý.

• Webcam máy tính đặt cố định, ưu tiên góc cao nhìn xuống nếu có thể, xử lý ngay trên máy, không lưu video, không nhận diện khuôn mặt hay danh tính; chỉ gửi con số lên server.

• Video dùng để đánh giá (nếu có) chỉ lưu tạm, hạn chế truy cập trong nhóm, xóa sau khi tính xong; không đưa lên Git; ghi rõ trong báo cáo.

• Chỉ lưu số liệu tổng hợp ẩn danh. Dữ liệu đặt phòng gắn với mã sinh viên được thu thập tối thiểu, bảo mật và xóa sau khi kết thúc dự án nếu không cần.

• Email và mã sinh viên của người thử là dữ liệu cá nhân: chỉ thu thập khi người dùng đồng ý, lưu tối thiểu, mã OTP chỉ lưu dạng băm, xóa sau khi kết thúc dự án. Không nhận hay lưu mật khẩu portal của sinh viên.

• Đối chiếu với Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân và nêu rõ trong báo cáo.

• Báo cáo trung thực các hạn chế (đếm sai khi đông, che khuất, ánh sáng yếu).

## 16. Quy tắc làm việc

• Họp: Sprint Planning đầu tuần (30 phút), Daily Standup 15 phút (hoặc cập nhật qua chat), Sprint Review + Retro cuối tuần (45 phút).

• Git: nhánh main (ổn định), dev, feature/SEAT-x-ten-ngan, fix/..., docs/...; mọi thay đổi vào dev phải qua Pull Request và có ít nhất một người khác review. Commit theo dạng SEAT-x loai: noi dung (feat, fix, docs, ...). Chi tiết trong tài liệu "Quy ước làm việc nhóm – Git và Jira" và README.

• Cấu trúc repo: cv/, backend/, frontend/, docs/; file Docker Compose: [vị trí chưa chốt].

• Ghi quyết định: mọi thay đổi kiến trúc ghi vào docs/decisions.md.

• Definition of Done: code đã được review, chạy được trên môi trường thật (trong Docker nếu thuộc phạm vi), đã kiểm thử, có ghi chú/tài liệu ngắn, bảng công việc được cập nhật.

## 17. Nhật ký quyết định (Decision log)

| # | Quyết định | Lý do |
| --- | --- | --- |
| 1 | Chọn đề tài D6 | Có đủ AI, web và khách hàng thật |
| 2 | Ban đầu dùng hai phương án A (cảm biến) và B (camera + YOLO) để so sánh (đã được thay thế bởi quyết định 6) | Tạo chiều sâu nghiên cứu, có phương án dự phòng |
| 3 | Đã cân nhắc bỏ camera sang cảm biến khác (radar, nhiệt…) rồi quyết định giữ nguyên thiết kế ban đầu (đã được thay thế bởi quyết định 6) | Giữ phạm vi gọn, tập trung hoàn thành |
| 4 | Dùng YOLOv8n, giảm độ phân giải/FPS, đánh giá offline | Lo ngại laptop không đủ mạnh |
| 5 | Backend FastAPI, CSDL PostgreSQL, web responsive | Cùng ngôn ngữ Python, dễ ghép và demo |
| 6 | Chốt Phương án B (camera + YOLOv8n + ByteTrack); bỏ phần cứng/cảm biến (Phương án A) |  |
| 7 | Chạy hệ thống kèm Docker (Docker Compose) | Chuẩn hóa môi trường, chạy cả hệ thống bằng một lệnh |
| 8 | Dùng webcam tích hợp sẵn trên laptop để kiểm thử và demo; không mua camera, không lắp đặt tại thư viện (phần không lắp đặt được thay bằng quyết định #16) | Tiết kiệm chi phí, bỏ rủi ro xin phép và lắp đặt, tập trung hoàn thành phần mềm và thực nghiệm |
| 9 | Chạy mô-đun CV/AI ngoài Docker, đọc trực tiếp webcam laptop; các dịch vụ còn lại chạy bằng Docker Compose | Docker Desktop trên Windows/macOS khó dùng webcam trong container |
| 10 | Chia không gian thành hai loại: khu tự học tự do (chỉ xem mật độ, không đặt chỗ) và phòng chuyên đề (đặt theo khung giờ) | Khớp cách thư viện vận hành; camera đếm chỉ có ý nghĩa với khu tự do, đặt chỗ chỉ cần cho phòng nhóm |
| 11 | Làm ứng dụng cho sinh viên dạng PWA, không làm app native (được thay bằng quyết định #14) | Dùng lại mã React + Vite, không phải build và ký ứng dụng, phù hợp thời gian còn lại |
| 12 | Đăng nhập bằng mã OTP qua email sinh viên; đăng nhập và đăng ký chung một luồng, không mật khẩu | Giảm số màn hình và rủi ro lưu mật khẩu; thử được với sinh viên thật khi chưa có portal |
| 13 | Chỉ tích hợp portal của trường khi trường cấp văn bản đồng ý và cách kết nối chính thức; thiết kế lớp đăng nhập thay thế được | Tránh vi phạm quy định và Nghị định 13/2023; không nhận mật khẩu portal |
| 14 | Thêm ứng dụng Android native cho sinh viên (thay quyết định #11); ứng dụng iOS ngoài phạm vi | Nhóm muốn có app riêng cho sinh viên dùng chung API với web; chấp nhận rủi ro về thời gian |
| 15 | Hệ thống hỗ trợ hai cơ sở thư viện CS1 và CS3: mỗi phòng thuộc một cơ sở, dữ liệu tách theo cơ sở | Dự án triển khai tại hai thư viện; dùng chung một backend để dễ quản lý |
| 16 | Triển khai thử nghiệm tại CS1 và CS3 khi đủ điều kiện (văn bản đồng ý, mạng, điện), dùng webcam của máy tính; trước đó kiểm thử bằng webcam laptop | Thực hiện đúng mục tiêu dự án; giữ phương án kiểm thử để không bị chặn nếu xin phép chậm |
| 17 | Chốt dùng webcam của máy tính cho cả kiểm thử và triển khai; bỏ ngân sách mua camera | Giảm chi phí, tránh phụ thuộc giao hàng và lắp đặt |
| 18 | Mỗi phiên đếm bắt đầu bằng số người do người vận hành kiểm tra và nhập; nếu thiếu số ban đầu đáng tin cậy thì không công bố chỗ trống/mức đông chính thức; hiệu chỉnh được lưu riêng có truy vết | Không cộng dồn số liệu thiếu căn cứ và giữ được lịch sử kiểm toán |
| 19 | Kiểm thử người ngoài nhóm ưu tiên cùng Wi-Fi; đường hầm/hosting chỉ dùng khi Uyên phê duyệt, có xác thực và giới hạn truy cập | Tránh mở hệ thống thử nghiệm công khai hoặc không kiểm soát |
| 20 | Chốt Android native bằng Kotlin, phát hành thử nghiệm APK trực tiếp; iOS ngoài phạm vi | Khớp lựa chọn nhóm và tránh phụ thuộc cửa hàng ứng dụng |

Các quyết định #18–#20 được Uyên duyệt cho phát triển/kiểm thử nội bộ ngày 10/11/2026; không thay thế phê duyệt của thư viện, nhà trường hoặc giáo viên hướng dẫn. Quyết định về sức chứa thực tế, vị trí webcam, thu thập dữ liệu và chính sách vận hành tại thư viện vẫn cần văn bản xác nhận trước khi triển khai.

## 18. Phê duyệt

Bằng việc ký tên dưới đây, các thành viên đồng ý với phạm vi, mục tiêu và quy tắc làm việc của dự án.

| Họ tên | Vai trò | Chữ ký | Ngày |
| --- | --- | --- | --- |
| [ ] | Nhóm trưởng |  |  |
| [ ] | AI / CV |  |  |
| [ ] | Backend |  |  |
| [ ] | Frontend / UI-UX |  |  |
| [ ] | Giáo viên hướng dẫn |  |  |

## 19. Lịch sử thay đổi

| Phiên bản | Ngày | Thay đổi | Người cập nhật |
| --- | --- | --- | --- |
| 1.0 | 26/10/2026 | Bản đầu tiên | LD |
| 1.1 | 26/10/2026 | Giữ camera + cảm biến | LD |
| 1.2 | 28/10/2026 | Chốt Phương án B, bỏ phần cứng/cảm biến, thêm Docker; cập nhật phạm vi, KPI, vai trò, tiến độ, ngân sách, rủi ro | LD |
| 1.3 | 07/11/2026 | Chuyển sang kiểm thử bằng webcam laptop, bỏ mua và lắp camera tại thư viện; cập nhật phạm vi, KPI, tiến độ, ngân sách, rủi ro, quyền riêng tư; thêm quyết định #8, #9 | LD |
| 1.4 | 07/11/2026 | Chia hai loại không gian (khu tự học tự do, phòng chuyên đề); PWA thay app native; đăng nhập OTP qua email, bỏ đăng ký riêng; portal là tùy chọn; thêm quyết định #10 đến #13 | LD |
| 1.5 | 07/11/2026 | Thêm app Android native; hỗ trợ hai cơ sở CS1 và CS3; triển khai thử nghiệm tại thư viện khi đủ điều kiện; khôi phục ngân sách, rủi ro, quyền riêng tư cho camera thật; thêm quyết định #14 đến #16 | LD |
| 1.6 | 07/11/2026 | Chốt dùng webcam của máy tính; bỏ ngân sách mua camera và phụ kiện; cập nhật rủi ro, quyền riêng tư; thêm quyết định #17 | LD |
| 1.7 | 10/11/2026 | Bổ sung quy trình số người ban đầu/hiệu chỉnh; giới hạn truy cập thử nghiệm; chốt Kotlin/APK và đồng bộ KPI với SRS 1.8; thêm quyết định #18–#20 | LD |
