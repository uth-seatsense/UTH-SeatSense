# Project Charter: UTH-SeatSense (Đề tài D6)

*Hệ thống theo dõi mật độ sử dụng phòng đọc và đặt phòng học nhóm tại Thư viện UTH*

Học kỳ doanh nghiệp · Phiên bản 1.2 (cập nhật: chốt Phương án B – camera + YOLO, bỏ phần cứng, chạy kèm Docker) · Ngày lập: 26/10/2026 · Cập nhật: 28/10/2026

## 1. Thông tin chung

| Mục | Nội dung |
| --- | --- |
| Tên dự án | UTH-SeatSense (tên tạm, có thể đổi) |
| Mã đề tài | D6 – Đặt chỗ và theo dõi mật độ sử dụng phòng đọc |
| Đơn vị hưởng lợi | Trung tâm Thông tin Thư viện UTH |
| Nhóm trưởng / Project Manager | Vũ Nguyễn Nhã Uyên |
| Giáo viên hướng dẫn | TS.Đặng Nhân Cánh |
| Thời gian thực hiện | 2.5 tháng, từ \[26/10/2026\] đến \[26/12/2026\] |
| Ngân sách trần | Chưa thống kê |
| Kho mã nguồn | <https://github.com/uth-seatsense/UTH-SeatSense> |
| Bảng công việc | <https://nhauyen70205.atlassian.net/jira/software/projects/SEAT/boards/2?filter=&groupBy=none> |
| Tài liệu hướng dẫn chạy dự án | README.md trong kho mã nguồn |

## 2. Bối cảnh và vấn đề

Sinh viên thường phải đến tận nơi mới biết phòng đọc còn chỗ hay không, mất thời gian tìm chỗ và đôi khi phải quay về. Phòng học nhóm có thể được đặt nhưng không sử dụng (no-show), gây lãng phí. Thủ thư chưa có số liệu mật độ theo giờ/ngày để bố trí không gian và nhân sự.

Các vấn đề này sẽ được **xác nhận bằng số liệu khảo sát thật** ở Tuần 1–2 (phỏng vấn thủ thư, khảo sát 50–100 sinh viên). Các con số trong mục KPI sẽ được hiệu chỉnh lại sau khảo sát.

## 3. Mục tiêu dự án

1. Hiển thị số chỗ trống và mức độ đông của phòng đọc gần thời gian thực trên web.
2. Cho phép sinh viên đặt phòng học nhóm theo khung giờ, check-in bằng QR, tự động nhả phòng khi quá hạn.
3. Cung cấp dashboard thống kê cho thủ thư (mật độ theo giờ/ngày, tỳ lệ sử dụng phòng, tỳ lệ no-show).
4. Đánh giá độ chính xác và tốc độ xử lý của phương pháp đếm người bằng camera + YOLO, rút ra kết luận bằng số liệu thực nghiệm.
5. Đóng gói hệ thống bằng Docker để cả nhóm chạy cùng một môi trường.
6. Xây dựng kế hoạch kinh doanh cho sản phẩm (mô hình doanh thu, chi phí, điểm hòa vốn).

## 4. Câu hỏi nghiên cứu

- Camera dùng YOLO có đếm số người đủ chính xác (sai số ≤ 10% so với đếm tay), đủ nhanh trên laptop thường và bảo vệ được quyền riêng tư không?
- Hiển thị chỗ trống thời gian thực và đặt phòng online có giúp giảm thời gian tìm chỗ và tăng hiệu suất sử dụng phòng không?

## 5. Phạm vi

**Trong phạm vi (In scope)**

- 1 phòng đọc và 1–2 phòng học nhóm.
- **Phương án B (đã chốt):** camera + YOLOv8 (bản nhẹ) + tracker (ByteTrack), đếm khi người cắt đường ảo.
- Web responsive: xem chỗ trống, đặt phòng, check-in QR, dashboard thủ thư.
- Đóng gói và chạy các dịch vụ bằng Docker Compose.
- Thực nghiệm đối chiếu đếm tay, thử nghiệm người dùng (SUS), báo cáo và kế hoạch kinh doanh.

