# Mẫu bảng ghi thực nghiệm đối chiếu đếm tay

**SEAT-35 · Lê Văn Trí**

Dùng với [kế hoạch thực nghiệm](experiment-plan.md). Sao chép cho mỗi phiên.
A/B dùng hai bản đếm tay riêng; đối soát sau khi nộp. Mẫu dưới đây để trống.
**0 là số đã quan sát; ô trống là chưa ghi; N/A là không áp dụng.**

## 1. Thông tin phiên

| Nội dung | Điền thông tin |
|---|---|
| Mã phiên / ngày / địa điểm, cơ sở | |
| Người vận hành / người đếm A / B | |
| Thời gian bắt đầu / kết thúc / thời lượng thực | |
| CV trong Docker hoặc ngoài Docker / webcam hoặc video | |
| Máy, CPU/GPU/RAM / model / phiên bản mã hoặc image | |
| Ảnh YOLO thực dùng / confidence / đường đếm, chiều IN | |
| Mã phiên CV / camera / phòng / nơi lưu file kết quả | |
| N0 theo A / B / số thống nhất / sức chứa nếu biết | |
| Cho phép thử / biển thông báo / người giữ dữ liệu, hạn xóa | |

Chưa biết N0 thì ghi chưa biết. Bật IN/OUT và thử hai chiều trước phiên chính.

## 2. Bảng đếm tay

Người đếm A hoặc B: ______. IN/OUT cộng dồn từ đầu phiên.
Hiện diện: đếm trực tiếp hoặc suy từ N0 + IN − OUT, ghi rõ cách dùng.
Thêm mốc 35–60 nếu phiên dài hơn 30 phút; mốc 0 chỉ dùng kiểm N0.

| Phút | IN tay | OUT tay | Hiện diện tay | Cách đếm / ghi chú |
|---|---|---|---|---|
| 0 | | | | |
| 5 | | | | |
| 10 | | | | |
| 15 | | | | |
| 20 | | | | |
| 25 | | | | |
| 30 | | | | |

## 3. Đối soát và sai số AT-01

Mỗi dòng ghi một nhóm IN, OUT hoặc hiện diện. IN/OUT dùng tổng cuối phiên;
hiện diện dùng mốc 5 phút. Không cộng các bộ đếm tích lũy giữa các mốc.

| Mốc / nhóm | A | B | Số thống nhất | CV | Sai số tuyệt đối | Sai số % hoặc N/A |
|---|---|---|---|---|---|---|
| | | | | | | |

Mã frame / thời gian nguồn ghép với từng mốc: ______.
Lý do A/B lệch, mẫu thiếu hoặc chưa đối soát: ______.
Không chọn số gần CV làm đáp án; giữ hai bảng gốc.

| Nhóm | Tổng sai số tuyệt đối | Tổng đếm tay | Sai số tổng hợp % | Trung bình / trung vị / xấu nhất của sai số từng mẫu |
|---|---|---|---|---|
| IN | | | | |
| OUT | | | | |
| Hiện diện | | | | |

Sai số tổng hợp = 100 × tổng sai số tuyệt đối / tổng đếm tay.
Đếm tay bằng 0 thì tỷ lệ mẫu là N/A, vẫn tính sai số tuyệt đối.
Phiên/nhóm tổng đếm tay bằng 0 báo riêng, không chia cho 0; cách tổng hợp
nhiều phiên theo kế hoạch. Mẫu thiếu không được điền sai số 0.

## 4. Độ trễ AT-02

Chỉ đo sau khi tích hợp CV → Backend → web. Ghi thời điểm có múi giờ,
dùng đồng hồ đã đồng bộ và ghép đúng mã sự kiện/bản ghi web.

| Mã sự kiện | CV ghi nhận | Web hiển thị | Độ trễ giây | Mất / không ghép / ghi chú |
|---|---|---|---|---|
| | | | | |

| Mẫu dự kiến / hợp lệ / thiếu | Trung bình | Trung vị | p95 | Lớn nhất | Mẫu >5 giây |
|---|---|---|---|---|---|
| | | | | | |

p95: sắp độ trễ tăng dần, lấy vị trí `ceil(0.95 × n)`, tính từ 1.
Mục tiêu p95 ≤5 giây. Có mẫu mất hoặc chưa ghép được thì ghi giới hạn kết luận.
Nếu chưa tích hợp, ghi **chưa đo được**, không dùng thời gian xử lý CV thay thế.

## 5. Tốc độ AT-03

Phạm vi: chỉ detector / detector + tracking / toàn luồng CV: ______.
Ảnh thực dùng và cách xác minh: ______. Thời gian làm nóng: ______.
Đo ít nhất 60 giây sau làm nóng; sao chép dòng dưới cho từng khoảng một giây.

| Khoảng giây | Frame hoàn tất / FPS | Ghi chú |
|---|---|---|
| | | |

| Thời lượng đo | Tổng frame | FPS trung vị | FPS thấp nhất | FPS trung bình = frame / giây |
|---|---|---|---|---|
| | | | | |

Mục tiêu trung vị ≥5 FPS ở khoảng 416 px. Không lấy nhãn UI hoặc FPS nguồn
làm bằng chứng. Khoảng đo được nhưng 0 frame ghi 0; mất dữ liệu đo ghi thiếu.

## 6. Sự cố và hiệu chỉnh

| Thời điểm | Lỗi / thao tác | Giá trị trước → sau nếu chỉnh | Lý do / người thực hiện | Ảnh hưởng kết quả |
|---|---|---|---|---|
| | | | | |

Ghi Pause, đổi góc, mất camera, khởi động lại hoặc dừng muộn. Giữ dữ liệu gốc;
hiệu chỉnh hoặc đổi cấu hình thì tách đoạn, không xóa kết quả trước đó.

## 7. Tổng kết và xác nhận

| Chỉ tiêu | Kết quả | Đạt / không đạt / chưa đủ dữ liệu | Giới hạn |
|---|---|---|---|
| AT-01 IN | | | |
| AT-01 OUT | | | |
| AT-01 hiện diện | | | |
| AT-02 p95 | | | |
| AT-03 FPS trung vị | | | |

Nguyên nhân sai chính và đề xuất thử lại: ______.
A/B đã đối soát, người / ngày: ______.
Uyên duyệt kế hoạch, ngày / bằng chứng: ______.
Người rà soát kết quả: ______.
Dữ liệu lưu ở đâu, người giữ / hạn xóa / đã xử lý: ______.

Không ghi video webcam mặc định; video thử có đồng ý được xóa sau xử lý.
Chỉ chia sẻ số liệu tổng hợp ẩn danh. Không dùng lần thử ngắn thay cho
5–10 phiên chính thức hoặc điền sẵn kết quả đạt vào mẫu này.
