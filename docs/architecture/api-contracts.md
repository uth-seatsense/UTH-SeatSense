# Hợp đồng API - UTH-SeatSense

> **Công việc:** SEAT-18 - Thống nhất hợp đồng API với mô-đun CV.
> **Trạng thái:** Backend, CV và Frontend đã thống nhất hợp đồng; các tuyến API Backend của SEAT-19 đã được triển khai. Việc tích hợp bộ gửi dữ liệu từ CV đến Backend còn chờ thực hiện.
> **Nguồn:** Hợp đồng dữ liệu CV v1.0 và thiết kế lưu trữ PostgreSQL của SEAT-24.
> **Cập nhật lần cuối:** 2026-11-11 — Lê Văn Trí bổ sung SEAT-34 tại mục 13.
>
> **Đối chiếu dev `df1c311`:** Mục 1–12 giữ hợp đồng SEAT-18 và ghi nhận lịch sử,
> không phải bằng chứng chạy thực tế hiện tại. Sai lệch mã nguồn và thiết kế sự kiện chưa
> triển khai được phân biệt tại mục 13.

## API số người hiện tại cho bảng tổng quan

- `GET /api/v1/occupancy/current` trả tổng số người từ bản ghi mới nhất của
  từng phòng đang hoạt động, gồm `current_count`, `updated_at` và `location`.
  Số người và thời điểm là `null` khi chưa có bản ghi.
- API tổng hợp tất cả phòng đang hoạt động vì cấu trúc dữ liệu phòng hiện tại
  chưa có mã cơ sở. Muốn lọc theo cơ sở cần bổ sung ánh xạ vào mô hình dữ liệu.

## 1. Mục đích và trạng thái

Tài liệu ghi lại hợp đồng trao đổi dữ liệu đã thống nhất cho bản ghi số đếm CV và dữ liệu số người mới nhất hiển thị trên Frontend. Người phụ trách CV đồng ý tuân theo hợp đồng Backend, giữ nguyên phần CV đã được ghi nhận trong lịch sử mã nguồn. Frontend đã duyệt phản hồi GET và cách hiển thị, gồm phân biệt chưa biết với số 0, xử lý khi thiếu dữ liệu, ngưỡng dữ liệu cũ 30 giây và chu kỳ lấy dữ liệu 5 giây.

Mô-đun CV v1.0 hiện ghi bản ghi JSONL cục bộ. Tài liệu định nghĩa giao tiếp HTTP của các tuyến Backend SEAT-19; việc tích hợp bộ gửi và gửi lại dữ liệu từ CV vẫn chưa hoàn tất. Các tuyến thử nghiệm video/webcam cục bộ của CV được mô tả ở mục 12, tách biệt với API nghiệp vụ Backend. Định dạng yêu cầu số người hiện có của SEAT-19 vẫn tách biệt với bản ghi CV thô theo từng khung hình.

## 2. Quy ước chung

- Đường dẫn gốc API: `/api/v1`.
- Nội dung yêu cầu/phản hồi dùng JSON mã hóa UTF-8, tên trường theo `snake_case`.
- Số nguyên JSON phải là số, không phải chuỗi chứa số. Thiếu giá trị khác với `0`.
- Thời điểm dùng chuỗi ngày giờ ISO 8601 có múi giờ. Backend chuẩn hóa thời điểm trả về thành UTC với hậu tố `Z`.
- `timestamp_ms` là độ lệch thời gian tương đối trong nguồn hoặc phiên xử lý, không phải thời gian Unix.
- Dữ liệu CV v1.0 từ chối trường không được định nghĩa. Không tự ý đổi tên trường mà không cập nhật hợp đồng.
- `CountResult` là bản ghi theo khung hình. `CrossingEvent` là sự kiện riêng, không được API nhận bản ghi số đếm v1 bên dưới chấp nhận.

## 3. Các trường dữ liệu CV v1.0

### 3.1 Bản ghi số đếm CountResult

