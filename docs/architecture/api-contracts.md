# API contract — tổng quan

> Trạng thái: bản rà soát / đề xuất, chưa phải toàn bộ contract đã được triển khai.
> Ngày đối chiếu: 2026-11-11. Contract CV chi tiết nằm ở phụ lục cuối tài liệu.

## Quy ước chung

- Prefix `/api/v1`; JSON UTF-8, tên trường `snake_case`.
- Date-time dùng ISO 8601 có múi giờ; server trả UTC dạng `Z`. Thời điểm không có timezone bị từ chối.
- Danh sách dùng `limit` (mặc định 50, tối đa 100) và `offset` (mặc định 0); response đề xuất `{ "items": [], "limit": 50, "offset": 0, "total": 0 }`. Chưa có quy ước phân trang được triển khai/đồng thuận trong mã.
- Lỗi có dạng `{ "error": { "code": "...", "message": "...", "details": [{ "field": "...", "issue": "..." }] } }`; bỏ `details` nếu không có. `400` JSON sai, `401` thiếu/sai token, `403` không đủ quyền, `404` không tồn tại, `409` xung đột trạng thái/khóa idempotency, `422` dữ liệu hợp lệ về cú pháp nhưng sai quy tắc. Mã 401/403 là mục tiêu, chưa có auth middleware hiện tại.
- Mọi API nghiệp vụ người dùng yêu cầu `Authorization: Bearer <access_token>`. Web và Android native dùng chung issuer/audience và token; refresh/revoke, thời hạn, lưu trữ token và CSRF cho web chưa chốt.
- Portal/SSO: dành integration seam (`provider=portal`, `external_subject`), trạng thái chờ trường cung cấp issuer, protocol, claim mapping và quy trình duyệt. Không thu hoặc lưu mật khẩu Portal. MVP hiện có thể dùng OTP email theo DEC-08.
- CV dùng API key riêng, không dùng token người dùng: `X-API-Key`. Cách cấp/luân chuyển/lưu key và production secret store chưa chốt.
- CV event: `event_id` UUID là idempotency key; cùng ID cùng payload trả lại receipt đã tạo, cùng ID payload khác trả `409 event_id_conflict`. Đây là đề xuất cho endpoint sự kiện tương lai; endpoint CV hiện tại nhận frame batch với khóa `(session_id, frame_index)`, chưa nhận `event_id`.

## Endpoint inventory và vai trò

`STUB` nghĩa là router hiện rỗng; `PROPOSED` là hợp đồng cần triển khai. Các endpoint CV/occupancy đang có được đánh dấu `IMPLEMENTED` theo source hiện tại.

