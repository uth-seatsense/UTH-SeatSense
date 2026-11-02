# Mẫu bảng ghi thực nghiệm SEAT-35

Sao chép mẫu này cho mỗi phiên theo [kế hoạch](experiment-plan.md). Đây là
mẫu trống, không phải kết quả thực nghiệm. Giữ riêng hai bản đếm tay A/B rồi
đối soát sau khi nộp bảng gốc; kết quả CV điền độc lập. Ô trống là chưa ghi,
`N/A` là không áp dụng theo phương pháp; số 0 phải được ghi rõ khi quan sát
thực sự bằng 0. Thời gian có ngày/múi giờ; duration và latency ghi đơn vị.

## 1. Thông tin và cấu hình phiên

| Trường                                                                    | Giá trị cần điền |
| --------------------------------------------------------------------------- | --------------------- |
| Mã phiên / ngày / phòng / khu vực                                      |                       |
| Chế độ offline/live; t0 và thời điểm kết thúc UTC                  |                       |
| Thời lượng dự kiến / thực tế (phút); status                         |                       |
| Người vận hành; người đếm A; người đếm B                        |                       |
| Duyệt kế hoạch: bằng chứng / ngày                                     |                       |
| Câu 14, 15 SRS: phiên bản phương pháp / bằng chứng xác nhận       |                       |
| Chấp thuận địa điểm / camera / video; biển thông báo               |                       |
| Nơi lưu cục bộ; người quản lý; người được truy cập; hạn xóa |                       |
| Git SHA; model tên/phiên bản/hash; Python/Ultralytics/Torch              |                       |
| OS; CPU/GPU/RAM; device; phần mềm khác chạy cùng                       |                       |
| Nguồn hình, góc/vị trí; độ phân giải và FPS nguồn                |                       |
| Ảnh YOLO thực dùng; confidence; line/hướng                             |                       |
| Deadband; cooldown_ms; max_gap_ms                                           |                       |
| Số đầu phiên A/B/đồng thuận; phương pháp xác nhận               |                       |
| session_id/camera_id/room_id; cấu hình Backend/Frontend/polling           |                       |
| Sức chứa đã xác nhận; mức đông và điều kiện ánh sáng         |                       |
| Thời gian làm nóng; cách đo wall time; khoảng đo FPS                 |                       |
| Đồng bộ đồng hồ trước/sau; lệch tối đa và sai số đo           |                       |
| Tuổi bản ghi tối đa đã duyệt; cách ánh xạ mốc thời gian         |                       |

## 2. Bảng gốc cho từng người đếm

Mỗi người dùng **một bản riêng**. IN/OUT là tích lũy từ t0, không phải số
trong từng khoảng. Hiện diện ghi là quan sát trực tiếp hoặc suy từ N0 +
IN − OUT; nêu rõ cách nào. Ghi mốc 0 làm baseline; thêm các mốc 35–60 phút
nếu phiên dài hơn 30 phút. Khi chưa quan sát được, ghi lý do thiếu mẫu.

Người đếm A hoặc B: ______; mã bản gốc: ______; giờ nộp: ______.

| Mốc (phút) | Thời điểm thực/timeline nguồn | IN tay | OUT tay | Hiện diện tay | Cách đếm / điều kiện / mẫu thiếu |
| ------------ | ---------------------------------- | ------ | ------- | --------------- | ---------------------------------------- |
| 0            |                                    |        |         |                 |                                          |
| 5            |                                    |        |         |                 |                                          |
| 10           |                                    |        |         |                 |                                          |
| 15           |                                    |        |         |                 |                                          |
| 20           |                                    |        |         |                 |                                          |
| 25           |                                    |        |         |                 |                                          |
| 30           |                                    |        |         |                 |                                          |

## 3. Đối soát tham chiếu và kết quả CV

Mỗi dòng cho một mốc và một loại `IN`, `OUT`, `hiện diện`. Chỉ dùng kết quả
đồng thuận đã xác nhận làm tham chiếu; không lấy trung bình A/B hoặc chọn
số gần CV. Mốc cuối phiên dùng cho tổng IN/OUT; mốc 5 phút dùng cho hiện diện.
Lặp lại hàng trống theo số mẫu; không cộng các counters giữa mốc với nhau.

| Mốc / loại | Giá trị A | Giá trị B | Đồng thuận / unresolved | Lý do / bằng chứng / người đối soát |
| ------------ | ----------- | ----------- | -------------------------- | ------------------------------------------- |
|              |             |             |                            |                                             |

| Mốc / loại | frame_index / timestamp_ms | Tuổi bản ghi (ms) | Giá trị CV | Underflow / thiếu mẫu | AE | RE (%) hoặc N/A |
| ------------ | -------------------------- | ------------------- | ------------ | ----------------------- | -- | ---------------- |
|              |                            |                     |              |                         |    |                  |

Giữ liên kết theo mã phiên + mốc + loại giữa hai bảng; khi có hiệu chỉnh,
ghi mã đoạn riêng. Reference=0 thì RE=N/A, AE vẫn phải tính. Thiếu CV hoặc
tham chiếu unresolved thì không tự điền AE/RE bằng 0.

