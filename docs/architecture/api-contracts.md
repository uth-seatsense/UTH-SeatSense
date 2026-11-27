# API contract — tổng quan

> Trạng thái: bản rà soát / đề xuất, chưa phải toàn bộ contract đã được triển khai.
> Ngày đối chiếu: 15-11-2026. Đối chiếu source và OpenAPI runtime; contract CV chi tiết nằm ở phụ lục cuối tài liệu.

## Quy ước chung

- Prefix `/api/v1`; JSON UTF-8, tên trường `snake_case`.
- Date-time dùng ISO 8601 có múi giờ; server trả UTC dạng `Z`. Thời điểm không có timezone bị từ chối.
- Danh sách dùng `limit` (mặc định 50, tối đa 100) và `offset` (mặc định 0); response đề xuất `{ "items": [], "limit": 50, "offset": 0, "total": 0 }`. Chưa có quy ước phân trang được triển khai/đồng thuận trong mã.
- Các API mới dùng lỗi dạng `{ "error": { "code": "...", "message": "..." } }`; các API cũ có thể còn response khác. `400` JSON sai, `401` thiếu/sai token, `403` không đủ quyền, `404` không tồn tại, `409` xung đột trạng thái/khóa idempotency, `422` dữ liệu hợp lệ về cú pháp nhưng sai quy tắc, `429` vượt rate limit. Auth middleware được dùng cho API nghiệp vụ người dùng đã triển khai.
- API nghiệp vụ được bảo vệ dùng `Authorization: Bearer <access_token>`. OTP cấp access token opaque; Backend chỉ lưu SHA-256 hash, có thời hạn và logout thu hồi phiên. Refresh token chưa được triển khai. Android và các client khác dùng chung API/token; CSRF cho web cần xem xét khi tích hợp cookie.
- Các endpoint auth đăng ký/đăng nhập/đăng xuất/thông tin tài khoản dùng chung cho web, ứng dụng native và Portal; client không có bộ endpoint hay định dạng token riêng. Portal/SSO là phương thức xác thực chờ trường phê duyệt/cung cấp thông số.
- Portal/SSO: dành integration seam (`provider=portal`, `external_subject`), trạng thái chờ trường cung cấp issuer, protocol, claim mapping và quy trình duyệt. Không thu hoặc lưu mật khẩu Portal. MVP hiện có thể dùng OTP email theo DEC-08.
- CV dùng API key riêng, không dùng token người dùng: `X-API-Key`. Cách cấp/luân chuyển/lưu key và production secret store chưa chốt.
- CV event: `event_id` UUID là idempotency key; cùng ID/cùng payload trả receipt
  cũ, cùng ID/khác payload trả `409 event_id_conflict`. Payload không chứa ảnh,
  video hoặc ID theo dõi lâu dài. Heartbeat thiết bị là request riêng, không
  được tính thành sự kiện IN/OUT. CountResult batch của SEAT-34 vẫn là contract
  riêng trên `POST /api/v1/cv/count-records`.

## Endpoint inventory và vai trò

`IMPLEMENTED` chỉ áp dụng khi có handler trong source hiện tại; `PROPOSED` là contract cần triển khai. Đã tái sử dụng nội dung SEAT-18, payload CV từ SEAT-34 và đặc tả occupancy/rooms từ SEAT-39. Source có hai route occupancy, route nhận CV, auth OTP/session, danh sách phòng, booking và check-in QR. Dashboard, occupancy history, CV events và device status vẫn chưa có handler.

| Nhóm | Phương thức / URL | Vai trò gọi | Trạng thái và ý nghĩa |
|---|---|---|---|
| Auth | `POST /api/v1/auth/register` | Public | IMPLEMENTED — gửi OTP; lần xác minh đầu tiên tự tạo hồ sơ |
| Auth | `POST /api/v1/auth/login` | Public | IMPLEMENTED — xác minh OTP và cấp Bearer token opaque |
| Auth | `POST /api/v1/auth/logout` | `authenticated` | IMPLEMENTED — thu hồi access session hiện tại |
| Auth | `GET /api/v1/auth/me` | `authenticated` | IMPLEMENTED — hồ sơ và role hiện tại |
| Occupancy | `GET /api/v1/occupancy/current` | Public hoặc user đã đăng nhập; role/scope chờ chốt | IMPLEMENTED — hiện chỉ trả tổng `current_count`, `updated_at`, `location`; chưa có danh sách từng phòng, campus filter hoặc phân trang của contract mục tiêu |
| Occupancy | `GET /api/v1/occupancy/rooms/{room_id}/latest` | User được xem occupancy; auth chưa có | IMPLEMENTED legacy response — target Sprint 4 trả occupancy tổng hợp từ event, freshness và device status; hiện chưa được triển khai |
| Occupancy | `GET /api/v1/rooms/{room_id}/occupancy/history` | `librarian`, `admin`; quyền student chờ chốt | PROPOSED — lịch sử mật độ theo khoảng thời gian (SEAT-39) |
| Rooms | `GET /api/v1/rooms` | `authenticated` | IMPLEMENTED — danh sách/phân trang phòng đang hoạt động |
| Rooms | `GET /api/v1/rooms/{room_id}` | `authenticated` | IMPLEMENTED — chi tiết phòng đang hoạt động |
| Bookings | `GET /api/v1/bookings` | User đã đăng nhập | IMPLEMENTED — chỉ liệt kê booking của user hiện tại |
| Bookings | `POST /api/v1/bookings` | User đã đăng nhập | IMPLEMENTED — tạo booking theo chính sách cấu hình |
| Bookings | `GET /api/v1/bookings/{booking_id}` | Chủ booking | IMPLEMENTED — chi tiết booking; ngoài owner trả 404 |
| Bookings | `DELETE /api/v1/bookings/{booking_id}` | Chủ booking | IMPLEMENTED — hủy nếu còn trong thời hạn |
| Check-in | `POST /api/v1/bookings/{booking_id}/check-in-token` | Chủ booking | IMPLEMENTED — phát QR token opaque dùng một lần |
| Check-in | `POST /api/v1/check-in` | Chủ booking | IMPLEMENTED — xác minh token và ghi nhận check-in một lần |
| Dashboard | `GET /api/v1/dashboard/summary` | `librarian`, `admin` | PROPOSED — FR-DASH-01/02 mức Should; chỉ số vận hành và filters cần chốt |
| Health | `GET /health`, `GET /api/v1/health`, `GET /health/db` | Public/monitoring | IMPLEMENTED — health service và database health |
| CV | `POST /api/v1/cv/count-records` | CV service; API key cần bổ sung | IMPLEMENTED — payload CountResult theo SEAT-34; handler hiện chưa kiểm tra `X-API-Key` |
| CV events | `POST /api/v1/cv/events` | CV service với API key | PROPOSED — event_id idempotent, chưa triển khai |
| CV status | `PUT /api/v1/cv/devices/{device_id}/status` | CV service với API key | PROPOSED — heartbeat/status riêng, không ảnh hưởng bộ đếm |

## Payload mẫu cho API

Quy ước đọc bảng dưới: body/response là JSON mẫu; `—` nghĩa không có body/params. Các hàng `IMPLEMENTED` phản ánh handler hiện tại; các hàng `PROPOSED` vẫn là contract mục tiêu để review.

## Đặc tả operation đầy đủ

