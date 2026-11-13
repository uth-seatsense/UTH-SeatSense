# API contract — tổng quan

> Trạng thái: bản rà soát / đề xuất, chưa phải toàn bộ contract đã được triển khai.  
> Ngày đối chiếu: 13-11-2026. Contract CV chi tiết nằm ở phụ lục cuối tài liệu.

## Quy ước chung

- Prefix `/api/v1`; JSON UTF-8, tên trường `snake_case`.
- Date-time dùng ISO 8601 có múi giờ; server trả UTC dạng `Z`. Thời điểm không có timezone bị từ chối.
- Danh sách dùng `limit` (mặc định 50, tối đa 100) và `offset` (mặc định 0); response đề xuất `{ "items": [], "limit": 50, "offset": 0, "total": 0 }`. Chưa có quy ước phân trang được triển khai/đồng thuận trong mã.
- Lỗi có dạng `{ "error": { "code": "...", "message": "...", "details": [{ "field": "...", "issue": "..." }] } }`; bỏ `details` nếu không có. `400` JSON sai, `401` thiếu/sai token, `403` không đủ quyền, `404` không tồn tại, `409` xung đột trạng thái/khóa idempotency, `422` dữ liệu hợp lệ về cú pháp nhưng sai quy tắc. Mã 401/403 là mục tiêu, chưa có auth middleware hiện tại.
- Mọi API nghiệp vụ người dùng yêu cầu `Authorization: Bearer <access_token>`. Web và Android native dùng chung issuer/audience và token; refresh/revoke, thời hạn, lưu trữ token và CSRF cho web chưa chốt.
- Các endpoint auth đăng ký/đăng nhập/đăng xuất/thông tin tài khoản dùng chung cho web, ứng dụng native và Portal; client không có bộ endpoint hay định dạng token riêng. Portal/SSO là phương thức xác thực chờ trường phê duyệt/cung cấp thông số.
- Portal/SSO: dành integration seam (`provider=portal`, `external_subject`), trạng thái chờ trường cung cấp issuer, protocol, claim mapping và quy trình duyệt. Không thu hoặc lưu mật khẩu Portal. MVP hiện có thể dùng OTP email theo DEC-08.
- CV dùng API key riêng, không dùng token người dùng: `X-API-Key`. Cách cấp/luân chuyển/lưu key và production secret store chưa chốt.
- CV event: `event_id` UUID là idempotency key; cùng ID cùng payload trả lại receipt đã tạo, cùng ID payload khác trả `409 event_id_conflict`. Đây là đề xuất endpoint sự kiện riêng. Contract CountResult batch của SEAT-34 dùng khóa `(session_id, frame_index)`; route ingestion chưa có trong nhánh hiện tại.

## Endpoint inventory và vai trò

`IMPLEMENTED` chỉ áp dụng khi có handler trong source hiện tại; `PROPOSED` là contract cần triển khai. Đã tái sử dụng nội dung SEAT-18, payload CV từ SEAT-34 và đặc tả occupancy/rooms từ SEAT-39. Các endpoint nghiệp vụ dưới đây hiện chưa được triển khai trong nhánh đang rà soát, kể cả occupancy và CV ingestion.

| Nhóm | Phương thức / URL | Vai trò gọi | Trạng thái và ý nghĩa |
|---|---|---|---|
| Auth | `POST /api/v1/auth/register` | Public | PROPOSED — đăng ký email/OTP; chưa có router |
| Auth | `POST /api/v1/auth/login` | Public | PROPOSED — xác minh OTP, phát token chung web/native |
| Auth | `POST /api/v1/auth/logout` | `authenticated` | PROPOSED — thu hồi refresh session; semantics chờ chốt |
| Auth | `GET /api/v1/auth/me` | `authenticated` | PROPOSED — hồ sơ và role hiện tại |
| Occupancy | `GET /api/v1/occupancy/current` | Public hoặc user đã đăng nhập; role/scope chờ chốt | PROPOSED — UC-01/SEAT-39; danh sách occupancy phòng active, có thể lọc campus khi có mapping |
| Occupancy | `GET /api/v1/occupancy/rooms/{room_id}/latest` | User được xem occupancy | PROPOSED — bản ghi webcam mới nhất; phân biệt không có record và phòng không tồn tại |
| Occupancy | `GET /api/v1/rooms/{room_id}/occupancy/history` | `librarian`, `admin`; quyền student chờ chốt | PROPOSED — lịch sử mật độ theo khoảng thời gian (SEAT-39) |
| Rooms | `GET /api/v1/rooms` | `authenticated` | STUB — danh sách/phân trang đề xuất |
| Rooms | `GET /api/v1/rooms/{room_id}` | `authenticated` | STUB — chi tiết phòng đề xuất |
| Bookings | `GET /api/v1/bookings` | Chủ booking; librarian/admin xem phạm vi được cấp | PROPOSED — đổi tên từ reservations để thống nhất thuật ngữ; hiện schema/router placeholder reservations |
| Bookings | `POST /api/v1/bookings` | `student` | PROPOSED — tạo booking |
| Bookings | `GET /api/v1/bookings/{booking_id}` | Chủ booking, librarian/admin | PROPOSED — chi tiết |
| Bookings | `DELETE /api/v1/bookings/{booking_id}` | Chủ booking, librarian/admin | PROPOSED — hủy; semantics hủy chờ chốt |
| Check-in | `POST /api/v1/check-in` | `student` | PROPOSED — check-in booking bằng QR/token |
| Dashboard | `GET /api/v1/dashboard/summary` | `librarian`, `admin` | PROPOSED — chỉ số vận hành; metrics/filters cần chốt |
| Health | `GET /health`, `GET /api/v1/health` | Public/monitoring | IMPLEMENTED — hai route trong backend cùng trả trạng thái service; chưa có health DB riêng |
| CV | `POST /api/v1/cv/count-records` | CV service với API key riêng | PROPOSED — payload CountResult theo SEAT-34; key chưa triển khai |
| CV events | `POST /api/v1/cv/events` | CV service với API key | PROPOSED — event_id idempotent, chưa triển khai |

## Payload mẫu cho các route đang đề xuất

Quy ước đọc bảng dưới: body/response là JSON mẫu; `—` nghĩa không có body/params. Danh sách lỗi nêu các mã áp dụng cho operation đó; mọi lỗi vẫn dùng envelope ở trên. Với route PROPOSED, đây là contract mục tiêu để review, chưa phải cam kết từ OpenAPI/runtime.

