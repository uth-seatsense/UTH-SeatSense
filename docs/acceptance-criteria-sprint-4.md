# Tiêu chí nghiệm thu Sprint 4

Các tiêu chí dưới đây được đối chiếu với backlog Sprint 4 ngày 15/11/2026
(SEAT-51–64) và SRS 1.9. Mỗi tiêu chí gắn với FR/BR và mã kiểm thử hiện có
trong SRS. Tài liệu này chưa cập nhật Jira; nhãn `AC-ready` và xác nhận của
dev chỉ được ghi nhận sau khi cập nhật issue và có comment thực tế.

## Các điểm phải thống nhất trong Jira trước khi đóng task

1. **SEAT-54 — số ban đầu:** công thức SRS là
   `max(0, N0 + tổng IN − tổng OUT)`. Chỉ dùng `tổng IN − tổng OUT` khi
   `N0 = 0` đã được người vận hành kiểm tra và ghi nhận; không tự mặc định N0.
2. **SEAT-56 — không có occupancy:** task nêu 503 khi chưa có dữ liệu, còn
   SRS yêu cầu giao diện báo chưa đủ dữ liệu và API contract cũ dùng 404.
   Phân biệt phòng không tồn tại (404), occupancy chưa khởi tạo (mã lỗi nghiệp
   vụ rõ ràng, không hiển thị số giả) và lỗi dịch vụ/DB (503).
3. **SEAT-51/53/57 — heartbeat:** SEAT-51 yêu cầu gửi `device_status` định kỳ,
   trong khi SEAT-53 hiện chỉ mô tả POST sự kiện đếm. Chốt endpoint/payload
   heartbeat cùng API contract trước khi bắt đầu tích hợp.
4. **SEAT-52 — tiêu chí sai số:** backlog yêu cầu sai lệch “chấp nhận được”
   nhưng chưa nêu ngưỡng đã duyệt. Ghi rõ ground truth, sai số và giới hạn
   của lần chạy; không tự tuyên bố đạt ngưỡng chưa được phê duyệt.

## SEAT-51 — Gửi sự kiện CV đến API

**Traceability:** FR-OCC-01/02; BR-13; NFR-SEC-02, NFR-PRI-01; TC-22.

1. Given CV xác nhận một lượt cắt đường ảo và có `room_id`, `device_id`,
   `direction`, `event_time` UTC cùng `event_id` UUID, When gửi sự kiện đến
   API, Then backend nhận đúng payload và tạo một bản ghi `CountEvent`
   (FR-OCC-01, TC-22).
2. Given backend ngừng phản hồi trong một phút và CV đã lưu sự kiện trong hàng
   đợi cục bộ, When backend hoạt động lại, Then CV gửi lại cùng `event_id`,
   sự kiện được ghi đúng một lần và hàng đợi chỉ xóa sau xác nhận hợp lệ
   (BR-13, TC-22).
3. Given API key thiếu/sai hoặc camera không khả dụng, When CV gửi yêu cầu hoặc
   cập nhật trạng thái nguồn, Then yêu cầu không được ghi như sự kiện hợp lệ,
   trạng thái lỗi được báo rõ, và payload không chứa ảnh hay ID theo dõi lâu
   dài (NFR-SEC-02, NFR-PRI-01, TC-03, TC-22).

## SEAT-52 — Đếm người qua đường ảo bằng webcam

**Traceability:** FR-CV-01–04; BR-11, BR-13; NFR-PER-02; TC-04, TC-22.

1. Given video mẫu có ground truth IN/OUT đã được hai người đối soát, When CV
   xử lý các lượt cắt đường, Then kết quả ghi đúng hướng và không đếm lặp
   track trong cùng một lượt qua đường (FR-CV-01–03, BR-13, TC-04).
2. Given webcam không mở được hoặc video không đọc được, When CV khởi chạy,
   Then tiến trình báo lỗi nguồn hình, không tạo sự kiện giả và không ghi hình
   vào kho dữ liệu (FR-CV-04, BR-11, TC-03, TC-04).
3. Given webcam laptop hoạt động trong phiên kiểm thử 30 phút, When CV chạy
   liên tục ở cấu hình đã ghi, Then không có lỗi dừng tiến trình và báo FPS
   trung vị đo ít nhất 60 giây ở kích thước khoảng 416 px; kết quả được lưu
   cùng cấu hình và ground truth (NFR-PER-02, TC-04).

## SEAT-53 — API nhận dữ liệu đếm

**Traceability:** FR-OCC-01; BR-13; NFR-SEC-02; TC-22.