| Method / URL | Gọi bởi | Path/query/header | Request body | Response thành công | Lỗi dự kiến |
|---|---|---|---|---|---|
| `POST /api/v1/auth/register` IMPLEMENTED | Public | — | `{"email":"sv@example.edu.vn"}` | `202 {"status":"otp_sent"}` | 422 email sai/không thuộc miền được phép; 429 gửi lại quá sớm; 503 auth/SMTP chưa cấu hình hoặc gửi email lỗi |
| `POST /api/v1/auth/login` IMPLEMENTED | Public | — | `{"email":"sv@example.edu.vn","otp":"123456"}` | `200 {"access_token":"<opaque-token>","token_type":"bearer","expires_at":"2026-11-12T03:00:00Z","user":{"id":123,"email":"sv@example.edu.vn","display_name":"Nguyễn An","role":"student"}}` | 401 OTP sai/hết hạn/đã dùng; 422 field sai; 503 auth chưa cấu hình |
| `POST /api/v1/auth/logout` IMPLEMENTED | `authenticated` | Bearer token | `—` | `204` không body | 401 token thiếu/sai/hết hạn |
| `GET /api/v1/auth/me` IMPLEMENTED | `authenticated` | Bearer token | `—` | `200 {"id":123,"email":"sv@example.edu.vn","display_name":"Nguyễn An","role":"student"}` | 401 token thiếu/sai/hết hạn |
| `GET /api/v1/occupancy/current` IMPLEMENTED (SEAT-57 đã bổ sung data_status) | Public hoặc user đã đăng nhập; role/scope chờ chốt | Hiện chưa nhận query | `—` | `200 {"current_count":23,"updated_at":"2026-11-11T10:25:30Z","location":"Thư viện UTH","data_status":"fresh"}`; `data_status` nhận `fresh|stale|disconnected|null` dựa trên `occupancy_stale_seconds` (30s) và `device_offline_seconds` (90s) | OpenAPI hiện khai báo `200`; query campus và pagination chưa implement |
| `GET /api/v1/occupancy/rooms/{room_id}/latest` IMPLEMENTED legacy / target response PROPOSED | User xem occupancy; role/scope chờ chốt | `room_id`: integer >0 (ID DB) | `—` | `200 {"room_id":14,"room_code":"A101","capacity":40,"estimated_occupancy":23,"available_seats":17,"is_over_capacity":false,"density_level":"medium","device_status":"online","occupancy_status":"fresh","recorded_at":"2026-11-11T08:00:00Z","received_at":"2026-11-11T08:00:01Z"}` | 401/403 theo auth/scope; 404 `room_not_found`; 422 room_id sai; 503 `occupancy_unavailable` khi chưa có baseline/occupancy và `service_unavailable` khi DB/dịch vụ lỗi |
| `GET /api/v1/rooms/{room_id}/occupancy/history` PROPOSED (SEAT-39) | `librarian`, `admin`; student access chờ chốt | `start_time`, `end_time` ISO 8601 UTC; `limit` 1..500 (default 100); `offset` ≥0 | `—` | `200 {"room_id":14,"room_code":"A101","start_time":"2026-11-11T09:00:00Z","end_time":"2026-11-11T10:00:00Z","records":[{"id":1001,"current_count":20,"available_seats":30,"recorded_at":"2026-11-11T09:00:00Z","source":"cv","device_status":"online"}],"limit":100,"offset":0,"total":1}` | 400 query sai; 401; 403 role/scope; 404 `room_not_found`; 409 không áp dụng; 422 datetime/range/limit/offset sai; 503 DB/service lỗi |
| `GET /api/v1/rooms` IMPLEMENTED | `authenticated` | `limit` 1..100 (default 50), `offset` ≥0 (default 0), tùy chọn `campus_code` (`CS1`/`CS3`), `room_type` (`free_area`/`topic_room`) | `—` | `200 {"items":[{"id":14,"code":"A101","name":"Phòng A101","room_type":"free_area","capacity":40,"campus_code":"CS1","building":"Cơ sở 1","location":null,"is_active":true}],"limit":50,"offset":0,"total":1}` | 401 thiếu token; 422 filter/pagination sai |
| `GET /api/v1/rooms/{room_id}` IMPLEMENTED | `authenticated` | `room_id` integer dương | `—` | `200` đối tượng phòng như item GET list | 401; 404 `room_not_found`; 422 id sai |
| `GET /api/v1/bookings` IMPLEMENTED | User đã đăng nhập; chỉ booking của mình | `limit`, `offset` | `—` | `200 {"items":[{"id":456,"room_id":14,"user_id":123,"participant_count":3,"status":"booked","starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z","checkin_at":null,"no_show_at":null,"room":{"id":14,"code":"A101","name":"A101","room_type":"topic_room","capacity":40,"campus_code":"CS1","building":"Cơ sở 1","location":null,"is_active":true}}],"limit":50,"offset":0,"total":1}` | 401; 422 pagination sai |
| `POST /api/v1/bookings` IMPLEMENTED | User đã đăng nhập | Bearer token | `{"room_id":14,"starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z","participant_count":3}` | `201` booking object như response GET | 401; 404 room không tồn tại; 409 `booking_conflict`, `daily_limit_exceeded` hoặc `room_not_bookable`; 422 thời lượng, ngày đặt trước, sĩ số hoặc thời gian sai |
| `GET /api/v1/bookings/{booking_id}` IMPLEMENTED | Chủ booking | `booking_id` số nguyên dương | `—` | `200` booking object như response GET list | 401; 404 `booking_not_found` (bao gồm booking ngoài owner); 422 id sai |
| `DELETE /api/v1/bookings/{booking_id}` IMPLEMENTED | Chủ booking | `booking_id` số nguyên dương | `—` | `204` không body | 401; 403 không phải chủ booking; 404 không tồn tại; 409 booking không hoạt động/đã qua hạn hủy |
| `POST /api/v1/bookings/{booking_id}/check-in-token` IMPLEMENTED | Chủ booking | Bearer token; `booking_id` số nguyên dương | `—` | `201 {"booking_id":456,"qr_token":"<opaque-single-use-token>","valid_from":"2026-11-12T02:00:00Z","expires_at":"2026-11-12T02:15:00Z"}` | 401; 403 không phải chủ booking; 404 booking không tồn tại; 409 booking không hoạt động/cửa sổ đã đóng |
| `POST /api/v1/check-in` IMPLEMENTED | Chủ booking | Bearer token | `{"booking_id":456,"qr_token":"<opaque-single-use-token>"}` | `200 {"booking_id":456,"status":"checked_in","checked_in_at":"2026-11-12T02:04:00Z"}` | 401 token/OTP sai hoặc QR sai; 403 không phải chủ booking; 404 booking không tồn tại; 409 cửa sổ check-in chưa mở/đã đóng hoặc booking không hoạt động |
| `GET /api/v1/dashboard/summary` PROPOSED | `librarian`, `admin` | `from`, `to` ISO8601; scope campus/building chờ chốt | `—` | `200 {"occupancy":{"current":12,"capacity":40},"bookings":{"total":8,"checked_in":5,"no_show":1},"generated_at":"2026-11-11T08:00:00Z"}` | 400 malformed query; 401; 403 role/scope; 404 scope không tồn tại (nếu lọc theo scope); 409 range conflict; 422 date/filter sai |
| `POST /api/v1/cv/count-records` IMPLEMENTED (SEAT-34; thiếu auth) | CV service | Hiện chỉ có `Content-Type: application/json`; `X-API-Key` là yêu cầu cần tích hợp; body `records` gồm 1..1000 CountResult | `{"records":[{"schema_version":"1.0","session_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","camera_id":"cam-01","room_id":"A101","source_type":"webcam","frame_index":100,"timestamp_ms":10000,"recorded_at":"2026-11-11T08:00:00Z","people_count":3,"tracked_count":2,"line_enabled":true,"in_count":4,"out_count":1,"initial_occupancy":0,"estimated_occupancy":3,"occupancy_underflow":false}]}` | `200 {"status":"accepted","created_count":1,"duplicate_count":0,"records":[{"record_id":8123,"session_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","frame_index":100,"room_code":"A101","room_id":14,"received_at":"2026-11-11T08:00:01Z","duplicate":false}]}` | Hiện có: 400 JSON sai; 409 cùng `(session_id, frame_index)` khác payload; 422 batch/schema sai; 503 DB unavailable. Khi thêm key cần bổ sung 401/403 |
| `POST /api/v1/cv/events` IMPLEMENTED (SEAT-53) | CV service với API key | `X-API-Key` | `{"event_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","session_id":"0acbaf47-e9f1-4f69-88e7-bab7f5a1cde0","room_id":14,"device_id":"cam-01","direction":"in","event_time":"2026-11-11T08:00:00Z","device_status":"online"}` | `201 {"event_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","room_id":14,"received_at":"2026-11-11T08:00:01Z","duplicate":false}`; retry trả receipt cũ `201`/`duplicate:true` | 400 JSON sai; 401 API key sai/thiếu; 404 `room_not_found`; 409 `event_id_conflict`; 422 schema sai; 503 DB lỗi |
| `PUT /api/v1/cv/devices/{device_id}/status` PROPOSED (SEAT-51/57) | CV service với API key | `X-API-Key`; `device_id` trong path | `{"room_id":14,"device_status":"online","reported_at":"2026-11-11T08:00:00Z"}` | `200 {"device_id":"cam-01","device_status":"online","last_seen_at":"2026-11-11T08:00:00Z"}` | 401 API key sai/thiếu; 403 scope sai; 404 `room_not_found`; 422 status/time sai; 503 DB/service lỗi |
| `GET /api/v1/notifications/subscriptions` PROPOSED / OPTIONAL (FR-OPT-01) | `authenticated` | Bearer token; `limit`, `offset` | `—` | `200 {"items":[{"id":"ntf_123","room_id":14,"condition":"seats_available","threshold":5,"enabled":true,"channel":"email"}],"limit":50,"offset":0,"total":1}` | 400 query sai; 401; 403; 404 không áp dụng; 409 không áp dụng; 422 pagination sai |
| `POST /api/v1/notifications/subscriptions` PROPOSED / OPTIONAL (FR-OPT-01) | `student` | Bearer token | `{"room_id":14,"condition":"seats_available","threshold":5,"channel":"email"}` | `201 {"id":"ntf_123","room_id":14,"condition":"seats_available","threshold":5,"enabled":true,"channel":"email","created_at":"2026-11-11T08:00:00Z"}` | 400 malformed JSON; 401; 403 role/scope; 404 room không tồn tại; 409 subscription trùng; 422 room không hỗ trợ occupancy hoặc field/channel không hợp lệ |
| `DELETE /api/v1/notifications/subscriptions/{subscription_id}` PROPOSED / OPTIONAL (FR-OPT-01) | Chủ subscription; admin | Bearer token; `subscription_id` string | `—` | `204` không body | 400 không áp dụng; 401; 403 không phải owner; 404 subscription không tồn tại; 409 đã bị xử lý/xóa; 422 id sai |
| `GET /health`, `GET /api/v1/health`, `GET /health/db` IMPLEMENTED | Public/monitor | — | `—` | `200 {"status":"ok","service":"backend"}` với hai route service health; `/health/db` trả trạng thái kết nối DB | 400/401/403/404/409/422 không áp dụng |

Các endpoint đã triển khai dùng phiên Bearer opaque của SEAT-65. Dependency `get_current_user` kiểm tra phiên và tài khoản; `require_roles(...)` kiểm tra vai trò từ User trong database, không lấy vai trò do client gửi. Các endpoint còn đánh dấu PROPOSED chưa có handler và chưa được xem là đã bảo vệ.

### Bảng quyền SEAT-66

| Endpoint | Quyền hiện tại | Điều kiện bổ sung |
| --- | --- | --- |
| `POST /api/v1/auth/register`, `POST /api/v1/auth/login` | Public | Quy tắc email/OTP theo SEAT-65 |
| `GET /api/v1/auth/me`, `POST /api/v1/auth/logout` | Tài khoản đã đăng nhập và đang hoạt động | Phiên chưa hết hạn, chưa bị thu hồi |
| `GET /api/v1/bookings` | Tài khoản đã đăng nhập và đang hoạt động | Chỉ liệt kê booking của người gọi |
| `POST /api/v1/bookings` | Tài khoản đã đăng nhập và đang hoạt động | Chủ booking lấy từ token, không lấy user ID từ client |
| `GET /api/v1/bookings/{booking_id}` | Chủ booking đã đăng nhập | Booking người khác trả 404 để không lộ thông tin |
| `DELETE /api/v1/bookings/{booking_id}` | Chủ booking đã đăng nhập | Không phải chủ trả 403; vẫn kiểm tra thời hạn hủy |
| `POST /api/v1/bookings/{booking_id}/check-in-token` | Chủ booking đã đăng nhập | Không phải chủ trả 403; kiểm tra trạng thái booking |
| `POST /api/v1/check-in` | Chủ booking đã đăng nhập | Không phải chủ trả 403; kiểm tra QR và cửa sổ check-in |
| `POST /api/v1/occupancy/rooms/{room_id}/counting-sessions` | `librarian`, `admin` | `student` và vai trò khác trả 403 |
| `GET /api/v1/dashboard/summary` | PROPOSED: `librarian`, `admin` | Chưa có handler; không tạo endpoint giả để chứng minh phân quyền |

- Thiếu token, sai scheme, token không hợp lệ, hết hạn hoặc đã logout: `401 unauthorized`.
- Tài khoản không hoạt động: `403 account_inactive`. Sai vai trò: `403 forbidden`.
- `librarian`/`admin` không tự động được truy cập booking của người khác qua các route dành cho chủ booking. Quyền quản lý mở rộng cần được thiết kế riêng.
- Booking/check-in đã có dependency đăng nhập và kiểm tra ownership; SEAT-66 giữ nguyên các quy tắc đó, không mặc định cấm thủ thư đặt phòng.
- Test: `python -m pytest tests/test_authz.py tests/test_auth_otp.py tests/test_mobile_api.py tests/test_counting_session.py -q` từ thư mục backend.
- Bằng chứng Swagger cần có response thực tế: gọi `GET /api/v1/bookings` không token để nhận 401; gọi endpoint counting-sessions bằng token sinh viên với body `{"initial_count":3}` để nhận 403. Che token trước khi chia sẻ ảnh.

## Option thông báo bổ sung theo SRS

SRS 1.9, FR-OPT-01 xếp dự báo mật độ 1–2 giờ hoặc thông báo chỗ trống vào mức Could, không bắt buộc trong bản đầu. Vì vậy ba operation notification ở bảng trên là option mở rộng: mặc định không tạo subscription nếu user chưa chủ động bật; không gửi thông báo trong MVP. Payload mẫu tạo subscription là `{"room_id":14,"condition":"seats_available","threshold":5,"channel":"email"}`. Contract trên chưa khẳng định hệ thống gửi email/push ngay: kênh, ngưỡng chỗ trống, tần suất/cooldown, giờ yên lặng, quyền riêng tư email và xử lý khi occupancy `null` cần được xác nhận trước khi triển khai. Dự báo 1–2 giờ là một option khác, cần nguồn dữ liệu/mô hình và chỉ nên công bố sau khi được xác nhận; endpoint dự báo chưa được đề xuất ở đây.