| Trường | Kiểu dữ liệu | Bắt buộc | Ý nghĩa và kiểm tra hợp lệ |
|---|---|---:|---|
| `schema_version` | chuỗi | Không; mặc định `"1.0"` | Phiên bản hợp đồng CV. Backend hỗ trợ `1.0`. |
| `session_id` | chuỗi UUID | Có | Định danh một phiên xử lý CV. |
| `camera_id` | chuỗi | Có | Định danh camera; dài 1–100 ký tự, không chỉ gồm khoảng trắng. |
| `room_id` | chuỗi hoặc null | Không | Mã phòng CV; nếu có phải dài 1–100 ký tự, không chỉ gồm khoảng trắng. Backend giữ nguyên trong `room_code`, chỉ liên kết với `rooms.id` khi khớp chính xác `rooms.code`. |
| `source_type` | chuỗi | Không; mặc định `"video"` | `"video"` hoặc `"webcam"`. Chỉ bản ghi webcam cung cấp dữ liệu cho API GET số người hiện tại theo phòng. |
| `frame_index` | số nguyên | Có | Số thứ tự khung hình từ 0, không âm. |
| `timestamp_ms` | số | Có | Độ lệch thời gian trong video/phiên, hữu hạn và không âm. |
| `recorded_at` | chuỗi ngày giờ | Có | Thời điểm CV xử lý bản ghi, bắt buộc có múi giờ; không nhất thiết là thời điểm camera chụp hình. |
| `people_count` | số nguyên | Có | Số người phát hiện trong khung hình, kể cả người chưa có mã theo dõi được xác nhận; không âm. Không bảo đảm là số người trong toàn phòng. |
| `tracked_count` | số nguyên | Có | Số người phát hiện đã có mã theo dõi được xác nhận; `0 <= tracked_count <= people_count`. |
| `line_enabled` | giá trị đúng/sai | Có | Có bật đếm qua đường ảo hay không. |
| `in_count` | số nguyên hoặc null | Không | Tổng lượt IN trong phiên. Bắt buộc khi `line_enabled` là true; null khi false. |
| `out_count` | số nguyên hoặc null | Không | Tổng lượt OUT trong phiên. Bắt buộc khi `line_enabled` là true; null khi false. |
| `initial_occupancy` | số nguyên hoặc null | Không | Số người ban đầu đã biết, không âm. |
| `estimated_occupancy` | số nguyên hoặc null | Không | `max(0, initial_occupancy + in_count - out_count)` nếu tính được; nếu chưa biết thì null. |
| `occupancy_underflow` | giá trị đúng/sai | Không; mặc định false | True khi ước tính trước khi kẹp về 0 là số âm. |

`people_count` là số người camera nhìn thấy. `estimated_occupancy` ước tính số người trong phòng, phụ thuộc số người ban đầu chính xác và khả năng quan sát các lối vào/ra. `null` nghĩa là chưa biết; `0` là ước tính hợp lệ. IN/OUT là số cộng dồn trong phiên, không được cộng các giá trị này giữa các khung hình, phiên hoặc camera.

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

### 3.3 Sự kiện cắt đường ảo CrossingEvent

CV v1.0 còn định nghĩa `CrossingEvent` gồm `event_id`, `session_id`, `camera_id`, `room_id` tùy chọn, `frame_index`, `timestamp_ms`, `recorded_at`, `track_id`, `direction` (`IN`/`OUT`) và `confidence` (`0..1`). Đây là một sự kiện cắt đường ảo riêng lẻ, không phải bản ghi số người tại một thời điểm.

**Phạm vi v1 đã thống nhất:** chỉ lưu CountResult. Không gửi CrossingEvent đến API số đếm v1. Nếu cần lịch sử sự kiện, bổ sung API và cơ chế lưu sự kiện riêng trong bước sau.

## 4. CV → Backend: lưu bản ghi số đếm

### 4.1 Điểm cuối API

```http
POST /api/v1/cv/count-records
Content-Type: application/json
```

Yêu cầu chứa một lô từ 1–1000 bản ghi CountResult. Backend kiểm tra toàn bộ lô và lưu trong một giao dịch cơ sở dữ liệu; nếu có bản ghi không hợp lệ hoặc xung đột, hoàn tác toàn bộ lô.

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

- Mỗi khung hình lưu một dòng trong `cv_count_records`, tách biệt với `occupancy_records`. Không ánh xạ `people_count` sang `occupied_count`.
- Giữ chuỗi `room_id` của CV trong `room_code`. Chỉ ánh xạ sang số `rooms.id` khi `room_code` khớp chính xác `rooms.code`. Với mã chưa biết hoặc null, giữ nguyên mã và để liên kết phòng trong cơ sở dữ liệu là null; không ép thành ID số hoặc tự tạo phòng.
- Khóa chống ghi trùng là `(session_id, frame_index)`. Cùng khóa và cùng nội dung trả bản ghi đã có; cùng khóa nhưng khác nội dung CV trả `409 cv_record_conflict`.
- Gửi lại phải dùng cùng khóa phiên/khung hình. Ánh xạ phòng là dữ liệu bổ trợ; gửi lại không ghi đè bản ghi đã lưu.

### 4.3 Gửi dữ liệu và phản hồi

- CV gửi các bản ghi cần lưu lịch sử theo lô, không gửi một yêu cầu HTTP cho mỗi khung hình. Gửi khi đủ 100 bản ghi hoặc sau 1 giây, tùy điều kiện nào đến trước; tối đa 1000 bản ghi/lô. Gửi các bản ghi còn lại khi kết thúc phiên.
- Khi hết thời gian chờ mạng hoặc nhận `503`, gửi lại tối đa ba lần, chờ lần lượt 1, 2 và 4 giây, giữ nguyên khóa. Không tự gửi lại với `400`, `409`, `422`. Giữ bản ghi chưa được xác nhận ở máy cục bộ để gửi lại sau.
- Backend trả `200 OK` khi chấp nhận lô, kể cả bản ghi trùng đã được xử lý. Bản ghi phản hồi giữ thứ tự như yêu cầu.

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

