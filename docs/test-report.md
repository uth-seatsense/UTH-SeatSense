# Báo cáo kiểm thử

## Đợt kiểm tra — 2026-11-15 (tài liệu và giao diện web)

Phạm vi: cập nhật tài liệu; không thay đổi mã nguồn frontend. Các lệnh được
chạy trong thư mục `frontend` sau khi khôi phục dependency bằng `npm.cmd ci`.

| Lệnh | Kết quả | Ghi chú |
|---|---|---|
| `npm.cmd run format:check` | Không đạt | Prettier báo lỗi định dạng ở 14 tệp mã nguồn/kiểm thử frontend có sẵn. Các tệp này không thuộc phạm vi thay đổi tài liệu ban đầu. |
| `npm.cmd test` | Đạt | 4 tệp kiểm thử, tổng cộng 39 kiểm thử. |
| `npm.cmd run lint` | Đạt, có cảnh báo | Mã thoát 0; không có lỗi, có 14 cảnh báo `react/prop-types` đã tồn tại trong `src/pages/DashboardPage.jsx`. |
| `npm.cmd run build` | Đạt | Hoàn tất build production bằng Vite. |

Trong đợt kiểm tra tài liệu ban đầu, chưa chạy kiểm thử Backend, Docker Compose,
end-to-end hoặc Android native. Kết quả chạy sau đó được ghi ở các mục bên
dưới. Báo cáo này chỉ ghi kết quả các lệnh, không chứng minh rằng toàn bộ yêu
cầu Sprint 4 hoặc tiêu chí nghiệm thu Jira đã hoàn tất.

## Đợt kiểm tra — 2026-11-15 (Backend, Docker, Android)

| Lệnh / nội dung kiểm tra | Kết quả | Ghi chú |
|---|---|---|
| `$env:SEAT24_RUN_DB_TESTS = '1'; .\.venv\Scripts\python.exe -m pytest backend\tests -q` | Không đạt: 25 đạt, 1 lỗi | `test_cv_batch_receipt_and_idempotent_retry`: gửi lại cùng lô dữ liệu CV trả HTTP 409 thay vì HTTP 200 như mong đợi. Lệnh này bật kiểm thử lưu trữ PostgreSQL thực tế. |
| `$env:SEAT24_RUN_DB_TESTS = '1'; .\.venv\Scripts\python.exe -m unittest discover -s database\tests -p test_cv_migration.py -v` | Đạt: 6 kiểm thử | Kiểm thử migration và constraint PostgreSQL chạy trong container tạm thời. |
| `$env:SEAT24_RUN_COMPOSE_TESTS = '1'; .\.venv\Scripts\python.exe -m unittest discover -s database\tests -p test_compose_persistence.py -v` | Đạt: 2 kiểm thử | Kiểm tra Compose cô lập gồm khởi tạo database mới, nâng cấp migration, đọc/ghi Backend, database mất kết nối, khởi động lại và tính bền vững dữ liệu. Tài nguyên kiểm thử tạm đã được dọn. |
| `docker compose config --quiet` | Đạt | Cấu hình Compose hợp lệ. |
| `http://localhost:8000/health/db` và `http://localhost:3000/` | Đạt: mỗi URL trả HTTP 200 | Kiểm tra nhanh Backend và Frontend container đang chạy tại máy. |
| Kiểm tra dự án/toolchain Android | Bị chặn | Chưa có dự án Android, Gradle wrapper, `AndroidManifest.xml`, `adb` hoặc biến môi trường Android SDK. Không thể kiểm tra APK/runtime. |

Ở thời điểm kiểm tra này, lỗi gửi lại CV của Backend chưa được khắc phục và
chưa có module/toolchain Android. Các lần sửa và kiểm tra tiếp theo được ghi
bên dưới; riêng từng đợt không đồng nghĩa toàn bộ Sprint 4 đã được nghiệm thu.

## Đợt kiểm tra — 2026-11-15 (tiếp nối triển khai ứng dụng di động)