## Đối chiếu yêu cầu SRS và mục cần bổ sung

| SRS | Đã phản ánh trong contract | Thiếu / cần thông báo bổ sung |
|---|---|---|
| FR-AUTH-01/02/04, BR-15 | OTP, tự tạo hồ sơ lần đầu, login/logout đã có khung operation | Tài khoản chỉ tự tạo sau lần xác minh OTP đầu tiên; OTP 6 số, chỉ lưu hash, hết hạn sau 5 phút, tối đa 5 lần nhập sai, gửi lại sau 60 giây, giới hạn email được phép và thông báo lỗi chung. Trả `429` khi vượt giới hạn; không tiết lộ email có tồn tại hay không. Các ngưỡng theo SRS 1.9, tạm thời chờ rà soát bảo mật. |
| FR-AUTH-05, BR-16 | Portal/SSO seam được đánh dấu chờ trường | Chỉ bật sau văn bản đồng ý, đầu mối kỹ thuật và giao thức/claim chính thức. |
| FR-SITE-01 | Đã thêm entity `campuses` và `rooms.campus_id` vào schema/migration; contract room mang cả `campus_id` và `campus_code` | Phòng dữ liệu cũ được để `campus_id = null` cho tới khi xác minh CS1/CS3. Phải ánh xạ dữ liệu phòng trước khi bật filter/tổng hợp theo campus; không tự suy ra campus từ `building`. |
| FR-OCC-01–06, BR-01/02 | Target latest occupancy có số người, chỗ trống, mức đông và trạng thái nguồn; CountEvent có event UUID | API runtime hiện chưa tính occupancy từ event/N0. Target cần phiên đếm, N0/audit, heartbeat, `available_seats`, mức đông và trạng thái tin cậy; không công bố số chính thức khi thiếu baseline. |
| FR-BOOK-02–06, BR-03/04/18/19 | Booking create/list/get/cancel có khung; request có `participant_count`, response có object `room` để tránh gọi bổ sung từng phòng | Quy tắc 30–120 phút, đặt trước tối đa 7 ngày, buffer 15 phút, 2–6 người, quota một lượt/người/ngày và cutoff hủy 30 phút đã ghi theo SRS 1.9; giá trị tạm nội bộ, cần thư viện xác nhận trước vận hành. |
| FR-CHK-01–03, BR-05–08 (Should) | Đã đề xuất endpoint phát token QR; token opaque, dùng một lần; đã mô tả cửa sổ check-in và xử lý no-show định kỳ | QR/no-show là Should, không phải điều kiện FR Must. Thời gian chờ mặc định 15 phút dùng `{{NO_SHOW_WAIT_MINUTES}}`, có thể cấu hình; quy tắc tạm chờ xác nhận thư viện. |
| FR-DASH-01/02, BR-10 (Should) | Dashboard summary sơ bộ | Mức độ chi tiết theo phòng/campus/khoảng thời gian, utilization, no-show, mẫu số và quyền tổng hợp cần chốt trước khi triển khai. |
| FR-ADMIN-01, BR-09/20 | Chưa có endpoint quản trị | Cần operation quản lý phòng/sức chứa/active state, gán vai trò, cấu hình chính sách và audit log; giới hạn cho tài khoản admin được cấp quyền. |
| FR-OPT-01 | Đã thêm option subscription thông báo | Could, ngoài MVP; channel/threshold/cooldown cần xác nhận. |

Đây là danh sách gap để chủ tài liệu SRS/nhóm nghiệp vụ nhận thông báo và quyết định có bổ sung API hay không. Không sửa nội dung SRS hoặc coi các giá trị tạm là chính sách thư viện đã duyệt.

### Auth

`POST /auth/register` chỉ yêu cầu gửi OTP, không tạo mật khẩu hoặc hồ sơ riêng → `202 {"status":"otp_sent"}`. Email phải thuộc danh sách cho phép; OTP 6 số được lưu dạng hash, dùng một lần, hết hạn sau 5 phút, tối đa 5 lần nhập sai và chỉ gửi lại sau 60 giây. Lần xác minh thành công đầu tiên tự tạo hồ sơ. `POST /auth/login` body `{"email":"sv@example.edu.vn","otp":"123456"}` → `200 {"access_token":"<opaque-token>","token_type":"bearer","expires_at":"2026-11-27T06:00:00Z","user":{"id":123,"email":"sv@example.edu.vn","display_name":"Nguyễn An","role":"student"}}`. `POST /auth/logout` → `204`; `GET /auth/me` trả cùng hồ sơ gồm `display_name`. Trả lỗi chung để không tiết lộ email tồn tại; trả `429` khi vượt giới hạn. Token opaque có thời hạn cấu hình bằng ACCESS_TOKEN_TTL_MINUTES (mặc định 60 phút); logout thu hồi phiên hiện tại. Chưa triển khai refresh token.

### Rooms

`GET /rooms?campus_code=CS1&limit=50&offset=0` → `200`
`{"items":[{"id":14,"code":"A101","name":"A101","room_type":"free_area","capacity":40,"campus_code":"CS1","building":"Cơ sở 1","is_active":true}],"limit":50,"offset":0,"total":1}`.
`GET /rooms/14` trả cùng một room object. Phòng chưa xác minh campus không
xuất hiện trong kết quả lọc; không suy ra campus từ `building`.

### Bookings

`POST /bookings` body `{"room_id":14,"starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z","participant_count":3}` → `201` booking gồm `participant_count` và object `room`. `GET /bookings?from=...&to=...&limit=50&offset=0` → trang booking có nested `room` để giao diện không cần gọi từng phòng. Kiểm tra phòng chuyên đề, thời lượng 30–120 phút, đặt trước tối đa 7 ngày, 2–6 người, tối đa một lượt/người/ngày và cách lượt liền kề 15 phút; xung đột trả `409 booking_conflict`. Các giới hạn nhóm/ngày và buffer là giá trị tạm, phải được thư viện xác nhận. SRS chưa quy định giờ hoạt động; contract không tự áp một khung giờ và đánh dấu chính sách giờ mở cửa là cần xác nhận. Trạng thái lưu: `booked`, `checked_in`, `completed`, `cancelled`, `no_show`.

### Check-in

`POST /bookings/{booking_id}/check-in-token` chỉ cấp cho chủ booking đang `booked`. Sinh 32 byte ngẫu nhiên bằng CSPRNG, mã hóa Base64URL và thêm tiền tố phiên bản `urn:seatsense:check-in:v1:`. QR chứa đúng chuỗi `qr_token`, không nhúng email/tên/số sinh viên. Backend chỉ lưu SHA-256 của token, gắn token với booking và thời hạn; phát token mới vô hiệu token chưa dùng trước đó. Đây là định dạng đề xuất cho FR-CHK (Should). Token chỉ hợp lệ từ `start_time` tới trước `start_time + {{NO_SHOW_WAIT_MINUTES}}`; dùng thành công một lần. `POST /check-in` body `{"booking_id":"bkg_456","qr_token":"urn:seatsense:check-in:v1:<base64url-256-bit-token>"}` → `200 {"booking_id":"bkg_456","status":"checked_in","checked_in_at":"2026-11-12T02:04:00Z"}`. Mã sai/hết hạn, booking hủy/no-show hoặc check-in lặp bị từ chối (`401`/`404`/`409` theo trường hợp).

Tác vụ nền chạy định kỳ chọn booking còn `booked`, chưa check-in/chưa hủy và đã qua `start_time + {{NO_SHOW_WAIT_MINUTES}}`; cập nhật `no_show` một lần, ghi `no_show_at` và loại booking khỏi tập giữ chỗ để giải phóng phần giờ còn lại. Booking đã check-in không chuyển no-show. Mặc định tạm là 15 phút theo BR-05–08; cấu hình và lịch chạy phải được xác nhận với thư viện trước vận hành thật.

### Dashboard

`GET /dashboard/summary?from=...&to=...` → `200` `{"occupancy":{"current":12,"capacity":40},"bookings":{"total":8,"checked_in":5,"no_show":1},"generated_at":"2026-11-11T08:00:00Z"}`. Định nghĩa metrics, quyền theo campus và phạm vi thời gian chưa chốt.

### CV event đề xuất

`POST /cv/events` với `X-API-Key: <service-key>` nhận `event_id`, `session_id`,
numeric `room_id`, `device_id`, `direction` (`in`/`out`), `event_time` UTC và
`device_status`. Sự kiện mới trả `201`; cùng ID/cùng nội dung trả receipt cũ
với `201 duplicate:true`; cùng ID/khác nội dung trả `409 event_id_conflict`.
Không gửi track ID, ảnh hoặc video. Heartbeat định kỳ dùng
`PUT /cv/devices/{device_id}/status`; hai endpoint này và persistence là target
Sprint 4, chưa được xác nhận trong runtime.

## Quy tắc occupancy/rooms tái sử dụng từ SEAT-39

- `available_seats = max(0, capacity - estimated_occupancy)` khi N0/occupancy và sức chứa đã xác nhận; nếu thiếu dữ liệu thì trả `null`, không đổi `null` thành `0`.
- `occupancy_level`: `low` khi tỷ lệ sử dụng ≤50%, `medium` khi >50% và <80%, `high` khi ≥80%. Ngưỡng này cần được xác nhận với nghiệp vụ trước triển khai.
- Freshness dựa trên trạng thái nguồn và ngưỡng cấu hình SEAT-57; không hard-code 30 giây. Client polling occupancy 3–5 giây khi trang đang hoạt động, có thể backoff khi lỗi.
- Danh sách phòng mục tiêu lọc bằng `GET /api/v1/rooms?campus_code=CS1|CS3`; occupancy lấy theo phòng từ `GET /api/v1/occupancy/rooms/{room_id}/latest`. Phòng hiện có chưa được gán cơ sở khi thiếu dữ liệu xác nhận; không bật lọc chính thức trước khi mapping hoàn tất.
- Lịch sử occupancy lấy theo phòng và khoảng `start_time`–`end_time`, giới hạn/phân trang theo quy ước chung. Quyền student xem lịch sử chưa chốt.

## Đối chiếu FastAPI OpenAPI sinh từ mã

FastAPI sinh schema tại `/openapi.json` và giao diện `/docs`. Đã nạp `backend/main.py` bằng môi trường `.venv` của repo và gọi `app.openapi()` thành công; OpenAPI 3.1.0 hiện có 6 operation: `GET /health`, `GET /health/db`, `GET /api/v1/health`, `GET /api/v1/occupancy/current`, `GET /api/v1/occupancy/rooms/{room_id}/latest`, `POST /api/v1/cv/count-records`. Router rooms, reservations, check-in và dashboard hiện rỗng; auth chưa được đăng ký.

Đối chiếu schema runtime: occupancy current chỉ trả `current_count`, `updated_at`, `location` và không có query; contract mục tiêu per-room/campus chưa implement. Occupancy latest có `room_id` path và phản hồi `200/404/422/503`. CV count-records có body `CVCountBatch`, response `200/400/409/422/503`; handler chưa kiểm tra `X-API-Key`, nên phần API-key trong contract chưa được thực thi. Các endpoint booking/auth/QR/dashboard là contract đề xuất và chưa xuất hiện trong OpenAPI.