1. Given API key hợp lệ và payload sự kiện hợp lệ, When POST sự kiện mới,
   Then API trả 201, lưu `CountEvent` và trả receipt chứa `event_id`
   (FR-OCC-01, TC-22).
2. Given `event_id` đã được lưu với cùng nội dung, When CV gửi lại yêu cầu,
   Then API trả receipt cũ, đánh dấu trùng và không tạo bản ghi thứ hai
   (BR-13, TC-22).
3. Given API key sai, payload sai schema hoặc cùng `event_id` nhưng nội dung
   khác, When gửi yêu cầu, Then API lần lượt trả 401, 422 hoặc 409 theo contract
   và không ghi sự kiện không hợp lệ (NFR-SEC-02, TC-22).

## SEAT-54 — Tính số người hiện tại và chỗ trống

**Traceability:** FR-OCC-02–04, FR-OCC-06; BR-01, BR-02, BR-13, BR-21, BR-24;
TC-02, TC-20, TC-22, TC-23.

1. Given phòng sức chứa đã xác nhận là 40, phiên có N0 đã kiểm tra bằng 0 và
   nhận 45 sự kiện IN hợp lệ, When OccupancyService tính occupancy, Then số
   người ước tính là 45, chỗ trống là 0 và phòng có cờ vượt sức chứa
   (FR-OCC-02/03, BR-01/02, TC-02).
2. Given phiên chưa có N0 hoặc sức chứa chưa được xác nhận, When người dùng
   lấy occupancy, Then số chỗ trống và mức đông được trả là chưa xác định,
   không thay bằng 0 hoặc số liệu mặc định (FR-OCC-03/06, BR-01/24,
   TC-20/23).
3. Given sự kiện có `event_id` đã xử lý hoặc tổng OUT vượt N0 cộng tổng IN,
   When dịch vụ cập nhật occupancy, Then sự kiện trùng không làm tăng/giảm
   số lần thứ hai, occupancy không âm và trạng thái underflow được ghi nhận
   (FR-OCC-02, BR-02/13/21, TC-02/22).

## SEAT-55 — Hiển thị trạng thái dữ liệu cũ

**Traceability:** FR-OCC-04/05; BR-12; NFR-USA-02; TC-03, TC-11, TC-20.

1. Given API trả dữ liệu mới, cũ, mất kết nối hoặc chưa đủ dữ liệu, When
   StaleWarning hiển thị từng fixture, Then mỗi trạng thái có thông báo tiếng
   Việt và thời điểm cập nhật cuối khi có dữ liệu thời gian (FR-OCC-05,
   BR-12, TC-03).
2. Given occupancy đã cũ hoặc nguồn mất kết nối, When giao diện hiển thị phòng,
   Then dữ liệu cũ không được trình bày như số liệu chính thức và có cảnh báo
   nhìn thấy được (FR-OCC-04/05, BR-12, TC-03).
3. Given trạng thái lỗi được mở ở viewport 360 px, When người dùng đọc cảnh
   báo và thao tác thử lại, Then nội dung/nút không bị cắt và trang không cuộn
   ngang (NFR-USA-02, TC-11).

## SEAT-56 — API phòng và occupancy

**Traceability:** FR-SITE-01, FR-OCC-03/04; BR-01/17/24; TC-01, TC-02, TC-18, TC-20.

1. Given phòng đã ánh xạ CS1 hoặc CS3, When gọi danh sách phòng với bộ lọc cơ
   sở, Then chỉ trả phòng thuộc cơ sở đó và response occupancy có thời điểm
   ghi nhận cùng trạng thái dữ liệu (FR-SITE-01, BR-17, TC-01/18).
2. Given `room_id` không tồn tại, When gọi chi tiết phòng/occupancy, Then API
   trả 404 theo error envelope và không trả phòng giả (TC-01).
3. Given phòng tồn tại nhưng chưa có phiên/N0 hợp lệ, When lấy occupancy,
   Then response phân biệt rõ trạng thái chưa đủ dữ liệu và không trả chỗ
   trống/mức đông chính thức; lỗi DB/dịch vụ trả 503 riêng (FR-OCC-03/04,
   BR-01/24, TC-20).

## SEAT-57 — Trạng thái nguồn dữ liệu phía backend

**Traceability:** FR-OCC-05; BR-12; NFR-PER-01; TC-03.

1. Given thiết bị gửi heartbeat thành công trong ngưỡng cấu hình, When lấy
   occupancy, Then trạng thái nguồn là online/fresh và thời điểm nhận gần nhất
   được trả về (FR-OCC-05, TC-03).