Bản ghi phản hồi có `room_id: null` nếu thiếu mã phòng CV hoặc chưa ánh xạ được. Gửi lại cùng nội dung trả `duplicate: true` và không đổi `received_at`.

### 4.4 Phản hồi lỗi

Backend dùng cấu trúc lỗi sau. Chuỗi thông báo trong ví dụ được giữ nguyên theo API:

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

| Mã HTTP | Mã lỗi | Ý nghĩa và cách CV xử lý |
|---|---|---|
| `400` | `malformed_json` | Nội dung không phải JSON hợp lệ; sửa trước khi gửi lại. |
| `409` | `cv_record_conflict` | Cùng khóa phiên/khung hình nhưng khác nội dung; dừng gửi lại tự động và kiểm tra nguyên nhân. |
| `422` | `validation_error` | Trường thiếu hoặc không hợp lệ; sửa bản ghi trước khi gửi lại. |
| `503` | `database_unavailable` | Backend/cơ sở dữ liệu tạm lỗi; gửi lại với khóa cũ. |

Mã phòng chưa biết không làm yêu cầu tiếp nhận bị lỗi: Backend lưu mã gốc và để liên kết phòng là null. API dành cho mạng nội bộ giữa các dịch vụ; phương thức xác thực khi triển khai thực tế cần Backend và người phụ trách bảo mật rà soát trước khi cho truy cập từ bên ngoài.

## 5. Backend → Frontend: số người mới nhất theo phòng

### 5.1 Điểm cuối API

```http
GET /api/v1/occupancy/rooms/{room_id}/latest
```

`room_id` trong URL là số `rooms.id` do API phòng của Backend trả về. API đọc bản ghi `webcam` mới nhất đã ánh xạ vào phòng đó, không cộng số đếm từ nhiều camera. Bản ghi `video` dùng cho lịch sử/thử nghiệm, không cập nhật số người trực tiếp.

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

`is_stale` là true nếu đã quá 30 giây kể từ lúc nhận bản ghi, tính theo `received_at`. Nếu `estimated_occupancy` là null, Frontend hiển thị chưa biết; nếu bằng 0, hiển thị `0`. Chỉ được hiển thị `people_count` với nhãn ghi rõ đây là số người camera nhìn thấy.

### 5.3 Phản hồi khi thiếu dữ liệu hoặc có lỗi

Phòng tồn tại nhưng chưa có bản ghi webcam thì trả `404 occupancy_not_found`. ID phòng không tồn tại thì trả `404 room_not_found`. Frontend phải phân biệt hai trường hợp này với số 0 hợp lệ và lỗi yêu cầu/dịch vụ.

```json
{
  "error": {
    "code": "occupancy_not_found",
    "message": "No live occupancy record is available for this room"
  }
}
```

Frontend đã duyệt chu kỳ lấy dữ liệu 5 giây và ngưỡng dữ liệu cũ 30 giây. Null được hiểu là chưa biết, còn 0 là số đếm hợp lệ.

## 6. Quy tắc kiểm tra dữ liệu

- `schema_version` phải là phiên bản được hỗ trợ (`1.0`).
- `session_id` phải là UUID; định danh không được chỉ gồm khoảng trắng.
- `frame_index` và số đếm phải không âm, nằm trong phạm vi số nguyên được quy định; `timestamp_ms` phải hữu hạn và không âm.
- `tracked_count` không được vượt `people_count`.
- `recorded_at` phải có múi giờ; Backend lưu và trả về UTC.
- Khi `line_enabled` là true, bắt buộc có `in_count` và `out_count`. Khi false, cả hai trường này và `initial_occupancy` phải là null.
- Khi biết `initial_occupancy`, `estimated_occupancy` và `occupancy_underflow` phải phù hợp công thức `max(0, initial_occupancy + in_count - out_count)`.
- Từ chối trường không được định nghĩa. Không đổi số đếm bị thiếu thành 0.

## 7. Giới hạn dữ liệu và độ mới

- `people_count` là số người nhìn thấy trong một khung hình, không bảo đảm là số người trong toàn phòng.
- `estimated_occupancy` phụ thuộc số người ban đầu chính xác và camera quan sát đủ các lối vào/ra liên quan.
- Bộ đếm CV đặt lại theo từng phiên. V1 hỗ trợ một nguồn camera hoạt động cho mỗi phòng khi hiển thị trực tiếp; tổng hợp nhiều camera ngoài phạm vi.
- `recorded_at` là thời điểm CV xử lý. Backend gán `received_at` khi lưu bản ghi lần đầu và dùng để tính độ mới. `timestamp_ms` vẫn là độ lệch tương đối trong nguồn/phiên.
- Kiểm thử logic không chứng minh độ chính xác ngoài thực tế. Vị trí camera, che khuất, mất dấu theo dõi và cấu hình đường đếm đều có thể ảnh hưởng kết quả.