| Nhóm | Phương thức / URL | Vai trò gọi | Trạng thái và ý nghĩa |
|---|---|---|---|
| Auth | `POST /api/v1/auth/register` | Public | PROPOSED — đăng ký email/OTP; chưa có router |
| Auth | `POST /api/v1/auth/login` | Public | PROPOSED — xác minh OTP, phát token chung web/native |
| Auth | `POST /api/v1/auth/logout` | `authenticated` | PROPOSED — thu hồi refresh session; semantics chờ chốt |
| Auth | `GET /api/v1/auth/me` | `authenticated` | PROPOSED — hồ sơ và role hiện tại |
| Occupancy | `GET /api/v1/occupancy/current` | `student`, `librarian`, `admin` | IMPLEMENTED — tổng occupancy phòng active; không có campus filter |
| Occupancy | `GET /api/v1/occupancy/rooms/{room_id}/latest` | `student`, `librarian`, `admin` | IMPLEMENTED — CV webcam mới nhất; 404 nếu không có record |
| Rooms | `GET /api/v1/rooms` | `authenticated` | STUB — danh sách/phân trang đề xuất |
| Rooms | `GET /api/v1/rooms/{room_id}` | `authenticated` | STUB — chi tiết phòng đề xuất |
| Bookings | `GET /api/v1/bookings` | Chủ booking; librarian/admin xem phạm vi được cấp | PROPOSED — đổi tên từ reservations để thống nhất thuật ngữ; hiện schema/router placeholder reservations |
| Bookings | `POST /api/v1/bookings` | `student` | PROPOSED — tạo booking |
| Bookings | `GET /api/v1/bookings/{booking_id}` | Chủ booking, librarian/admin | PROPOSED — chi tiết |
| Bookings | `DELETE /api/v1/bookings/{booking_id}` | Chủ booking, librarian/admin | PROPOSED — hủy; semantics hủy chờ chốt |
| Check-in | `POST /api/v1/check-in` | `student` | PROPOSED — check-in booking bằng QR/token |
| Dashboard | `GET /api/v1/dashboard/summary` | `librarian`, `admin` | PROPOSED — chỉ số vận hành; metrics/filters cần chốt |
| Health | `GET /health`, `GET /health/db` | Public/monitoring | IMPLEMENTED nhưng ngoài `/api/v1` |
| CV | `POST /api/v1/cv/count-records` | CV service với API key | IMPLEMENTED trong mã, nhưng API key chưa triển khai |
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
| `GET /api/v1/occupancy/current` IMPLEMENTED | User có quyền xem occupancy (role enforcement chưa triển khai) | — | `—` | `200 {"current_count":12,"updated_at":"2026-11-11T08:00:00Z","location":"Thư viện UTH"}`; các count/time có thể `null` khi chưa có record | 400 không áp dụng; 401/403 dự kiến sau auth; 404 không áp dụng; 409 không áp dụng; 422 hiện không có query/path input |
| `GET /api/v1/occupancy/rooms/{room_id}/latest` IMPLEMENTED | User có quyền xem occupancy (role enforcement chưa triển khai) | `room_id`: integer >0, id database; Bearer token tương lai | `—` | `200 {"room_id":14,"room_code":"A101","camera_id":"cam-01","source_type":"webcam","people_count":3,"tracked_count":2,"estimated_occupancy":3,"occupancy_underflow":false,"recorded_at":"2026-11-11T08:00:00Z","received_at":"2026-11-11T08:00:01Z","is_stale":false}` | 400 không áp dụng; 401/403 dự kiến; 404 `room_not_found` hoặc `occupancy_not_found`; 409 không áp dụng; 422 room_id không hợp lệ |
| `GET /api/v1/rooms` PROPOSED (router STUB) | `authenticated` | `limit` 1..100 (default 50), `offset` ≥0 (default 0), tùy chọn `building`, `is_active` | `—` | `200 {"items":[{"id":14,"code":"A101","name":"Phòng A101","capacity":40,"is_active":true}],"limit":50,"offset":0,"total":1}` | 400 malformed query; 401 thiếu token; 403 không có quyền; 404 không áp dụng; 409 không áp dụng; 422 limit/offset/filter sai |
| `GET /api/v1/rooms/{room_id}` PROPOSED (router STUB) | `authenticated` | `room_id` integer dương | `—` | `200 {"id":14,"code":"A101","name":"Phòng A101","capacity":40,"is_active":true}` | 400 không áp dụng; 401; 403; 404 `room_not_found`; 409 không áp dụng; 422 id sai |
| `GET /api/v1/bookings` PROPOSED | User; mặc định chỉ booking của mình; librarian/admin theo scope | `from`, `to` ISO8601 tùy chọn; `status`; `limit`, `offset` | `—` | `200 {"items":[{"id":"bkg_456","room_id":14,"status":"confirmed","starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z"}],"limit":50,"offset":0,"total":1}` | 400 malformed query; 401; 403 truy cập ngoài scope; 404 không áp dụng; 409 range/filter conflict; 422 date/status/pagination sai |
| `POST /api/v1/bookings` PROPOSED | `student` | Bearer token | `{"room_id":14,"starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z"}` | `201 {"id":"bkg_456","room_id":14,"user_id":"usr_123","status":"confirmed","starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z","created_at":"2026-11-11T08:00:00Z"}` | 400 malformed JSON; 401; 403 role/booking quota; 404 room không tồn tại; 409 lịch phòng bị trùng; 422 khoảng giờ/field không hợp lệ |
| `GET /api/v1/bookings/{booking_id}` PROPOSED | Chủ booking, librarian/admin cùng scope | `booking_id` string | `—` | `200` booking object như response POST | 400 không áp dụng; 401; 403 ngoài owner/scope; 404 `booking_not_found`; 409 không áp dụng; 422 id sai |
| `DELETE /api/v1/bookings/{booking_id}` PROPOSED | Chủ booking, librarian/admin cùng scope | `booking_id` string | `—` | `204` không body | 400 không áp dụng; 401; 403 ngoài owner/scope; 404 không tồn tại; 409 đã check-in/không thể hủy; 422 id sai |
| `POST /api/v1/check-in` PROPOSED | `student` là chủ booking | Bearer token | `{"booking_id":"bkg_456","qr_token":"<opaque>"}` | `200 {"booking_id":"bkg_456","status":"checked_in","checked_in_at":"2026-11-12T02:04:00Z"}` | 400 malformed JSON; 401; 403 không phải chủ booking; 404 booking/token không tồn tại; 409 đã check-in/ngoài cửa sổ; 422 token hoặc body sai |
| `GET /api/v1/dashboard/summary` PROPOSED | `librarian`, `admin` | `from`, `to` ISO8601; scope campus/building chờ chốt | `—` | `200 {"occupancy":{"current":12,"capacity":40},"bookings":{"total":8,"checked_in":5,"no_show":1},"generated_at":"2026-11-11T08:00:00Z"}` | 400 malformed query; 401; 403 role/scope; 404 scope không tồn tại (nếu lọc theo scope); 409 range conflict; 422 date/filter sai |
| `POST /api/v1/cv/count-records` IMPLEMENTED, auth chưa có | CV service qua API key (header mục tiêu `X-API-Key`, chưa được code kiểm tra) | Header `Content-Type: application/json`; `X-API-Key` tương lai | `{"records":[{"schema_version":"1.0","session_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","camera_id":"cam-01","room_id":"A101","source_type":"webcam","frame_index":100,"timestamp_ms":10000,"recorded_at":"2026-11-11T08:00:00Z","people_count":3,"tracked_count":2,"line_enabled":true,"in_count":4,"out_count":1,"initial_occupancy":0,"estimated_occupancy":3,"occupancy_underflow":false}]}` | `200 {"status":"accepted","created_count":1,"duplicate_count":0,"records":[{"record_id":8123,"session_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","frame_index":100,"room_code":"A101","room_id":14,"received_at":"2026-11-11T08:00:01Z","duplicate":false}]}` | 400 JSON sai; 401 API key thiếu/sai (sau khi triển khai); 403 key hợp lệ nhưng không có scope; 404 không áp dụng; 409 cùng session/frame khác payload; 422 batch/schema sai |
| `POST /api/v1/cv/events` PROPOSED | CV service với API key | `X-API-Key` | `{"event_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","session_id":"...","camera_id":"cam-01","room_id":"A101","frame_index":100,"timestamp_ms":10000,"recorded_at":"2026-11-11T08:00:00Z","track_id":12,"direction":"IN","confidence":0.98}` | `200 {"event_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","accepted":true,"duplicate":false}`; retry giống payload trả `duplicate:true` | 400 JSON sai; 401 API key sai; 403 scope sai; 404 không áp dụng; 409 `event_id_conflict`; 422 schema sai |
| `GET /api/v1/notifications/subscriptions` PROPOSED / OPTIONAL (FR-OPT-01) | `authenticated` | Bearer token; `limit`, `offset` | `—` | `200 {"items":[{"id":"ntf_123","room_id":14,"condition":"seats_available","threshold":5,"enabled":true,"channel":"email"}],"limit":50,"offset":0,"total":1}` | 400 query sai; 401; 403; 404 không áp dụng; 409 không áp dụng; 422 pagination sai |
| `POST /api/v1/notifications/subscriptions` PROPOSED / OPTIONAL (FR-OPT-01) | `student` | Bearer token | `{"room_id":14,"condition":"seats_available","threshold":5,"channel":"email"}` | `201 {"id":"ntf_123","room_id":14,"condition":"seats_available","threshold":5,"enabled":true,"channel":"email","created_at":"2026-11-11T08:00:00Z"}` | 400 malformed JSON; 401; 403 role/scope; 404 room không tồn tại; 409 subscription trùng; 422 room không hỗ trợ occupancy hoặc field/channel không hợp lệ |
| `DELETE /api/v1/notifications/subscriptions/{subscription_id}` PROPOSED / OPTIONAL (FR-OPT-01) | Chủ subscription; admin | Bearer token; `subscription_id` string | `—` | `204` không body | 400 không áp dụng; 401; 403 không phải owner; 404 subscription không tồn tại; 409 đã bị xử lý/xóa; 422 id sai |
| `GET /health` IMPLEMENTED | Public/monitor | — | `—` | `200 {"status":"ok","service":"backend"}` | 400/401/403/404/409/422 không áp dụng |
| `GET /health/db` IMPLEMENTED | Public/monitor | — | `—` | `200 {"status":"ok","database":"postgresql"}` | `503 database_unavailable`; 400/401/403/404/409/422 không áp dụng |

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

