# Database design

The initial PostgreSQL schema defines:

- `rooms`: room identity, building, and capacity.
- `reservations`: room, time interval, requester, and workflow status.
- `occupancy_records`: timestamped observed occupancy by room.

Add reviewed, versioned migrations before making schema changes beyond the
initial development database.

## Dữ liệu CV SEAT-24

`cv_count_records` lưu một hàng cho mỗi frame đã xử lý, độc lập với bảng
occupancy_records phục vụ số người trong phòng. Chỉ lưu số liệu tổng hợp,
không lưu video, ảnh, bbox hay nhận diện cá nhân. Migration chuẩn:
`database/init/002_cv_count_records.sql`.

| Trường | Kiểu | Quy tắc |
| --- | --- | --- |
| id | BIGINT IDENTITY | PK tự sinh |
| schema_version | VARCHAR(10) | Bắt buộc, hiện là 1.0 |
| session_id | UUID | Phiên do CV cấp |
| camera_id | VARCHAR(100) | Không rỗng |
| room_code | VARCHAR(100), null | Giữ nguyên room_id chuỗi từ CV |
| room_id | BIGINT, null | FK rooms.id; ON DELETE RESTRICT |
| source_type | VARCHAR(10) | video hoặc webcam |
| frame_index | BIGINT | Không âm; thứ tự frame trong phiên |
| timestamp_ms | DOUBLE PRECISION | Không âm, hữu hạn; thời gian tương đối |
| recorded_at | TIMESTAMPTZ | Thời điểm xử lý do CV gửi, hữu hạn |
| received_at | TIMESTAMPTZ | Database cấp NOW() khi ghi mới |
| people_count | INTEGER | Số người hiện thấy, không âm |
| tracked_count | INTEGER | 0 đến people_count |
| line_enabled | BOOLEAN | Bật hoặc tắt đếm qua đường |
| in_count / out_count | BIGINT, null | Không âm; bắt buộc nếu bật line, null nếu tắt |
| initial_occupancy | BIGINT, null | Số ban đầu nếu biết, không âm |
| estimated_occupancy | BIGINT, null | max(0, initial + IN - OUT); null nếu initial null |
| occupancy_underflow | BOOLEAN | true nếu công thức trước clamp âm |

Unique `(session_id, frame_index)` chống ghi trùng và hỗ trợ truy vấn frame
theo phiên. Index `(camera_id, recorded_at DESC, id DESC)` và partial index
`(room_id, recorded_at DESC, id DESC)` khi room_id khác null hỗ trợ lịch sử.
schema_migrations ghi phiên bản SQL đã áp dụng và applied_at.

### Ánh xạ đầu ra CV

Nguồn lưu là `backend_counts.jsonl`; từng dòng được kiểm tra bằng
`CVCountInput` ở Backend. Không đưa dữ liệu debug results.jsonl có bbox vào
schema này. UUID, giới hạn số nguyên, timestamp có múi giờ và tính nhất quán
counters được kiểm tra trước khi ghi; database tiếp tục áp dụng ràng buộc.

room_id từ CV được giữ ở room_code. Backend tìm đúng rooms.code để gán FK;
mã chưa có hoặc null cho FK null, không ép chuỗi số thành rooms.id và không
tạo phòng giả. Retry không thay đổi ánh xạ đã lưu khi danh mục phòng thay đổi.
Giới hạn rooms.code là 50 ký tự; mã CV dài hơn vẫn được lưu nhưng không khớp
danh mục phòng hiện tại.

people_count không có nghĩa là tổng người trong phòng. Không tự chuyển nó
sang occupancy_records. IN/OUT là counters tích lũy trong phiên, không cộng
chúng giữa các frame. estimated_occupancy chỉ có khi biết số người ban đầu;
độ tin cậy vẫn phụ thuộc vị trí camera và tracking. Chưa lưu từng crossing
event hoặc hợp nhất số đếm giữa nhiều camera.

### Thời gian, ghi trùng và truy vấn

TIMESTAMPTZ giữ thời điểm tuyệt đối, không giữ nhãn múi giờ ban đầu. Backend
từ chối datetime thiếu múi giờ, dùng session DB UTC và xuất DTO theo UTC.
recorded_at là giờ xử lý, không phải giờ camera quay. timestamp_ms của video
là frame_index/FPS, webcam là monotonic từ đầu phiên; không đổi trường này
thành ngày giờ thật. received_at là giờ nhận tại DB, không đổi khi retry.

Repository INSERT ON CONFLICT DO NOTHING theo unique phiên/frame. Cùng nội
dung trả bản cũ; nội dung khác gây CVRecordConflict. Cả batch rollback nếu
có lỗi, không lưu một phần batch. Cơ chế này cũng được kiểm tra khi hai yêu
cầu trùng nội dung chạy đồng thời.

Lịch sử mặc định mới nhất trước theo recorded_at, rồi id. Khoảng thời gian
lọc là [start,end), limit tối đa 500. Offset pagination không bảo đảm snapshot
khi dữ liệu đang được ghi mới. latest trả None nếu chưa có dữ liệu, không
trả số 0 giả.

### Triển khai

Volume mới chạy init 001/002; volume cũ phải áp dụng 002 riêng. Không sửa
schema bằng ORM create_all hoặc xóa volume để nâng cấp. File SQL chạy trong
transaction và có advisory lock; migration mới cần file phiên bản mới.
Xem [hướng dẫn database](../../database/README.md) và
[bàn giao SEAT-24](../seat24-handover.md).