## 8. Các trường hợp cần kiểm thử tích hợp

| Trường hợp | Kết quả mong đợi |
|---|---|
| Lô hợp lệ có một bản ghi | Lưu bản ghi và trả xác nhận tiếp nhận. |
| Lô hợp lệ có nhiều bản ghi | Lưu toàn bộ trong một giao dịch và trả xác nhận theo thứ tự yêu cầu. |
| Gửi lại cùng phiên/khung hình và nội dung | Trả bản ghi đã có với `duplicate: true`, không tạo dòng thứ hai. |
| Cùng khóa nhưng khác nội dung | Trả `409 cv_record_conflict`, hoàn tác toàn bộ lô. |
| Mã phòng chưa biết hoặc null | Chấp nhận và giữ nguyên mã, trả `room_id: null`. |
| Số người nhìn thấy/ước tính bằng 0 | Chấp nhận `0` là giá trị hợp lệ. |
| Số người ước tính là null | Giữ null; Frontend hiển thị chưa biết, không đổi thành 0. |
| Thiếu trường, sai kiểu hoặc sai công thức đếm | Trả `422 validation_error` kèm đường dẫn trường. |
| `recorded_at` không có múi giờ | Từ chối bằng `422 validation_error`. |
| Backend hết thời gian chờ hoặc trả `503` | CV gửi lại với khóa phiên/khung hình cũ. |
| GET phòng chưa có dữ liệu webcam | Trả `404 occupancy_not_found`. |
| GET ước tính hợp lệ bằng 0 | Trả `200` với `estimated_occupancy: 0`. |
| GET bản ghi đã nhận quá 30 giây | Trả bản ghi với `is_stale: true`. |

## 9. Trạng thái triển khai

| Hạng mục | Trạng thái |
|---|---|
| Trường và ý nghĩa CountResult CV v1.0 | CV cung cấp; đã mô tả trong tài liệu này. |
| Cấu trúc lưu Backend và ánh xạ mã phòng | Hợp đồng đã thống nhất dựa trên thiết kế lưu trữ SEAT-24. |
| API HTTP nhận lô CV và phản hồi | Đã triển khai trong Backend SEAT-19. |
| Bộ gửi CV, hàng đợi gửi lại và URL Backend | Chưa có trong phần CV SEAT-17 đã ghi vào lịch sử mã nguồn; cần triển khai tiếp. Các thay đổi CV đã ghi nhận trước đó được giữ nguyên. |
| Phản hồi mới nhất và xử lý dữ liệu cũ/thiếu cho Frontend | Frontend đã xác nhận; Backend SEAT-19 đã triển khai API. |
| Tiếp nhận CrossingEvent qua HTTP | Ngoài phạm vi v1 đã thống nhất. |
| Xác thực tích hợp CV, Backend và Frontend | Ghi nhận lịch sử: chờ triển khai điểm cuối API; đã có ví dụ yêu cầu/phản hồi để thực hiện bước này. |

## 10. Ghi nhận nội dung đã thống nhất

| Quyết định | Hợp đồng đã thống nhất | Trạng thái |
|---|---|---|
| Giá trị hiển thị là số người trong phòng | Dùng `estimated_occupancy`; giữ riêng `people_count`. | CV và Frontend đã xác nhận |
| Ánh xạ phòng | `room_id` CV là mã phòng; đối chiếu chính xác `rooms.code`, mã chưa ánh xạ có khóa ngoại null. | CV đồng ý theo hợp đồng Backend |
| Tổng hợp camera/phiên | V1 dùng một camera hoạt động/phòng; không tổng hợp các phiên/camera. | Phạm vi Backend v1; CV tuân theo |
| Gửi bản ghi số đếm | Lô tối đa 1000; gửi khi đủ 100 bản ghi hoặc 1 giây; gửi lại giữ `(session_id, frame_index)`. | CV đã đồng ý; chưa triển khai bộ gửi |
| CrossingEvent | Không gửi/lưu qua API số đếm v1; bổ sung API riêng trong task sau nếu cần. | Ngoài phạm vi v1 |
| Phản hồi cho Frontend | ID phòng Backend dạng số; `estimated_occupancy`, dữ liệu bổ trợ, `received_at`, `is_stale`. | Frontend đã xác nhận |
| Thiếu dữ liệu và độ mới | `404 occupancy_not_found`; dữ liệu cũ sau 30 giây; Frontend lấy dữ liệu mỗi 5 giây. | Frontend đã xác nhận |
| Xác thực dịch vụ | Mạng riêng khi phát triển; chốt xác thực triển khai thực tế trước khi cho truy cập từ bên ngoài. | Backend/người phụ trách bảo mật cần chốt |

Người phụ trách Backend báo cáo xác nhận của CV và Frontend ngày 30/10/2026. Cập nhật hợp đồng nếu một trong hai nhóm yêu cầu thay đổi. Chốt riêng phương thức xác thực triển khai thực tế trước khi cho truy cập từ bên ngoài.