CV service có health riêng ở service CV. Route `/api/v1/cv/count-records` đang chạy theo payload SEAT-34. Sau khi bổ sung handler, cần so sánh lại method/path, query/path params, schema JSON, status code và error response của từng route đề xuất với `/openapi.json`; lưu snapshot hoặc đưa kiểm tra lệch contract vào CI.

Lưu ý về scope CV: SEAT-34 chốt nhận CountResult batch với idempotency key `(session_id, frame_index)`; cùng key/cùng payload là duplicate, cùng key/khác payload trả `409 cv_record_conflict`. `CrossingEvent` và `event_id` là đề xuất endpoint riêng được yêu cầu bổ sung trong contract này, chưa thuộc payload batch SEAT-34 và chưa có persistence. Với endpoint riêng, cùng `event_id`/cùng payload trả receipt duplicate, payload khác trả `409 event_id_conflict`. API key `X-API-Key` cũng là yêu cầu bảo vệ contract, chưa được triển khai.

## Việc cần chốt / sửa

1. Hoàn thiện occupancy per-room/campus; triển khai auth, rooms/history, bookings, check-in, dashboard và CV event; đối chiếu từng route với OpenAPI sinh ra.
2. Chốt role matrix và scope xem dashboard/booking; thêm auth middleware và API key CV.
3. Chốt token/OTP và Portal SSO dựa trên thông tin trường; không chặn MVP OTP.
4. Đồng bộ schema/router legacy `reservations` sang target `bookings`; xác nhận pagination, timezone và chính sách xung đột trước khi triển khai.
5. Xác nhận QR/no-show mặc định 15 phút với thư viện; FR-CHK và dashboard thuộc Should. Giờ hoạt động chưa được SRS quy định, cần quyết định nghiệp vụ trước khi thêm validation.
6. Đã sinh OpenAPI runtime 3.1.0 từ source; lưu snapshot hoặc thêm đối chiếu CI sau khi các route còn thiếu được triển khai.

---

## Phụ lục lịch sử: Contract CV và occupancy

> Các đoạn lịch sử bên dưới lưu đặc tả SEAT-18/19, có thể chứa path, mã lỗi
> hoặc ngưỡng cũ. Hợp đồng mục tiêu hiện hành nằm ở Endpoint inventory và các
> mục UC-01/UC-06 phía trên; không dùng nội dung lịch sử thay cho target Sprint 4.
> Các câu ghi nhận nhóm đã duyệt/thống nhất trong bản cũ không được xem là bằng
> chứng xác nhận Jira hoặc biên bản họp.

## 1. Mục đích và trạng thái

Đây là bản lưu nội dung hợp đồng CV/occupancy SEAT-18. Các nội dung dưới đây mô tả lịch sử và không xác nhận phê duyệt hiện hành; target mới nhất được mô tả trong các mục chính của tài liệu.

Bộ tạo dữ liệu CV schema 1.0 hiện ghi bản ghi JSONL cục bộ. Backend đã có route nhận CountResult batch theo SEAT-18/34; bộ gửi/thử lại từ CV vẫn đang chờ tích hợp. Route chưa xác thực API key, cần hoàn tất trước khi mở kết nối ngoài môi trường tin cậy. Các route kiểm thử video và webcam cục bộ của CV được mô tả ở mục 12, không phải endpoint nghiệp vụ của Backend. CountResult batch vẫn tách biệt với API occupancy trả dữ liệu cho Frontend.

### Bản lưu đặc tả SEAT-18 (lịch sử)

> **Nhiệm vụ:** SEAT-18 – Hợp đồng API với mô-đun CV
> **Trạng thái:** Nhóm máy chủ, CV và giao diện đã thống nhất hợp đồng. Các tuyến API phía máy chủ của SEAT-19 đã được triển khai. Phần gửi dữ liệu từ CV lên máy chủ còn chờ tích hợp.
> **Nguồn:** Hợp đồng dữ liệu CV v1.0 và thiết kế lưu trữ PostgreSQL của SEAT-24.
> **Cập nhật lần cuối:** 2026-10-30

## API tổng hợp số người cho bảng tổng quan

- `GET /api/v1/occupancy/current` trả về tổng số người dựa trên bản ghi mới nhất
  của từng phòng đang hoạt động, gồm `current_count`, `updated_at`, `location`
  và `data_status` (SEAT-57). Số người và thời điểm cập nhật là `null` khi chưa có bản ghi.
- `data_status` nhận giá trị: `fresh` (dữ liệu mới), `stale` (vượt ngưỡng
  `occupancy_stale_seconds`, mặc định 30s), `disconnected` (vượt ngưỡng
  `device_offline_seconds`, mặc định 90s, hoặc `device_status` là `offline|error`),
  hoặc `null` (chưa có dữ liệu). Ngưỡng được cấu hình qua biến môi trường
  `OCCUPANCY_STALE_SECONDS` và `DEVICE_OFFLINE_SECONDS`.
- API tổng hợp tất cả phòng đang hoạt động vì mô hình phòng hiện tại
  chưa có mã cơ sở. Để lọc theo cơ sở, cần bổ sung ánh xạ này
  vào mô hình dữ liệu.

## 1. Mục đích và trạng thái

Đây là bản lưu đặc tả cũ về CountResult và occupancy. Các câu lịch sử về phê duyệt giao diện/CV không được coi là xác nhận hiện hành; ngưỡng 30 giây và polling 5 giây bên dưới không phải target Sprint 4.

Mô-đun CV v1.0 hiện ghi bản ghi JSONL cục bộ. Tài liệu xác định giao tiếp HTTP cho các tuyến máy chủ của SEAT-19. Việc tích hợp bộ gửi và cơ chế gửi lại của CV còn chờ thực hiện. Mục 12 mô tả các tuyến thử video và webcam cục bộ của CV. Các tuyến này tách riêng với API nghiệp vụ của máy chủ. Định dạng yêu cầu về số người hiện có của SEAT-19 tách riêng với bản ghi thô theo từng khung hình.

## 2. Quy ước chung

- Đường dẫn gốc của API là `/api/v1`.
- Nội dung yêu cầu và phản hồi dùng JSON UTF-8 với tên trường theo kiểu `snake_case`.
- Biểu diễn số nguyên bằng giá trị số trong JSON. Phân biệt giá trị bị thiếu với `0`.
- Dấu thời gian dùng chuỗi ngày giờ ISO 8601 có múi giờ. Máy chủ chuẩn hóa thời gian trả về sang UTC với hậu tố `Z`.
- `timestamp_ms` là độ lệch tương đối trên dòng thời gian của nguồn hoặc phiên. Trường này dùng mốc của nguồn hoặc phiên thay cho mốc Unix.
- Dữ liệu CV v1.0 bị từ chối nếu có trường chưa định nghĩa. Cần thông báo nếu đổi tên trường.
- `CountResult` là bản ghi theo khung hình. `CrossingEvent` là sự kiện riêng và tuyến nhận bản ghi số đếm v1 bên dưới từ chối kiểu này.

## 3. Các trường dữ liệu CV v1.0

### 3.1 Bản ghi CountResult

| Trường | Kiểu | Bắt buộc | Ý nghĩa và quy tắc kiểm tra |
|---|---|---:|---|
| `schema_version` | Chuỗi | Không, mặc định `"1.0"` | Phiên bản hợp đồng CV. Máy chủ hỗ trợ `1.0`. |
| `session_id` | Chuỗi UUID | Có | Mã định danh của một phiên xử lý CV. |
| `camera_id` | Chuỗi | Có | Mã camera, dài 1–100 ký tự và không được để trắng. |
| `room_id` | Chuỗi hoặc `null` | Không | Mã phòng do CV gửi. Khi có giá trị, mã dài 1–100 ký tự và không được để trắng. Máy chủ giữ mã dưới trường `room_code` và chỉ liên kết với `rooms.id` khi trùng chính xác `rooms.code`. |
| `source_type` | Chuỗi | Không, mặc định `"video"` | Nhận `"video"` hoặc `"webcam"`. Tuyến GET lấy số người hiện tại chỉ dùng bản ghi webcam. |
| `frame_index` | Số nguyên | Có | Số thứ tự khung hình, bắt đầu từ 0. |
| `timestamp_ms` | Số | Có | Độ lệch hữu hạn và không âm trong video hoặc phiên. |
| `recorded_at` | Chuỗi ngày giờ | Có | Thời điểm CV xử lý bản ghi, bắt buộc có múi giờ. Thời điểm này có thể khác thời điểm camera ghi hình. |
| `people_count` | Số nguyên | Có | Số người phát hiện trong khung hình, kể cả người chưa có mã theo dõi đã xác nhận. Giá trị không âm và chỉ phản ánh vùng quan sát. |
| `tracked_count` | Số nguyên | Có | Số người phát hiện có mã theo dõi đã xác nhận. Điều kiện `0 <= tracked_count <= people_count`. |
| `line_enabled` | Luận lý | Có | Cho biết chế độ đếm qua đường ảo đã bật hay chưa. |
| `in_count` | Số nguyên hoặc `null` | Không | Số lượt vào cộng dồn trong phiên. Bắt buộc khi `line_enabled` là `true`, nhận `null` khi là `false`. |
| `out_count` | Số nguyên hoặc `null` | Không | Số lượt ra cộng dồn trong phiên. Bắt buộc khi `line_enabled` là `true`, nhận `null` khi là `false`. |
| `initial_occupancy` | Số nguyên hoặc `null` | Không | Số người ban đầu đã biết, có giá trị không âm. |
| `estimated_occupancy` | Số nguyên hoặc `null` | Không | Tính theo `max(0, initial_occupancy + in_count - out_count)` khi đủ dữ liệu. Nếu thiếu dữ liệu thì trả `null`. |
| `occupancy_underflow` | Luận lý | Không, mặc định `false` | Nhận `true` nếu số người ước tính trước khi áp dụng ngưỡng dưới 0 có giá trị âm. |

`people_count` cho biết số người trong vùng camera quan sát được. `estimated_occupancy` ước tính số người trong phòng, phụ thuộc vào số người ban đầu và khả năng camera bao quát các lối ra vào. `null` nghĩa là chưa biết. `0` là giá trị ước tính hợp lệ. Số lượt vào/ra đã được cộng dồn trong từng phiên, vì vậy không cộng tiếp qua các khung hình, phiên hoặc camera.

### 3.2 Ví dụ CountResult

```json
{
  "schema_version": "1.0",
  "session_id": "6f228318-ea31-46b3-a1a7-c562288ea97e",
  "camera_id": "cam-01",
  "room_id": "A101",
  "source_type": "webcam",
  "frame_index": 100,
  "timestamp_ms": 10000.0,
  "recorded_at": "2026-10-30T00:00:00Z",
  "people_count": 3,
  "tracked_count": 2,
  "line_enabled": true,
  "in_count": 4,
  "out_count": 1,
  "initial_occupancy": 0,
  "estimated_occupancy": 3,
  "occupancy_underflow": false
}
```

### 3.3 Sự kiện CrossingEvent