**Ngoài phạm vi (Out of scope)**

- Phương án A (ESP32 + cảm biến khoảng cách) và mọi phần cứng IoT.
- Nhận diện khuôn mặt hoặc định danh người trong ảnh.
- Lưu trữ video/hình ảnh lâu dài.
- Tích hợp với hệ thống đào tạo/tài khoản chính thức của trường.
- Ứng dụng native (iOS/Android).
- Triển khai toàn bộ thư viện hoặc nhiều tòa nhà.

## 6. Giải pháp tổng quan

| Thành phần | Công nghệ | Vai trò |
| --- | --- | --- |
| CV/AI (`cv/`) | Camera + YOLOv8n + ByteTrack, đếm qua đường ảo | Đếm người vào/ra, chỉ gửi con số lên server |
| Backend (`backend/`) | FastAPI | Nhận dữ liệu đếm, API, logic đặt phòng, check-in, tự nhả phòng |
| CSDL | PostgreSQL | Lưu dữ liệu hệ thống |
| Frontend (`frontend/`) | Web responsive (framework: \[chưa chốt\]) | Chỗ trống, đặt phòng, dashboard |
| Docker | Docker Compose | Đóng gói, chạy các dịch vụ bằng một lệnh |

```
[Camera + YOLOv8n + ByteTrack] -> (số lượng vào/ra) -> Server (FastAPI) -> PostgreSQL -> Web / Dashboard
```

**Vai trò của Docker:** chuẩn hóa môi trường để mọi thành viên chạy cùng một hệ thống; khởi động toàn bộ dịch vụ bằng `docker compose up -d --build`; giữ dữ liệu PostgreSQL trong volume; hỗ trợ demo và triển khai. Docker chỉ là lớp đóng gói và chạy, không tham gia xử lý nghiệp vụ hay nhận diện người.

**Lưu ý về camera trong Docker:** Docker Desktop trên Windows/macOS thường khó cho container dùng webcam USB. Cách xử lý (chạy CV/AI ngoài Docker hoặc cho CV/AI đọc video quay sẵn trong Docker): \[nhóm chốt\].

**Nguyên tắc giảm tải cho CV/AI:** dùng YOLOv8n, độ phân giải đầu vào 320–416 px, xử lý 3–5 khung hình/giây, cắt vùng quan tâm quanh cửa, có thể xuất sang ONNX/OpenVINO. Phần **đánh giá nghiên cứu** chạy offline trên video quay sẵn (Google Colab hoặc chạy qua đêm); phần **demo trực tiếp** chạy ở mức nhẻ.

## 7. Chỉ tiêu thành công (KPI)

| Chỉ số | Mục tiêu | Cách đo |
| --- | --- | --- |
| Sai số đếm | ≤ 10% | So với đếm tay, 5–10 phiên × 30–60 phút, nhiều mức đông |
| Độ trễ cập nhật | ≤ 5 giây | Từ lúc có người vào đến lúc web hiển thị |
| Độ ổn định | Chạy liên tục ≥ \[x\] giờ, ít mất kết nối | Nhật ký hệ thống |
| Tốc độ xử lý CV/AI | ≥ 5 FPS ở 416 px (hoặc chạy offline nếu thấp hơn) | Script đo FPS |
| Trải nghiệm người dùng | Điểm SUS ≥ 70 | 15–30 sinh viên dùng thử |
| Hiệu quả đặt phòng | Tỷ lệ no-show giảm so với trước khi có check-in | Số liệu thư viện cung cấp (nếu được phép) |
| Chi phí | Không vượt ngân sách trần | Bảng chi tiêu thực tế |

*Các mục tiêu số sẽ được rà soát lại sau khảo sát thực địa.*

## 8. Các bên liên quan