## Đặc tả operation đầy đủ

| Method / URL | Gọi bởi | Path/query/header | Request body | Response thành công | Lỗi dự kiến |
|---|---|---|---|---|---|
| `POST /api/v1/auth/register` PROPOSED | Public | — | `{"email":"sv@example.edu.vn"}` | `202 {"status":"otp_sent"}` | 400 malformed JSON; 401/403 không áp dụng; 409 email/session conflict; 422 email sai/không thuộc miền được phép |
| `POST /api/v1/auth/login` PROPOSED | Public | — | `{"email":"sv@example.edu.vn","otp":"123456"}` | `200 {"access_token":"<jwt>","token_type":"bearer","expires_in":900,"user":{"id":"usr_123","email":"sv@example.edu.vn","role":"student"}}` | 400 malformed JSON; 401 OTP sai/hết hạn; 403 tài khoản bị khóa; 404 account không tồn tại (có thể gộp với 401 để tránh dò email); 422 thiếu/sai field |
| `POST /api/v1/auth/logout` PROPOSED | `authenticated` | Bearer token | `—` | `204` không body | 401 thiếu/hết hạn token; 403 session không thuộc user; 404 session không tồn tại; 422 token/session format sai |
| `GET /api/v1/auth/me` PROPOSED | `authenticated` | Bearer token | `—` | `200 {"id":"usr_123","email":"sv@example.edu.vn","role":"student","provider":"email_otp"}` | 401 token thiếu/sai/hết hạn; 403 tài khoản chưa được phép; 404 user đã bị xóa |
| `GET /api/v1/occupancy/current` PROPOSED (SEAT-39) | User xem occupancy; role/scope chờ chốt | Query `campus` tùy chọn (`CS1`, `CS3`; mapping campus chưa có); `limit` 1..100 (default 50), `offset` ≥0 | `—` | `200 {"campus":"CS1","rooms":[{"room_id":14,"room_code":"A101","room_name":"Khu tự học CS1","room_type":"free_area","capacity":50,"current_count":23,"available_seats":27,"occupancy_level":"medium","recorded_at":"2026-11-11T10:25:30Z","updated_at":"2026-11-11T10:25:30Z","is_stale":false,"device_status":"online"}],"limit":50,"offset":0,"total_rooms":1,"last_updated":"2026-11-11T10:25:30Z"}`; count/available seats có thể null khi chưa có baseline/record | 400 query sai; 401 thiếu/sai token nếu yêu cầu auth; 403 ngoài scope; 404 `occupancy_not_found` khi campus không có dữ liệu; 409 không áp dụng; 422 campus/pagination sai; 503 nguồn/DB lỗi |
| `GET /api/v1/occupancy/rooms/{room_id}/latest` PROPOSED | User xem occupancy; role/scope chờ chốt | `room_id`: integer >0 (ID DB) | `—` | `200 {"room_id":14,"room_code":"A101","camera_id":"cam-01","source_type":"webcam","people_count":3,"tracked_count":2,"estimated_occupancy":3,"occupancy_underflow":false,"recorded_at":"2026-11-11T08:00:00Z","received_at":"2026-11-11T08:00:01Z","is_stale":false}` | 400 không áp dụng; 401/403 theo auth/scope; 404 `room_not_found` hoặc `occupancy_not_found`; 409 không áp dụng; 422 room_id sai; 503 DB/service lỗi |
| `GET /api/v1/rooms/{room_id}/occupancy/history` PROPOSED (SEAT-39) | `librarian`, `admin`; student access chờ chốt | `start_time`, `end_time` ISO 8601 UTC; `limit` 1..500 (default 100); `offset` ≥0 | `—` | `200 {"room_id":14,"room_code":"A101","start_time":"2026-11-11T09:00:00Z","end_time":"2026-11-11T10:00:00Z","records":[{"id":1001,"current_count":20,"available_seats":30,"recorded_at":"2026-11-11T09:00:00Z","source":"cv","device_status":"online"}],"limit":100,"offset":0,"total":1}` | 400 query sai; 401; 403 role/scope; 404 `room_not_found`; 409 không áp dụng; 422 datetime/range/limit/offset sai; 503 DB/service lỗi |
| `GET /api/v1/rooms` PROPOSED (router STUB) | `authenticated` | `limit` 1..100 (default 50), `offset` ≥0 (default 0), tùy chọn `campus`, `building`, `room_type`, `status` | `—` | `200 {"items":[{"id":14,"code":"A101","name":"Phòng A101","capacity":40,"is_active":true}],"limit":50,"offset":0,"total":1}` | 400 malformed query; 401 thiếu token; 403 không có quyền; 404 không áp dụng; 409 không áp dụng; 422 limit/offset/filter sai |
| `GET /api/v1/rooms/{room_id}` PROPOSED (router STUB) | `authenticated` | `room_id` integer dương | `—` | `200 {"id":14,"code":"A101","name":"Phòng A101","capacity":40,"is_active":true}` | 400 không áp dụng; 401; 403; 404 `room_not_found`; 409 không áp dụng; 422 id sai |
| `GET /api/v1/bookings` PROPOSED | User; mặc định chỉ booking của mình; librarian/admin theo scope | `from`, `to` ISO8601 tùy chọn; `status` (`booked`, `checked_in`, `completed`, `cancelled`, `no_show`); `limit`, `offset` | `—` | `200 {"items":[{"id":"bkg_456","room_id":14,"status":"booked","starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z"}],"limit":50,"offset":0,"total":1}` | 400 malformed query; 401; 403 truy cập ngoài scope; 404 không áp dụng; 409 range/filter conflict; 422 date/status/pagination sai |
| `POST /api/v1/bookings` PROPOSED | `student` | Bearer token | `{"room_id":14,"starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z"}` | `201 {"id":"bkg_456","room_id":14,"user_id":"usr_123","status":"booked","starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z","created_at":"2026-11-11T08:00:00Z"}` | 400 malformed JSON; 401; 403 role/booking quota; 404 room không tồn tại; 409 lịch phòng bị trùng; 422 khoảng giờ/field không hợp lệ |
| `GET /api/v1/bookings/{booking_id}` PROPOSED | Chủ booking, librarian/admin cùng scope | `booking_id` string | `—` | `200` booking object như response POST | 400 không áp dụng; 401; 403 ngoài owner/scope; 404 `booking_not_found`; 409 không áp dụng; 422 id sai |
| `DELETE /api/v1/bookings/{booking_id}` PROPOSED | Chủ booking, librarian/admin cùng scope | `booking_id` string | `—` | `204` không body | 400 không áp dụng; 401; 403 ngoài owner/scope; 404 không tồn tại; 409 đã check-in/không thể hủy; 422 id sai |
| `POST /api/v1/check-in` PROPOSED | `student` là chủ booking | Bearer token | `{"booking_id":"bkg_456","qr_token":"<opaque>"}` | `200 {"booking_id":"bkg_456","status":"checked_in","checked_in_at":"2026-11-12T02:04:00Z"}` | 400 malformed JSON; 401; 403 không phải chủ booking; 404 booking/token không tồn tại; 409 đã check-in/ngoài cửa sổ; 422 token hoặc body sai |
| `GET /api/v1/dashboard/summary` PROPOSED | `librarian`, `admin` | `from`, `to` ISO8601; scope campus/building chờ chốt | `—` | `200 {"occupancy":{"current":12,"capacity":40},"bookings":{"total":8,"checked_in":5,"no_show":1},"generated_at":"2026-11-11T08:00:00Z"}` | 400 malformed query; 401; 403 role/scope; 404 scope không tồn tại (nếu lọc theo scope); 409 range conflict; 422 date/filter sai |
| `POST /api/v1/cv/count-records` PROPOSED (SEAT-34) | CV service qua API key riêng `X-API-Key` | Header `Content-Type: application/json`, `X-API-Key`; body `records` gồm 1..1000 CountResult | `{"records":[{"schema_version":"1.0","session_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","camera_id":"cam-01","room_id":"A101","source_type":"webcam","frame_index":100,"timestamp_ms":10000,"recorded_at":"2026-11-11T08:00:00Z","people_count":3,"tracked_count":2,"line_enabled":true,"in_count":4,"out_count":1,"initial_occupancy":0,"estimated_occupancy":3,"occupancy_underflow":false}]}` | `200 {"status":"accepted","created_count":1,"duplicate_count":0,"records":[{"record_id":8123,"session_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","frame_index":100,"room_code":"A101","room_id":14,"received_at":"2026-11-11T08:00:01Z","duplicate":false}]}` | 400 JSON sai; 401 API key thiếu/sai; 403 key hợp lệ nhưng thiếu scope; 404 không áp dụng; 409 cùng `(session_id, frame_index)` khác payload; 422 batch/schema sai |
| `POST /api/v1/cv/events` PROPOSED | CV service với API key | `X-API-Key` | `{"event_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","session_id":"...","camera_id":"cam-01","room_id":"A101","frame_index":100,"timestamp_ms":10000,"recorded_at":"2026-11-11T08:00:00Z","track_id":12,"direction":"IN","confidence":0.98}` | `200 {"event_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","accepted":true,"duplicate":false}`; retry giống payload trả `duplicate:true` | 400 JSON sai; 401 API key sai; 403 scope sai; 404 không áp dụng; 409 `event_id_conflict`; 422 schema sai |
| `GET /api/v1/notifications/subscriptions` PROPOSED / OPTIONAL (FR-OPT-01) | `authenticated` | Bearer token; `limit`, `offset` | `—` | `200 {"items":[{"id":"ntf_123","room_id":14,"condition":"seats_available","threshold":5,"enabled":true,"channel":"email"}],"limit":50,"offset":0,"total":1}` | 400 query sai; 401; 403; 404 không áp dụng; 409 không áp dụng; 422 pagination sai |
| `POST /api/v1/notifications/subscriptions` PROPOSED / OPTIONAL (FR-OPT-01) | `student` | Bearer token | `{"room_id":14,"condition":"seats_available","threshold":5,"channel":"email"}` | `201 {"id":"ntf_123","room_id":14,"condition":"seats_available","threshold":5,"enabled":true,"channel":"email","created_at":"2026-11-11T08:00:00Z"}` | 400 malformed JSON; 401; 403 role/scope; 404 room không tồn tại; 409 subscription trùng; 422 room không hỗ trợ occupancy hoặc field/channel không hợp lệ |
| `DELETE /api/v1/notifications/subscriptions/{subscription_id}` PROPOSED / OPTIONAL (FR-OPT-01) | Chủ subscription; admin | Bearer token; `subscription_id` string | `—` | `204` không body | 400 không áp dụng; 401; 403 không phải owner; 404 subscription không tồn tại; 409 đã bị xử lý/xóa; 422 id sai |
| `GET /health`, `GET /api/v1/health` IMPLEMENTED | Public/monitor | — | `—` | `200 {"status":"ok","service":"backend"}` | 400/401/403/404/409/422 không áp dụng; chưa có route health DB riêng |