| Lệnh / nội dung kiểm tra | Kết quả | Ghi chú |
|---|---|---|
| `$env:SEAT24_RUN_DB_TESTS = '1'; .\.venv\Scripts\python.exe -m pytest backend\tests -q` | Đạt: 31 kiểm thử | Bao gồm gửi lại CV idempotent và các kiểm thử API OTP/session, phòng, đặt phòng và QR dùng một lần. Còn một cảnh báo không tương thích trong Starlette/httpx. Việc gửi email SMTP được giả lập trong kiểm thử API. |
| `$env:SEAT24_RUN_COMPOSE_TESTS = '1'; .\.venv\Scripts\python.exe -m unittest discover -s database\tests -p test_compose_persistence.py -v` | Đạt: 2 kiểm thử | Dự án Compose tạm thời; khởi tạo mới xác nhận migration 009 và chạy lại an toàn; kiểm thử tính bền vững bao gồm health/restart Backend. Không sửa volume database của người dùng. |
| `docker compose config --quiet` | Đạt | Compose chấp nhận các biến môi trường OTP, SMTP và quy tắc đặt phòng mới. |
| `gradle -p android testDebugUnitTest assembleDebug --no-daemon` với Gradle 8.11.1 và Android SDK 35 | Đạt | Biên dịch Kotlin và đóng gói APK debug thành công. `testDebugUnitTest` báo `NO-SOURCE`; hiện chưa có kiểm thử Android unit. APK: `android/app/build/outputs/apk/debug/app-debug.apk`. |
| `.\android\gradlew.bat testDebugUnitTest assembleDebug` | Bị chặn ở lần đầu | Tải Gradle Wrapper bị ngắt kết nối. Wrapper đã được tạo; build cùng nội dung thành công khi dùng bản Gradle đã tải về máy. |
| `adb devices` | Không có thiết bị kết nối | Chưa cài/khởi chạy APK; chưa xác minh Android runtime và quét camera/QR. |
| Kiểm thử/build Frontend | Không chạy lại trong đợt này | Không sửa mã nguồn frontend. Kết quả trước đó vẫn là 39/39 kiểm thử và build đạt; `format:check` vẫn báo 14 tệp tồn tại từ trước như đã nêu. |
| `git diff --check` | Đạt | Không có lỗi khoảng trắng trong worktree. |

Lỗi so sánh datetime UTC/không timezone gây ra HTTP 409 khi gửi lại CV đã
được sửa; toàn bộ Backend suite mới nhất tại đợt đó đã đạt. API 26 vẫn là mức
tối thiểu tạm thời, chờ xác nhận sản phẩm. Chưa kiểm tra gửi SMTP qua máy chủ
mail thật, Android runtime/E2E hoặc áp dụng migration 009 lên volume người
dùng hiện có; cần sao lưu volume PostgreSQL hiện hữu và chạy migration thủ công
theo hướng dẫn trong `database/README.md`.

## Đợt kiểm tra — 2026-11-16 (tích hợp API web)

| Lệnh / nội dung kiểm tra | Kết quả | Ghi chú |
|---|---|---|
| `npm.cmd test` | Đạt: 37 kiểm thử | Bao gồm yêu cầu OTP, dùng chung Bearer token cho các endpoint web, xử lý lỗi Backend, route được bảo vệ và payload QR tương thích Android. |
| `npm.cmd run lint` | Đạt, có cảnh báo | Mã thoát 0; không có lỗi, có 16 cảnh báo `react/prop-types` (14 cảnh báo có sẵn trong Dashboard và 2 cảnh báo với component con của auth). |
| `npm.cmd run build` | Đạt | Hoàn tất build production bằng Vite. |
| Chạy Prettier trên các tệp frontend đã sửa | Đạt | Các tệp JS/JSX/CSS đã sửa đúng định dạng. Kiểm tra toàn repository hiện báo 6 tệp không liên quan đã tồn tại: `main.jsx`, `HealthPage.jsx`, `HomePage.jsx`, `App.test.jsx`, `DashboardStatus.test.jsx` và `Health.test.js`. |