| Bên liên quan | Vai trò | Mối quan tâm chính |
| --- | --- | --- |
| Sinh viên | Người dùng cuối | Biết chỗ trống, đặt phòng dễ, không bị theo dõi cá nhân |
| Thủ thư / Ban quản lý thư viện | Khách hàng, người cấp phép | Số liệu quản lý, không ảnh hưởng hoạt động, an toàn dữ liệu |
| Giáo viên hướng dẫn | Đánh giá, cố vấn | Chất lượng nghiên cứu, tiến độ |
| Nhóm dự án | Thực hiện | Hoàn thành đúng hạn, học được kỹ năng |

## 9. Tổ chức nhóm và vai trò

| Vai trò | Người phụ trách | Người dự phòng | Trách nhiệm chính |
| --- | --- | --- | --- |
| Leader | Vũ Nguyễn Nhã Uyên |  | Kế hoạch, họp, làm việc với thư viện, kế hoạch kinh doanh, báo cáo |
| AI / CV Engineer | Lê Văn Trí |  | YOLO + tracking, đếm người, đo FPS, đánh giá độ chính xác |
| Backend Developer | Nguyễn Bình Khiêm và Nguyễn Lương Thắng |  | API, CSDL, logic đặt phòng, tự nhả phòng |
| Frontend / UI-UX DeveDeveloper | Đỗ Lê Thùy Trâm và Le Thị Ngọc Thi |  | Web chỗ trống, đặt phòng, dashboard, wireframe |
| Docker / tích hợp&#32; | Nguyễn Bình Khiêm |  | Docker Compose, `.env.example`, kiểm tra luồng dữ liệu giữa các dịch vụ |

## 10. Yêu cầu và thứ tự ưu tiên (MoSCoW)

| Ưu tiên | Yêu cầu |
| --- | --- |
| **Must** | Xem số chỗ trống phòng đọc gần thời gian thực |
| **Must** | Đặt phòng nhóm theo khung giờ, kiểm tra trùng lịch |
| **Must** | Đếm vào/ra bằng camera + YOLO + ByteTrack với sai số chấp nhận được (ít nhất chạy offline trên video) |
| **Must** | Chạy được toàn hệ thống bằng Docker Compose |
| **Must** | Thực nghiệm đối chiếu đếm tay |
| **Should** | Check-in QR và tự động nhả phòng khi quá 10–15 phút |
| **Should** | Dashboard thống kê cho thủ thư |
| **Should** | CV/AI chạy trực tiếp với camera (demo thời gian thực) |
| **Could** | Dự báo mật độ 1–2 giờ tới, thông báo khi có chỗ trống |
| **Won't (lần này)** | Cảm biến/IoT, nhận diện khuôn mặt, app native, tích hợp tài khoản của trường |

**Quy tắc:** chỉ làm *Should* khi *Must* đã xong; chỉ làm *Could* khi *Should* đã ổn định. Khi trễ tiến đớ, cắt từ dưới lên.

## 11. Các mốc tiến độ

| Tuần | Sprint | Kết quả phải có |
| --- | --- | --- |
| 1–2 | Sprint 0 | Charter được duyệt, khảo sát xong, thư viện đồng ý bằng văn bản, chốt kiến trúc, chuẩn bị camera và môi trường Docker |
| 3 | Sprint 1 | YOLOv8n đếm được trên video mẫu; API và CSDL khung chạy được; `docker compose up` chạy được bộ khung |
| 4 | Sprint 2 | CV/AI gửi dữ liệu lên server; web hiển thị số người (bản thô) |
| 5 | Sprint 3 | Module đặt phòng hoàn chỉnh, giao diện theo wireframe |
| 6 | Sprint 4 | Lắp thử camera tại thư viện, ghi dữ liệu thật; check-in QR và tự nhả phòng |
| 7 | Sprint 5 | Thu thập số liệu đối chiếu đếm tay; dashboard thủ thư |
| 8 | Sprint 6 | Sửa lỗi, tối ưu, thử nghiệm người dùng (SUS) |
| 9–10 | Sprint 7 | Đóng băng tính năng, báo cáo, slide, poster, video demo |