`POST /bookings` body `{"room_id":14,"starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z"}` → `201` `{"id":"bkg_456","room_id":14,"user_id":"usr_123","status":"confirmed","starts_at":"2026-11-12T02:00:00Z","ends_at":"2026-11-12T03:00:00Z","created_at":"2026-11-11T08:00:00Z"}`. `GET /bookings?from=...&to=...&limit=50&offset=0` → trang có `items` booking và metadata phân trang. Trùng lịch trả `409 booking_conflict`; thời lượng, giờ hoạt động, trạng thái, timezone nghiệp vụ và tên route reservations vs bookings chưa chốt.

### Check-in

`POST /check-in` body `{"booking_id":"bkg_456","qr_token":"<opaque>"}` → `200` `{"booking_id":"bkg_456","status":"checked_in","checked_in_at":"2026-11-12T02:04:00Z"}`. Token QR, cửa sổ check-in, retry idempotency và response khi đã check-in chưa chốt.

### Dashboard

`GET /dashboard/summary?from=...&to=...` → `200` `{"occupancy":{"current":12,"capacity":40},"bookings":{"total":8,"checked_in":5,"no_show":1},"generated_at":"2026-11-11T08:00:00Z"}`. Định nghĩa metrics, quyền theo campus và phạm vi thời gian chưa chốt.