## 11. Danh sách kiểm tra nghiệm thu SEAT-18

- [x] Bản thảo liệt kê trường CV, kiểu, ý nghĩa và quy tắc kiểm tra.
- [x] Có ví dụ yêu cầu/phản hồi CV → Backend và Backend → Frontend.
- [x] Định nghĩa cách xử lý đề xuất cho dữ liệu thiếu/sai/trùng, thời điểm và mất kết nối.
- [x] CV đồng ý tuân theo hợp đồng Backend; giữ nguyên các file CV đã ghi vào lịch sử mã nguồn.
- [x] Frontend xác nhận phản hồi GET, cách xử lý null/0/thiếu dữ liệu/dữ liệu cũ và chu kỳ lấy dữ liệu.
- [x] Có ví dụ JSON cho kiểm thử tích hợp tiếp theo.

Các tuyến Backend và ví dụ đã được mô tả để tích hợp. Kiểm thử toàn luồng với bộ gửi CV trực tiếp và Frontend là công việc tiếp theo, không phải điều kiện phê duyệt tài liệu hợp đồng SEAT-18 này.

## 12. API thử nghiệm CV cục bộ của SEAT-17

Các tuyến sau thuộc dịch vụ thử nghiệm CV cục bộ, tách biệt với API nghiệp vụ Backend và không triển khai API tiếp nhận của Backend ở mục 4.

### Giao diện thử nghiệm CV cục bộ

- `GET /`: giao diện HTML thử nghiệm cục bộ; tài nguyên nằm trong `/static/`.
- `GET /api/config`: trạng thái có sẵn của mô hình và thiết bị xử lý đã chọn, không trả đường dẫn cục bộ.
- `POST /api/jobs`: gửi video qua trường `file` dạng multipart và chuỗi JSON `options`; trả `202` kèm ID tác vụ. Giới hạn 200 MB; một tác vụ tại một thời điểm (`409` khi bận), `503` nếu thiếu mô hình, `415` nếu phần mở rộng không được hỗ trợ, `422` nếu cấu hình không hợp lệ.
- `GET /api/jobs/{id}`: trạng thái, bản ghi mới nhất và ảnh JPEG base64 tương ứng, sự kiện gần đây, bản tóm tắt và lỗi đã loại thông tin nhạy cảm. Trạng thái đi từ tải lên/nạp/xử lý đến hoàn tất/hủy/thất bại.
- `POST /api/jobs/{id}/stop`: yêu cầu dừng; tác vụ kết thúc sau khi xử lý xong khung hình hiện tại.
- `GET /api/jobs/{id}/preview`: ảnh JPEG mới nhất; trả `404` khi chưa có khung hình đầu tiên.
- `GET /api/jobs/{id}/files/{kind}`: tải dữ liệu theo loại `csv/jsonl/debug/events/summary`; chỉ cho phép sau khi hoàn tất/hủy (trường hợp khác trả `409`). ID hoặc loại không tồn tại trả `404`.

Đây là các tuyến thử CV, tách biệt với API nghiệp vụ Backend. Thông tin tác vụ nằm trong bộ nhớ và mất khi khởi động lại; file đầu ra vẫn lưu cục bộ đến khi được xóa thủ công.

### Thử webcam qua trình duyệt

- `POST /api/webcam`: cấu hình JSON như video; giữ suất xử lý suy luận và bắt đầu phiên theo dõi mới, trả `202` kèm ID tác vụ.
- `POST /api/webcam/{id}/frame`: dữ liệu JPEG tối đa 2 MB, cạnh ảnh sau giải mã không quá 1920 px. Trả bản ghi số đếm với `source_type: webcam` và khung bao phục vụ kiểm tra. Xử lý từng khung hình; trả `409` nếu bận/đã dừng, `422` nếu khung hình không hợp lệ.
- Dừng và xuất dữ liệu dùng cùng các API tác vụ. Thời gian nguồn webcam tính từ đầu phiên bằng đồng hồ đơn điệu; `recorded_at` là giờ xử lý UTC.
- Trình duyệt chỉ lấy hình sau khi người dùng bấm Start Test và cấp quyền camera. Không lấy âm thanh hoặc ghi video webcam. Dừng trước khi rời trang; nếu trình duyệt lỗi, có thể cần khởi động lại dịch vụ cục bộ để giải phóng phiên còn treo.

## 13. Dữ liệu CV gửi Backend cho SEAT-34
### 13.1 Hiện trạng và ranh giới tương thích