**Cổng kiểm soát (Go/No-go):** cuối Tuần 2 (có giấy phép thư viện chưa?), cuối Tuần 4 (dữ liệu đã chảy từ CV/AI đến web chưa?), cuối Tuần 7 (đã đủ số liệu thực nghiệm chưa?).

## 12. Ngân sách và nguồn lực

| Hạng mục | Số lượng | Đơn giá | Thành tiền | Nguồn giá |
| --- | --- | --- | --- | --- |
| Camera (webcam/USB) | \[ \] | \[ \] | \[ \] | \[link\] |
| Giá đỡ, dây, phụ kiện lắp camera | \[ \] | \[ \] | \[ \] | \[link\] |
| Máy chủ/hosting (nếu cần) | \[ \] | \[ \] | \[ \] | \[link\] |
| In ấn (poster, biển thông báo) | \[ \] | \[ \] | \[ \] | \[ \] |
| **Tổng** |  |  | **\[ \]** |  |

Giá phải do nhóm tự tra tại thời điểm mua và ghi rõ nguồn. Phần mềm sử dụng ưu tiên miễn phí/mã nguồn mở (FastAPI, PostgreSQL, Docker, Ultralytics, Google Colab, GitHub, Jira).

## 13. Quản lý rủi ro

| Rủi ro | Xác suất | Ảh hưởng | Phương án đối pló | Người theo dõi |
| --- | --- | --- | --- | --- |
| Thư viện không cho lắp camera | Trung bình | Rất cao | Xin phép sớm; dự phòng: thử ở khu vực khác của trường hoặc dùng video quay thử có phép | PM |
| Laptop không đủ mạnh cho YOLO | Trung bình | Trung bình | YOLOv8n, giảm độ phân giải/FPS, ONNX/OpenVINO, đánh giá offline trên Colab | AI/CV |
| YOLO đếm sai khi đông hoặc bị che khuất | Cao | Trung bình | Coi là kết quả nghiên cứu, phân tích lỗi, điều chỉnh vị trí camera và đường ảo | AI/CV |
| CV/AI không truy cập được camera trong Docker | Cao | Trung bình | Chạy CV/AI ngoài Docker hoặc cho CV/AI đọc video quay sẵn trong Docker | AI/CV |
| Camera giao chậm hoặc hỏng | Trung bình | Cao | Đặt hàng ngay Tuần 2, chuẩn bị camera dự phòng | AI/CV |
| Thành viên bận hoặc nghỉ | Trung bình | Cao | Người dự phòng, tài liệu hóa công việc | LD |
| Lo ngại quyền riêng tư về camera | Trung bình | Cao | Camera nhìn từ trên xuống, xử lý tại chỗ, không lưu video, biển thông báo, văn bản đồng ý | LD |
| Trễ tiến độ | Cao | Cao | Cắt tính năng *Could/Should*, không cắt *Must* | LD |

Rủi rođược rà soát lại trong buổi họp cuối mỗi tuần.

## 14. Giả định và ràng buộc

**Giả định**

- Thư viện đồng ý cho lắp thử camera tại một khu vực với điều kiện hợp lý.
- Có nguồn điện và Wi-Fi tại vị trí lắp đặt.
- Mỗi thành viên dành tối thiểu \[x\] giờ/tuần cho dự án.

**Ràng buộc**

- Thời gian 10 tuần, ngân sách trần như mục 12.
- Cấu hình máy hạn chế (laptop cá nhân), không có GPU chuyên dụng.
- Phải tuân thủ quy định của thư viện và nhà trường.

## 15. Quyền riêng tư và đạo đức dữ liệu

- Có văn bản/email đồng ý của thư viện **trước** khi lắp camera, và có biển thông báo tại khu vực.
- Camera đặt trên cao nhìn xuống, **Ỵ lý ngay trên máy, không lưu video**, không nhận diện khuôn mặt hay danh tính; chỉ gửi con số lên server.
- Video dùng để đánh giá (nếu có) chỉ lưu tạm, hạn chế truy cập trong nhóm, xóa sau khi tính xong; không đưa lên Git; ghi rõ trong báo cáo.
- Chỉ lưu số liệu tổng hợp ẩn danh. Dữ liệu đặt phòng gắn với mã sinh viên được thu thập tối thiểu, bảo mật và xóa sau khi kết thúc dự án nếu không cần.
- Đối chiếu với Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân và nêu rõ trong báo cáo.
- Báo cáo trung thực các hạn chế (đếm sai khi đông, che khuất, ánh sáng yếu).