CV v1.0 cũng định nghĩa `CrossingEvent` với các trường `event_id`, `session_id`, `camera_id`, `room_id` (không bắt buộc), `frame_index`, `timestamp_ms`, `recorded_at`, `track_id`, `direction` (`IN` hoặc `OUT`) và `confidence` (`0..1`). Mỗi bản ghi mô tả một lượt cắt đường ảo riêng lẻ.

**Phạm vi tương thích:** `POST /cv/count-records` vẫn nhận `CountResult`
batch theo SEAT-34. Sprint 4 bổ sung route event riêng; khi ánh xạ từ
`CrossingEvent`, không gửi `track_id`, `confidence`, ảnh hoặc bounding box.

## 4. CV → Máy chủ: lưu bản ghi số đếm

### 4.1 Tuyến API

```http
POST /api/v1/cv/count-records
Content-Type: application/json
```

Mỗi yêu cầu chứa một lô từ 1 đến 1.000 bản ghi `CountResult`. Máy chủ kiểm tra toàn bộ lô và lưu trong một giao dịch cơ sở dữ liệu. Giao dịch được hoàn tác nếu có bản ghi không hợp lệ hoặc xung đột.

```json
{
  "records": [
    {
      "schema_version": "1.0",
      "session_id": "6f228318-ea31-46b3-a1a7-c562288ea97e",
      "camera_id": "cam-01",
      "room_id": "A101",
      "source_type": "webcam",
      "frame_index": 100,
      "timestamp_ms": 10000.0,
      "recorded_at": "2026-10-30T00:00:00Z",
      "people_count": 3,
      "tracked_count": 2,
      "line_enabled": true,
      "in_count": 4,
      "out_count": 1,
      "initial_occupancy": 0,
      "estimated_occupancy": 3,
      "occupancy_underflow": false
    }
  ]
}
```

### 4.2 Ánh xạ và chống ghi trùng

- Mỗi khung hình được lưu thành một hàng trong `cv_count_records`, tách riêng với `occupancy_records`. Không ánh xạ `people_count` sang `occupied_count`.
- Giữ chuỗi `room_id` do CV gửi trong `room_code`. Chỉ gán `room_id` dạng số theo `rooms.id` khi `room_code` trùng chính xác `rooms.code`. Với mã chưa biết hoặc `null`, giữ mã gốc và để liên kết phòng là `null`. Không ép mã sang số hoặc tự tạo phòng.
- Khóa chống ghi trùng là `(session_id, frame_index)`. Cùng khóa và cùng nội dung thì trả về bản ghi đã lưu. Cùng khóa nhưng khác nội dung CV thì trả về `409 cv_record_conflict`.
- Khi gửi lại, dùng nguyên khóa phiên và khung hình. Ánh xạ phòng là thông tin bổ sung. Việc gửi lại không ghi đè bản ghi đã lưu.

### 4.3 Gửi dữ liệu và phản hồi

- CV gom các bản ghi cần lưu lịch sử thành lô. Gửi khi đủ 100 bản ghi hoặc sau 1 giây, tùy điều kiện nào đến trước. Mỗi lô tối đa 1.000 bản ghi. Gửi hết phần còn lại khi kết thúc phiên.
- Khi kết nối hết thời gian chờ hoặc nhận `503`, gửi lại tối đa ba lần, chờ lần lượt 1, 2 và 4 giây và giữ nguyên khóa. Không gửi lại khi nhận `400`, `409` hoặc `422`. Giữ bản ghi chưa được xác nhận ở máy cục bộ để gửi lại sau.
- Máy chủ trả `200 OK` khi chấp nhận lô, kể cả khi có bản ghi gửi trùng hợp lệ. Bản ghi trong phản hồi giữ nguyên thứ tự yêu cầu.

```json
{
  "status": "accepted",
  "created_count": 1,
  "duplicate_count": 0,
  "records": [
    {
      "record_id": 8123,
      "session_id": "6f228318-ea31-46b3-a1a7-c562288ea97e",
      "frame_index": 100,
      "room_code": "A101",
      "room_id": 14,
      "received_at": "2026-10-30T00:00:01Z",
      "duplicate": false
    }
  ]
}
```

Nếu mã phòng CV bị thiếu hoặc chưa ánh xạ, phản hồi có `room_id: null`. Lần gửi lại với nội dung giống hệt nhận `duplicate: true` và giữ nguyên `received_at`.

### 4.4 Phản hồi lỗi

Máy chủ dùng cấu trúc sau để trả lỗi.

```json
{
  "error": {
    "code": "validation_error",
    "message": "Một hoặc nhiều bản ghi CV không hợp lệ",
    "details": [
      { "field": "records[0].tracked_count", "issue": "không được vượt quá people_count" }
    ]
  }
}
```

| Mã HTTP | Mã lỗi | Ý nghĩa và cách CV xử lý |
|---|---|---|
| `400` | `malformed_json` | Nội dung yêu cầu không phải JSON hợp lệ. Sửa trước khi gửi lại. |
| `409` | `cv_record_conflict` | Cùng khóa phiên và khung hình nhưng khác nội dung. Dừng gửi lại và kiểm tra. |
| `422` | `validation_error` | Thiếu trường hoặc giá trị không hợp lệ. Sửa bản ghi trước khi gửi lại. |
| `503` | `database_unavailable` | Máy chủ hoặc cơ sở dữ liệu tạm thời gặp lỗi. Gửi lại với khóa cũ. |

Máy chủ chấp nhận mã phòng chưa biết, lưu mã gốc và để liên kết phòng là `null`. API dùng trong mạng nội bộ giữa các dịch vụ. Nhóm máy chủ và bảo mật cần rà soát cách xác thực cho môi trường vận hành trước khi mở truy cập từ bên ngoài.

## 5. Máy chủ → Giao diện: số người mới nhất theo phòng

### 5.1 Tuyến API

```http
GET /api/v1/occupancy/rooms/{room_id}/latest
```

`room_id` trong URL là mã số `rooms.id` do API phòng của máy chủ trả về. Tuyến này chỉ đọc bản ghi `webcam` đã ánh xạ mới nhất của phòng, không cộng số đếm từ nhiều camera. Bản ghi `video` dùng cho lịch sử hoặc thử nghiệm, không cập nhật số người theo thời gian thực.

### 5.2 Phản hồi khi có bản ghi

```json
{
  "room_id": 14,
  "room_code": "A101",
  "camera_id": "cam-01",
  "source_type": "webcam",
  "people_count": 3,
  "tracked_count": 2,
  "estimated_occupancy": 3,
  "occupancy_underflow": false,
  "recorded_at": "2026-10-30T00:00:00Z",
  "received_at": "2026-10-30T00:00:01Z",
  "is_stale": false
}
```

`is_stale` là `true` khi đã hơn 30 giây kể từ `received_at`. Nếu `estimated_occupancy` là `null`, giao diện hiển thị trạng thái chưa biết (`unknown`). Nếu giá trị bằng 0, giao diện hiển thị `0`. Chỉ hiển thị `people_count` với nhãn nêu rõ đây là số người trong vùng camera quan sát được.

### 5.3 Phản hồi khi thiếu dữ liệu hoặc có lỗi

**Runtime hiện được đối chiếu:** phòng tồn tại nhưng chưa có bản ghi webcam trả
`404 occupancy_not_found`; mã phòng không tồn tại trả `404 room_not_found`.
**Target SEAT-56:** giữ 404 cho phòng không tồn tại; trả `503 occupancy_unavailable`
khi occupancy/N0 chưa khởi tạo (frontend ánh xạ mã này thành trạng thái
“chưa đủ dữ liệu”, không hiển thị số 0); lỗi DB/dịch vụ trả
`503 service_unavailable`. Target chưa được triển khai hoặc xác nhận bằng
OpenAPI runtime.

```json
{
  "error": {
    "code": "occupancy_unavailable",
    "message": "Chưa đủ dữ liệu mật độ cho phòng này"
  }
}
```

Nhóm giao diện xác nhận chu kỳ truy vấn 5 giây và ngưỡng lỗi thời 30 giây. Giá trị `null` biểu thị chưa biết, còn số 0 là số đếm hợp lệ.

## 6. Quy tắc kiểm tra dữ liệu

- `schema_version` phải thuộc phiên bản được hỗ trợ (`1.0`).
- `session_id` phải là UUID. Các mã định danh không được để trắng.
- `frame_index` và các số đếm phải không âm và nằm trong phạm vi số nguyên đã quy định. `timestamp_ms` phải hữu hạn và không âm.
- `tracked_count` không được lớn hơn `people_count`.
- `recorded_at` phải có thông tin múi giờ. Máy chủ lưu và trả thời gian theo UTC.
- Khi `line_enabled` là `true`, bắt buộc có `in_count` và `out_count`. Khi là `false`, hai trường này và `initial_occupancy` phải là `null`.
- Khi đã biết `initial_occupancy`, `estimated_occupancy` và `occupancy_underflow` phải nhất quán với phép tính `max(0, initial_occupancy + in_count - out_count)`.
- Từ chối các trường chưa định nghĩa. Không chuyển số đếm bị thiếu thành 0.

## 7. Giới hạn và độ mới của dữ liệu

- `people_count` chỉ phản ánh số người quan sát được trong một khung hình.
- `estimated_occupancy` phụ thuộc vào số người ban đầu chính xác và camera bao quát các lối ra vào liên quan.
- Bộ đếm CV được đặt lại mỗi phiên. Trong v1, giao diện trực tiếp chỉ dùng một nguồn camera đang hoạt động cho mỗi phòng. Tổng hợp nhiều camera nằm ngoài phạm vi.
- `recorded_at` là thời điểm CV xử lý. Máy chủ gán `received_at` khi lưu bản ghi lần đầu và dùng giá trị này để kiểm tra độ mới. `timestamp_ms` vẫn là độ lệch tương đối trong nguồn hoặc phiên.
- Kiểm thử quy tắc xử lý chưa đủ để xác nhận độ chính xác thực tế. Vị trí camera, tình trạng che khuất, việc mất dấu đối tượng và cấu hình đường ảo có thể ảnh hưởng kết quả.

## 8. Các tình huống cần kiểm thử tích hợp

| Tình huống | Kết quả mong đợi |
|---|---|
| Lô hợp lệ có một bản ghi | Lưu bản ghi và trả xác nhận tiếp nhận. |
| Lô hợp lệ có nhiều bản ghi | Lưu toàn bộ lô trong một giao dịch và trả xác nhận theo thứ tự yêu cầu. |
| Gửi lại cùng khóa phiên và khung hình với nội dung giống hệt | Trả bản ghi cũ với `duplicate: true` mà không tạo thêm hàng. |
| Cùng khóa, khác nội dung | Trả `409 cv_record_conflict` và hoàn tác cả lô. |
| Mã phòng chưa biết hoặc `null` | Chấp nhận, giữ mã gốc và trả `room_id: null`. |
| Số người quan sát được hoặc ước tính bằng 0 | Chấp nhận `0` là giá trị hợp lệ. |
| Số người ước tính là `null` | Giữ `null` và hiển thị trạng thái chưa biết trên giao diện. |
| Thiếu trường, sai kiểu hoặc sai công thức tính | Trả `422 validation_error` kèm đường dẫn tới trường lỗi. |
| `recorded_at` thiếu múi giờ | Từ chối với `422 validation_error`. |
| Máy chủ hết thời gian chờ hoặc trả `503` | CV gửi lại bằng cùng khóa phiên và khung hình. |
| GET phòng không tồn tại | Trả `404 room_not_found`. |
| GET phòng chưa có occupancy/N0 hợp lệ (target SEAT-56) | Trả `503 occupancy_unavailable`; UI hiển thị chưa đủ dữ liệu, không hiển thị số 0. |
| GET với số người ước tính hợp lệ bằng 0 | Trả `200` với `estimated_occupancy: 0`. |
| GET với bản ghi cũ hơn 30 giây | Trả bản ghi với `is_stale: true`. |