| Nội dung | Hợp đồng hoặc mã hiện có | Cần cho thiết kế sự kiện |
|---|---|---|
| Tiếp nhận | POST `/api/v1/cv/count-records`, nhận lô bản ghi số đếm, khai báo 200 | Tuyến riêng; đề xuất POST `/api/v1/cv/events`, mỗi yêu cầu một sự kiện |
| Chống trùng | Hợp đồng v1 dùng phiên/khung hình; mã nguồn hiện chưa khớp | `event_id` duy nhất, xác nhận tiếp nhận gốc và cập nhật số người đúng một lần |
| Phòng | Bản ghi số đếm nhận mã chuỗi như `A101`, ánh xạ `rooms.code` → `rooms.id` | Sự kiện dùng ID số đã xác minh cùng nguồn/phiên |
| Lưu trữ | Bản ghi số đếm lưu vào `cv_count_records`; mô hình CountEvent dùng ID số nguyên | Cập nhật cấu trúc dữ liệu để nhận ID từ CV và lưu sự kiện, số người, xác nhận tiếp nhận trong một giao dịch |
| Web đang dùng | `/occupancy/current`, làm mới 30 giây, đọc `occupancy_records` | Chốt GET theo phòng/cơ sở và thông tin trạng thái từ nguồn sự kiện |
| GET bản ghi số đếm | `/occupancy/rooms/{room_id}/latest` đọc `cv_count_records` | Không giả định đã đọc OccupancyRecord hoặc tổng hợp sự kiện |
| Xác thực/trạng thái | Chưa có khóa tiếp nhận hoặc tuyến trạng thái thiết bị | Chốt khóa API, quyền nguồn và tín hiệu định kỳ báo nguồn còn hoạt động

### 13.2 Nội dung sự kiện và ánh xạ từ CV

| Trường | Kiểu / bắt buộc trong bản đề xuất | Quy tắc và ánh xạ |
|---|---|---|
| `schema_version` | chuỗi / có | `event-draft-1`; không dùng lẫn bản ghi số đếm `1.0` |
| `event_id` | chuỗi UUID / có | Bộ gửi tạo một lần và lưu bền vững trước gửi; giữ khi gửi lại/khởi động lại; không nhúng mã theo dõi |
| `session_id` | chuỗi UUID / có, bổ sung đề xuất | Phiên CV, gắn số người ban đầu N0; mỗi phiên mới cần bản ghi số ban đầu mới |
| `sequence_no` | số nguyên ≥ 0 / có, bổ sung đề xuất | Thứ tự liên tiếp của sự kiện trong nguồn/phiên, bắt đầu 0; không dùng `frame_index` vì khung hình có thể không sinh sự kiện |
| `room_id` | số nguyên > 0 / có | Ánh xạ mã phòng CV qua danh mục đã xác nhận; không ép chuỗi `A101` thành số hoặc tự tạo phòng |
| `source` | chuỗi / có | `cv`; phân biệt nguồn xử lý với định danh thiết bị |
| `device_id` | chuỗi / có | 1–100 ký tự không rỗng, ánh xạ từ `camera_id`, nguồn ổn định được phép ghi vào phòng |
| `direction` | giá trị liệt kê / có | `IN` hoặc `OUT`; một sự kiện là một lượt, không phải bộ đếm cộng dồn |
| `event_time` | ISO 8601 UTC / có | Thời điểm xác nhận cắt đường ảo, hậu tố `Z`, đồng hồ đã đồng bộ; không đổi độ lệch `timestamp_ms` thành thời gian Unix |
| `device_status` | giá trị liệt kê / có | `online` tại thời điểm cắt đường ảo; trạng thái `offline`/`error` gửi bằng thông điệp riêng |
```js
{
  "schema_version": "event-draft-1",
  "event_id": "076ccfac-ea81-4213-9d9f-6b7bb4387010",
  "session_id": "6f228318-ea31-46b3-a1a7-c562288ea97e",
  "sequence_no": 0,
  "room_id": 14,
  "source": "cv",
  "device_id": "cam-01",
  "direction": "IN",
  "event_time": "2026-11-11T07:00:00Z",
  "device_status": "online"
}
```
### 13.3 Giao dịch, xác nhận tiếp nhận và lỗi

| Trường hợp | Hành vi mục tiêu |
|---|---|
| Sự kiện mới hợp lệ | HTTP 201 sau khi xác nhận lưu giao dịch (COMMIT); sự kiện, số người và xác nhận tiếp nhận lưu trong một giao dịch |
| Cùng `event_id`, cùng nội dung chuẩn hóa | HTTP 200, xác nhận gốc với `duplicate=true`; không đổi số đếm hoặc `received_at` |
| Cùng `event_id`, khác nội dung | HTTP 409 `event_conflict`; không cập nhật dữ liệu; cách ly để điều tra |
| Thiếu/sai khóa | HTTP 401 `unauthorized`; không ghi dữ liệu |
| Khóa/nguồn không có quyền ghi phòng/phiên | HTTP 403 `forbidden` |
| Phòng không tồn tại | HTTP 404 `room_not_found`; không tự tạo phòng |
| JSON hỏng / sai cấu trúc dữ liệu | HTTP 400 `malformed_json` / 422 `validation_error` |
| Phiên chưa đăng ký / sai thứ tự / phiên đóng | Đề xuất 409 `session_not_ready` / `event_out_of_order` / `session_closed`; giữ để đối soát |
| Cơ sở dữ liệu không khả dụng | HTTP 503 `database_unavailable`; hoàn tác phần chưa xác nhận lưu |

