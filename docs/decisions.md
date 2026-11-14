# Architecture decisions

## SEAT-31 — Quyết định theo tài liệu hiện hành

Nguồn: [Charter v1.7](requirements/Project%20Charter.md),
[SRS v1.9](requirements/srs.md) và
[yêu cầu SEAT-31](https://nhauyen70205.atlassian.net/browse/SEAT-31).

| Mã | Ngày | Quyết định | Lý do | Phương án đã loại | Người quyết | Ảnh hưởng |
| --- | --- | --- | --- | --- | --- | --- |
| DEC-01 | 10/11/2026, ngày rà soát; Charter mục 6, quyết định #5 | Backend dùng FastAPI. | Dùng chung hệ sinh thái Python với CV, thuận tiện tích hợp và demo. | Nguồn không ghi framework Backend thay thế đã được đánh giá. | Nhóm theo Charter; chưa ghi người duyệt riêng cho quyết định ban đầu. | Backend cung cấp API và xử lý nghiệp vụ, tách khỏi CV và giao diện. |
| DEC-02 | 10/11/2026, ngày rà soát; Charter mục 6; SRS Q-10 | PostgreSQL là CSDL chính; môi trường dev dùng 16.6 Alpine. | Lưu dữ liệu nghiệp vụ thống nhất; phù hợp cấu hình Compose hiện tại. | SQLite không phải CSDL chính trong tài liệu hiện hành. | Nhóm theo Charter; Uyên báo xác nhận Q-10, chưa có trả lời gốc trong repo. | Giữ dữ liệu trong volume; cấu hình production cần chốt riêng. |
| DEC-03 | 10/11/2026, ngày rà soát; Charter quyết định #6, #17 | Webcam máy tính + YOLOv8n + ByteTrack; bỏ IoT/cảm biến và không mua camera. | Theo phạm vi camera đã chốt và giảm chi phí phần cứng. | ESP32/cảm biến và mua camera riêng. | Nhóm theo Charter; chưa ghi người duyệt riêng của quyết định ban đầu. | Kiểm thử bằng webcam laptop; triển khai CS1/CS3 chỉ khi đủ điều kiện. |
| DEC-04 | 10/11/2026, ngày rà soát; Charter mục 5–6, quyết định #18 | Đếm IN/OUT qua đường ảo; số đầu phiên do người vận hành kiểm tra và nhập, hiệu chỉnh lưu riêng có truy vết. | Phân biệt người đang thấy với hiện diện; tránh công bố chỗ trống thiếu căn cứ. | Nhận diện danh tính, cộng counters giữa các frame, sửa dữ liệu CV thô để hiệu chỉnh. | Nhóm theo Charter; Uyên duyệt nội bộ quyết định #18 ngày 10/11/2026. | Giữ công thức và giới hạn SEAT-33 bên dưới; thiếu số đầu phiên hoặc sức chứa tin cậy thì không công bố chỗ trống/mức đông chính thức. |
| DEC-05 | 10/11/2026, ngày rà soát; Charter mục 6, quyết định #9 | CV đọc webcam trên host ngoài Docker; Backend, PostgreSQL và Frontend chạy bằng Docker Compose. | Docker Desktop có hạn chế truy cập webcam từ container. | Dùng webcam trực tiếp trong container làm chế độ camera chuẩn. | Nhóm theo Charter và yêu cầu SEAT-31; chưa ghi người duyệt riêng. | SEAT-42/36 đối chiếu kết nối host/container và hướng dẫn chạy; video offline không chứng minh container truy cập được webcam. |
| DEC-06 | 10/11/2026, ngày rà soát; Charter mục 6; SRS v1.9 Q-16 | Web dùng React + Vite (JavaScript). | Phù hợp scaffold hiện có; PoC React build, test và gọi API đạt; PoC Vue cũng chạy nhưng không cho thấy lợi ích đủ để thay thế code đang dùng. | Vue + Vite; không có lý do đủ mạnh để thay thế frontend React hiện hữu. | Uyên duyệt giữ React + Vite ngày 10/11/2026 theo SEAT-48. | Payload/endpoint phải đối chiếu contract riêng khi tích hợp; lựa chọn thư viện QR/biểu đồ còn chờ kiểm thử. |
| DEC-07 | 10/11/2026; Charter quyết định #14, #20; SRS Q-17 | Android native dùng Kotlin, thử bằng APK trực tiếp; iOS ngoài phạm vi. | Dùng chung API với web, hỗ trợ camera quét QR và tránh phụ thuộc cửa hàng ứng dụng khi thử nghiệm. | PWA thay cho native đã được quyết định #14 thay thế; không phát triển iOS. | Uyên duyệt nội bộ quyết định #20; quy định nền tảng của trường chưa có nguồn gốc trong repo. | Android là Should, ưu tiên web/API; phiên bản Android tối thiểu vẫn cần ghi nhận. |
| DEC-08 | 10/11/2026; Charter quyết định #12–13; SRS Q-01 | MVP đăng nhập OTP email; chỉ tích hợp Portal/SSO khi có văn bản và cách kết nối chính thức. | Kiểm thử được khi chưa có hệ thống trường, không thu mật khẩu portal. | Phụ thuộc bắt buộc vào SSO hoặc nhận mật khẩu portal. | Uyên báo đã xác nhận Q-01; đầu mối CNTT và trả lời gốc chưa có trong repo. | Giữ lớp đăng nhập thay thế được; các ngưỡng OTP vẫn là giá trị thử nghiệm cần rà soát. |
| DEC-09 | 10/11/2026; SRS Q-06, BR-05–08 | No-show tạm sau 15 phút kể từ giờ bắt đầu; thời gian phải cấu hình được. | Có quy tắc cụ thể để phát triển và kiểm thử. | Không giữ 10–15 phút như một lựa chọn chưa xác định; không coi 15 phút là chính sách thư viện đã duyệt. | Uyên duyệt giá trị tạm nội bộ; thư viện chưa xác nhận. | Không xử lý lượt đã check-in thành no-show; cần xác nhận trước vận hành thật. |

### Chờ chốt và theo dõi

| Mã | Phần còn cần chốt | Chủ sở hữu/đầu mối | Hạn đề xuất và điều kiện |
| --- | --- | --- | --- |
| OPEN-01 | SEAT-48 ghi nhận React/Vite và Kotlin theo Charter/SRS; chỉ đánh giá lại khi có thay đổi được duyệt. | Uyên điều phối SEAT-48; người thực hiện cụ thể cần xác nhận. | Rà soát trước khi chốt hướng dẫn triển khai web/Android; đề xuất xác nhận đầu mối trước 11/11/2026. |
| OPEN-02 | Phiên bản Android tối thiểu và thiết bị kiểm thử; không có yêu cầu iOS tối thiểu vì iOS ngoài phạm vi. | Uyên điều phối; nhóm Android chưa được phân công theo SRS Q-17. | Chốt trước cấu hình minSdk và nghiệm thu Android; đề xuất phân công trước 11/11/2026. |
| OPEN-03 | Nguồn xác nhận gốc Q-01 và đầu mối Portal/SSO; không chặn OTP nội bộ. | Uyên điều phối, đầu mối CNTT nhà trường chưa được chỉ định. | Trước mọi tích hợp SSO; đề xuất cập nhật đầu mối trong lần rà soát kế tiếp trước 11/11/2026. |
| OPEN-04 | Thư viện xác nhận no-show 15 phút hoặc giá trị thay thế; email Q-06 đang hoãn theo SRS. | Uyên điều phối, đại diện thư viện chưa được chỉ định. | Bắt buộc trước vận hành tại thư viện; chưa có ngày phản hồi được xác nhận. Đề xuất rà soát lịch xin xác nhận trước 11/11/2026. |

SEAT-31 ghi nhận và liên kết quyết định; SEAT-28 duy trì yêu cầu, SEAT-48 theo dõi
lựa chọn công nghệ, SEAT-34/40 chốt payload, SEAT-42/36 hoàn thiện triển khai.
Các mục lịch sử và phần thuật toán SEAT-33 bên dưới được giữ nguyên từ `dev`.

## Initial service boundaries

- **Status:** Accepted for the project scaffold
- **Decision:** Keep the web UI, business API, and CV processing in separate
  service directories, with PostgreSQL as the shared persistence layer.
- **Reason:** The components have distinct responsibilities and runtime needs.
- **Follow-up:** Validate deployment, authentication, and inter-service
  communication requirements with the team.

## SEAT-17 CV output and counting semantics

- **Status:** Implemented in CV, pending team review.
- **Date:** 2026-10-30.
- **Decision:** Version the transport-neutral CV output as 1.0. Keep aggregate
  count records separate from local bbox debug records. Define the output
  before Backend implements ingestion; no HTTP endpoint is assumed yet.
- **Counting:** Visible person count is independent of cumulative line IN/OUT.
  Only estimate room occupancy when an initial value is explicitly configured.
  Clamp negative estimates to zero while flagging underflow.
- **Tracking:** Bottom-center anchors cross a finite normalized segment, with
  deadband, cooldown and stale-state expiry. Counters reset for each session.
- **Follow-up:** Backend ingestion, storage and UI are separate stages.

## SEAT-48 Frontend and native framework selection

- **Date:** 2026-11-10.
- **Status:** Approved by Uyên on 2026-11-10 for React + Vite web and Android
  native with Kotlin. The native build/runtime spike remains a follow-up; this
  approval does not claim that Kotlin or native QR/chart integrations were
  prototyped.
- **Scope:** Select the web framework and native-app approach. iOS is outside
  the current project scope.

| Candidate | Group experience / learning | QR and chart ecosystem | iOS build requirement | Code reuse | Docker fit |
|---|---|---|---|---|---|
| React + Vite (web) | Existing frontend, API client, pages and tests provide direct project experience; lowest migration cost. | Mature web choices exist (for example, Chart.js/ECharts and browser QR scanning with ZXing); no chart or QR package is selected in this repository yet. | Web build is platform-independent; no macOS needed. | Reuses the current React/JavaScript frontend. | Already builds with the existing Node/Vite Docker service; keep camera/CV outside Docker. |
| Vue + Vite (web) | Similar JavaScript/Vite workflow, but the project has no Vue code; requires learning Vue and replacing existing React UI. | Mature web choices exist (for example, Chart.js/ECharts and browser QR scanning with ZXing); no package was evaluated for production use. | Web build is platform-independent; no macOS needed. | Shares browser standards and API contracts, not React components. | Can be built in a Node/Vite container just like React; it does not improve the existing service boundary. |
| Flutter (native) | Dart and Flutter are new to this repository; additional framework learning is required. | Native QR and chart packages are available (for example, `mobile_scanner`, `qr_flutter`, and `fl_chart`); compatibility was not tested here. | iOS builds require macOS and Xcode; Android can be built with the Android toolchain. | Flutter UI is separate from the React web UI; API models/business rules may be shared only if deliberately extracted. | Native app builds need their own Flutter/Android build environment; not part of the current web Docker service. |
| React Native (native) | JavaScript knowledge transfers, but React Native is not React DOM and needs native-module/build knowledge. | Native camera/QR and chart packages are available; package compatibility and maintenance were not tested here. | iOS builds require macOS and Xcode; Android needs its SDK/Gradle toolchain. | Can share some JavaScript validation/API code, but not the web component tree. | Mobile builds remain separate from the web Docker service and need native SDKs. |
| Swift (iOS native) | Requires Swift/iOS skills not evidenced in this repository. | Native scanning/chart frameworks or packages are available; not evaluated because iOS is out of scope. | Requires macOS and Xcode. | Separate app and platform-specific code. | Not a fit for the current Android-only target or Docker web service. |
| Kotlin (Android native) | Already recorded as the team's Android direction in the Charter/SRS; actual team Android experience is not evidenced by a repository scaffold. | Android QR/scanning and chart libraries are available; no library was installed or validated for this project. | Android builds use JDK, Gradle and Android SDK; no macOS requirement. | Separate UI from React web; share API contract and potentially plain business rules. | Android APK builds need a separate native build environment; do not put them in the web Docker image. |

### Prototype evidence

- **React + Vite:** Ran `npm run build` successfully and all 9 frontend tests
  passed. Started the existing app and called
  `/api/v1/occupancy/current` through Vite's proxy; both page and API returned
  HTTP 200. The real API currently returns `current_count: null`, which is an
  empty-data state, not a valid count.
- **Vue + Vite:** Scaffolded a temporary, uncommitted Vue app, built it
  successfully, and rendered an empty/loading/error-aware screen after calling
  the same real endpoint through a Vite proxy; page and API returned HTTP 200.
  The spike added no Vue dependencies to the repository.
- **Native:** No blank-app/API prototype was run. This machine has no Android
  SDK, `adb`, Gradle, or Flutter installation, and the repository has no native
  app scaffold. Therefore the native recommendation below is not backed by a
  runtime/build spike.
- **QR/chart packages:** No candidate package was added or tested for either
  web framework or native platform. Select and verify concrete libraries when
  the corresponding UI stories are implemented.

### Recommendation and alternatives

- **Web:** Retain React + Vite. It is already integrated, builds in the current
  Docker setup, passes its tests, and successfully calls the live backend. Vue
  also passed a minimal API spike, but switching would replace working React
  code without a demonstrated benefit.
- **Native:** Retain Android native with Kotlin, consistent with the recorded
  project scope and Android-only target. Do not select Flutter or React Native
  solely for hypothetical code sharing: both still require a distinct mobile
  UI/build pipeline, while iOS is out of scope. Swift is not selected because
  it targets iOS.
- **Approval / follow-up:** Uyên approved React + Vite and Android native with
  Kotlin on 2026-11-10. Before native implementation is considered validated,
  run a 30-minute Kotlin blank-app/API spike on a machine with Android SDK and
  Gradle; Uyên will assign the runner and record the result in SEAT-48. Do not
  claim the native build or QR/chart integrations have been tested.
- **Dependencies:** This decision record is for SEAT-48 and the SRS topics
  Q-16/Q-17. SEAT-31 remains an upstream dependency for the dependent
  implementation work.
## SEAT-33 thuat toan dem nguoi qua duong ao

- **Trạng thái:** Tài liệu hóa thuật toán đã có trong CV
- **Ngày rà soát:** 09/11/2026.
- **Nguồn:** [SEAT-33](https://nhauyen70205.atlassian.net/browse/SEAT-33),
  `cv/app/counting/line_counter.py` và `cv/app/schemas/count_result.py`.
- **Quyết định:** Dùng YOLOv8n và ByteTrack, lấy tâm cạnh dưới bbox của cùng
  track để xác định hướng khi cắt đoạn đường ảo hữu hạn. Dùng deadband,
  cooldown và hết hạn trạng thái mất dấu để giảm đếm lặp. Mỗi lần cắt hợp lệ
  sinh một sự kiện; track có thể quay lại sau cooldown.
- **Lý do:** Cần đếm lượt qua cửa theo hướng IN/OUT, tách số người đang thấy
  trong khung hình khỏi ước tính số người trong phòng. Track ID chỉ là ID
  tạm trong phiên, không dùng để nhận diện danh tính.
- **Phương án không dùng:** Không lấy `people_count` làm số người toàn phòng,
  không cộng counters tích lũy qua các frame, không giới hạn một ID chỉ được
  đếm một lần trong toàn phiên.
- **Công thức:** Khi biết số đầu phiên, hiện diện bằng
  `max(0, initial_occupancy + IN - OUT)`; số âm bật `occupancy_underflow`.
  Chỉ dùng IN trừ OUT khi đã xác nhận số đầu phiên bằng 0; chưa biết số đầu
  phiên thì hiện diện là `null`.
- **Ảnh hưởng:** Theo BR-02, số chỗ trống cần kẹp về 0 và đánh dấu khi vượt
  sức chứa; không kẹp số người xuống sức chứa. Kết hợp sức chứa và cảnh báo
  thuộc Backend/Frontend; `CountResult` hiện chưa có các trường này.
- **Giới hạn triển khai:** 416 px và 3–5 FPS là cấu hình mục tiêu, không phải
  hiệu năng đã đo. CLI mặc định 640, chưa lấy mẫu 3–5 FPS; CV xuất dữ liệu
  cục bộ, chưa có bộ gửi HTTP/retry đến Backend.
- **Bàn giao:** Chi tiết pipeline, tham số và giới hạn ở
  [Thuật toán đếm người](../cv/README.md#thuật-toán-đếm-người--seat-33).
  Thắng và Khiêm cần xác nhận giải thích đúng công thức và cách xử lý số âm
  theo tiêu chí SEAT-33; chưa ghi nhận xác nhận này khi rà soát.