## 16. Quy tắc làm việc

- **Họp:** Sprint Planning đầu tuần (30 phút), Daily Standup 15 phút (hoặc cập nhật qua chat), Sprint Review + Retro cuối tuần (45 phút).
- **Git:** nhánh `main` (ổn định), `dev`, `feature/SEAT-x-ten-ngan`, `fix/...`, `docs/...`; mọi thay đổi vào `dev` phải qua Pull Request và có ít nhất một người khác review. Commit theo dạng `SEAT-x loai: noi dung` (`feat`, `fix`, `docs`, ...). Chi tiết trong tài liệu "Quy ước làm việc nhóm – Git và Jira" và README.
- **Cấu trúc repo:** `cv/`, `backend/`, `frontend/`, `docs/`; file Docker Compose: \[ị trí chưa chốt\].
- **Ghi quyết định:** mọi thay đổi kiến trúc ghi vào `docs/decisions.md`.
- **Definition of Done:** code đã được review, chạy được trên môi trường thật (trong Docker nếu thuộc phạm vi), đã kiểm thử, có ghi chú/tài liệu ngắn, bảng công việc được cập nhật.

## 17. Nhật ký quyết định (Decision log)

| # | Quyết định | Lý do |
| --- | --- | --- |
| 1 | Chọn đề tài D6 | Có đủ AI, web và khách hàng thật |
| 2 | Ban đầu dùng hai phương án A (cảm biến) và B (camera + YOLO) để so sánh *(đã được thay thế bởi quyết định 6)* | Tạo chiều sâu nghiên cứu, có phương án dự phòng |
| 3 | Đã cân nhắc bỏ camera sang cảm biến khác (radar, nhiệt…) rồi quyết định giữ nguyên thiết kế ban đầu *(đã được thay thế bởi quyết định 6)* | Giữ phạm vi gọn, tập trung hoàn thành |
| 4 | Dùng YOLOv8n, giảm độ phân giải/FPS, đánh giá offline | Lo ngại laptop không đủ mạnh |
| 5 | Backend FastAPI, CSDL PostgreSQL, web responsive | Cùng ngôn ngữ Python, dễ ghép và demo |
| 6 | **Chốt Phương án B (camera + YOLOv8n + ByteTrack); bỏ phần cứng/cảm biến (Phương án A)** |  |
| 7 | **Chạy hệ thống kèm Docker (Docker Compose)** | Chuẩn hóa môi trường, chạy cả hệ thống bằng một lệnh |

## 18. Phê duyệt

Bằng việc ký tên dưới đây, các thành viên đồng ý với phạm vi, mục tiêu và quy tắc làm việc của dự án.

| Họ tên | Vai trò | Chữ ký | Ngày |
| --- | --- | --- | --- |
| \[ \] | Nhóm trưởng&#32; |  |  |
| \[ \] | AI / CV |  |  |
| \[ \] | Backend |  |  |
| \[ \] | Frontend / UI-UX |  |  |
| \[ \] | Giáo viên hướng dẫn |  |  |

## 19. Lịch sử thay đổi

| Phiên bản | Ngày | Thay đổi | Người cập nhật |
| --- | --- | --- | --- |
| 1.0 | 26/10/2026 | Bản đầu tiên | LD |
| 1.1 | 26/10/2026 | Giữ camera + cảm biến | LD |
| 1.2 | 28/10/2026 | Chốt Phương án B, bỏ phần cứng/cảm biến, thêm Docker; cập nhật phạm vi, KPI, vai trò, tiến độ, ngân sách, rủi ro | LD |
