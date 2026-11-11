# Hợp đồng API - UTH-SeatSense

> **Công việc:** SEAT-18 - Hợp đồng API với mô-đun CV
> **Trạng thái:** Backend, CV và Frontend đã thống nhất hợp đồng; các route Backend thuộc SEAT-19 đã được triển khai. Tích hợp bộ gửi dữ liệu từ CV sang Backend vẫn đang chờ thực hiện.
> **Nguồn:** Hợp đồng dữ liệu CV schema 1.0 và thiết kế lưu trữ PostgreSQL SEAT-24.
> **Cập nhật gần nhất:** 2026-10-30

## Endpoint tổng occupancy cho Dashboard

- `GET /api/v1/occupancy/current` trả tổng số người từ bản ghi mới nhất của từng
  phòng đang hoạt động, cùng các trường `current_count`, `updated_at` và
  `location`. Số lượng và thời điểm là `null` nếu chưa có dữ liệu.
- Endpoint tổng hợp mọi phòng đang hoạt động vì schema phòng hiện tại chưa có
  mã cơ sở. Muốn lọc theo cơ sở cần bổ sung ánh xạ này vào mô hình dữ liệu.

## 1. Mục đích và trạng thái

Tài liệu này ghi lại hợp đồng trao đổi dữ liệu đã thống nhất cho bản ghi đếm của CV và dữ liệu occupancy mới nhất mà Frontend hiển thị. Nhóm CV đồng ý dùng hợp đồng Backend; các thay đổi CV đã commit được giữ nguyên. Frontend đã duyệt response GET và cách hiển thị, gồm phân biệt null với 0, xử lý không có dữ liệu, ngưỡng dữ liệu cũ 30 giây và chu kỳ polling 5 giây.

Bộ tạo dữ liệu CV schema 1.0 hiện ghi bản ghi JSONL cục bộ. Tài liệu này định nghĩa giao tiếp HTTP cho các route Backend thuộc SEAT-19; tích hợp gửi dữ liệu và thử lại từ CV vẫn đang chờ. Các route kiểm thử video và webcam cục bộ của CV được mô tả ở mục 12, không phải endpoint nghiệp vụ của Backend. Định dạng request occupancy hiện có của SEAT-19 vẫn tách biệt với bản ghi CV thô theo từng frame.

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
| Endpoint HTTP nhận lô dữ liệu CV và response | Đã được triển khai trong API Backend thuộc SEAT-19. |
| Bộ gửi CV, hàng đợi retry và cấu hình URL Backend | Chưa có trong phần CV SEAT-17 đã commit; cần thực hiện tiếp. Các commit CV hiện có được giữ nguyên. |
| Response mới nhất và cách xử lý dữ liệu cũ/thiếu của Frontend | Frontend xác nhận; API Backend thuộc SEAT-19 đã triển khai. |
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