Role labels là bản đề xuất cho contract; nguồn hiện hành chưa có enum role hoặc access-control implementation. Thời hạn token, rule ownership, room fields, booking status transitions, cửa sổ check-in và metric definitions cần được chốt trước khi xem các response/error này là ổn định.

## Option thông báo bổ sung theo SRS

SRS 1.8, FR-OPT-01 xếp dự báo mật độ 1–2 giờ hoặc thông báo chỗ trống vào mức Could, không bắt buộc trong bản đầu. Vì vậy ba operation notification ở bảng trên là option mở rộng: mặc định không tạo subscription nếu user chưa chủ động bật; không gửi thông báo trong MVP. Payload mẫu tạo subscription là `{"room_id":14,"condition":"seats_available","threshold":5,"channel":"email"}`. Contract trên chưa khẳng định hệ thống gửi email/push ngay: kênh, ngưỡng chỗ trống, tần suất/cooldown, giờ yên lặng, quyền riêng tư email và xử lý khi occupancy `null` cần được xác nhận trước khi triển khai. Dự báo 1–2 giờ là một option khác, cần nguồn dữ liệu/mô hình và chỉ nên công bố sau khi được xác nhận; endpoint dự báo chưa được đề xuất ở đây.

## Đối chiếu yêu cầu SRS và mục cần bổ sung