### CV event đề xuất

`POST /cv/events` với `X-API-Key: <service-key>` body `{"event_id":"6f228318-ea31-46b3-a1a7-c562288ea97e","session_id":"...","camera_id":"cam-01","room_id":"A101","frame_index":100,"timestamp_ms":10000,"recorded_at":"2026-11-11T08:00:00Z","track_id":12,"direction":"IN","confidence":0.98}` → `200` `{"event_id":"...","accepted":true,"duplicate":false}`. Cùng event gửi lại trả `duplicate:true`; khác nội dung cùng ID trả `409`. Lưu event và quan hệ event/frame chưa có trong persistence hiện tại.

## Đối chiếu FastAPI OpenAPI sinh từ mã

OpenAPI chuẩn nằm ở `/openapi.json` khi app khởi động. Tại lần rà soát này không thể sinh schema: import `backend/main.py` lỗi `ImportError: cannot import name 'CVRecordConflict' from app.repositories.cv_count_repository` (CV endpoint import symbol không tồn tại). Đây là blocker phải sửa trước khi có thể đối chiếu schema máy chính xác.

Đọc source cho thấy endpoint business được khai báo là `GET /api/v1/occupancy/current`, `GET /api/v1/occupancy/rooms/{room_id}/latest`, `POST /api/v1/cv/count-records`. Router `rooms`, `reservations`, `checkin`, `dashboard` rỗng; auth không có. `GET /health` và `/health/db` ở root, ngoài prefix. OpenAPI nếu sinh được sẽ phản ánh tình trạng này, không thể hiện các route PROPOSED ở trên.

Có thêm khác biệt contract/implementation cần giải quyết: tài liệu CV nói trùng khóa frame cùng nội dung trả bản ghi cũ, payload khác trả 409; implementation repository hiện dùng upsert overwrite và trả `duplicate=false`, trong khi endpoint import exception conflict chưa tồn tại. `GET /occupancy/rooms/{id}/latest` document có 503 nhưng decorator OpenAPI mới khai báo 404/422/503 trong source; response có thể phụ thuộc schema. Contract tổng quát hiện không được đảm bảo bởi auth, pagination hay quyền vì chưa có implementation.