Web hiện gọi chung các route auth, rooms, occupancy, booking và check-in của
Backend với Android. Chưa chạy E2E OTP/đặt phòng/quét QR camera từ trình duyệt
đến Backend thật; cần SMTP đã cấu hình và database sẵn sàng. Quét camera dùng
API `BarcodeDetector` của trình duyệt nếu được hỗ trợ, nếu không có thể nhập
nội dung QR bằng văn bản.

## Đợt kiểm thử — 2026-11-18 (API sự kiện CV của SEAT-53)

| Lệnh / nội dung kiểm tra | Kết quả | Ghi chú |
|---|---|---|
| `python -m pytest tests/test_count_event_api.py tests/test_cv_api.py -q` | Đạt: 20 kiểm thử | Chạy từ thư mục `backend`; bao gồm tạo/gửi lại sự kiện CV, API key, hướng không hợp lệ, phòng không tồn tại, JSON sai định dạng và trường dữ liệu thừa. |
| `docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm backend-test` | Đạt: 33 kiểm thử, bỏ qua 6 | Chạy bộ kiểm thử Backend trong image kiểm thử với các dịch vụ Docker Compose. |
| Kiểm tra migration bằng `docker compose exec db psql ...` | Đạt | Migration `010_cv_count_event_uuid.sql` tạo `count_events.event_id` kiểu PostgreSQL `uuid` cùng các cột session/device/status bắt buộc. |
| Gửi curl thực tế lần đầu tới `/api/v1/cv/events` | Đạt: HTTP 201 | Payload dùng `room_id` 5 và `event_id` UUID duy nhất; phản hồi có `duplicate=false`. |
| Gửi lại cùng payload curl | Đạt: HTTP 201 | Phản hồi có `duplicate=true`; PostgreSQL chỉ lưu một dòng cho `event_id` đó. |
| Gửi curl với API key sai | Đạt: HTTP 401 | Mã lỗi trả về là `unauthorized`. |
| Gửi curl với JSON sai định dạng | Đạt: HTTP 400 | Mã lỗi trả về là `malformed_json`. |
| Kiểm tra bản ghi PostgreSQL/Adminer | Đạt | Bảng `count_events` còn một dòng; yêu cầu gửi lại không tạo thêm bản ghi. |
| Chụp endpoint bằng Swagger | Đạt | Ảnh: `seat53-swagger.png`. |
| Chụp bản ghi bằng Adminer | Đạt | Ảnh: `seat53-adminer-count-events.png`. |

API key nhận dữ liệu CV được tạo cục bộ và cấu hình giống nhau cho
`CV_API_KEY` và `CV_INGEST_API_KEY` trong `.env`. Docker Compose nhận các biến
này; giá trị key không được ghi vào tệp kết quả hoặc báo cáo.

Các tệp bằng chứng nằm trong thư mục bằng chứng của phiên làm việc:
`seat53-curl-first.txt`, `seat53-curl-duplicate-key-json.txt`,
`seat53-payload.json`, `seat53-swagger.png`,
`seat53-adminer-count-events.png`, `seat53-pytest-host.txt` và
`seat53-pytest-docker.txt`.

Các việc còn lại, nằm ngoài phạm vi endpoint SEAT-53:

- Cập nhật `OccupancyRecord` khi nhận sự kiện `in`/`out` hợp lệ.
- Kiểm tra nhiều yêu cầu trùng được gửi đồng thời với PostgreSQL, không chỉ gửi lại tuần tự.
- Kiểm tra phản hồi HTTP 503 khi database mất kết nối và xác nhận giao dịch được rollback đúng.
- Đưa các thay đổi schema phòng còn đang áp dụng trực tiếp cho database kiểm thử vào migration chính thức cho các volume hiện có.