| SRS | Đã phản ánh trong contract | Thiếu / cần thông báo bổ sung |
|---|---|---|
| FR-AUTH-01/02/04, BR-15 | OTP, tự tạo hồ sơ, login/logout đã có khung operation | Danh sách email cho phép, OTP 6 số, hash-at-rest, 5 phút, tối đa 5 lần sai, resend 60 giây và lỗi chung phải được đưa vào schema/response/rate-limit contract; không nên lộ email tồn tại. Thông số bảo mật đang tạm chờ rà soát. |
| FR-AUTH-05, BR-16 | Portal/SSO seam được đánh dấu chờ trường | Chỉ bật sau văn bản đồng ý, đầu mối kỹ thuật và giao thức/claim chính thức. |
| FR-SITE-01 | Chưa đủ | SRS yêu cầu lọc theo CS1/CS3 và dashboard theo từng cơ sở/tổng hợp; room hiện chưa có `campus_id` trong endpoint/schema. Bổ sung `campus_id` filter cho rooms, occupancy, bookings và dashboard khi model đã có mapping. |
| FR-OCC-01–06, BR-01/02 | Current/latest occupancy và giới hạn CV được ghi | Thiếu API availability (`available_seats`/mức đông), occupancy adjustment có audit, trạng thái dữ liệu tin cậy và quản trị số đầu phiên. SRS nói không công bố chỗ trống chính thức nếu không có baseline đáng tin cậy. |
| FR-BOOK-02–06, BR-03/04/18/19 | Booking create/list/get/cancel có khung | Request thiếu `participant_count`; cần trả validation/conflict cho 30–120 phút, đặt trước tối đa 7 ngày, buffer 15 phút, 2–6 người, một lượt/ngày và cutoff hủy 30 phút. Đây là giá trị tạm nội bộ, phải xác nhận với thư viện trước vận hành. |
| FR-CHK-01–03, BR-05–08 | Check-in submit có khung | Thiếu API lấy/tạo QR token gắn booking và no-show job/state transition; quy tắc cửa sổ đến +15 phút, QR dùng một lần, check-in lặp, giải phóng phần giờ còn lại cần nêu rõ. Xác nhận thư viện còn chờ. |
| FR-DASH-01/02, BR-10 | Dashboard summary sơ bộ | Cần lọc phòng/campus/khoảng thời gian, mật độ theo thời gian, utilization và no-show; định nghĩa mẫu số và quyền tổng hợp chưa chốt. |
| FR-ADMIN-01, BR-09/20 | Chưa có endpoint quản trị | Cần operation quản lý phòng/sức chứa/active state, gán vai trò, cấu hình chính sách và audit log; giới hạn cho tài khoản admin được cấp quyền. |
| FR-OPT-01 | Đã thêm option subscription thông báo | Could, ngoài MVP; channel/threshold/cooldown cần xác nhận. |

Đây là danh sách gap để chủ tài liệu SRS/nhóm nghiệp vụ nhận thông báo và quyết định có bổ sung API hay không. Không sửa nội dung SRS hoặc coi các giá trị tạm là chính sách thư viện đã duyệt.

### Auth

`POST /auth/register` body: `{"email":"sv@example.edu.vn"}` → `202` `{"status":"otp_sent"}`. `POST /auth/login` body: `{"email":"sv@example.edu.vn","otp":"123456"}` → `200` `{"access_token":"<jwt>","token_type":"bearer","expires_in":900,"user":{"id":"usr_123","email":"sv@example.edu.vn","role":"student"}}`. `POST /auth/logout` body rỗng → `204`. `GET /auth/me` → `200` cùng object `user`. OTP expiry/attempt limits, token claims, refresh flow và logout behavior chưa chốt.

### Rooms

`GET /rooms?limit=50&offset=0` → `200` `{"items":[{"id":14,"code":"A101","name":"Phòng A101","capacity":40,"is_active":true}],"limit":50,"offset":0,"total":1}`. `GET /rooms/14` trả cùng một room object. Tên trường, lọc campus/building và quyền đọc inactive rooms chưa chốt.

### Bookings

`POST /bookings` body `{"room_id":14,"starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z"}` → `201` `{"id":"bkg_456","room_id":14,"user_id":"usr_123","status":"booked","starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z","created_at":"2026-11-11T08:00:00Z"}`. `GET /bookings?from=...&to=...&limit=50&offset=0` → trang có `items` booking và metadata phân trang. Trùng lịch trả `409 booking_conflict`; thời lượng, giờ hoạt động, timezone nghiệp vụ và tên route reservations vs bookings chưa chốt. Trạng thái lưu là `booked`, `checked_in`, `completed`, `cancelled`, `no_show`.

### Check-in

`POST /check-in` body `{"booking_id":"bkg_456","qr_token":"<opaque>"}` → `200` `{"booking_id":"bkg_456","status":"checked_in","checked_in_at":"2026-11-12T02:04:00Z"}`. Token QR, cửa sổ check-in, retry idempotency và response khi đã check-in chưa chốt.

### Dashboard

`GET /dashboard/summary?from=...&to=...` → `200` `{"occupancy":{"current":12,"capacity":40},"bookings":{"total":8,"checked_in":5,"no_show":1},"generated_at":"2026-11-11T08:00:00Z"}`. Định nghĩa metrics, quyền theo campus và phạm vi thời gian chưa chốt.

### CV event đề xuất

`POST /cv/events` với `X-API-Key: <service-key>` body `{"event_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","session_id":"...","camera_id":"cam-01","room_id":"A101","frame_index":100,"timestamp_ms":10000,"recorded_at":"2026-11-11T08:00:00Z","track_id":12,"direction":"IN","confidence":0.98}` → `200` `{"event_id":"...","accepted":true,"duplicate":false}`. Cùng event gửi lại trả `duplicate:true`; khác nội dung cùng ID trả `409`. Lưu event và quan hệ event/frame chưa có trong persistence hiện tại.

## Quy tắc occupancy/rooms tái sử dụng từ SEAT-39

- `available_seats = max(0, capacity - current_count)` khi cả capacity và current_count đã biết; nếu thiếu baseline hoặc occupancy thì trả `null`, không đổi `null` thành `0`.
- `occupancy_level`: `low` khi tỷ lệ sử dụng ≤50%, `medium` khi >50% và <80%, `high` khi ≥80%. Ngưỡng này cần được xác nhận với nghiệp vụ trước triển khai.
- Dữ liệu cũ hơn 30 giây (`updated_at`/`received_at`) trả `is_stale: true`; vẫn trả dữ liệu kèm cảnh báo. Client polling 5 giây khi trang đang hoạt động, có thể backoff khi lỗi.
- `GET /occupancy/current` lọc theo campus `CS1`/`CS3` theo đề xuất SEAT-39; repository hiện chưa có mapping campus nên filter này phụ thuộc bổ sung model. Không có dữ liệu trong scope lọc trả `404 occupancy_not_found`; lỗi DB/service trả `503 service_unavailable`.
- Lịch sử occupancy lấy theo phòng và khoảng `start_time`–`end_time`, giới hạn/phân trang theo quy ước chung. Quyền student xem lịch sử chưa chốt.