## Việc cần chốt / sửa

1. Sửa `CVRecordConflict` và semantics upsert/idempotency; chọn frame idempotency theo contract CV hiện hành.
2. Chốt role matrix và scope xem dashboard/booking; thêm auth middleware và API key CV.
3. Chốt token/OTP và Portal SSO dựa trên thông tin trường; không chặn MVP OTP.
4. Chốt route `bookings` hay `reservations`, pagination, timezone và chính sách xung đột.
5. Chốt QR/check-in, metrics dashboard và room/campus model.
6. Sau khi app import thành công, lưu snapshot `/openapi.json` hoặc chạy đối chiếu CI để phát hiện contract lệch implementation.

---

## Phụ lục: Contract CV và occupancy chi tiết

# API Contracts - UTH-SeatSense

> Tổng quan contract API, endpoint auth/rooms/bookings/check-in/dashboard,
> quy ước chung và đối chiếu OpenAPI được ghi ở phần đầu tài liệu.
> Tài liệu hiện tại tiếp tục ghi contract chi tiết CV và occupancy.

> Task: SEAT-18 - API contract with the CV module
> Status: Contract agreed by Backend, CV, and Frontend; SEAT-19 Backend routes are implemented. CV-to-Backend sender integration remains pending.
> Source: CV Data Contract schema 1.0 and the SEAT-24 PostgreSQL persistence design.
> Last updated: 2026-10-30

## Dashboard occupancy endpoint

- `GET /api/v1/occupancy/current` returns the total occupancy from the latest
  record for each active room, with `current_count`, `updated_at`, and
  `location`. The count and timestamp are `null` when no records exist.
- The endpoint aggregates all active rooms because the current room schema has
  no campus identifier. Campus-specific filtering requires adding that mapping
  to the data model.

## 1. Purpose and status

This document records the agreed wire contract for CV count records and the latest occupancy data shown by Frontend. The CV owner agreed to follow the Backend contract, with already committed CV work left untouched. Frontend approved the GET response and display behavior, including null versus zero, no-data handling, the 30-second stale threshold, and 5-second polling.

The CV schema 1.0 producer currently writes local JSONL records. This document defines the HTTP boundary used by the SEAT-19 Backend routes; the CV sender/retry integration is still pending. CV's local video and webcam testing routes are described in section 12 and are not Backend business endpoints. The existing SEAT-19 occupancy request format remains separate from raw per-frame CV records.

## 2. General conventions

- API base path: `/api/v1`.
- Request and response bodies use UTF-8 JSON with `snake_case` field names.
- JSON integers are numbers, not numeric strings. A missing value is not the same as `0`.
- Timestamps are ISO 8601 date-time strings with a timezone. Backend normalizes returned timestamps to UTC with a `Z` suffix.
- `timestamp_ms` is a relative offset within the source or session timeline. It is not Unix time.
- CV schema 1.0 payloads reject unknown fields. Do not rename fields silently.
- A `CountResult` is a frame record. A `CrossingEvent` is a separate event and is not accepted by the count-record endpoint below.

## 3. CV schema 1.0 data fields

### 3.1 CountResult

| Field | Type | Required | Meaning and validation |
|---|---|---:|---|
| `schema_version` | string | No; defaults to `"1.0"` | CV contract version. Backend supports `1.0`. |
| `session_id` | UUID string | Yes | Identifier for one CV processing session. |
| `camera_id` | string | Yes | Camera identifier; 1-100 non-blank characters. |
| `room_id` | string or null | No | CV room code; 1-100 non-blank characters when present. Backend preserves it as `room_code` and links it to `rooms.id` only when it exactly matches `rooms.code`. |
| `source_type` | string | No; defaults to `"video"` | `"video"` or `"webcam"`. Only webcam records feed the current-occupancy GET endpoint. |
| `frame_index` | integer | Yes | Zero-based frame number; non-negative. |
| `timestamp_ms` | number | Yes | Non-negative, finite offset within the video/session. |
| `recorded_at` | date-time string | Yes | Time CV processed the record; must include a timezone. It is not necessarily camera capture time. |
| `people_count` | integer | Yes | People detected in this frame, including detections without confirmed track IDs; non-negative. It is not guaranteed whole-room occupancy. |
| `tracked_count` | integer | Yes | Detected people with confirmed track IDs; `0 <= tracked_count <= people_count`. |
| `line_enabled` | boolean | Yes | Whether virtual-line counting is enabled. |
| `in_count` | integer or null | No | Cumulative IN count for this session. Required when `line_enabled` is true; null when false. |
| `out_count` | integer or null | No | Cumulative OUT count for this session. Required when `line_enabled` is true; null when false. |
| `initial_occupancy` | integer or null | No | Known starting number of people; non-negative. |
| `estimated_occupancy` | integer or null | No | `max(0, initial_occupancy + in_count - out_count)` when calculable; otherwise null. |
| `occupancy_underflow` | boolean | No; defaults to false | True when the unclamped estimate was negative. |