2. Given `recorded_at` vượt ngưỡng stale rồi vượt ngưỡng offline, When service
   đánh giá trạng thái bằng clock kiểm thử, Then response chuyển lần lượt sang
   stale và offline theo các ngưỡng cấu hình (FR-OCC-05, BR-12, TC-03).
3. Given thiết bị gửi heartbeat trở lại, When backend nhận heartbeat mới,
   Then trạng thái được phục hồi thành online/fresh trong tối đa một chu kỳ
   polling đã cấu hình và không xóa lịch sử sự kiện (NFR-PER-01, TC-03/22).

## SEAT-58 — Seed, migration và biến Compose

**Traceability:** FR-OPS-01/02, FR-SITE-01; BR-17; TC-01, TC-12, TC-18, TC-22.

1. Given checkout sạch và biến môi trường mẫu đã được cấu hình cục bộ, When
   chạy `docker compose up -d --build`, Then migration và seed tạo được hai
   campus cùng phòng mẫu có loại không gian theo SRS (`free_area`, `topic_room`)
   (FR-OPS-01, FR-SITE-01, TC-01/18).
2. Given đã ghi occupancy/event trong volume phát triển, When chạy `docker
   compose down` rồi `docker compose up -d`, Then dữ liệu PostgreSQL vẫn còn
   (FR-OPS-02, TC-12).
3. Given cấu hình CV API key và ngưỡng trạng thái được nạp từ environment,
   When kiểm tra Compose/config mẫu và Git diff, Then không có secret thật trong
   repository và giá trị cấu hình không phải hard-code trong source
   (NFR-SEC-02, TC-12/22).

## SEAT-59 — Kịch bản tích hợp và cổng Go/No-go

**Traceability:** FR-CV-01–04, FR-OCC-01–06; BR-02/12/13; NFR-PER-01;
TC-03, TC-04, TC-12, TC-22.

1. Given video mẫu được phép sử dụng và hệ thống sẵn sàng, When chạy luồng CV
   → API → `CountEvent` → `OccupancyRecord` → API occupancy → web, Then web
   hiển thị đúng số người/chỗ trống và mỗi sự kiện chỉ được áp dụng một lần
   (FR-OCC-01–04, BR-02/13, TC-04/22).
2. Given cùng một sự kiện được gửi lặp hoặc backend bị ngắt một phút, When
   backend phục hồi, Then bản ghi không bị nhân đôi/mất và kết quả kiểm thử
   cùng log được lưu theo từng ca (BR-13, TC-12/22).
3. Given có ít nhất 20 lượt đo từ lúc CV ghi nhận đến khi web cập nhật, When
   tính phân vị 95 theo công thức của AT-02, Then p95 không quá 5 giây; khi
   dừng CV, web hiển thị trạng thái stale/offline theo ngưỡng cấu hình
   (NFR-PER-01, FR-OCC-05, BR-12, TC-03).

## SEAT-60 — Danh sách phòng và lọc cơ sở

**Traceability:** FR-SITE-01, FR-OCC-03/04; BR-01/17/24; NFR-USA-02;
TC-01, TC-02, TC-11, TC-18, TC-20.

1. Given API có phòng ở CS1 và CS3, When chọn từng cơ sở, Then danh sách
   chỉ hiện phòng của cơ sở đã chọn cùng tên, occupancy và chỗ trống hợp lệ
   (FR-SITE-01, FR-OCC-04, BR-17, TC-01/18).
2. Given API trả danh sách rỗng, thiếu occupancy hoặc lỗi mạng, When mở trang,
   Then giao diện hiển thị đúng empty/insufficient-data/error state, không
   thay lỗi bằng dữ liệu mock hoặc số 0 (FR-OCC-03, BR-01/24, TC-20).
3. Given màn danh sách ở viewport 360 px và 1440 px, When lọc và mở thẻ phòng,
   Then thao tác dùng được và toàn trang không cuộn ngang (NFR-USA-02, TC-11).

## SEAT-61 — Trang tình trạng phòng, tự cập nhật

**Traceability:** FR-OCC-03–05; BR-01/02/12/24; NFR-PER-01, NFR-USA-02;
TC-02, TC-03, TC-11, TC-20, TC-23.