## Đối chiếu FastAPI OpenAPI sinh từ mã

FastAPI sinh schema tại `/openapi.json` và giao diện `/docs` khi backend chạy. Đã thử nạp `backend/main.py` để lấy schema trực tiếp nhưng môi trường hiện tại thiếu package `fastapi`, nên chưa thể đọc OpenAPI runtime. Đối chiếu source tĩnh cho thấy backend đăng ký `GET /health` và `GET /api/v1/health`; các router occupancy, rooms, reservations, check-in và dashboard hiện rỗng; router auth và CV ingestion chưa được đăng ký. Vì vậy OpenAPI hiện tại chỉ mô tả health routes, không mô tả contract đề xuất trong tài liệu.

CV service có `GET /health` riêng ở service CV. Endpoint `/api/v1/cv/count-records` trong phụ lục là wire contract được tái sử dụng từ SEAT-34, chưa phải route đang chạy trong backend hiện tại. Các ví dụ API nghiệp vụ được đánh dấu PROPOSED và phải được so sánh lại với `/openapi.json` sau khi triển khai. Khi đó cần xác minh method/path, query/path params, schema JSON, status code và error response; lưu snapshot hoặc đưa kiểm tra lệch contract vào CI.

Lưu ý về scope CV: SEAT-34 chốt nhận CountResult batch với idempotency key `(session_id, frame_index)`; cùng key/cùng payload là duplicate, cùng key/khác payload trả `409 cv_record_conflict`. `CrossingEvent` và `event_id` là đề xuất endpoint riêng được yêu cầu bổ sung trong contract này, chưa thuộc payload batch SEAT-34 và chưa có persistence. Với endpoint riêng, cùng `event_id`/cùng payload trả receipt duplicate, payload khác trả `409 event_id_conflict`. API key `X-API-Key` cũng là yêu cầu bảo vệ contract, chưa được triển khai.

## Việc cần chốt / sửa

1. Triển khai các route auth, occupancy, rooms/history, bookings, check-in, dashboard và CV; đối chiếu từng route với OpenAPI sinh ra.
2. Chốt role matrix và scope xem dashboard/booking; thêm auth middleware và API key CV.
3. Chốt token/OTP và Portal SSO dựa trên thông tin trường; không chặn MVP OTP.
4. Chốt route `bookings` hay `reservations`, `check-in` hay prefix hiện có `/checkin`, pagination, timezone và chính sách xung đột.
5. Chốt QR/check-in, metrics dashboard và room/campus model.
6. Sau khi môi trường có dependency và app khởi động được, lưu snapshot `/openapi.json` hoặc chạy đối chiếu CI để phát hiện contract lệch implementation.

---\n\n## Phụ lục: Contract CV và occupancy chi tiết\n\n> Phần này giữ đặc tả CV đã thống nhất ở SEAT-18; payload lấy từ SEAT-34. Occupancy/rooms được hợp nhất với UC-01 của SEAT-39 ở phần contract chung phía trên.\n\n## 1. Mục đích và trạng thái

Tài liệu này ghi lại hợp đồng trao đổi dữ liệu đã thống nhất cho bản ghi đếm của CV và dữ liệu occupancy mới nhất mà Frontend hiển thị. Nhóm CV đồng ý dùng hợp đồng Backend; các thay đổi CV đã commit được giữ nguyên. Frontend đã duyệt response GET và cách hiển thị, gồm phân biệt null với 0, xử lý không có dữ liệu, ngưỡng dữ liệu cũ 30 giây và chu kỳ polling 5 giây.

Bộ tạo dữ liệu CV schema 1.0 hiện ghi bản ghi JSONL cục bộ. Phần này giữ contract HTTP đã thống nhất trong SEAT-18/34; các route ingestion không có trong nhánh hiện tại và bộ gửi/thử lại từ CV vẫn đang chờ. Các route kiểm thử video và webcam cục bộ của CV được mô tả ở mục 12, không phải endpoint nghiệp vụ của Backend. CountResult batch vẫn tách biệt với API occupancy trả dữ liệu cho Frontend.

## 2. Quy ước chung

- Tiền tố API: `/api/v1`.
- Body request và response dùng JSON UTF-8, tên trường theo `snake_case`.
- Số nguyên JSON phải là kiểu số, không phải chuỗi số. Thiếu giá trị không đồng nghĩa với `0`.
- Thời điểm dùng chuỗi date-time ISO 8601 có múi giờ. Backend chuẩn hóa thời điểm trả về thành UTC với hậu tố `Z`.
- `timestamp_ms` là độ lệch tương đối trong timeline nguồn hoặc phiên, không phải Unix time.
- Payload CV schema 1.0 từ chối trường không xác định; không tự ý đổi tên trường.
- `CountResult` là bản ghi của một frame. `CrossingEvent` là sự kiện riêng và không được nhận tại endpoint lưu bản ghi đếm hiện hành.

## 3. Các trường dữ liệu CV schema 1.0

### 3.1 CountResult (kết quả đếm)