## 9. Trạng thái triển khai

| Hạng mục | Trạng thái |
|---|---|
| Trường và ý nghĩa của `CountResult` trong CV v1.0 | Nhóm CV cung cấp, đã ghi trong tài liệu này. |
| Cấu trúc lưu trữ máy chủ và ánh xạ mã phòng | Đã thống nhất dựa trên thiết kế lưu trữ SEAT-24. |
| Tuyến HTTP nhận lô dữ liệu CV và phản hồi | Đã triển khai trong API máy chủ của SEAT-19. |
| Bộ gửi CV, hàng đợi gửi lại và cấu hình URL máy chủ | Chưa có trong phần CV đã đưa vào Git ở SEAT-17. Triển khai là công việc tiếp theo. Các phiên bản CV đã ghi vào Git được giữ nguyên. |
| Phản hồi dữ liệu mới nhất và xử lý dữ liệu cũ hoặc thiếu | Nhóm giao diện đã xác nhận. API máy chủ của SEAT-19 đã triển khai. |
| Tiếp nhận `CrossingEvent` qua HTTP | Ngoài phạm vi v1 đã thống nhất. |
| Kiểm thử tích hợp giữa CV, máy chủ và giao diện | Chờ triển khai tuyến API. Tài liệu đã có ví dụ yêu cầu và phản hồi phục vụ việc kiểm thử. |

## 10. Nội dung đã thống nhất

| Quyết định | Hợp đồng đã thống nhất | Trạng thái |
|---|---|---|
| Số người hiển thị cho phòng | Dùng `estimated_occupancy` và giữ riêng `people_count`. | Nhóm CV và giao diện đã xác nhận |
| Ánh xạ phòng | `room_id` do CV gửi là mã phòng. So khớp chính xác với `rooms.code`. Nếu chưa ánh xạ, giữ mã và để khóa ngoại là `null`. | Nhóm CV đồng ý theo hợp đồng của máy chủ |
| Tổng hợp theo camera và phiên | V1 dùng một camera hoạt động cho mỗi phòng. Không cộng gộp giữa các phiên hoặc camera. | Thuộc phạm vi v1 của máy chủ, nhóm CV tuân theo hợp đồng này |
| Gửi bản ghi số đếm | Mỗi lô tối đa 1.000 bản ghi. Gửi khi đủ 100 bản ghi hoặc sau 1 giây. Gửi lại với cùng `(session_id, frame_index)`. | Nhóm CV đồng ý theo hợp đồng, bộ gửi chưa được triển khai |
| `CrossingEvent` | Không gửi hoặc lưu qua tuyến số đếm v1. Bổ sung API riêng trong nhiệm vụ sau nếu cần. | Ngoài phạm vi v1 |
| Phản hồi cho giao diện | Mã phòng dạng số từ máy chủ, `estimated_occupancy`, thông tin bổ sung, `received_at` và `is_stale`. | Nhóm giao diện đã xác nhận |
| Thiếu dữ liệu và độ mới | Runtime cũ trả 404 khi thiếu bản ghi; target SEAT-56 trả `503 occupancy_unavailable` khi thiếu occupancy/N0. Freshness dùng trạng thái nguồn/ngưỡng cấu hình SEAT-57. | Cần xác nhận OpenAPI và giao diện |
| Xác thực dịch vụ | Môi trường phát triển dùng mạng dịch vụ riêng. Cần chốt cách xác thực cho môi trường vận hành trước khi mở truy cập từ bên ngoài. | Nhóm máy chủ và bảo mật chưa chốt phương án triển khai |

Người phụ trách máy chủ ghi nhận xác nhận từ nhóm CV và giao diện vào ngày 2026-10-30. Cập nhật hợp đồng nếu một trong hai nhóm yêu cầu thay đổi. Cách xác thực cho môi trường vận hành cần được chốt riêng trước khi mở truy cập từ bên ngoài.

## 11. Danh sách kiểm tra nghiệm thu SEAT-18

- [x] Bản thảo nêu các trường dữ liệu CV, kiểu, ý nghĩa và quy tắc kiểm tra.
- [x] Bản thảo có ví dụ yêu cầu và phản hồi cho luồng CV → máy chủ và máy chủ → giao diện.
- [x] Bản thảo đề xuất cách xử lý dữ liệu thiếu, sai hoặc trùng, dấu thời gian và lỗi kết nối.
- [x] Nhóm CV đồng ý theo hợp đồng của máy chủ. Các tệp CV đã đưa vào Git được giữ nguyên.
- [x] Nhóm giao diện xác nhận phản hồi GET, cách xử lý giá trị `null`, số 0, dữ liệu thiếu hoặc lỗi thời và chu kỳ truy vấn.
- [x] Có ví dụ JSON phục vụ kiểm thử tích hợp sau này.

Tài liệu cung cấp các tuyến máy chủ và ví dụ để tích hợp. Kiểm thử toàn luồng với bộ gửi CV chạy thực tế và giao diện là công việc tiếp theo, nằm ngoài tiêu chí phê duyệt tài liệu này.

## 12. API thử nghiệm CV cục bộ của SEAT-17

Các tuyến dưới đây thuộc dịch vụ thử nghiệm CV cục bộ. Chúng tách riêng với API nghiệp vụ máy chủ và không triển khai tuyến tiếp nhận ở mục 4.

### Giao diện thử nghiệm CV cục bộ

- `GET /` trả giao diện thử nghiệm HTML cục bộ. `/static/` chứa tài nguyên của giao diện.
- `GET /api/config` trả thông tin mô hình có sẵn hay không và thiết bị đã chọn, không kèm đường dẫn cục bộ.
- `POST /api/jobs` nhận tệp video ở trường `file` và chuỗi JSON `options` qua yêu cầu `multipart`. Trả `202` kèm mã tác vụ. Giới hạn 200 MB và một tác vụ tại một thời điểm. Trả `409` khi đang bận, `503` nếu thiếu mô hình, `415` nếu phần mở rộng không được hỗ trợ, hoặc `422` nếu tùy chọn không hợp lệ.
- `GET /api/jobs/{id}` trả trạng thái, bản ghi mới nhất, ảnh JPEG tương ứng ở dạng Base64, sự kiện gần đây, bản tóm tắt và lỗi đã lọc. Các trạng thái gồm đang tải lên (`uploading`), đang nạp (`loading`), đang xử lý (`processing`), đã hoàn tất (`completed`), đã hủy (`cancelled`) và thất bại (`failed`).
- `POST /api/jobs/{id}/stop` yêu cầu tác vụ dừng sau khi xử lý xong khung hình hiện tại.
- `GET /api/jobs/{id}/preview` trả ảnh JPEG mới nhất. Trả `404` nếu chưa có khung hình đầu tiên.
- `GET /api/jobs/{id}/files/{kind}` hỗ trợ `csv`, `jsonl`, `debug`, `events` và `summary`. Chỉ tải được khi tác vụ đã hoàn tất hoặc đã hủy. Các trạng thái khác trả `409`. Mã tác vụ hoặc loại tệp không tồn tại trả `404`.

Thông tin tác vụ nằm trong bộ nhớ và mất khi khởi động lại. Tệp kết quả được giữ cục bộ cho đến khi xóa thủ công.

### Thử webcam qua trình duyệt

- `POST /api/webcam` nhận tùy chọn JSON giống khi thử video, giữ một suất xử lý suy luận và bắt đầu phiên theo dõi mới. Trả `202` kèm mã tác vụ.
- `POST /api/webcam/{id}/frame` nhận dữ liệu JPEG tối đa 2 MB, với cạnh dài nhất sau giải mã tối đa 1.920 px. Trả bản ghi số đếm có `source_type: webcam` và các khung bao phục vụ gỡ lỗi. Mỗi lần xử lý một khung hình. Trả `409` khi đang bận hoặc đã dừng, hoặc `422` nếu khung hình không hợp lệ.
- Việc dừng và xuất kết quả dùng cùng các tuyến tác vụ. Dấu thời gian của nguồn webcam được tính theo đồng hồ đơn điệu kể từ lúc bắt đầu phiên. `recorded_at` ghi thời điểm xử lý theo UTC.
- Trình duyệt chỉ truy cập camera sau khi người dùng bấm nút `Start Test` và cấp quyền. Giao diện không ghi âm hoặc ghi video webcam. Hãy dừng tác vụ trước khi rời trang. Nếu ứng dụng phía trình duyệt gặp sự cố, có thể cần khởi động lại dịch vụ cục bộ để giải phóng phiên còn treo.

---

## 13. UC-01: Xem chỗ trống – Luồng API mục tiêu

**Nhiệm vụ:** SEAT-39 – Sơ đồ tuần tự UC-01 và đặc tả API số người và danh sách phòng
**Trạng thái:** Target Sprint 4; endpoint per-room chưa có response target được triển khai. Runtime legacy được ghi riêng ở endpoint inventory.
>
> **Cập nhật lần cuối:** 2026-11-11

### 13.1 Sơ đồ tuần tự

Luồng UC-01: Sinh viên xem tình trạng khu tự học tự do

```mermaid
sequenceDiagram
    participant User as Sinh viên
    participant Frontend as Giao diện
    participant API as OccupancyRouter
    participant Service as OccupancyService
    participant Repo as OccupancyRepository
    participant DB as PostgreSQL

    User->>Frontend: Mở trang chủ / chọn cơ sở và phòng
    Frontend->>API: GET /api/v1/rooms?campus_code=CS1
    API->>DB: Lấy danh sách phòng đã xác minh theo cơ sở
    DB-->>API: Danh sách phòng
    API-->>Frontend: HTTP 200 + danh sách phòng
    Frontend->>API: GET /api/v1/occupancy/rooms/{room_id}/latest
    API->>DB: Đọc N0, sự kiện IN/OUT, sức chứa và trạng thái nguồn
    DB-->>API: Occupancy hoặc thiếu dữ liệu

    alt N0 và dữ liệu occupancy hợp lệ
        API-->>Frontend: HTTP 200 + occupancy, available_seats, density_level
        Frontend->>Frontend: Hiển thị: số người, chỗ trống,<br/>mức độ đông, thời gian cập nhật
        Frontend-->>User: Hiển thị bảng tổng quan
    else N0 hoặc dữ liệu occupancy chưa sẵn sàng
        API-->>Frontend: HTTP 503 occupancy_unavailable
        Frontend-->>User: "Chưa đủ dữ liệu"; không hiển thị số 0/chỗ trống giả
    else Nguồn stale hoặc offline
        API-->>Frontend: HTTP 200 với trạng thái nguồn/freshness
        Frontend-->>User: Hiển thị cảnh báo "Dữ liệu lỗi thời"
    end

    Note over Frontend: Làm mới occupancy mỗi 3–5 giây khi trang hiển thị
    Frontend->>API: GET /api/v1/occupancy/rooms/{room_id}/latest
```

