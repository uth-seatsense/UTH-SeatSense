# Hợp đồng dữ liệu CV phiên bản 1.0

Đầu ra do SEAT-17 định nghĩa để Backend triển khai tiếp nhận sau. Hiện xuất
file cục bộ, chưa có endpoint HTTP, xác thực, retry hoặc giao nhận mạng.
Không diễn giải tài liệu này là API Backend đã triển khai.

## Bản ghi số đếm

Nguồn: `backend_counts.jsonl`, mỗi frame một bản ghi đã kiểm tra bằng
`cv/app/schemas/count_result.py`. JSON Schema nằm trong `docs/schemas/`;
ví dụ nằm trong `docs/examples/`. CSV chứa cùng trường với bản ghi số đếm.

| Trường | Ý nghĩa |
| --- | --- |
| schema_version | Chuỗi `1.0`; thay đổi không tương thích sẽ tăng phiên bản |
| session_id | UUID phiên xử lý, mới cho mỗi lần chạy |
| camera_id | Định danh camera do cấu hình; mặc định camera-01 chỉ dùng thử |
| room_id | Định danh phòng tùy chọn, không biết thì null |
| source_type | `video` hoặc `webcam` |
| frame_index | Số nguyên từ 0, khóa thứ tự trong phiên |
| timestamp_ms | Video: frame_index × 1000 / FPS; webcam: thời gian monotonic từ đầu phiên |
| recorded_at | UTC có múi giờ lúc xử lý, không phải giờ camera quay |
| people_count | Số bbox người hiện thấy vượt confidence; không phải tổng người trong phòng |
| tracked_count | Số người trong đó đã được xác nhận track ID |
| line_enabled | Có cấu hình đường đếm hay không |
| in_count / out_count | Tổng lượt trong phiên; null khi không bật line, 0 khi chưa có lượt |
| initial_occupancy | Số người ban đầu biết trước, hoặc null |
| estimated_occupancy | max(0, initial + IN - OUT), null nếu chưa biết số ban đầu |
| occupancy_underflow | true khi công thức trước clamp âm, cần kiểm tra cấu hình hoặc số đếm |

Backend nên dùng `(session_id, frame_index)` để chống ghi trùng số đếm. Không
cộng các counter tích lũy của mỗi frame với nhau. Không cộng lượt giữa nhiều
camera có cùng vùng nhìn nếu chưa có quy tắc hợp nhất. Số 0 là dữ liệu hợp lệ;
thiếu bản ghi không được coi là 0. Phiên dừng/lỗi có thể chỉ xuất một phần.
`summary.json` chỉ có khi xử lý kết thúc thành công theo bộ giải mã OpenCV.

## Sự kiện IN/OUT

Nguồn: `events.jsonl`, rỗng nếu chưa có sự kiện. Mỗi sự kiện có schema_version,
event_id, session_id, camera_id, room_id, frame_index, timestamp_ms, recorded_at,
track_id, direction (`IN`/`OUT`) và confidence [0,1]. Dùng `event_id` chống ghi
trùng; ID được tạo từ phiên, frame, track và hướng. Track ID chỉ có nghĩa trong
phiên, không phải danh tính con người. Thời điểm sự kiện là frame xác nhận
qua line, không nội suy thời điểm chính xác trong khoảng hai frame.

## Giới hạn và phạm vi

Schema này kiểm tra số đếm không âm, tracked_count <= people_count, thời gian
có múi giờ và sự nhất quán giữa counters/ước tính. Không xuất bbox trong bản
ghi Backend; bbox nằm ở results.jsonl để kiểm tra cục bộ.
Video hiện giả định FPS cố định. ID đổi, che khuất, chuyển động nhanh, vùng đệm
hoặc cooldown không phù hợp có thể gây bỏ lượt/đếm lặp. Ước tính phòng chỉ
có ý nghĩa nếu camera bao quát lối vào/ra và số ban đầu đúng.
Chưa có đánh giá ground truth tại thư viện; các kiểm thử logic không chứng
minh độ chính xác ngoài thực tế.