`people_count` describes people visible to the camera. `estimated_occupancy` estimates people in the room and depends on a correct starting count and camera coverage of entrances/exits. `null` means unknown; `0` is a valid estimate. IN/OUT values are cumulative within a session and must not be summed across frames, sessions, or cameras.

### 3.2 CountResult example

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

### 3.3 CrossingEvent

CV schema 1.0 also defines `CrossingEvent` with `event_id`, `session_id`, `camera_id`, optional `room_id`, `frame_index`, `timestamp_ms`, `recorded_at`, `track_id`, `direction` (`IN`/`OUT`) and `confidence` (`0..1`). It is a discrete line-crossing event, not a room occupancy snapshot.

Agreed scope: store CountResult records only. Do not send CrossingEvent to the count endpoint. Add an event endpoint and persistence separately if the team later needs event history.

## 4. CV -> Backend: store count records

### 4.1 Endpoint

```http
POST /api/v1/cv/count-records
Content-Type: application/json
```

The request contains a batch of 1-1000 CountResult records. Backend validates the whole batch and saves it in one database transaction; if any record is invalid or conflicting, the batch is rolled back.

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

### 4.2 Mapping and idempotency

- Store one row per frame in `cv_count_records`, separate from `occupancy_records`. Do not map `people_count` to `occupied_count`.
- Keep CV's `room_id` string in `room_code`. Resolve `room_id` to the numeric `rooms.id` only when `room_code` exactly matches `rooms.code`. Preserve unknown or null room codes with a null database room link; do not parse them as numeric IDs or create rooms.
- The count-record idempotency key is `(session_id, frame_index)`. Same key and same content returns the existing record; same key with different CV content returns `409 cv_record_conflict`.
- A retry must use the same session/frame key. Room mapping is metadata and a retry does not rewrite a previously stored record.

### 4.3 Delivery and response

- CV sends all records needed for history in batches, not one HTTP request per frame. Send when a batch reaches 100 records or after 1 second, whichever comes first; maximum batch size is 1000. Flush remaining records when a session ends.
- Retry network timeouts and `503` up to three times with 1, 2, and 4 second delays, keeping the same keys. Do not retry `400`, `409`, or `422`. Retain unacknowledged records locally for later replay.
- Backend returns `200 OK` when the batch is accepted, including idempotent duplicates. Response records retain request order.

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

A response record has `room_id: null` if the CV room code is missing or not yet mapped. An identical retry has `duplicate: true` and does not change `received_at`.

### 4.4 Error response

Backend uses this envelope for errors:

```json
{
  "error": {
    "code": "validation_error",
    "message": "One or more CV records are invalid",
    "details": [
      { "field": "records[0].tracked_count", "issue": "must not exceed people_count" }
    ]
  }
}
```

| Status | Error code | Meaning and CV action |
|---|---|---|
| `400` | `malformed_json` | Body is not valid JSON; correct it before sending again. |
| `409` | `cv_record_conflict` | Same session/frame key has different content; stop retrying and investigate. |
| `422` | `validation_error` | Invalid or missing field; correct the record before retrying. |
| `503` | `database_unavailable` | Temporary Backend/DB failure; retry using the same keys. |

An unknown room code is not an ingestion error: Backend stores the raw code and leaves the database room link null. The API is intended for the internal service network; the production authentication method still needs Backend/security review before external exposure.