### 13.2 Tuyến API GET /api/v1/occupancy/rooms/{room_id}/latest

Lấy occupancy hiện tại của một phòng. Danh sách phòng/cơ sở dùng endpoint
`GET /api/v1/rooms`; `campus_code` chỉ được dùng sau khi dữ liệu phòng đã được
xác minh.

**Tham số truy vấn**

Không có query parameter. Path `room_id` là ID phòng dương.

**Phản hồi thành công (HTTP 200)**

```json
{
  "room_id": 14,
  "room_code": "A101",
  "capacity": 40,
  "estimated_occupancy": 23,
  "available_seats": 17,
  "is_over_capacity": false,
  "density_level": "medium",
  "device_status": "online",
  "occupancy_status": "fresh",
  "recorded_at": "2026-11-11T10:25:30Z",
  "received_at": "2026-11-11T10:25:31Z"
}
```

**Mô tả các trường**

- `estimated_occupancy`: Số người ước tính; không công bố chính thức khi thiếu N0 hợp lệ
- `available_seats`: `max(0, capacity - estimated_occupancy)` khi sức chứa đã xác nhận
- `density_level`: `low` (≤50%), `medium` (>50% và <80%), `high` (≥80%)
- `occupancy_status`: trạng thái freshness theo ngưỡng cấu hình; không hard-code tại UI
- `device_status`: Trạng thái thiết bị: `online`, `offline`, `error`

**Phản hồi khi chưa có dữ liệu hoặc N0 (HTTP 503)**

```json
{
  "error": {
    "code": "occupancy_unavailable",
    "message": "Chưa đủ dữ liệu để tính occupancy"
  }
}
```

**Phòng không tồn tại (HTTP 404)**

```json
{
  "error": {
    "code": "room_not_found",
    "message": "Không tìm thấy phòng"
  }
}
```

### 13.3 Tuyến API GET /api/v1/rooms

Lấy danh sách phòng có thể lọc theo cơ sở và loại phòng.

**Tham số truy vấn**

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `campus` | Chuỗi | Không | Lọc theo cơ sở: 'CS1', 'CS3' |
| `room_type` | Chuỗi | Không | Lọc theo loại: 'free_area', 'topic_room' |
| `status` | Chuỗi | Không | Lọc theo trạng thái: 'active', 'maintenance', 'closed' |

**Phản hồi thành công (HTTP 200)**

```json
{
  "rooms": [
    {
      "id": 1,
      "code": "A101",
      "name": "Khu tự học CS1",
      "room_type": "free_area",
      "building": "CS1",
      "capacity": 50,
      "location": "Tầng 1, Khu A",
      "status": "active",
      "is_active": true,
      "created_at": "2026-10-01T00:00:00Z"
    },
    {
      "id": 2,
      "code": "A201",
      "name": "Phòng học nhóm 1",
      "room_type": "topic_room",
      "building": "CS1",
      "capacity": 10,
      "location": "Tầng 2, Khu A",
      "status": "active",
      "is_active": true,
      "created_at": "2026-10-01T00:00:00Z"
    }
  ],
  "total": 2
}
```

### 13.4 Tuyến API GET /api/v1/rooms/{room_id}

Lấy chi tiết một phòng cụ thể.

**Phản hồi thành công (HTTP 200)**

```json
{
  "id": 1,
  "code": "A101",
  "name": "Khu tự học CS1",
  "room_type": "free_area",
  "building": "CS1",
  "capacity": 50,
  "location": "Tầng 1, Khu A",
  "status": "active",
  "is_active": true,
  "created_at": "2026-10-01T00:00:00Z"
}
```

**Không tìm thấy phòng (HTTP 404)**

```json
{
  "error": {
    "code": "room_not_found",
    "message": "Không tìm thấy phòng với ID này"
  }
}
```

### 13.5 Tuyến API GET /api/v1/rooms/{room_id}/occupancy/history

Lấy lịch sử mật độ của một phòng.

**Tham số truy vấn**

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `start_time` | Ngày giờ | Có | Thời gian bắt đầu (ISO 8601) |
| `end_time` | Ngày giờ | Có | Thời gian kết thúc (ISO 8601) |
| `limit` | Số nguyên | Không | Số bản ghi tối đa (mặc định: 100, tối đa 500) |

**Phản hồi thành công (HTTP 200)**

```json
{
  "room_id": 1,
  "room_code": "A101",
  "room_name": "Khu tự học CS1",
  "start_time": "2026-11-11T09:00:00Z",
  "end_time": "2026-11-11T10:00:00Z",
  "records": [
    {
      "id": 1001,
      "current_count": 20,
      "available_seats": 30,
      "recorded_at": "2026-11-11T09:00:00Z",
      "source": "cv",
      "device_status": "online"
    },
    {
      "id": 1002,
      "current_count": 25,
      "available_seats": 25,
      "recorded_at": "2026-11-11T09:05:00Z",
      "source": "cv",
      "device_status": "online"
    }
  ],
  "total": 2
}
```

### 13.6 Các trường hợp ngoại lệ và cách xử lý lỗi

**Dữ liệu lỗi thời**
- Ngưỡng: Dữ liệu cũ hơn **30 giây** được đánh dấu `is_stale: true`
- giao diện hiển thị cảnh báo: "⚠️ Dữ liệu lỗi thời - cập nhật lần cuối lúc {time}"
- Máy chủ vẫn trả HTTP 200 kèm trường `is_stale`

**Mất kết nối**
- Khi `device_status: "offline"` hoặc không nhận được dữ liệu mới
- giao diện hiển thị: "❌ Mất kết nối với camera"
- Giữ dữ liệu cũ nhưng tạm dừng truy vấn định kỳ

**Không có dữ liệu ban đầu:**
- `current_count: null`, `available_seats: null`
- giao diện hiển thị: "Chưa có dữ liệu - Đang chờ cấu hình"

**Bảng mã lỗi**

| Mã HTTP | Mã lỗi | Khi nào xảy ra | Cách giao diện xử lý |
|-----------|------------|----------------|----------------|
| 200 | — | Thành công, có thể có `is_stale: true` | Hiển thị dữ liệu + cảnh báo nếu dữ liệu lỗi thời |
| 404 | `occupancy_not_found` | Phòng tồn tại nhưng chưa có dữ liệu | "Chưa có dữ liệu mật độ" |
| 404 | `room_not_found` | Mã phòng không tồn tại | "Không tìm thấy phòng" |
| 503 | `service_unavailable` | Cơ sở dữ liệu hoặc dịch vụ không hoạt động | "Hệ thống tạm thời không khả dụng" |

### 13.7 Lưu ý tích hợp giao diện

**Cách truy vấn định kỳ**
- Chu kỳ **5 giây**, đã thống nhất với nhóm giao diện
- Chỉ truy vấn khi thẻ trình duyệt đang hiển thị, dùng Page Visibility API
- Khi gặp lỗi, tăng thời gian chờ giữa các lần thử lên 5 → 10 → 20 → tối đa 30 giây

**Quy tắc hiển thị**
```javascript
if (data.is_stale) {
  showWarning("Dữ liệu lỗi thời");
}
if (data.device_status === "offline") {
  showError("Mất kết nối camera");
}
if (data.current_count === null) {
  showPlaceholder("Chưa có dữ liệu");
} else if (data.current_count === 0) {
  showCount(0); // Số 0 là giá trị hợp lệ
}
```

**Màu biểu thị mức độ đông**
- `low` (≤50%): Xanh lá 🟢
- `medium` (>50%, <80%): Vàng 🟡
- `high` (≥80%): Đỏ 🔴

## 14. UC-06: Dữ liệu CV gửi máy chủ cho SEAT-34