```json
{
  "event_id": "076ccfac-ea81-4213-9d9f-6b7bb4387010",
  "room_id": 14,
  "received_at": "2026-11-11T07:00:01Z",
  "duplicate": false
}
```


### 13.4 Giao nhận và trạng thái nguồn

- Bộ gửi lưu hàng đợi bền vững trước gửi; mỗi nguồn/phiên chỉ có một yêu cầu
  chờ xác nhận. Chỉ bỏ sự kiện khi phản hồi 201/200 hợp lệ khớp `event_id`.
- Đề xuất thời gian chờ kết nối 3 giây, toàn yêu cầu 10 giây. Khi mất kết nối,
  hết thời gian chờ hoặc nhận 503, gửi lại ba lượt sau lần đầu, chờ tăng dần
  1, 2, 4 giây, giữ nguyên ID/nội dung và thứ tự. Hết lượt vẫn giữ hàng đợi và
  báo vận hành để gửi lại sau.
- Với lỗi 4xx, không tự gửi lại; giữ/cách ly, báo nguyên nhân và đối soát. Không bỏ
  sự kiện lỗi rồi áp dụng sự kiện phụ thuộc nó. Giới hạn hàng đợi, cảnh báo
  đầy, thời hạn lưu và phục hồi cần chốt; không tự xóa sự kiện chưa được xác
  nhận. Các giá trị thời gian chờ/gửi lại là đề xuất, chưa được triển khai.
- Camera mất nhưng CV còn mạng: đề xuất POST `/api/v1/cv/device-status` riêng.
  Không gửi IN/OUT giả hoặc đặt số đếm về 0. CV mất mạng/dừng đột ngột không
  thể gửi trạng thái mất kết nối ngay; Backend cần tín hiệu định kỳ để phát
  hiện mất nguồn.
- Đề xuất gửi tín hiệu nguồn còn hoạt động mỗi 10 giây, quá 30 giây thì đánh
  dấu dữ liệu cũ, chờ xác nhận. Ngưỡng này khác cơ chế GET bản ghi số đếm hiện
  tại dựa trên tuổi `received_at`.
- Trạng thái có thứ tự riêng theo nguồn/phiên. Thông báo trạng thái cũ gửi lại
  không ghi đè trạng thái mới; gửi lại xác nhận không làm dữ liệu cũ bị hiểu
  thành mới. Sau gián đoạn, nguồn đang kết nối và số người đã đồng bộ là hai
  điều kiện riêng.

Nội dung trạng thái đề xuất:

```json
{
  "schema_version": "status-draft-1",
  "status_id": "d171547f-6385-4df0-a662-9b283187255e",
  "session_id": "6f228318-ea31-46b3-a1a7-c562288ea97e",
  "status_sequence_no": 1,
  "room_id": 14,
  "source": "cv",
  "device_id": "cam-01",
  "device_status": "offline",
  "event_time": "2026-11-11T07:01:00Z"
}
```

`device_status` là `online|offline|error`, không có hướng vào/ra hoặc số đếm.
Đề xuất trạng thái mới trả 201, trùng cùng nội dung trả 200 với xác nhận gốc,
khác nội dung trả 409; không cập nhật số người. Tên tuyến/cấu trúc và thông tin
bổ trợ của GET chờ chốt. API đọc/giao diện cần phân biệt chưa biết, số 0 hợp
lệ, số đếm cũ, mất kết nối và lỗi HTTP.
Chưa có N0/sức chứa hợp lệ thì không công bố chỗ trống hoặc mức đông chính thức.

### 13.5 Khóa API qua biến môi trường

Đề xuất trường tiêu đề HTTP `X-API-Key`; bộ gửi đọc `CV_API_KEY`, Backend đọc
`CV_INGEST_API_KEY` qua môi trường. Đây là tên thiết kế, chưa có xác thực tương
ứng trong mã nguồn. Không đưa khóa vào URL, JSON, nhật ký hoặc Frontend; không
đưa `.env` vào lịch sử Git. Backend phải xác thực khóa và quyền nguồn/phòng,
không chỉ kiểm tra có tiêu đề. Cách cấp/đổi khóa, ánh xạ quyền và so sánh khóa
an toàn cần chốt với Backend. Dùng HTTPS khi truyền qua mạng; không mở API
tiếp nhận công khai từ bản chạy thử.

### 13.6 Ví dụ curl và kế hoạch xác thực

Các lệnh dùng PowerShell và `curl.exe`, chỉ dành cho môi trường thử riêng có
cơ sở dữ liệu đã nạp dữ liệu mẫu. Chưa chạy trong lần soạn tài liệu; không gọi
vào dữ liệu chung/môi trường vận hành thực tế, không ghi file thử vào thư mục
hỗ trợ được bảo vệ.