## 5. Backend -> Frontend: latest room occupancy

### 5.1 Endpoint

```http
GET /api/v1/occupancy/rooms/{room_id}/latest
```

`room_id` in this URL is the numeric `rooms.id` returned by the Backend room API. The endpoint reads the newest mapped `webcam` record for that room. It does not combine counts from multiple cameras. `video` records are history/test data and do not update live occupancy.

### 5.2 Response when a record exists

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

`is_stale` is true when the record was received more than 30 seconds ago, based on `received_at`. If `estimated_occupancy` is null, Frontend displays `unknown`; if it is zero, Frontend displays `0`. `people_count` may be shown only with a label that makes clear it is the number visible to the camera.

### 5.3 No-data and error response

If the room exists but has no webcam record, return `404 occupancy_not_found`. If the numeric room ID does not exist, return `404 room_not_found`. Frontend distinguishes both from a valid zero count and from request/service errors.

```json
{
  "error": {
    "code": "occupancy_not_found",
    "message": "No live occupancy record is available for this room"
  }
}
```

Frontend approved a polling interval of 5 seconds and a stale threshold of 30 seconds. Frontend treats null as unknown and zero as a valid count.

## 6. Validation rules

- `schema_version` must be supported (`1.0`).
- `session_id` must be a UUID; identifiers must not be blank.
- `frame_index` and counts must be non-negative and fit their documented integer ranges; `timestamp_ms` must be finite and non-negative.
- `tracked_count` must not exceed `people_count`.
- `recorded_at` must include timezone information; Backend stores UTC and returns UTC.
- When `line_enabled` is true, `in_count` and `out_count` are required. When false, they and `initial_occupancy` must be null.
- When `initial_occupancy` is known, `estimated_occupancy` and `occupancy_underflow` must agree with `max(0, initial_occupancy + in_count - out_count)`.
- Unknown fields are rejected. An absent count must not be converted to zero.

## 7. Data limitations and freshness

- `people_count` is the number of people visible in one frame, not guaranteed whole-room occupancy.
- `estimated_occupancy` depends on a correct initial occupancy and a camera covering the relevant entrances/exits.
- CV counters reset for each session. The current contract supports one active camera source per room for the live Frontend view; multi-camera aggregation is out of scope.
- `recorded_at` is the CV processing time. `received_at` is assigned by Backend when the row is first stored and is used for freshness. `timestamp_ms` remains a relative source/session offset.
- Logic tests do not prove real-world accuracy. Camera placement, occlusion, dropped tracks, and line configuration can affect results.

## 8. Integration examples to verify

| Case | Expected behavior |
|---|---|
| Valid one-record batch | Save one record and return its receipt. |
| Valid multi-record batch | Save all records atomically and return receipts in request order. |
| Identical session/frame retry | Return the existing record with `duplicate: true`; do not create a second row. |
| Same key, different content | Return `409 cv_record_conflict`; roll back the whole batch. |
| Unknown/null room code | Accept and preserve the code; return `room_id: null`. |
| Zero visible/estimated count | Accept `0` as a valid value. |
| Null estimated occupancy | Preserve null; Frontend shows unknown rather than zero. |
| Missing field, invalid type, invalid counter formula | Return `422 validation_error` with the field path. |
| Timezone-free `recorded_at` | Reject with `422 validation_error`. |
| Backend timeout or `503` | CV retries with the same session/frame keys. |
| GET for room with no webcam data | Return `404 occupancy_not_found`. |
| GET for valid zero estimate | Return `200` with `estimated_occupancy: 0`. |
| GET for record older than 30 seconds | Return the record with `is_stale: true`. |

## 9. Implementation status

| Item | Status |
|---|---|
| CV schema 1.0 CountResult fields and semantics | Supplied by CV; documented here. |
| Backend storage shape and room-code mapping | Agreed contract based on the SEAT-24 persistence design. |
| CV batch HTTP endpoint and response | Implemented by the SEAT-19 Backend API. |
| CV sender, retry queue, and Backend URL configuration | Not present in the committed SEAT-17 CV material; implementation remains follow-up work. Existing CV commits are unchanged. |
| Frontend latest response and stale/no-data behavior | Confirmed by Frontend; implemented by the SEAT-19 Backend API. |
| CrossingEvent HTTP ingestion | Excluded from the agreed scope. |
| Integration verification across CV, Backend, and Frontend | Pending endpoint implementation; request and response examples are included for that work. |