Bản đề xuất cho luồng sự kiện IN/OUT. Xem [sơ đồ tuần tự UC-06](system-architecture.md#sơ-đồ-tuần-tự-uc-06-đếm-qua-đường-ảo). Các tuyến, cấu trúc dữ liệu và hành vi trong mục này cần được nhóm CV và nhóm máy chủ xác nhận trước khi tích hợp.

### 14.1 Hiện trạng và ranh giới tương thích

| Nội dung | Hợp đồng hoặc mã hiện có | Cần cho thiết kế sự kiện |
|---|---|---|
| Tiếp nhận | POST `/api/v1/cv/count-records`, nhận lô bản ghi số đếm, khai báo 200 | Tuyến riêng; đề xuất POST `/api/v1/cv/events`, mỗi yêu cầu một sự kiện |
| Chống trùng | Mục 4.2 đặc tả khóa phiên/khung hình. Trên bản dev đối chiếu, lớp truy cập dữ liệu cập nhật bản ghi khi trùng khóa và tuyến API tham chiếu đến một lớp lỗi chưa được định nghĩa tại đó | `event_id` duy nhất, xác nhận tiếp nhận gốc và cập nhật số người đúng một lần |
| Phòng | Bản ghi số đếm nhận mã chuỗi như `A101`, ánh xạ `rooms.code` → `rooms.id` | Sự kiện dùng mã phòng dạng số đã xác minh cùng nguồn/phiên |
| Lưu trữ | Bản ghi số đếm hiện lưu vào `cv_count_records`; schema `CountEvent` hiện hành chưa dùng UUID từ CV | Target Sprint 4 dùng UUID `event_id`, gắn với `session_id`, và cập nhật event/occupancy nhất quán |
| Giao diện đang dùng | `/occupancy/current`, làm mới 30 giây, đọc `occupancy_records` | Chốt tuyến GET theo phòng, theo cơ sở và chốt thông tin trạng thái từ nguồn sự kiện |
| GET bản ghi số đếm | `/occupancy/rooms/{room_id}/latest` đọc `cv_count_records` | Không giả định đã đọc `OccupancyRecord` hoặc tổng hợp sự kiện |
| Xác thực/trạng thái | Chưa có khóa tiếp nhận hoặc tuyến trạng thái thiết bị | Chốt khóa API, quyền nguồn và tín hiệu định kỳ báo nguồn còn hoạt động

### 14.2 Nội dung sự kiện và ánh xạ từ CV

Payload target của SEAT-51/53 bám theo các trường issue yêu cầu; `session_id`
được thêm để gắn sự kiện với N0 của phiên. `device_status` trong event là
snapshot; heartbeat định kỳ vẫn dùng endpoint trạng thái riêng.

| Trường | Kiểu / bắt buộc | Quy tắc và ánh xạ |
|---|---|---|
| `event_id` | UUID / có | CV tạo và lưu bền vững trước gửi; giữ nguyên qua retry/restart; khóa idempotency |
| `session_id` | UUID / có | Phiên đếm gắn N0 đã kiểm tra; phiên mới cần N0 mới |
| `room_id` | số nguyên dương / có | Mã `rooms.id` đã xác minh; không tự tạo hoặc suy diễn phòng |
| `device_id` | chuỗi 1–100 ký tự / có | Mã nguồn ổn định; không phải track/person ID |
| `direction` | `in` hoặc `out` / có | Một lượt qua đường; không gửi counter tích lũy |
| `event_time` | ISO 8601 UTC / có | Thời điểm lượt cắt đường ảo được xác nhận |
| `device_status` | `online`, `offline` hoặc `error` / có | Trạng thái nguồn tại lúc gửi sự kiện; heartbeat định kỳ cập nhật qua endpoint riêng |

Không gửi ảnh, video, bounding box, confidence hay ID theo dõi lâu dài.

```json
{
  "event_id": "076ccfac-ea81-4213-9d9f-6b7bb4387010",
  "session_id": "6f228318-ea31-46b3-a1a7-c562288ea97e",
  "room_id": 14,
  "device_id": "cam-01",
  "direction": "in",
  "event_time": "2026-11-11T07:00:00Z",
  "device_status": "online"
}
```
### 14.3 Giao dịch, xác nhận tiếp nhận và lỗi

| Trường hợp | Hành vi mục tiêu |
|---|---|
| Sự kiện mới hợp lệ | HTTP 201 sau COMMIT; `CountEvent`, cập nhật occupancy và receipt được lưu nhất quán |
| Cùng `event_id`, cùng nội dung chuẩn hóa | HTTP 201 với receipt gốc và `duplicate=true`; không đổi occupancy hoặc `received_at` |
| Cùng `event_id`, khác nội dung | HTTP 409 `event_id_conflict`; không cập nhật dữ liệu |
| Thiếu/sai khóa | HTTP 401 `unauthorized`; không ghi dữ liệu |
| Khóa/nguồn không có quyền ghi phòng/phiên | HTTP 403 `forbidden` |
| Phòng không tồn tại | HTTP 404 `room_not_found`; không tự tạo phòng |
| JSON hỏng / sai cấu trúc dữ liệu | HTTP 400 `malformed_json` / 422 `validation_error` |
| Phiên chưa khởi tạo N0 hoặc đã đóng | HTTP 409 `session_not_ready` / `session_closed`; không cập nhật occupancy |
| Cơ sở dữ liệu không khả dụng | HTTP 503 `database_unavailable`; hoàn tác phần chưa xác nhận lưu |

```json
{
  "event_id": "076ccfac-ea81-4213-9d9f-6b7bb4387010",
  "room_id": 14,
  "received_at": "2026-11-11T07:00:01Z",
  "duplicate": false
}
```


### 14.4 Giao nhận và trạng thái nguồn

- Bộ gửi lưu hàng đợi bền vững trước gửi; mỗi nguồn/phiên chỉ có một yêu cầu
  chờ xác nhận. Chỉ bỏ sự kiện khi phản hồi 201/200 hợp lệ khớp `event_id`.
- Đề xuất thời gian chờ kết nối 3 giây, toàn yêu cầu 10 giây. Khi mất kết nối,
  hết thời gian chờ hoặc nhận 503, gửi lại ba lượt sau lần đầu, chờ tăng dần
  1, 2, 4 giây, giữ nguyên mã sự kiện, nội dung và thứ tự. Hết lượt vẫn giữ hàng đợi và
  báo vận hành để gửi lại sau.
- Với lỗi 4xx, không tự gửi lại; giữ/cách ly, báo nguyên nhân và đối soát. Không bỏ
  sự kiện lỗi rồi áp dụng sự kiện phụ thuộc nó. Giới hạn hàng đợi, cảnh báo
  đầy, thời hạn lưu và phục hồi cần chốt; không tự xóa sự kiện chưa được xác
  nhận. Các giá trị thời gian chờ/gửi lại là đề xuất, chưa được triển khai.
- Camera mất nhưng CV còn mạng: dùng PUT `/api/v1/cv/devices/{device_id}/status`
  riêng.
  Không gửi IN/OUT giả hoặc đặt số đếm về 0. CV mất mạng/dừng đột ngột không
  thể gửi trạng thái mất kết nối ngay; máy chủ cần tín hiệu định kỳ để phát
  hiện mất nguồn.
- Chu kỳ heartbeat và ngưỡng stale/offline lấy từ cấu hình có tên; giá trị mặc
  định cần được thống nhất trước khi chạy. Không dùng tuổi `received_at` của
  một event đơn lẻ làm heartbeat.
- Trạng thái có thứ tự riêng theo nguồn/phiên. Thông báo trạng thái cũ gửi lại
  không ghi đè trạng thái mới; gửi lại xác nhận không làm dữ liệu cũ bị hiểu
  thành mới. Sau gián đoạn, nguồn đang kết nối và số người đã đồng bộ là hai
  điều kiện riêng.

Ví dụ dữ liệu trạng thái đề xuất

```json
{
  "room_id": 14,
  "device_status": "offline",
  "reported_at": "2026-11-11T07:01:00Z"
}
```

Body heartbeat có `device_id` trong path, `room_id`, `device_status` và
`reported_at`. `device_status` là `online|offline|error`, không có hướng vào/ra
hoặc số đếm. Backend chỉ nhận thời điểm mới hơn thời điểm đã lưu; heartbeat
không cập nhật occupancy. API đọc/giao diện cần phân biệt chưa biết, số 0 hợp
lệ, số đếm cũ, mất kết nối và lỗi HTTP.
Chưa có N0/sức chứa hợp lệ thì không công bố chỗ trống hoặc mức đông chính thức.

### 14.5 Khóa API qua biến môi trường

Trường tiêu đề HTTP là `X-API-Key`; bộ gửi đọc `CV_API_KEY`, máy chủ đọc
`CV_INGEST_API_KEY` qua môi trường. Hai biến phải được cấu hình cùng một secret
được quản lý ngoài Git. Đây là tên thiết kế, chưa có xác thực tương
ứng trong mã nguồn. Không đưa khóa vào URL, JSON, nhật ký hoặc giao diện; không
đưa `.env` vào lịch sử Git. Máy chủ phải xác thực khóa và quyền nguồn/phòng,
không chỉ kiểm tra có tiêu đề. Cách cấp/đổi khóa, ánh xạ quyền và so sánh khóa
an toàn cần chốt với máy chủ. Dùng HTTPS khi truyền qua mạng; không mở API
tiếp nhận công khai từ bản chạy thử.

### 14.6 Ví dụ curl và kế hoạch xác thực

Các lệnh dùng PowerShell và `curl.exe`, chỉ dành cho môi trường thử riêng có
cơ sở dữ liệu đã nạp dữ liệu mẫu. Chưa chạy trong lần soạn tài liệu; không gọi
vào dữ liệu chung/môi trường vận hành thực tế, không ghi tệp thử vào thư mục
hỗ trợ được bảo vệ.

Với **bản ghi số đếm SEAT-19**, lưu một lô theo mục 4.1 vào `count-batch.json` trong thư
mục thử nghiệm. API khai báo 200. Xem mục 14.1 về sai khác đã ghi nhận trong mã
nguồn trước khi thử.

```powershell
$seat34BaseUrl = 'http://127.0.0.1:8000'
curl.exe --silent --show-error --max-time 10 --include `
  -H 'Content-Type: application/json' `
  --data-binary '@count-batch.json' "$seat34BaseUrl/api/v1/cv/count-records"
curl.exe --silent --show-error --max-time 10 --include `
  "$seat34BaseUrl/api/v1/occupancy/rooms/14/latest"
```

Với **sự kiện có khóa**, lưu JSON mục 14.2 vào `crossing-event.json` trong thư mục
thử; nạp khóa thử nghiệm vào môi trường. Chỉ chạy sau khi máy chủ có tuyến và
xác thực theo hợp đồng đã duyệt. Lệnh là ví dụ thiết kế, không chứng minh API
có sẵn.

```powershell
$seat34BaseUrl = 'http://127.0.0.1:8000'
if ([string]::IsNullOrWhiteSpace($env:CV_API_KEY)) {
  throw 'Chưa nạp CV_API_KEY cho môi trường thử nghiệm'
}
curl.exe --silent --show-error --connect-timeout 3 --max-time 10 --include `
  -H 'Content-Type: application/json' -H "X-API-Key: $env:CV_API_KEY" `
  --data-binary '@crossing-event.json' "$seat34BaseUrl/api/v1/cv/events"
```

Gửi lại cùng tệp để thử chống trùng, không tạo UUID mới. Để thử trạng thái,
lưu JSON mục 14.4 vào `device-status.json`, dùng cùng tiêu đề/khóa ở tuyến
trạng thái đề xuất. Không dùng `--verbose` hoặc ghi lệnh đã chứa giá trị khóa
vào nhật ký làm bằng chứng chia sẻ.

| Kiểm tra | Mong đợi | Trạng thái ngày 11/11/2026 |
|---|---|---|
| Lô số đếm hợp lệ / gửi lại / xung đột | 200 mới; 200 trùng; 409 khác nội dung theo v1 | Chưa chạy; mã nguồn đang lệch mục 14.1 |
| Sự kiện mới / gửi lại / xung đột | 201; xác nhận cũ 200; 409; số đếm đổi đúng một lần | Chưa chạy; chưa có API sự kiện |
| Thiếu/sai khóa / sai quyền | 401 / 403, không ghi dữ liệu | Chưa chạy; chưa có xác thực nguồn |
| Mất xác nhận, yêu cầu đồng thời, cơ sở dữ liệu lỗi | Một sự kiện và một tác động; hoàn tác hoặc trả xác nhận đã lưu | Chưa chạy; cần PostgreSQL thử riêng |
| Khởi động lại CV, hàng đợi đầy, sai thứ tự | Giữ mã sự kiện và thứ tự, cảnh báo/đối soát; không mất sự kiện mà không báo | Chưa chạy; chưa có bộ gửi/hàng đợi |
| Chưa biết N0, lượt ra làm số đếm âm, vượt sức chứa, hiệu chỉnh | Chưa biết, đánh dấu dưới 0, kẹp chỗ trống, lịch sử truy vết | Chưa chạy tích hợp |
| Mất nguồn/mạng, tín hiệu hoạt động phục hồi | Cảnh báo nguồn, không đặt về 0, gửi lại không làm dữ liệu cũ thành mới | Chưa chạy; chưa có API trạng thái |
| Sự kiện → GET → giao diện | Đúng phòng/cơ sở và nguồn tính; đo từ cắt đường ảo đến hiển thị | Chưa chạy; giao diện hiện làm mới 30 giây |

### 14.7 Nội dung cần Khiêm và Thắng xác nhận

- [ ] Tuyến/phiên bản/cấu trúc sự kiện và trạng thái, phiên/số thứ tự đề xuất.
- [ ] Ánh xạ phòng khu tự học/cơ sở, nguồn/quyền khóa và dữ liệu video thử.
- [ ] UUID gửi mạng, cập nhật mã số nguyên, giao dịch và xác nhận khi mất phản hồi.
- [ ] Số ban đầu mỗi phiên, thứ tự/gửi lại, số đếm dưới 0 và hiệu chỉnh truy vết.
- [ ] Nguồn GET cho giao diện, chuyển bản ghi số đếm/sự kiện, chưa biết/mất kết nối, chu kỳ cập nhật.
- [ ] Tiêu đề HTTP/biến môi trường chứa khóa, thời gian chờ/chờ tăng dần, tín hiệu hoạt động và giới hạn hàng đợi.
- [ ] NFR-PRI-01/02 và ví dụ curl được thử với API thực tế sau khi gỡ trở ngại.