**Bản ghi số đếm SEAT-19:** lưu một lô mục 4.1 vào `count-batch.json` trong thư
mục thử nghiệm. API khai báo 200; lỗi mã nguồn mục 13.1 cần xử lý trước khi xác
nhận yêu cầu chạy được.

```powershell
$seat34BaseUrl = 'http://127.0.0.1:8000'
curl.exe --silent --show-error --max-time 10 --include `
  -H 'Content-Type: application/json' `
  --data-binary '@count-batch.json' "$seat34BaseUrl/api/v1/cv/count-records"
curl.exe --silent --show-error --max-time 10 --include `
  "$seat34BaseUrl/api/v1/occupancy/rooms/14/latest"
```

**Sự kiện có khóa:** lưu JSON mục 13.2 vào `crossing-event.json` trong thư mục
thử; nạp khóa thử nghiệm vào môi trường. Chỉ chạy sau khi Backend có tuyến và
xác thực theo hợp đồng đã duyệt. Lệnh là ví dụ thiết kế, không chứng minh API
có sẵn.

```powershell
$seat34BaseUrl = 'http://127.0.0.1:8000'
if ([string]::IsNullOrWhiteSpace($env:CV_API_KEY)) {
  throw 'Chua nap CV_API_KEY cho moi truong thu nghiem'
}
curl.exe --silent --show-error --connect-timeout 3 --max-time 10 --include `
  -H 'Content-Type: application/json' -H "X-API-Key: $env:CV_API_KEY" `
  --data-binary '@crossing-event.json' "$seat34BaseUrl/api/v1/cv/events"
```

Gửi lại cùng file để thử chống trùng, không tạo UUID mới. Để thử trạng thái,
lưu JSON mục 13.4 vào `device-status.json`, dùng cùng tiêu đề/khóa ở tuyến
trạng thái đề xuất. Không dùng `--verbose` hoặc ghi lệnh đã chứa giá trị khóa
vào nhật ký làm bằng chứng chia sẻ.

| Kiểm tra | Mong đợi | Trạng thái ngày 11/11/2026 |
|---|---|---|
| Lô số đếm hợp lệ / gửi lại / xung đột | 200 mới; 200 trùng; 409 khác nội dung theo v1 | Chưa chạy; mã nguồn đang lệch mục 13.1 |
| Sự kiện mới / gửi lại / xung đột | 201; xác nhận cũ 200; 409; số đếm đổi đúng một lần | Chưa chạy; chưa có API sự kiện |
| Thiếu/sai khóa / sai quyền | 401 / 403, không ghi dữ liệu | Chưa chạy; chưa có xác thực nguồn |
| Mất xác nhận, yêu cầu đồng thời, cơ sở dữ liệu lỗi | Một sự kiện và một tác động; hoàn tác hoặc trả xác nhận đã lưu | Chưa chạy; cần PostgreSQL thử riêng |
| Khởi động lại CV, hàng đợi đầy, sai thứ tự | Giữ ID/thứ tự, cảnh báo/đối soát; không mất sự kiện mà không báo | Chưa chạy; chưa có bộ gửi/hàng đợi |
| N0 chưa biết, OUT làm số đếm âm, vượt sức chứa, hiệu chỉnh | Chưa biết, đánh dấu dưới 0, kẹp chỗ trống, lịch sử truy vết | Chưa chạy tích hợp |
| Mất nguồn/mạng, tín hiệu hoạt động phục hồi | Cảnh báo nguồn, không đặt về 0, gửi lại không làm dữ liệu cũ thành mới | Chưa chạy; chưa có API trạng thái |
| Sự kiện → GET → web | Đúng phòng/cơ sở và nguồn tính; đo từ cắt đường ảo đến hiển thị | Chưa chạy; web hiện làm mới 30 giây |

### 13.7 Nội dung cần Khiêm và Thắng xác nhận

- [ ] Tuyến/phiên bản/cấu trúc sự kiện và trạng thái, phiên/số thứ tự đề xuất.
- [ ] Ánh xạ phòng khu tự học/cơ sở, nguồn/quyền khóa và dữ liệu video thử.
- [ ] UUID gửi mạng, cập nhật ID số nguyên, giao dịch và xác nhận khi mất phản hồi.
- [ ] Số ban đầu mỗi phiên, thứ tự/gửi lại, số đếm dưới 0 và hiệu chỉnh truy vết.
- [ ] Nguồn GET cho web, chuyển bản ghi số đếm/sự kiện, chưa biết/mất kết nối, chu kỳ cập nhật.
- [ ] Tiêu đề HTTP/biến môi trường chứa khóa, thời gian chờ/chờ tăng dần, tín hiệu hoạt động và giới hạn hàng đợi.
- [ ] NFR-PRI-01/02 và ví dụ curl được thử với API thực tế sau khi gỡ trở ngại.