| Trường | Kiểu | Bắt buộc | Ý nghĩa và kiểm tra |
|---|---|---:|---|
| `schema_version` | chuỗi | Không; mặc định `"1.0"` | Phiên bản schema dữ liệu CV. Backend hỗ trợ `1.0`. |
| `session_id` | chuỗi UUID | Có | Mã định danh một phiên xử lý CV. |
| `camera_id` | chuỗi | Có | Mã camera; từ 1 đến 100 ký tự và không được để trống. |
| `room_id` | chuỗi hoặc null | Không | Mã phòng phía CV; nếu có phải từ 1 đến 100 ký tự và không rỗng. Backend lưu nguyên giá trị vào `room_code`, chỉ liên kết với `rooms.id` khi khớp chính xác `rooms.code`. |
| `source_type` | chuỗi | Không; mặc định `"video"` | `"video"` hoặc `"webcam"`. Chỉ bản ghi webcam được dùng cho endpoint GET occupancy hiện tại. |
| `frame_index` | số nguyên | Có | Chỉ số frame bắt đầu từ 0, không âm. |
| `timestamp_ms` | số | Có | Độ lệch hữu hạn, không âm trong video/phiên. |
| `recorded_at` | chuỗi date-time | Có | Thời điểm CV xử lý bản ghi; phải có múi giờ, không nhất thiết là thời điểm camera ghi hình. |
| `people_count` | số nguyên | Có | Số người được phát hiện trong frame, kể cả người chưa có track ID xác nhận; không âm. Không đảm bảo đây là tổng số người trong phòng. |
| `tracked_count` | số nguyên | Có | Số người phát hiện có track ID xác nhận; `0 <= tracked_count <= people_count`. |
| `line_enabled` | boolean | Có | Cho biết chức năng đếm qua đường ảo có bật hay không. |
| `in_count` | số nguyên hoặc null | Không | Tổng tích lũy lượt IN trong phiên; bắt buộc khi `line_enabled` là true, phải null khi false. |
| `out_count` | số nguyên hoặc null | Không | Tổng tích lũy lượt OUT trong phiên; bắt buộc khi `line_enabled` là true, phải null khi false. |
| `initial_occupancy` | số nguyên hoặc null | Không | Số người ban đầu đã biết; không âm. |
| `estimated_occupancy` | số nguyên hoặc null | Không | `max(0, initial_occupancy + in_count - out_count)` nếu tính được; nếu không thì null. |
| `occupancy_underflow` | boolean | Không; mặc định false | True khi giá trị ước tính trước khi chặn về 0 là số âm. |

`people_count` là số người nhìn thấy được trên camera. `estimated_occupancy` ước tính số người trong phòng, phụ thuộc vào số ban đầu chính xác và việc camera quan sát được các lối vào/ra. `null` nghĩa là chưa biết; `0` là giá trị hợp lệ. IN/OUT là tổng tích lũy trong một phiên, không được cộng giữa các frame, phiên hoặc camera.

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

### 3.3 CrossingEvent (sự kiện cắt đường)

Schema CV 1.0 cũng định nghĩa `CrossingEvent` gồm `event_id`, `session_id`, `camera_id`, `room_id` tùy chọn, `frame_index`, `timestamp_ms`, `recorded_at`, `track_id`, `direction` (`IN`/`OUT`) và `confidence` (`0..1`). Đây là một sự kiện cắt đường riêng lẻ, không phải ảnh chụp occupancy của phòng.

**Phạm vi đã thống nhất:** chỉ lưu bản ghi CountResult. Không gửi CrossingEvent đến endpoint lưu bản ghi đếm hiện hành. Nếu sau này cần lịch sử sự kiện, bổ sung endpoint và cơ chế lưu trữ riêng.

## 4. CV → Backend: lưu bản ghi đếm

### 4.1 Endpoint

```http
POST /api/v1/cv/count-records
Content-Type: application/json
```

Request chứa một lô từ 1 đến 1000 bản ghi CountResult. Backend kiểm tra toàn bộ lô và lưu trong một transaction cơ sở dữ liệu; nếu có bản ghi sai hoặc xung đột, toàn bộ lô được rollback.

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

### 4.2 Ánh xạ dữ liệu và tính idempotent

- Lưu mỗi frame thành một hàng trong `cv_count_records`, tách biệt với `occupancy_records`. Không ánh xạ `people_count` thành `occupied_count`.
- Giữ chuỗi `room_id` của CV trong `room_code`. Chỉ ánh xạ sang `rooms.id` dạng số khi `room_code` khớp chính xác `rooms.code`. Nếu mã phòng không biết hoặc null, giữ nguyên mã và để liên kết phòng trong DB là null; không phân tích mã thành ID số và không tự tạo phòng.
- Khóa idempotent của bản ghi đếm là `(session_id, frame_index)`. Cùng khóa, cùng nội dung thì trả bản ghi hiện có; cùng khóa nhưng nội dung CV khác thì trả `409 cv_record_conflict`.
- Khi gửi lại phải dùng cùng khóa phiên/frame. Ánh xạ phòng là metadata; retry không ghi đè bản ghi đã lưu trước đó.

### 4.3 Gửi dữ liệu và response

- CV gửi các bản ghi cần lưu lịch sử theo lô, không gửi một request HTTP cho từng frame. Gửi khi lô đạt 100 bản ghi hoặc sau 1 giây, tùy điều kiện nào đến trước; kích thước tối đa là 1000. Gửi nốt dữ liệu còn lại khi phiên kết thúc.
- Thử lại tối đa ba lần khi timeout mạng hoặc nhận `503`, với khoảng chờ 1, 2 và 4 giây; giữ nguyên khóa. Không thử lại với `400`, `409` hoặc `422`. Giữ cục bộ các bản ghi chưa được xác nhận để gửi lại sau.
- Backend trả `200 OK` khi chấp nhận lô, kể cả các bản ghi trùng idempotent. Thứ tự bản ghi trong response giữ nguyên thứ tự request.

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

Bản ghi trong response có `room_id: null` nếu thiếu mã phòng CV hoặc mã chưa được ánh xạ. Gửi lại dữ liệu trùng khớp sẽ có `duplicate: true` và không làm thay đổi `received_at`.

### 4.4 Response lỗi

