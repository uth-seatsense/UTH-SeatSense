# Quyết định kiến trúc

## Quyết định theo tài liệu hiện hành

Nguồn: [Điều lệ dự án v1.7](requirements/Project%20Charter.md),
[Tài liệu đặc tả yêu cầu phần mềm (SRS) v1.9](requirements/srs.md) và
[yêu cầu SEAT-31](https://nhauyen70205.atlassian.net/browse/SEAT-31).

| Mã | Ngày | Quyết định | Lý do | Phương án đã loại | Người quyết | Ảnh hưởng |
| --- | --- | --- | --- | --- | --- | --- |
| DEC-01 | 10/11/2026, ngày rà soát; Điều lệ mục 6, quyết định #5 | Máy chủ ứng dụng dùng FastAPI. | Dùng chung hệ sinh thái Python với CV, thuận tiện tích hợp và trình diễn. | Nguồn không ghi nền tảng máy chủ thay thế đã được đánh giá. | Nhóm theo Điều lệ; chưa ghi người duyệt riêng cho quyết định ban đầu. | Cung cấp API và xử lý nghiệp vụ, tách khỏi CV và giao diện. |
| DEC-02 | 10/11/2026, ngày rà soát; Điều lệ mục 6; SRS Q-10 | PostgreSQL là CSDL chính; môi trường phát triển dùng 16.6 Alpine. | Lưu dữ liệu nghiệp vụ thống nhất; phù hợp cấu hình Docker Compose hiện tại. | SQLite không phải CSDL chính trong tài liệu hiện hành. | Nhóm theo Điều lệ; Uyên báo xác nhận Q-10, chưa có trả lời gốc trong kho mã. | Giữ dữ liệu trong vùng lưu trữ Docker; cấu hình môi trường thật cần chốt riêng. |
| DEC-03 | 10/11/2026, ngày rà soát; Điều lệ quyết định #6, #17 | Webcam máy tính + YOLOv8n + ByteTrack; bỏ IoT/cảm biến và không mua camera. | Theo phạm vi camera đã chốt và giảm chi phí phần cứng. | ESP32/cảm biến và mua camera riêng. | Nhóm theo Điều lệ; chưa ghi người duyệt riêng của quyết định ban đầu. | Kiểm thử bằng webcam máy tính xách tay; triển khai CS1/CS3 chỉ khi đủ điều kiện. |
| DEC-04 | 10/11/2026, ngày rà soát; Điều lệ mục 5–6, quyết định #18 | Đếm IN/OUT qua đường ảo; số đầu phiên do người vận hành kiểm tra và nhập, hiệu chỉnh lưu riêng có truy vết. | Phân biệt người đang thấy với số người hiện diện; tránh công bố chỗ trống thiếu căn cứ. | Nhận diện danh tính, cộng bộ đếm tích lũy giữa các khung hình, sửa dữ liệu CV thô để hiệu chỉnh. | Nhóm theo Điều lệ; Uyên duyệt nội bộ quyết định #18 ngày 10/11/2026. | Giữ công thức và giới hạn SEAT-33 bên dưới; thiếu số đầu phiên hoặc sức chứa tin cậy thì không công bố chỗ trống/mức đông chính thức. |
| DEC-05 | 10/11/2026, ngày rà soát; Điều lệ mục 6, quyết định #9 | CV đọc webcam trên máy chạy CV, ngoài Docker; máy chủ, PostgreSQL và giao diện chạy bằng Docker Compose. | Docker Desktop có hạn chế truy cập webcam từ vùng chứa. | Dùng webcam trực tiếp trong vùng chứa làm chế độ camera chuẩn. | Nhóm theo Điều lệ và yêu cầu SEAT-31; chưa ghi người duyệt riêng. | SEAT-42/36 đối chiếu kết nối giữa máy chạy CV và vùng chứa, đồng thời hoàn thiện hướng dẫn chạy; video ngoại tuyến không chứng minh vùng chứa truy cập được webcam. |
| DEC-06 | 10/11/2026, ngày rà soát; Điều lệ mục 6; SRS v1.9 Q-16 | Giao diện web dùng React + Vite (JavaScript). | Phù hợp bộ khung hiện có; nguyên mẫu React biên dịch, kiểm thử và gọi API đạt; nguyên mẫu Vue cũng chạy nhưng không cho thấy lợi ích đủ để thay thế mã nguồn hiện tại. | Vue + Vite; không có lý do đủ mạnh để thay thế giao diện React hiện hữu. | Uyên duyệt giữ React + Vite ngày 10/11/2026 theo SEAT-48. | Dữ liệu gửi và điểm cuối API phải đối chiếu hợp đồng API riêng khi tích hợp; lựa chọn thư viện QR/biểu đồ còn chờ kiểm thử. |
| DEC-07 | 10/11/2026; Điều lệ quyết định #14, #20; SRS Q-17 | Android gốc dùng Kotlin, thử bằng APK trực tiếp; iOS ngoài phạm vi. | Dùng chung API với giao diện web, hỗ trợ camera quét QR và tránh phụ thuộc cửa hàng ứng dụng khi thử nghiệm. | Ứng dụng web tiến bộ (PWA) đã được quyết định #14 thay thế; không phát triển iOS. | Uyên duyệt nội bộ quyết định #20; quy định nền tảng của trường chưa có nguồn gốc trong kho mã. | Android thuộc mức Nên, ưu tiên giao diện web và API; phiên bản Android tối thiểu vẫn cần ghi nhận. |
| DEC-08 | 10/11/2026; Điều lệ quyết định #12–13; SRS Q-01 | Bản tối thiểu đăng nhập bằng OTP qua thư điện tử; chỉ tích hợp cổng trường/SSO khi có văn bản và cách kết nối chính thức. | Có thể kiểm thử khi chưa có hệ thống trường; không thu mật khẩu cổng trường. | Phụ thuộc bắt buộc vào SSO hoặc nhận mật khẩu cổng trường. | Uyên báo đã xác nhận Q-01; đầu mối CNTT và trả lời gốc chưa có trong kho mã. | Giữ lớp đăng nhập có thể thay thế; các ngưỡng OTP vẫn là giá trị thử nghiệm cần rà soát. |
| DEC-09 | 10/11/2026; SRS Q-06, BR-05–08 | Tạm đánh dấu vắng mặt sau 15 phút kể từ giờ bắt đầu; thời gian phải cấu hình được. | Có quy tắc cụ thể để phát triển và kiểm thử. | Không giữ 10–15 phút như một lựa chọn chưa xác định; không coi 15 phút là chính sách thư viện đã duyệt. | Uyên duyệt giá trị tạm nội bộ; thư viện chưa xác nhận. | Không xử lý lượt đã check-in thành vắng mặt; cần xác nhận trước vận hành thật. |

### Chờ chốt và theo dõi

| Mã | Phần còn cần chốt | Chủ sở hữu/đầu mối | Hạn đề xuất và điều kiện |
| --- | --- | --- | --- |
| OPEN-01 | SEAT-48 ghi nhận React/Vite và Kotlin theo Điều lệ/SRS; chỉ đánh giá lại khi có thay đổi được duyệt. | Uyên điều phối SEAT-48; người thực hiện cụ thể cần xác nhận. | Rà soát trước khi chốt hướng dẫn triển khai web/Android; đề xuất xác nhận đầu mối trước 11/11/2026. |
| OPEN-02 | Phiên bản Android tối thiểu và thiết bị kiểm thử; không có yêu cầu iOS tối thiểu vì iOS ngoài phạm vi. | Uyên điều phối; nhóm Android chưa được phân công theo SRS Q-17. | Chốt trước cấu hình `minSdk` và nghiệm thu Android; đề xuất phân công trước 11/11/2026. |
| OPEN-03 | Nguồn xác nhận gốc Q-01 và đầu mối Portal/SSO; không chặn OTP nội bộ. | Uyên điều phối, đầu mối CNTT nhà trường chưa được chỉ định. | Trước mọi tích hợp SSO; đề xuất cập nhật đầu mối trong lần rà soát kế tiếp trước 11/11/2026. |
| OPEN-04 | Thư viện xác nhận no-show 15 phút hoặc giá trị thay thế; email Q-06 đang hoãn theo SRS. | Uyên điều phối, đại diện thư viện chưa được chỉ định. | Bắt buộc trước vận hành tại thư viện; chưa có ngày phản hồi được xác nhận. Đề xuất rà soát lịch xin xác nhận trước 11/11/2026. |

SEAT-31 ghi nhận và liên kết quyết định; SEAT-28 duy trì yêu cầu, SEAT-48 theo
dõi lựa chọn công nghệ, SEAT-34/40 chốt dữ liệu gửi, SEAT-42/36 hoàn thiện
triển khai. Các mục lịch sử và thuật toán SEAT-33 bên dưới được giữ nguyên từ
nhánh `dev`.

## Ranh giới ban đầu giữa các dịch vụ

- **Trạng thái:** Đã chấp thuận cho bộ khung dự án.
- **Quyết định:** Tách giao diện web, API nghiệp vụ và xử lý CV thành các thư
  mục dịch vụ riêng; dùng PostgreSQL làm tầng lưu trữ dữ liệu chung.
- **Lý do:** Các thành phần có trách nhiệm và yêu cầu vận hành khác nhau.
- **Việc tiếp theo:** Xác nhận với nhóm các yêu cầu triển khai, xác thực và giao
  tiếp giữa các dịch vụ.

## Đầu ra CV và quy tắc đếm

- **Trạng thái:** Đã triển khai trong mô-đun CV, còn chờ nhóm rà soát.
- **Ngày:** 30/10/2026.
- **Quyết định:** Đánh phiên bản 1.0 cho đầu ra CV không phụ thuộc giao thức
  truyền. Tách bản ghi số đếm tổng hợp khỏi bản ghi hộp giới hạn dùng để gỡ lỗi
  cục bộ. Xác định đầu ra trước khi máy chủ triển khai tiếp nhận; chưa mặc định
  phải có điểm cuối HTTP.
- **Quy tắc đếm:** Số người nhìn thấy độc lập với tổng lượt IN/OUT qua đường ảo.
  Chỉ ước tính số người trong phòng khi có cấu hình số đầu phiên rõ ràng. Kẹp
  ước tính âm về 0 và đồng thời đánh dấu hiện tượng hụt số.
- **Theo dõi:** Dùng điểm neo giữa cạnh dưới của hộp giới hạn. Khi điểm này cắt
  một đoạn thẳng hữu hạn đã chuẩn hóa, xác định hướng đi; áp dụng vùng chết,
  thời gian chờ và thời hạn xóa trạng thái mất dấu. Bộ đếm được đặt lại ở mỗi
  phiên.
- **Việc tiếp theo:** Tiếp nhận dữ liệu ở máy chủ, lưu trữ và hiển thị trên giao
  diện là các giai đoạn riêng.

##  Chọn công nghệ giao diện web và ứng dụng Android

- **Ngày:** 10/11/2026.
- **Trạng thái:** Uyên duyệt React + Vite cho web và ứng dụng Android gốc bằng
  Kotlin vào ngày 10/11/2026. Việc thử nghiệm biên dịch và chạy ứng dụng gốc là
  bước tiếp theo; quyết định này không khẳng định Kotlin hoặc phần tích hợp QR/
  biểu đồ cho ứng dụng gốc đã được tạo nguyên mẫu.
- **Phạm vi:** Chọn công nghệ giao diện web và hướng phát triển ứng dụng gốc.
  iOS nằm ngoài phạm vi dự án hiện tại.

| Phương án | Kinh nghiệm nhóm / công sức học | Hệ sinh thái QR và biểu đồ | Yêu cầu biên dịch iOS | Khả năng dùng chung mã | Khả năng phù hợp Docker |
|---|---|---|---|---|---|
| React + Vite (web) | Giao diện, thành phần gọi API, các trang và kiểm thử hiện có đem lại kinh nghiệm trực tiếp; chi phí chuyển đổi thấp nhất. | Có nhiều lựa chọn web ổn định, chẳng hạn Chart.js/ECharts và quét QR trên trình duyệt bằng ZXing; kho mã chưa chọn thư viện biểu đồ hoặc QR. | Có thể biên dịch giao diện web trên nhiều nền tảng; không cần macOS. | Dùng lại giao diện React/JavaScript hiện tại. | Đã biên dịch được bằng dịch vụ Node/Vite hiện có trong Docker; camera/CV tiếp tục chạy ngoài Docker. |
| Vue + Vite (web) | Quy trình JavaScript/Vite tương tự, nhưng dự án chưa có mã Vue; cần học Vue và thay giao diện React hiện tại. | Có nhiều lựa chọn web ổn định, chẳng hạn Chart.js/ECharts và quét QR trên trình duyệt bằng ZXing; chưa đánh giá thư viện nào để dùng chính thức. | Có thể biên dịch web trên nhiều nền tảng; không cần macOS. | Dùng chung tiêu chuẩn trình duyệt và hợp đồng API, không dùng lại được các thành phần React. | Có thể biên dịch trong vùng chứa Node/Vite như React; không cải thiện ranh giới dịch vụ hiện tại. |
| Flutter (ứng dụng gốc) | Kho mã chưa dùng Dart hoặc Flutter; cần thêm công sức học công nghệ. | Có thư viện QR và biểu đồ cho ứng dụng gốc, chẳng hạn `mobile_scanner`, `qr_flutter` và `fl_chart`; chưa kiểm tra tính tương thích. | Biên dịch iOS cần macOS và Xcode; Android có thể biên dịch bằng bộ công cụ Android. | Giao diện Flutter tách biệt với giao diện React web; chỉ có thể dùng chung mô hình API/quy tắc nghiệp vụ nếu chủ động tách riêng. | Cần môi trường biên dịch Flutter/Android riêng; không thuộc dịch vụ Docker web hiện tại. |
| React Native (ứng dụng gốc) | Có thể tận dụng kiến thức JavaScript, nhưng React Native khác React DOM và cần kiến thức về mô-đun/biên dịch ứng dụng gốc. | Có thư viện camera, QR và biểu đồ cho ứng dụng gốc; chưa kiểm tra khả năng tương thích và duy trì của thư viện. | Biên dịch iOS cần macOS và Xcode; Android cần bộ công cụ SDK/Gradle. | Có thể dùng chung một phần mã JavaScript kiểm tra dữ liệu/API, nhưng không dùng chung cây thành phần web. | Bản dựng di động tách khỏi dịch vụ Docker web và cần SDK riêng. |
| Swift (ứng dụng iOS gốc) | Kho mã chưa có bằng chứng về kỹ năng Swift/iOS. | Có nền tảng hoặc thư viện quét QR/biểu đồ cho ứng dụng gốc; không đánh giá vì iOS ngoài phạm vi. | Cần macOS và Xcode. | Ứng dụng riêng, dùng mã đặc thù nền tảng. | Không phù hợp mục tiêu chỉ Android và dịch vụ Docker web hiện tại. |
| Kotlin (ứng dụng Android gốc) | Điều lệ/SRS đã ghi nhận định hướng Android của nhóm; bộ khung kho mã chưa chứng minh kinh nghiệm Android thực tế. | Có thư viện quét QR và biểu đồ cho Android; chưa cài đặt hoặc kiểm chứng thư viện nào trong dự án. | Bản dựng Android dùng JDK, Gradle và Android SDK; không cần macOS. | Giao diện tách khỏi giao diện React trên web; có thể dùng chung hợp đồng API và một số quy tắc nghiệp vụ thuần. | Bản dựng APK cần môi trường Android riêng; không đưa vào ảnh Docker web. |

### Bằng chứng nguyên mẫu

- **React + Vite:** Đã chạy thành công `npm run build` và cả 9 kiểm thử giao
  diện đều đạt. Khởi chạy ứng dụng hiện có và gọi
  `/api/v1/occupancy/current` qua máy chủ trung gian của Vite; trang và API đều trả HTTP 200.
  API thật hiện trả `current_count: null`, thể hiện trạng thái chưa có dữ liệu,
  không phải số đếm hợp lệ.
- **Vue + Vite:** Đã tạo tạm một ứng dụng Vue chưa commit, biên dịch thành công
  và hiển thị màn hình có trạng thái rỗng/đang tải/lỗi sau khi gọi cùng điểm
  cuối thật qua máy chủ trung gian Vite; trang và API đều trả HTTP 200. Thử nghiệm không thêm
  phần phụ thuộc Vue vào kho mã.
- **Ứng dụng gốc:** Chưa tạo nguyên mẫu ứng dụng trống/API. Máy này chưa cài
  Android SDK, `adb`, Gradle hoặc Flutter; kho mã cũng chưa có bộ khung ứng dụng
  gốc. Vì vậy, đề xuất ứng dụng gốc dưới đây chưa được kiểm chứng bằng thử
  nghiệm biên dịch hoặc chạy.
- **Thư viện QR/biểu đồ:** Chưa thêm hoặc kiểm thử thư viện ứng viên cho giao
  diện web hay ứng dụng gốc. Chọn và xác minh thư viện cụ thể khi triển khai
  các câu chuyện giao diện tương ứng.

### Đề xuất và phương án thay thế

- **Web:** Giữ React + Vite. Công nghệ này đã được tích hợp, biên dịch trong
  cấu hình Docker hiện tại, vượt qua các kiểm thử và gọi thành công máy chủ
  đang chạy. Vue cũng vượt qua một thử nghiệm API tối thiểu, nhưng
  chuyển đổi sẽ thay thế mã React đang hoạt động mà chưa chứng minh được lợi
  ích.
- **Ứng dụng gốc:** Giữ hướng Android gốc bằng Kotlin, phù hợp phạm vi dự án đã
  ghi nhận và mục tiêu chỉ hỗ trợ Android. Không chọn Flutter hoặc React Native
  chỉ dựa trên khả năng dùng chung mã giả định: cả hai vẫn cần quy trình giao
  diện/biên dịch di động riêng, còn iOS nằm ngoài phạm vi. Không chọn Swift vì
  công nghệ này hướng tới iOS.
- **Phê duyệt và việc tiếp theo:** Uyên duyệt React + Vite và Android gốc bằng
  Kotlin vào ngày 10/11/2026. Trước khi xem việc triển khai ứng dụng gốc là đã
  kiểm chứng, cần thử nghiệm 30 phút với ứng dụng Kotlin trống và API trên máy
  có Android SDK, Gradle. Uyên sẽ phân công người chạy thử và ghi kết quả vào
  SEAT-48. Không tuyên bố đã kiểm thử bản dựng ứng dụng gốc hoặc tích hợp
  QR/biểu đồ.
- **Phụ thuộc:** Quyết định này phục vụ SEAT-48 và các câu hỏi Q-16/Q-17 trong
  SRS. SEAT-31 là công việc phụ thuộc trước khi triển khai các phần liên quan.

## Thuật toán đếm người qua đường ảo

- **Trạng thái:** Thuật toán đã được ghi lại trong mô-đun CV.
- **Ngày rà soát:** 09/11/2026.
- **Nguồn:** [SEAT-33](https://nhauyen70205.atlassian.net/browse/SEAT-33),
  `cv/app/counting/line_counter.py` và `cv/app/schemas/count_result.py`.
- **Quyết định:** Dùng YOLOv8n và ByteTrack; lấy tâm cạnh dưới của hộp giới hạn
  của cùng một đối tượng theo dõi để xác định hướng khi đối tượng cắt đoạn
  đường ảo hữu hạn. Dùng vùng chết, thời gian chờ và thời hạn xóa trạng thái mất
  dấu để giảm đếm lặp. Mỗi lần cắt hợp lệ tạo một sự kiện; đối tượng có thể
  được đếm lại sau thời gian chờ.
- **Lý do:** Cần đếm lượt qua cửa theo hướng IN/OUT, tách số người nhìn thấy
  trong khung hình khỏi số người ước tính trong phòng. Mã đối tượng theo dõi
  chỉ tạm thời trong phiên, không dùng để nhận diện danh tính.
- **Phương án không dùng:** Không lấy `people_count` làm số người toàn phòng,
  không cộng bộ đếm tích lũy qua các khung hình, không giới hạn mỗi mã đối
  tượng chỉ được đếm một lần trong toàn phiên.
- **Công thức:** Khi biết số đầu phiên, hiện diện bằng
  `max(0, initial_occupancy + IN - OUT)`; số âm bật `occupancy_underflow`.
  Chỉ dùng IN trừ OUT khi đã xác nhận số đầu phiên bằng 0; chưa biết số đầu
  phiên thì hiện diện là `null`.
- **Ảnh hưởng:** Theo BR-02, số chỗ trống phải được chặn ở mức 0 và có cảnh báo
  khi số người vượt sức chứa; không giới hạn số người theo sức chứa. Việc kết
  hợp sức chứa và cảnh báo thuộc phần máy chủ/giao diện; `CountResult` hiện
  chưa có các trường này.
- **Giới hạn triển khai:** 416 px và 3–5 FPS là cấu hình mục tiêu, chưa phải
  hiệu năng đã đo. Giao diện dòng lệnh (CLI) mặc định dùng 640 px; chưa lấy mẫu
  ở 3–5 FPS. CV xuất dữ liệu cục bộ, chưa có bộ gửi HTTP hoặc cơ chế thử gửi lại
  tới máy chủ.
- **Bàn giao:** Chi tiết quy trình xử lý, tham số và giới hạn ở
  [Thuật toán đếm người](../cv/README.md#thuật-toán-đếm-người--seat-33).
  Thắng và Khiêm cần xác nhận giải thích đúng công thức và cách xử lý số âm
  theo tiêu chí SEAT-33; chưa ghi nhận xác nhận này khi rà soát.
