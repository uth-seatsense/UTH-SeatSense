# Kế hoạch kiểm thử hệ thống

Kế hoạch này triển khai bộ kiểm thử cho SEAT-53, dựa trên tiêu chí nghiệm thu
Sprint 4 của SEAT-30 tại [acceptance-criteria-sprint-4.md](acceptance-criteria-sprint-4.md)
và yêu cầu, mã TC của SRS 1.9 tại [requirements/srs.md](requirements/srs.md).
Các tiêu chí responsive chi tiết tiếp tục được ghi tại
[mục 7](#7-kiểm-thử-giao-diện-responsive). Các test case giao diện chi tiết
nằm riêng tại [ui-test-plan.md](ui-test-plan.md). Đây là kế hoạch, không phải
bằng chứng các ca đã chạy.

## 1. Phạm vi và mức kiểm thử

| Mức kiểm thử | Phạm vi / mục tiêu | Ca liên quan |
| --- | --- | --- |
| Đơn vị | Quy tắc tính chỗ trống, ngưỡng dữ liệu hợp lệ, kiểm tra đầu vào/booking, xử lý OTP và sự kiện CV; dùng mock khi kiểm thử logic thuần. | TC-02, TC-04, TC-05, TC-15, TC-16 |
| API | Hợp đồng request/response, phân quyền, mã lỗi, dữ liệu phòng/đặt phòng/đếm và xác thực OTP. | TC-01–TC-10, TC-15–TC-16, TC-25 |
| Tích hợp | Backend với PostgreSQL; lưu và đọc booking; nhận sự kiện CV; kiểm tra tính duy nhất khi có request đồng thời. | TC-02–TC-10, TC-12, TC-15–TC-16 |
| Giao diện | Web responsive, dữ liệu hiển thị và trạng thái lỗi/rỗng/stale; không xem dữ liệu demo là dữ liệu thật. Mục bổ sung của Thi ở §7. | TC-01–TC-03, TC-05, TC-08, TC-10–TC-11, TC-15–TC-17 |
| Hệ thống | Luồng end-to-end qua Docker Compose: đăng nhập, xem phòng, đặt phòng; kiểm tra khởi động lại và tính bền vững dữ liệu. | TC-01, TC-05–TC-12, TC-15–TC-17 |
| Thực nghiệm | Chạy CV trên video thử được phép sử dụng, so sánh với đếm tay; đo chỉ tiêu theo SRS và thu SUS khi tổ chức thử người dùng. | TC-04, TC-13–TC-14 |

TC-16/TC-17 tuân theo số hiệu hiện hành trong SRS: TC-16 kiểm thử loại không
gian; TC-17 kiểm thử ứng dụng Android. TC-18 trong SRS đã dành cho kiểm thử hai
cơ sở, vì vậy Portal được bổ sung là TC-25 trong kế hoạch này để tránh xung đột
mã. Không thực hiện các luồng Portal hoặc native trước khi có đặc tả/điều kiện
kỹ thuật tương ứng.

## 2. Danh mục ca kiểm thử

“Người thực hiện” là người/nhóm chịu trách nhiệm chạy và lưu bằng chứng; có thể
phối hợp với vai trò liên quan. Các mức Must/Should/Could theo SRS. “Lên kế
hoạch” nghĩa là chưa có bằng chứng chạy đạt.

| Mã | Mô tả và kết quả cần xác nhận | FR/BR | Loại | Người thực hiện | Ưu tiên | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| TC-01 | Danh sách phòng: trả về và hiển thị đúng phòng hoạt động, loại phòng, cơ sở và trạng thái; không lẫn dữ liệu giữa CS1/CS3. | FR-SITE-01, FR-OCC-04, FR-BOOK-01; BR-17 | API, tích hợp, UI | Backend (Nguyễn Bình Khiêm, Nguyễn Lương Thắng); Frontend (Đỗ Lê Thùy Trâm, Lê Thị Ngọc Thi) | Must | Lên kế hoạch |
| TC-02 | Tính chỗ trống: tính theo sức chứa và số người ước tính, không âm; thiếu sức chứa đã xác nhận hoặc số ban đầu thì báo chưa đủ dữ liệu, không công bố số chính thức. | FR-OCC-03, FR-OCC-06; BR-01, BR-21, BR-24 | Đơn vị, API, UI | Backend; Frontend; người vận hành | Must | Lên kế hoạch |
| TC-03 | Mất kết nối/dữ liệu cũ: cảnh báo trạng thái nguồn và thời điểm cập nhật cuối; không trình bày dữ liệu cũ như dữ liệu mới. | FR-OCC-05; BR-02 | API, tích hợp, UI | Backend; Frontend | Must | Lên kế hoạch |
| TC-04 | Đếm qua đường ảo: chạy video thử để xác nhận phát hiện người, theo dõi, hướng vào/ra và hạn chế đếm lặp; kiểm tra sự kiện nhận được/cập nhật đúng một lần. | FR-OCC-01–02, FR-CV-01–04; BR-21 | Đơn vị, tích hợp, thực nghiệm | CV/AI (Lê Văn Trí); Backend | Must | Lên kế hoạch; cần video thử và ground truth được phép sử dụng |
| TC-05 | Đặt phòng hợp lệ: tạo và xác nhận lượt đặt khi phòng, thời gian, số thành viên và giới hạn tạm đều hợp lệ; từ chối đầu vào ngoài giới hạn mà không tạo booking. | FR-BOOK-02–03, FR-BOOK-05; BR-03, BR-18 | API, tích hợp, UI | Backend; Frontend | Must | Backend API tests đạt cho booking hợp lệ, giới hạn/ngày và xung đột; Docker/UI còn chờ |
| TC-06 | Đặt trùng giờ: từ chối lượt chồng lấn trên cùng phòng và trả lỗi phù hợp; dữ liệu hiện có không bị thay đổi sai. | FR-BOOK-04; BR-04 | API, tích hợp | Backend | Must | Lên kế hoạch |
| TC-07 | Đặt đồng thời: gửi các yêu cầu xung đột đồng thời; chỉ tối đa một lượt hợp lệ được lưu cho cùng phòng/khung giờ. | FR-BOOK-04; BR-04 | Tích hợp, hệ thống | Backend; Docker/tích hợp (Nguyễn Bình Khiêm) | Must | Lên kế hoạch |
| TC-08 | QR hợp lệ/không hợp lệ: chỉ mã gắn với booking hợp lệ trong cửa sổ thời gian được chấp nhận; mã sai, hết hạn, đã dùng hoặc booking không hợp lệ bị từ chối. | FR-CHK-01–03; BR-05–08 | API, tích hợp, UI | Backend; Frontend; nhóm Android khi sẵn sàng | Should | Backend API test đạt cho check-in và từ chối dùng lại QR; QR sai/hết hạn và UI/runtime còn chờ |
| TC-09 | No-show: booking chưa check-in được đánh dấu no-show và giải phóng phần thời gian còn lại sau ngưỡng tạm; booking đã check-in không bị đánh dấu. | FR-BOOK-07; BR-06–08 | Tích hợp, hệ thống | Backend; Docker/tích hợp | Should | Lên kế hoạch; ngưỡng 15 phút chỉ là giá trị tạm nội bộ |
| TC-10 | Dashboard/phân quyền: số liệu và bộ lọc đúng; người không đủ quyền bị chặn; thay đổi cấu hình phòng được ghi tác giả, thời điểm và nội dung. | FR-AUTH-03, FR-DASH-01–02, FR-ADMIN-01; BR-09–10, BR-20 | API, tích hợp, UI | Backend; Frontend; thủ thư/người quản trị thử nghiệm | Must (phân quyền); Should (dashboard/quản lý) | Lên kế hoạch |
| TC-11 | Responsive: luồng chính dùng được trên desktop/tablet/mobile, không tràn ngang trên viewport điện thoại; kiểm tra lỗi, empty/stale và thao tác bàn phím/touch theo ma trận thiết bị. | NFR-USA-01–02; TC-11 trong SRS | UI, hệ thống | Frontend (Đỗ Lê Thùy Trâm, Lê Thị Ngọc Thi) | Must | Lên kế hoạch; chiến lược và ma trận ở §7, case cụ thể tại [ui-test-plan.md](ui-test-plan.md) |
| TC-12 | Docker Compose: khởi chạy dịch vụ theo README; kiểm tra trạng thái sẵn sàng và dữ liệu PostgreSQL vẫn còn sau khi khởi động lại container. | FR-OPS-01–02 | Tích hợp, hệ thống | Docker/tích hợp (Nguyễn Bình Khiêm); Backend | Must | 2 Compose tests đạt trên project/volume cô lập; gồm bootstrap migration, Backend/DB health, restart và persistence |
| TC-13 | Đối chiếu đếm tay: lưu bảng đếm tay/camera, môi trường và công thức; báo sai số theo AT-01, ghi rõ giới hạn; đưa kết quả kiểm thử vào báo cáo thực nghiệm và phần đánh giá/kế hoạch kinh doanh. | FR-EXP-01, FR-EXP-03; NFR-ACC-01 | Thực nghiệm, rà soát báo cáo | CV/AI (Lê Văn Trí); trưởng nhóm (Vũ Nguyễn Nhã Uyên) | Must | Lên kế hoạch; mục tiêu sai số ≤10% đang chờ xác nhận theo SRS |
| TC-14 | SUS: thu phiếu theo cùng quy trình, tính điểm và báo cỡ mẫu/kết quả; không dùng SUS thay cho kiểm thử chức năng hoặc responsive. | FR-EXP-02; NFR-USA-03; AT-04 | Thực nghiệm, khả dụng | Frontend/UI-UX; trưởng nhóm; người tham gia thử nghiệm | Should | Lên kế hoạch; thực hiện khi có người tham gia |
| TC-15 | Đăng nhập OTP: email được phép nhận mã; xác minh thành công/tạo hồ sơ lần đầu; mã sai, hết hạn, dùng lại, quá số lần sai hoặc gửi lại quá sớm bị từ chối theo cấu hình tạm. | FR-AUTH-01–02, FR-AUTH-04; BR-15 | Đơn vị, API, tích hợp, UI | Backend; Frontend | Must | Backend API tests đạt cho OTP/session/domain/rate-limit; email SMTP thật và UI còn chờ; ngưỡng OTP là giá trị tạm |
| TC-16 | Loại không gian: yêu cầu đặt cho `free_area` bị từ chối ở API và giao diện không có thao tác đặt chỗ; `topic_room` vẫn cho phép luồng đặt hợp lệ. | FR-ROOM-01; BR-14 | API, tích hợp, UI | Backend; Frontend | Must | Backend API test xác nhận `free_area` bị từ chối và `topic_room` được đặt; UI còn chờ |
| TC-17 | Ứng dụng Android native: cài APK, đăng nhập OTP, xem chỗ trống, đặt phòng và check-in QR qua API dùng chung; iOS ngoài phạm vi. | FR-APP-01, FR-CHK-01–03; BR-05 | Native UI, tích hợp, hệ thống | Nhóm Android được phân công; Backend hỗ trợ API | Should | Mã Kotlin/Compose và API Backend đã có; debug APK build đạt với SDK 35. API 26 là giả định tạm; chờ xác nhận thiết bị/API tối thiểu và kiểm thử runtime |
| TC-25 | Portal/SSO (ca bổ sung, không thuộc danh mục TC hiện tại của SRS): chỉ kiểm thử sau khi có văn bản đồng ý, đầu mối kỹ thuật, giao thức và luồng tích hợp chính thức; không thu thập/lưu mật khẩu Portal. | FR-AUTH-05; BR-16 | API, tích hợp, rà soát luồng xác thực | Backend; đầu mối CNTT nhà trường khi được chỉ định | Could | Chờ đặc tả và chấp thuận của nhà trường; mặc định dùng OTP email |

### Đối chiếu FR Must

Các FR Must trong SRS 1.9 được bao phủ ít nhất một lần trong bảng trên:

| FR Must | Ca kiểm thử |
| --- | --- |
| FR-AUTH-01–04 | TC-10, TC-15 |
| FR-OCC-01–06 | TC-01–TC-04 |
| FR-ROOM-01, FR-SITE-01 | TC-01, TC-16 |
| FR-CV-01–04 | TC-04 |
| FR-BOOK-01–05 | TC-01, TC-05–TC-07 |
| FR-OPS-01–02 | TC-12 |
| FR-EXP-01, FR-EXP-03 | TC-13 |

FR-EXP-03 được kiểm tra bằng việc rà soát sản phẩm báo cáo/kế hoạch kinh
doanh, không phải bằng một kết quả API. TC-10 có cả nội dung Must và Should;
ghi nhận riêng kết quả từng phần để không coi việc chưa có dashboard là lỗi
đối với FR-AUTH-03.

## 3. Dữ liệu kiểm thử

- Dùng seed có sẵn trong repository tại
  [database/seeds/002_seed_data.sql](../database/seeds/002_seed_data.sql)
  làm nguồn dữ liệu mẫu: tài khoản demo, phòng, booking, check-in, occupancy,
  count event và audit log. Đây không phải dữ liệu của SEAT-37. Dữ liệu phải
  chạy trong cơ sở dữ liệu kiểm thử cô lập; không nạp seed vào môi trường
  production.
- SEAT-37 là ERD và từ điển dữ liệu, không phải nguồn test data; phạm vi
  SEAT-43 không chỉnh sửa các tài liệu đó.
- Trước khi nạp, xác nhận migrations và schema mục tiêu. Seed hiện có dùng một
  số giá trị `room_type` (`reading_room`, `group_study_room`) khác với SRS
  (`free_area`, `topic_room`); cần ánh xạ/chuẩn bị fixture phù hợp trong môi
  trường kiểm thử, không suy diễn rằng seed đã sẵn sàng để xác nhận TC-16.
- Seed có thời điểm tương đối (`NOW()`), dữ liệu ngẫu nhiên và các booking có
  thể thay đổi theo thời điểm chạy. Không dùng các giá trị đó làm expected
  result cố định. Mỗi ca cần ghi fixture/ID cụ thể, đồng hồ hoặc mốc thời gian
  kiểm thử, trạng thái ban đầu và cách dọn/reset dữ liệu.
- Bổ sung fixture có kiểm soát cho hai cơ sở, từng loại không gian, phòng bảo
  trì, booking xung đột/đồng thời, số ban đầu có/không có, dữ liệu mới/cũ/mất
  kết nối, OTP sai/hết hạn và mã QR hợp lệ/không hợp lệ. Dùng tài khoản giả;
  không ghi OTP hoặc dữ liệu cá nhân thật vào bằng chứng.
- TC-04/TC-13 cần bộ video thử được phép dùng và bảng ground truth đếm tay,
  ghi mã video, phiên bản/cấu hình và người đếm. Không dùng video nhận diện cá
  nhân nếu chưa có chấp thuận; không lưu video vào database.
- Dữ liệu người dùng trong seed là dữ liệu thử nghiệm. Không dùng email, mã
  OTP, mật khẩu hoặc bản sao dữ liệu thật trong báo cáo/chụp màn hình.

## 4. Điều kiện bắt đầu và kết thúc

### Điều kiện bắt đầu

- Đối chiếu tiêu chí SEAT-30 và phiên bản SRS/commit đang kiểm thử; mọi thay
  đổi yêu cầu phải được phản ánh vào FR/BR và ca liên quan trước khi chạy.
- Có migrations, seed/fixture phù hợp schema và database kiểm thử cô lập; đã
  ghi cách khởi tạo/reset để ca có thể lặp lại.
- Các dịch vụ, biến môi trường và tài khoản thử nghiệm được chuẩn bị theo
  README; Docker Compose, backend, database và frontend sẵn sàng theo phạm vi
  ca. Không lưu secrets vào hồ sơ kiểm thử.
- Có video/ground truth được phép dùng cho kiểm thử CV; kiểm thử tại thư viện
  hoặc thu dữ liệu người tham gia chỉ bắt đầu sau khi có chấp thuận cần thiết.
- Với TC-17 cần chốt thiết bị, OS và API tối thiểu; API 26 hiện chỉ là giả định.
  Debug APK đã build được nhưng chưa có runtime evidence vì chưa kết nối
  thiết bị/emulator. Với TC-25 cần đặc tả Portal và chấp thuận nhà trường.

### Điều kiện kết thúc

- Mỗi ca đã chạy có trạng thái Pass/Fail/Blocked, kết quả thực tế và bằng chứng
  theo mẫu §5; ca Blocked phải ghi rõ phụ thuộc còn thiếu.
- Tất cả FR Must có ít nhất một TC được chạy và Pass trước khi nghiệm thu
  Must. Không còn lỗi nghiêm trọng về phân quyền, trùng lịch hoặc nhất quán dữ
  liệu; lỗi chưa khắc phục được ghi nhận và được người phụ trách chấp nhận rõ.
- Các ca Should đã chạy hoặc có quyết định hoãn kèm lý do; ca Could/đang chờ
  đặc tả không được tính là đã nghiệm thu.
- Báo cáo kiểm thử cập nhật ngày chạy, commit, lệnh/cấu hình, số Pass/Fail/
  Blocked, lỗi còn mở và giới hạn. Chỉ tiêu AT/NFR đang chờ xác nhận phải được
  báo riêng, không tuyên bố đạt/chưa đạt như ngưỡng đã phê duyệt.

## 5. Mẫu ghi kết quả

| Trường | Giá trị |
| --- | --- |
| Mã TC / FR / BR |  |
| Ngày, giờ / người thực hiện |  |
| Commit / phiên bản |  |
| Môi trường, OS, thiết bị / viewport (px) / trình duyệt và phiên bản |  |
| Lệnh chạy / cấu hình liên quan |  |
| Seed/fixture, trạng thái ban đầu, tiền điều kiện |  |
| Bước chạy và dữ liệu đầu vào |  |
| Kết quả mong đợi |  |
| Kết quả thực tế |  |
| Trạng thái (Pass / Fail / Blocked) |  |
| Bằng chứng (ảnh chụp màn hình có viewport, log, đường dẫn kết quả) |  |
| Issue/lỗi và mức độ |  |
| Ghi chú, giới hạn, lần chạy lại |  |

Không đưa OTP, secrets, email thật hoặc hình ảnh nhận diện cá nhân vào bằng
chứng. Lưu bằng chứng tại vị trí nội bộ được nhóm thống nhất.

## 6. Chỉ tiêu thực nghiệm liên quan

- **TC-13 / AT-01:** so sánh theo công thức và quy trình trong SRS; ghi số
  phiên, mức đông, tổng đếm tay, tổng đếm camera và cách xử lý phiên có mẫu số
  bằng 0. Mục tiêu ≤10% hiện là mục tiêu tạm, chờ xác nhận.
- **Độ trễ / AT-02:** đo p95 từ lúc ghi nhận sự kiện đến lúc hiển thị; ghi
  môi trường và số mẫu. Mục tiêu ≤5 giây đang chờ xác nhận.
- **Tốc độ / AT-03:** đo trung vị FPS tối thiểu 60 giây ở cấu hình đã ghi; nếu
  không có quyền truy cập CS1/CS3 thì dùng video thử offline và nêu giới hạn.
- **TC-14 / AT-04:** thu khoảng 15–30 người theo quy trình được thống nhất;
  báo cỡ mẫu và cách tính SUS. Không dùng kết quả SUS thay cho chức năng.
- Chỉ thử nghiệm tại thư viện khi có chấp thuận; nếu chưa có, kiểm thử trong
  môi trường nhóm và ghi rõ không đại diện cho vận hành tại CS1/CS3.

## 7. Kiểm thử giao diện responsive

Mục tiêu là kiểm tra luồng chính trên điện thoại, máy tính bảng và laptop theo
TC-11, NFR-USA-02 và UI-07. Các bước test cụ thể cho UI-01–UI-08 nằm trong
[ui-test-plan.md](ui-test-plan.md); đây là ma trận và checklist điều phối.

### 7.1 Ma trận viewport và trình duyệt

Chạy các viewport CSS theo đúng ma trận. Dùng trình duyệt stable hiện hành,
ghi phiên bản đầy đủ, OS, thiết bị/simulator, viewport và ngày chạy. `N/A`
nghĩa là cặp thiết bị/trình duyệt không thuộc ma trận hỗ trợ, không tính là
đã test.

| Viewport rộng (px) | Chrome | Safari trên iOS/iPadOS | Edge |
| ---: | --- | --- | --- |
| 360 | Chrome Android hoặc responsive device emulation | iPhone simulator/device | N/A |
| 390 | Chrome Android hoặc responsive device emulation | iPhone simulator/device | N/A |
| 768 | Chrome tablet/responsive emulation | iPadOS simulator/device | Edge tablet/responsive emulation |
| 1024 | Chrome desktop/tablet | N/A | Edge desktop/tablet |
| 1440 | Chrome desktop | N/A | Edge desktop |

Ở 360 và 390 px, chạy luồng chính trên Chrome và Safari iOS. Ở 768 px, kiểm
tra ít nhất Chrome, Safari iPadOS và Edge. Ở 1024 và 1440 px, kiểm tra Chrome
và Edge. Nếu thiết bị thực tế không cung cấp đúng CSS width, dùng simulator/
responsive emulation, ghi rõ phương thức và kiểm tra ít nhất một thiết bị
điện thoại thật trước nghiệm thu.

### 7.2 Checklist theo screen-flow

| Screen / state | Checklist bắt buộc | Mã kiểm thử |
| --- | --- | --- |
| UI-01 — Đăng nhập OTP | Loading, nhập hợp lệ, OTP sai/hết hạn, lỗi gửi và giữ form có thể sửa | TC-15, TC-11 |
| UI-02 — Khu tự học tự do | Danh sách, lọc cơ sở, dữ liệu mới, rỗng/chưa đủ dữ liệu và lỗi API; không có thao tác đặt chỗ | TC-01, TC-16, TC-18, TC-20 |
| UI-03 — Đặt phòng chuyên đề | Form hợp lệ, xác nhận, trường thiếu/sai, phòng không khả dụng và xung đột | TC-05, TC-06, TC-07, TC-11 |
| UI-04 — Lịch đặt / QR | Có lịch, empty state, QR hợp lệ; QR sai/hết hạn/đã dùng và lỗi API | TC-08, TC-09, TC-11 |
| UI-05 — Dashboard | Dữ liệu, bộ lọc, empty/error, quyền không đủ và dữ liệu cũ | TC-03, TC-10, TC-11 |
| UI-06 — Trạng thái dữ liệu | Fresh, stale, offline, insufficient-data; hiện thời điểm cập nhật và không ngụy trang lỗi thành số 0 | TC-02, TC-03, TC-20, TC-23 |
| UI-07 — Responsive | Luồng xem phòng/đặt phòng/check-in ở từng viewport; không cuộn ngang toàn trang ở 360/390 px; thao tác touch và keyboard | TC-11 |
| UI-08 — Android native | Có debug APK; chạy khi chốt thiết bị/OS/API tối thiểu và có thiết bị/emulator; thử xem phòng, đặt phòng, OTP, QR | TC-17 |

Mỗi UI-01–UI-08 có tối thiểu hai trường hợp ghi trong
[ui-test-plan.md](ui-test-plan.md). UI-07 là tiêu chí xuyên suốt các màn hình,
không phải một route độc lập.

### 7.3 Màu sắc, kết quả và native

- Với các mức Vắng/Vừa/Đông, chụp màn hình màu và ảnh chuyển thang xám; xác
  nhận nhãn/chữ hoặc biểu tượng vẫn phân biệt được khi không dựa vào màu.
  Kiểm tra tương phản theo WCAG AA tại
  [ui-guideline.md](ui/ui-guideline.md).
- Mỗi ca lưu ảnh chụp màn hình có mã TC, viewport, OS/trình duyệt, phiên bản,
  trạng thái fixture và commit. Ghi đường dẫn ảnh trong mẫu kết quả §5.
- Liên kết kết quả khả dụng với TC-14 (SUS) để đối chiếu tác vụ/ngữ cảnh đã
  thử; SUS không thay thế Pass/Fail của các ca chức năng hoặc responsive.
- Câu trả lời Q-17 trong SRS chọn Android native/Kotlin nhưng chưa chốt thiết
  bị và phiên bản Android tối thiểu. Mã Kotlin/Compose đã được thêm; API 26 là
  giả định tạm, chưa được phê duyệt. Debug APK build đạt nhưng TC-17 vẫn
  Blocked cho tới khi chốt thiết bị/API level và có bằng chứng runtime.
- Không dùng dữ liệu/màn hình chứa OTP, secret, email hoặc hình ảnh nhận diện
  cá nhân trong ảnh bằng chứng.

## 8. Tài liệu kết quả

Ghi ngày, commit, lệnh chạy, kết quả và giới hạn trong
[test-report.md](test-report.md). Mục responsive và ma trận viewport ở §7;
test case chi tiết ở [ui-test-plan.md](ui-test-plan.md); tiêu chí SEAT-30 tại
[acceptance-criteria-sprint-4.md](acceptance-criteria-sprint-4.md).