## 4. AT-03 FPS

Mỗi hàng một cửa sổ 5 phút hoặc toàn phiên; nêu offline/live, phạm vi đo,
nguồn thời gian và kích thước ảnh. Chỉ dùng số frame/time cùng cửa sổ.

| Cửa sổ / phạm vi / ảnh px | t_start / t_end (cùng đồng hồ) | T_wall (s) | Frame hoàn tất N | Tổng processing_ms | FPS pipeline | FPS từ processing_ms | Thiếu/bỏ frame và lý do |
| ----------------------------- | ---------------------------------- | ---------- | ------------------ | ------------------- | ------------ | --------------------- | --------------------------- |
|                               |                                    |            |                    |                     |              |                       |                             |

FPS pipeline=N/T_wall; FPS từ processing_ms=1000*N/sum(processing_ms) trên
tập frame có duration hợp lệ. Nếu tập hợp khác nhau, ghi N riêng cho mỗi
phép đo. Không dùng FPS nguồn thay FPS pipeline. Giữ thời gian nạp model và
làm nóng riêng khỏi cửa sổ chính thức theo kế hoạch.

## 5. AT-02 Độ trễ

Chỉ điền kết quả khi có tích hợp và ánh xạ bản ghi tới UI thực. `t_cross`,
`t_cv`, `t_backend`, `t_render` dùng thời gian tương thích, kèm sai số. Mỗi
sự kiện dự kiến vẫn có hàng nếu mất/không ghép được; không chỉ ghi mẫu tốt.

| Mã sự kiện / phiên-frame / bản ghi UI | Hướng | t_cross UTC | t_cv UTC | t_backend UTC | t_render UTC |
| ------------------------------------------ | ------- | ----------- | -------- | ------------- | ------------ |
|                                            |         |             |          |               |              |

| Mã sự kiện | Render − cross (ms) | Render − CV (ms) | Sai số thời gian (ms) | Retry / polling / mất / không ghép được | Vượt 5s / chưa kết luận |
| ------------- | -------------------- | ----------------- | ----------------------- | --------------------------------------------- | ---------------------------- |
|               |                      |                   |                         |                                               |                              |

Nếu chưa có công cụ/tích hợp để đo, ghi trạng thái **chưa đo được** và phần
còn thiếu tại tổng kết, không dùng thời gian inference làm độ trễ AT-02.

## 6. Nhật ký sự cố và hiệu chỉnh

| Thời điểm / đoạn phiên | Loại lỗi | Hiện tượng / điều kiện | Bằng chứng cục bộ | Hiệu chỉnh / baseline mới / người thực hiện | Ảnh hưởng mẫu và cách phân tích |
| ---------------------------- | ---------- | ---------------------------- | --------------------- | -------------------------------------------------- | --------------------------------------- |
|                              |            |                              |                       |                                                    |                                         |

Không xóa dữ liệu trước hiệu chỉnh. Ghi camera mất/kết nối lỗi, đổi cấu
hình, restart, phiên dừng sớm và chênh lệch A/B chưa giải quyết.

## 7. Tổng hợp và xác nhận

Tách ba hàng nhóm AT-01: tổng IN/phiên, tổng OUT/phiên, hiện diện/mốc 5 phút.
Thêm bảng tổng hợp đợt sau khi có đủ phiên, không trộn đơn vị hay phương pháp.

| Nhóm AT-01 | Mẫu tổng | Cặp hợp lệ | Reference=0 | Thiếu/unresolved | RE TB/trung vị/max (%) | AE TB/trung vị/max |
| ----------- | ---------- | ------------- | ----------- | ----------------- | ----------------------- | ------------------- |
| IN          |            |               |             |                   |                         |                     |
| OUT         |            |               |             |                   |                         |                     |
| Hiện diện |            |               |             |                   |                         |                     |

| Chỉ tiêu | Trạng thái đo / cỡ mẫu | Kết quả | Ngưỡng và cách kết luận đã duyệt | Hạn chế / nguyên nhân chính |
| ---------- | --------------------------- | --------- | ----------------------------------------- | -------------------------------- |
| AT-01      |                             |           |                                           |                                  |
| AT-02      |                             |           |                                           |                                  |
| AT-03      |                             |           |                                           |                                  |

AT-02 báo thêm số sự kiện dự kiến/ghép/mất, độ trễ TB/trung vị/max và số
mẫu >5 giây. AT-03 báo FPS toàn phiên và trung vị/thấp nhất các cửa sổ.

| Xác nhận                                                                     | Người / ngày / mã bằng chứng |
| ------------------------------------------------------------------------------ | ---------------------------------- |
| A/B đã đối soát, giữ bảng gốc và số đồng thuận                    |                                    |
| Người vận hành rà soát dữ liệu thiếu và công thức                  |                                    |
| Uyên duyệt báo cáo; kết luận KPI theo phương pháp đã duyệt         |                                    |
| Video/ảnh/debug đã xóa theo hạn, thời điểm và người thực hiện     |                                    |
| File tổng hợp ẩn danh được phép chia sẻ; nơi lưu dữ liệu cần giữ |                                    |