1. Given trang chi tiết phòng đang mở và API có occupancy mới, When có sự
   kiện đếm mới, Then giao diện tự làm mới theo chu kỳ 3–5 giây, hiện số người,
   sức chứa, chỗ trống, mức đông và thời điểm cập nhật; khi rời trang timer
   dừng (FR-OCC-04, NFR-PER-01, TC-11).
2. Given số người vượt sức chứa, When trang cập nhật, Then chỗ trống bằng 0
   và có nhãn vượt sức chứa; khi thiếu N0/sức chứa, hiển thị chưa đủ dữ liệu
   thay vì giá trị chính thức (FR-OCC-03, BR-02/24, TC-02/20/23).
3. Given CV dừng hoặc API lỗi trong khi trang đang mở, When trạng thái stale/
   offline được trả về, Then StaleWarning hiển thị trạng thái và thời điểm
   cập nhật cuối mà không cần tải lại trang (FR-OCC-05, BR-12, TC-03).

## SEAT-62 — Mock có công tắc và khung test

**Traceability:** FR-OCC-03–05, FR-SITE-01; BR-12/17/24; TC-01, TC-03, TC-18, TC-20.

1. Given cờ môi trường bật mock, When gọi service phòng/occupancy, Then frontend
   dùng fixture khớp API contract cho trạng thái fresh, stale, offline và
   insufficient-data mà không gọi backend thật (TC-01/03/20).
2. Given cờ mock tắt, When gọi service, Then frontend dùng API thật; lỗi mạng/
   HTTP được giữ thành trạng thái lỗi, không có response thành công giả
   (BR-12, TC-03).
3. Given fixture chứa campus, loại phòng và occupancy theo contract, When chạy
   component tests, Then lọc cơ sở và các trạng thái được xác nhận bằng test
   tự động có thể lặp lại (FR-SITE-01, BR-17, TC-18).

## SEAT-63 — Theme và huy hiệu mức đông

**Traceability:** FR-OCC-04; BR-23; NFR-USA-01/02; TC-02, TC-11, TC-20.

1. Given tỷ lệ occupancy lần lượt là 50%, trên 50% nhưng dưới 80%, và 80%,
   When render badge, Then nhãn lần lượt là Vắng, Vừa, Đông theo đúng ngưỡng
   SRS (`≤50%`, `>50% và <80%`, `≥80%`) (FR-OCC-04, BR-23, TC-02).
2. Given ba mức badge được xem ở chế độ thang xám, When người dùng phân biệt
   trạng thái, Then mỗi badge vẫn có chữ và/hoặc biểu tượng, không phụ thuộc
   riêng vào màu (NFR-USA-01, TC-11).
3. Given cặp màu chữ/nền của theme được đo bằng công cụ kiểm tra tương phản,
   When kiểm tra trạng thái thường và tương tác, Then đạt WCAG AA: chữ thường
   ≥4.5:1, chữ lớn ≥3:1 và thành phần điều khiển ≥3:1 (NFR-USA-01, TC-11).

## SEAT-64 — Trang đăng nhập và đặt phòng khung

**Traceability:** FR-AUTH-01/02, FR-BOOK-01–03; BR-03/09/15; NFR-USA-02;
TC-05, TC-11, TC-15.

1. Given người dùng mở trang đăng nhập, When hiển thị form theo wireframe UI-01,
   Then có trường email, bước nhập OTP và thông báo lỗi có thể khôi phục; trang
   dùng fixture và không gửi OTP thật (FR-AUTH-01/02, BR-15, TC-15).
2. Given người dùng mở trang đặt phòng, When hiển thị wireframe UI-03, Then
   có trường cơ sở, ngày, giờ, phòng và số thành viên; dữ liệu mock không tạo
   booking trên backend (FR-BOOK-01–03, BR-03, TC-05).
3. Given hai trang được mở ở viewport 360 px, When người dùng nhập và chuyển
   bước, Then nhãn/trường/nút chính không bị cắt, toàn trang không cuộn ngang
   và thao tác dùng được (NFR-USA-02, TC-11).

## Cập nhật Jira và trạng thái hoàn tất

- Dán tiêu chí theo đúng issue key trong backlog; gắn nhãn `AC-ready` sau khi
  nội dung được cập nhật.
- Mỗi dev xác nhận bằng comment trên issue. Mẫu comment chỉ là gợi ý:
  `Confirmed: Acceptance criteria reviewed for SEAT-XX`.
- Đổi tên issue key SEAT-56–64 nếu Jira cấp key khác khi tạo task mới.
- Không đánh dấu đã được review, xác nhận hoặc đã gắn nhãn nếu chưa có bằng
  chứng tương ứng trên Jira.