## 10. Agreement record

| Decision | Agreed contract | Status |
|---|---|---|
| Count value shown as room occupancy | Use `estimated_occupancy`; preserve `people_count` separately. | CV and Frontend confirmed |
| Room mapping | CV `room_id` is a room code; resolve exact `rooms.code`, preserve unmapped code with null FK. | CV agreed to follow Backend contract |
| Camera/session aggregation | One active camera per room in the current contract; do not aggregate sessions/cameras. | Backend scope; CV follows this contract |
| Count endpoint delivery | Batch up to 1000; flush at 100 records or 1 second; retries reuse `(session_id, frame_index)`. | CV agreed to follow Backend contract; sender is not implemented |
| CrossingEvent | Do not send/store through the count endpoint; add separate API in a later task if needed. | Excluded from current scope |
| Frontend response | Numeric Backend room ID; `estimated_occupancy`, metadata, `received_at`, and `is_stale`. | Frontend confirmed |
| No-data and freshness | `404 occupancy_not_found`; stale after 30 seconds; FE polling every 5 seconds. | Frontend confirmed |
| Service authentication | Private service network for development; production auth method must be decided before external exposure. | Open deployment decision for Backend/security |

The CV and Frontend confirmations were reported by the Backend owner on 2026-10-30. Update this contract if either team requests a change. Decide production authentication separately before external exposure.

## 11. SEAT-18 acceptance checklist

- [x] Draft lists the CV fields, types, meanings, and validation rules.
- [x] Draft includes CV-to-Backend and Backend-to-Frontend request/response examples.
- [x] Draft defines proposed missing-data, invalid-data, duplicate, timestamp, and connection-failure behavior.
- [x] CV agrees to follow the Backend contract; already committed CV files remain untouched.
- [x] Frontend confirms the GET response, null/zero/no-data/stale behavior, and polling interval.
- [x] JSON examples are available for future integration testing.

The Backend routes and examples are documented for integration. End-to-end verification with the live CV sender and Frontend remains follow-up work; it is not required to approve this contract document.

## 12. SEAT-17 CV local testing APIs

The following routes belong to CV's local testing service. They are separate from Backend business APIs and do not implement the Backend ingestion endpoint in section 4.

### Local CV testing UI

- `GET /`: local HTML testing interface; `/static/` contains its assets.
- `GET /api/config`: model availability and selected device, with no local path.
- `POST /api/jobs`: multipart `file` video and JSON string `options`; returns `202` with a job ID. Limit 200 MB; one job at a time (`409` when busy), `503` if the model is missing, `415` for an unsupported extension, and `422` for invalid options.
- `GET /api/jobs/{id}`: status, latest record and matching JPEG base64, recent events, sanitized summary and error. Status progresses through uploading/loading/processing to completed/cancelled/failed.
- `POST /api/jobs/{id}/stop`: cooperative cancellation after the current frame.
- `GET /api/jobs/{id}/preview`: latest JPEG; `404` before the first frame.
- `GET /api/jobs/{id}/files/{kind}`: csv/jsonl/debug/events/summary; available only after completed/cancelled (`409` otherwise). Unknown ID or kind returns `404`.

These are CV testing routes, not Backend business endpoints. Job metadata is in memory and disappears on restart; outputs remain local until manually removed.

### Browser webcam testing

- `POST /api/webcam`: JSON options as for video; reserves the inference slot and starts a fresh tracking session, returning `202` with a job ID.
- `POST /api/webcam/{id}/frame`: JPEG bytes, maximum 2 MB and maximum decoded edge 1920 px. Returns a count record with `source_type: webcam` and debug bounding boxes. One frame at a time; `409` if busy/stopped, `422` for an invalid frame.
- Stop and exports use the same job endpoints. Webcam source timestamps use monotonic time since session start; `recorded_at` is UTC processing time.
- The browser obtains camera access only after explicit Start Test and permission. No audio or webcam video recording. Stop before leaving the page; a crashed client may require restarting the local service to release an orphan session.