Backend dùng cấu trúc sau cho response lỗi:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Một hoặc nhiều bản ghi CV không hợp lệ",
    "details": [
      { "field": "records[0].tracked_count", "issue": "không được lớn hơn people_count" }
    ]
  }
}
```

| Mã HTTP | Mã lỗi | Ý nghĩa và cách CV xử lý |
|---|---|---|
| `400` | `malformed_json` | Body không phải JSON hợp lệ; sửa trước khi gửi lại. |
| `409` | `cv_record_conflict` | Khóa phiên/frame đã có nội dung khác; dừng retry và kiểm tra xung đột. |
| `422` | `validation_error` | Trường sai hoặc bị thiếu; sửa bản ghi trước khi gửi lại. |
| `503` | `database_unavailable` | Backend/DB tạm thời không khả dụng; gửi lại với cùng khóa. |

Mã phòng chưa biết không phải lỗi tiếp nhận: Backend lưu nguyên mã và để liên kết phòng trong cơ sở dữ liệu là null. API này dành cho mạng nội bộ giữa các dịch vụ; Backend/an ninh cần rà soát phương thức xác thực production trước khi cho phép truy cập từ bên ngoài.

## 5. Backend → Frontend: occupancy mới nhất của phòng

### 5.1 Endpoint

```http
GET /api/v1/occupancy/rooms/{room_id}/latest
```

`room_id` trên URL là `rooms.id` dạng số do API phòng Backend trả về. Endpoint đọc bản ghi `webcam` mới nhất đã ánh xạ cho phòng đó; không cộng số liệu từ nhiều camera. Bản ghi `video` dùng cho lịch sử/kiểm thử và không cập nhật occupancy trực tiếp.

### 5.2 Response khi đã có bản ghi

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

`is_stale` là true khi bản ghi được nhận cách thời điểm hiện tại hơn 30 giây, căn cứ theo `received_at`. Nếu `estimated_occupancy` là null, Frontend hiển thị “chưa xác định”; nếu bằng 0 thì hiển thị `0`. Chỉ hiển thị `people_count` kèm nhãn nói rõ đây là số người camera nhìn thấy.

### 5.3 Response khi thiếu dữ liệu hoặc gặp lỗi

Nếu phòng tồn tại nhưng chưa có bản ghi webcam, trả `404 occupancy_not_found`. Nếu ID phòng dạng số không tồn tại, trả `404 room_not_found`. Frontend phân biệt hai trường hợp này với số đếm 0 hợp lệ và với lỗi request/dịch vụ.

```json
{
  "error": {
    "code": "occupancy_not_found",
    "message": "Phòng này hiện chưa có dữ liệu occupancy trực tiếp"
  }
}
```

Frontend đã duyệt chu kỳ polling 5 giây và ngưỡng dữ liệu cũ 30 giây. Frontend xem null là chưa xác định và 0 là số đếm hợp lệ.

## 6. Quy tắc kiểm tra dữ liệu

- `schema_version` phải thuộc schema được hỗ trợ (`1.0`).
- `session_id` phải là UUID; các mã định danh không được để trống.
- `frame_index` và các số đếm phải không âm, nằm trong phạm vi số nguyên đã quy định; `timestamp_ms` phải hữu hạn và không âm.
- `tracked_count` không được lớn hơn `people_count`.
- `recorded_at` phải có thông tin múi giờ; Backend lưu và trả thời điểm theo UTC.
- Khi `line_enabled` là true, phải có `in_count` và `out_count`. Khi false, hai trường này cùng `initial_occupancy` phải là null.
- Khi biết `initial_occupancy`, `estimated_occupancy` và `occupancy_underflow` phải khớp công thức `max(0, initial_occupancy + in_count - out_count)`.
- Từ chối trường không xác định. Không chuyển trường đếm bị thiếu thành 0.

## 7. Giới hạn dữ liệu và độ mới

- `people_count` là số người nhìn thấy trong một frame, không đảm bảo bằng tổng số người trong phòng.
- `estimated_occupancy` phụ thuộc vào số người ban đầu chính xác và việc camera bao quát được các lối ra/vào liên quan.
- Bộ đếm CV được đặt lại ở mỗi phiên. Hợp đồng hiện tại hỗ trợ một nguồn camera hoạt động trên mỗi phòng cho màn hình trực tiếp của Frontend; chưa bao gồm tổng hợp nhiều camera.
- `recorded_at` là thời điểm CV xử lý. Backend gán `received_at` khi lưu bản ghi lần đầu và dùng trường này để đánh giá độ mới. `timestamp_ms` vẫn là độ lệch tương đối trong nguồn/phiên.
- Kiểm thử logic không chứng minh độ chính xác thực tế. Vị trí camera, vật cản, mất track và cấu hình đường đếm có thể ảnh hưởng kết quả.

## 8. Các trường hợp tích hợp cần xác minh

| Trường hợp | Hành vi mong đợi |
|---|---|
| Lô hợp lệ có một bản ghi | Lưu một bản ghi và trả receipt. |
| Lô hợp lệ có nhiều bản ghi | Lưu toàn bộ một cách nguyên tử và trả receipt theo thứ tự request. |
| Gửi lại cùng khóa phiên/frame | Trả bản ghi hiện có với `duplicate: true`; không tạo hàng thứ hai. |
| Cùng khóa nhưng nội dung khác | Trả `409 cv_record_conflict`; rollback toàn bộ lô. |
| Mã phòng không biết hoặc null | Chấp nhận và giữ nguyên mã; trả `room_id: null`. |
| Số người nhìn thấy/ước tính bằng 0 | Chấp nhận `0` là giá trị hợp lệ. |
| Occupancy ước tính là null | Giữ null; Frontend hiển thị chưa xác định, không đổi thành 0. |
| Thiếu trường, sai kiểu hoặc sai công thức đếm | Trả `422 validation_error` kèm đường dẫn trường. |
| `recorded_at` không có múi giờ | Từ chối với `422 validation_error`. |
| Backend timeout hoặc trả `503` | CV gửi lại với cùng khóa phiên/frame. |
| GET phòng chưa có dữ liệu webcam | Trả `404 occupancy_not_found`. |
| GET có giá trị ước tính bằng 0 | Trả `200` với `estimated_occupancy: 0`. |
| GET có bản ghi cũ hơn 30 giây | Trả bản ghi với `is_stale: true`. |

## 9. Trạng thái triển khai

| Hạng mục | Trạng thái |
|---|---|
| Trường và ngữ nghĩa CountResult schema 1.0 | CV cung cấp; được ghi trong tài liệu này. |
| Cấu trúc lưu Backend và ánh xạ mã phòng | Hợp đồng thống nhất dựa trên thiết kế lưu trữ SEAT-24. |
| Endpoint HTTP nhận lô dữ liệu CV và response | Từng được triển khai trong SEAT-19; không có handler trong nhánh hiện tại. |
| Bộ gửi CV, hàng đợi retry và cấu hình URL Backend | Chưa có trong phần CV SEAT-17 đã commit; cần thực hiện tiếp. Các commit CV hiện có được giữ nguyên. |
| Response mới nhất và cách xử lý dữ liệu cũ/thiếu của Frontend | Frontend xác nhận trong SEAT-18/19; endpoint không có handler trong nhánh hiện tại. |
| Tiếp nhận CrossingEvent qua HTTP | Nằm ngoài phạm vi đã thống nhất. |
| Xác minh tích hợp CV, Backend và Frontend | Đang chờ triển khai endpoint; tài liệu đã có ví dụ request/response phục vụ công việc này. |

## 10. Biên bản thống nhất

| Quyết định | Hợp đồng thống nhất | Trạng thái |
|---|---|---|
| Quyết định | Hợp đồng thống nhất | Trạng thái |
| Giá trị hiển thị làm occupancy phòng | Dùng `estimated_occupancy`; lưu riêng `people_count`. | CV và Frontend xác nhận |
| Ánh xạ phòng | `room_id` của CV là mã phòng; chỉ ánh xạ chính xác với `rooms.code`, giữ mã chưa ánh xạ và để khóa ngoại null. | CV đồng ý theo hợp đồng Backend |
| Tổng hợp camera/phiên | Một camera hoạt động trên mỗi phòng; không tổng hợp nhiều phiên/camera. | Phạm vi Backend; CV theo hợp đồng này |
| Cách gửi endpoint đếm | Lô tối đa 1000; gửi khi đạt 100 bản ghi hoặc sau 1 giây; retry dùng lại `(session_id, frame_index)`. | CV đồng ý theo hợp đồng Backend; bộ gửi chưa được triển khai |
| CrossingEvent | Không gửi/lưu qua endpoint đếm; nếu cần lịch sử sự kiện thì tạo API riêng sau. | Ngoài phạm vi hiện tại |
| Response Frontend | ID phòng Backend dạng số; gồm `estimated_occupancy`, metadata, `received_at` và `is_stale`. | Frontend xác nhận |
| Không có dữ liệu và độ mới | `404 occupancy_not_found`; dữ liệu cũ sau 30 giây; Frontend polling 5 giây. | Frontend xác nhận |
| Xác thực dịch vụ | Dùng mạng riêng giữa các dịch vụ ở môi trường phát triển; Backend/an ninh cần quyết định phương thức production trước khi mở ra ngoài. | Quyết định triển khai còn mở |

Các xác nhận của CV và Frontend do chủ sở hữu Backend ghi nhận ngày 2026-10-30. Cập nhật hợp đồng nếu một trong hai nhóm yêu cầu thay đổi. Cần quyết định riêng phương thức xác thực production trước khi mở API ra bên ngoài.

## 11. Danh sách nghiệm thu SEAT-18

- [x] Bản thảo liệt kê các trường CV, kiểu dữ liệu, ý nghĩa và quy tắc kiểm tra.
- [x] Có ví dụ request/response giữa CV và Backend, Backend và Frontend.
- [x] Đề xuất cách xử lý dữ liệu thiếu/sai, bản ghi trùng, thời điểm và lỗi kết nối.
- [x] CV đồng ý theo hợp đồng Backend; các file CV đã commit được giữ nguyên.
- [x] Frontend xác nhận response GET, cách xử lý null/0/không có dữ liệu/dữ liệu cũ và chu kỳ polling.
- [x] Có ví dụ JSON phục vụ kiểm thử tích hợp sau này.

Các route Backend và ví dụ đã được ghi để phục vụ tích hợp. Việc xác minh end-to-end với bộ gửi CV và Frontend thực tế vẫn là công việc tiếp theo, không phải điều kiện phê duyệt tài liệu hợp đồng này.

## 12. API kiểm thử CV cục bộ thuộc SEAT-17

Các route sau thuộc dịch vụ kiểm thử cục bộ của CV. Chúng tách biệt với API nghiệp vụ Backend và không triển khai endpoint tiếp nhận của Backend ở mục 4.

### Giao diện kiểm thử CV cục bộ

- `GET /`: giao diện HTML kiểm thử cục bộ; tài nguyên giao diện nằm trong `/static/`.
- `GET /api/config`: trạng thái sẵn sàng của model và thiết bị đang chọn, không trả đường dẫn cục bộ.
- `POST /api/jobs`: nhận video multipart ở trường `file` và chuỗi JSON `options`; trả `202` cùng mã job. Giới hạn 200 MB; mỗi lần chỉ chạy một job (`409` nếu đang bận), `503` nếu thiếu model, `415` nếu phần mở rộng không hỗ trợ, `422` nếu options không hợp lệ.
- `GET /api/jobs/{id}`: trả trạng thái, bản ghi mới nhất cùng JPEG base64 tương ứng, sự kiện gần đây, bản tóm tắt đã lọc và lỗi. Trạng thái có thể lần lượt là uploading/loading/processing rồi completed/cancelled/failed.
- `POST /api/jobs/{id}/stop`: yêu cầu hủy hợp tác sau khi xử lý frame hiện tại.
- `GET /api/jobs/{id}/preview`: JPEG mới nhất; trả `404` trước frame đầu tiên.
- `GET /api/jobs/{id}/files/{kind}`: xuất csv/jsonl/debug/events/summary; chỉ có sau khi completed/cancelled (`409` nếu chưa). ID hoặc loại file không biết trả `404`.

Đây là route kiểm thử CV, không phải endpoint nghiệp vụ Backend. Metadata của job nằm trong bộ nhớ và mất khi khởi động lại; file đầu ra vẫn ở cục bộ cho đến khi được xóa thủ công.

### Kiểm thử webcam trên trình duyệt

- `POST /api/webcam`: nhận options JSON như khi xử lý video; giữ chỗ xử lý suy luận và bắt đầu phiên tracking mới, trả `202` cùng mã job.
- `POST /api/webcam/{id}/frame`: nhận byte JPEG, tối đa 2 MB và cạnh ảnh sau giải mã tối đa 1920 px. Trả bản ghi đếm có `source_type: webcam` cùng bounding box phục vụ gỡ lỗi. Xử lý từng frame một; `409` nếu đang bận/đã dừng, `422` nếu frame không hợp lệ.
- Dừng và xuất file dùng chung các endpoint job. Timestamp nguồn webcam dùng đồng hồ monotonic tính từ đầu phiên; `recorded_at` là thời điểm xử lý theo UTC.
- Trình duyệt chỉ truy cập camera sau khi người dùng bấm Start Test và cấp quyền. Không thu âm hoặc ghi video webcam. Dừng trước khi rời trang; nếu client bị crash, có thể cần khởi động lại dịch vụ cục bộ để giải phóng phiên còn treo.
