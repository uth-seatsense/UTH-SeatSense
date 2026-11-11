# Kế hoạch thực nghiệm đối chiếu đếm tay

**SEAT-35 · Lê Văn Trí ·**

So sánh số đếm CV với đếm tay, đo tốc độ xử lý và độ trễ lên web.
Dùng cùng [mẫu bảng ghi](experiment-record-template.md).
Căn cứ: [SRS v1.8](../requirements/UTH-SeatSense_SRS_v1.8.md),
[Charter v1.7](../requirements/Project%20Charter.md) và
[thuật toán SEAT-33](../../cv/README.md).

## 1. Tổ chức thực nghiệm

Thực hiện **5–10 phiên, mỗi phiên 30–60 phút**, ở nhiều mức đông và khung giờ.
Hai người A/B đếm độc lập, không nhìn kết quả CV; đối soát sau khi nộp bảng gốc.
Trí vận hành CV và tổng hợp. Điền tên A/B, lịch và địa điểm trước khi đo.

| Phiên | Điều kiện | Thời lượng |
|---|---|---|
| P01 | Ít người, từng người đi qua hai chiều | 30 phút |
| P02 | Mức đông trung bình, có lượt vào và ra | 30 phút |
| P03 | Đông hơn, người đi gần nhau hoặc bị che khuất | 30 phút |
| P04 | Ánh sáng khác các phiên trước | 30 phút |
| P05 | Lặp lại một điều kiện để kiểm tra tính ổn định | 30 phút |
| P06–P10 | Bổ sung điều kiện còn thiếu | 30–60 phút/phiên |

Ưu tiên thử tại địa điểm của nhóm. Chỉ đo ở CS1/CS3 khi được phép.

## 2. Cách thực hiện một phiên

1. Ghi cấu hình máy, model, phiên bản mã/image Docker, kích thước ảnh YOLO,
   confidence, vị trí đường đếm và chiều IN. Giữ camera cố định nhìn vào lối đi.
2. Bật IN/OUT, thử một lượt mỗi chiều. Hai người thống nhất số người ban đầu
   **N0**; chưa biết thì ghi chưa biết, không tự đặt 0.
3. Làm nóng khoảng 60 giây, sau đó bắt đầu phiên đo và ghi thời gian chung.
4. A/B đếm IN/OUT cộng dồn. Ghi số hiện diện tại phút 0, 5, 10, … đến cuối phiên.
   Mốc 0 kiểm tra N0, không tính vào thống kê hiện diện.
5. Ghép số CV ở cùng mốc bằng mã phiên, số khung hình và thời gian nguồn.
   Dữ liệu thiếu ghi rõ, không điền 0. Không cộng các bộ đếm tích lũy giữa các mốc.
6. Dừng phiên, xuất CSV/JSONL và đối soát A/B. Nếu chưa thống nhất đáp án thì
   ghi chưa đối soát, không chọn số gần CV hơn.

Số người nhìn thấy trong ảnh khác số hiện diện toàn phòng. Nếu không đếm trực
tiếp được toàn khu vực, có thể suy hiện diện từ `N0 + IN_tay − OUT_tay` và
ghi rõ cách này. Chưa biết N0 thì chỉ đánh giá IN/OUT.

Mọi hiệu chỉnh ghi thời điểm, giá trị trước/sau, người thực hiện và lý do.
Giữ dữ liệu gốc; đổi cấu hình, góc camera hoặc khởi động lại thì tách đoạn mới.

## 3. Cách đo ba chỉ tiêu

### AT-01 — Sai số đếm

Tính riêng **tổng IN**, **tổng OUT** cuối phiên và **hiện diện mỗi 5 phút**.

```text
Sai số tuyệt đối = |CV − đếm tay|
Sai số từng mẫu (%) = 100 × sai số tuyệt đối / đếm tay
Sai số tổng hợp (%) = 100 × tổng sai số tuyệt đối / tổng đếm tay
```

- Đếm tay bằng 0: tỷ lệ từng mẫu là N/A, vẫn báo sai số tuyệt đối.
- Trong phiên có tổng đếm tay >0, lỗi ở mẫu đếm tay bằng 0 vẫn vào tử số.
- Phiên có tổng đếm tay bằng 0 báo riêng bằng sai số tuyệt đối. Khi tổng hợp
  đợt, cộng tử số/mẫu số các phiên còn lại theo từng nhóm, không lấy trung bình tỷ lệ.
- Báo trung bình, trung vị, xấu nhất của sai số từng mẫu hợp lệ và số mẫu thiếu.
  Không đổi N/A thành 0%. Mục tiêu tạm: **sai số tổng hợp ≤10%**.

### AT-02 — Độ trễ lên web

Ghép đúng sự kiện với bản ghi web; dùng đồng hồ đã đồng bộ:
`độ trễ = lúc web hiển thị − lúc CV ghi nhận sự kiện`.
Có thể ghi thêm lúc người thực qua đường đếm để kiểm tra trễ phát hiện.

Sắp xếp n độ trễ tăng dần; p95 là giá trị ở vị trí `ceil(0.95 × n)`, tính từ 1.
Báo số mẫu, trung bình, trung vị, p95, lớn nhất và mẫu mất/không ghép được.
Mục tiêu tạm: **p95 ≤5 giây**. Không bỏ mẫu lỗi để kết luận đạt.

Hiện **chưa đo được AT-02** vì còn thiếu tích hợp CV → Backend → web.
Số “Pipeline Latency” trên giao diện CV chỉ đo xử lý CV, không phải độ trễ này.

### AT-03 — Tốc độ xử lý

Sau làm nóng, đo ít nhất **60 giây ở kích thước ảnh YOLO khoảng 416 px**.
Đề xuất đếm số frame hoàn tất trong từng khoảng một giây, lấy trung vị FPS
các khoảng; báo thêm tổng frame / tổng thời gian và FPS thấp nhất.
Khoảng đo được nhưng không có frame là 0 FPS; mất dữ liệu đo phải ghi thiếu.
Mục tiêu tạm: **trung vị ≥5 FPS**.

Ghi rõ đo chỉ detector, detector + tracking hay toàn luồng CV; đề xuất dùng
toàn luồng CV làm chỉ số chính để Uyên duyệt. Không dùng FPS nguồn thay FPS xử lý.
Nhãn “416×416” trên UI chưa chứng minh cấu hình thực là 416; mã hiện mặc định
640, CLI có `--image-size 416`. Ngoại tuyến và webcam phải báo riêng.

## 4. Thử sơ bộ đã có

Ngày 11/11/2026 đã thử CV trong Docker, trình duyệt gửi hình webcam qua cổng
8001. SRS mô tả CV ngoài Docker; mỗi phiên phải ghi đúng chế độ thực dùng.

| Kết quả | Giới hạn |
|---|---|
| Webcam: 146 frame trong khoảng 15,6 giây; 10 giây đầu có 94 bản ghi | Nhịp quan sát khoảng 9,4 frame/giây, chưa phải phép đo AT-03 chuẩn |
| Phát hiện 1–2 người, khung cuối 1 người; Trí xác nhận khớp thực tế | Một lần thử ngắn, chưa có hai người đếm độc lập |
| 9 kiểm thử logic đạt; API nhận ảnh/video và xuất CSV/JSONL hoạt động | Chưa chứng minh độ chính xác ngoài thực tế |
| Detector CPU ở 416 px đạt trung bình khoảng 54,1 FPS trong 60 giây | Chỉ detector trên ảnh mẫu lặp, không phải toàn luồng CV |

Phiên webcam chưa bật IN/OUT và chưa có N0. Chưa kết luận AT-01/02/03 đạt.
Hồ sơ cục bộ: `seat35-cv-docker-test/results.json` và
`seat35-cv-docker-test/webcam-retest-results.json`.

## 5. Phân tích lỗi và dữ liệu

Ghi nguyên nhân theo nhóm: phát hiện thiếu/thừa, che khuất, đổi mã tracking,
sai đường đếm, thiếu N0, mất kết nối hoặc đáp án A/B chưa thống nhất.
Đổi góc camera/confidence để thử lại ở phiên mới; giữ kết quả trước hiệu chỉnh.

Có chấp thuận và biển thông báo khi cần. Mặc định không ghi video webcam.
Video thử chỉ dùng người đã đồng ý và xóa sau xử lý theo SRS. Không đưa ảnh,
video hoặc dữ liệu nhận dạng lên Git. Ghi người giữ dữ liệu và hạn xóa;
số đếm tổng hợp tạm giữ tối đa 90 ngày sau đánh giá, không áp dụng cho ảnh/video.

## 6. Điều kiện hoàn thành

- [ ] Kế hoạch đủ phiên, hai người đếm độc lập và mẫu bảng ghi.
- [ ] AT-01/02/03 có cách đo; nêu rõ phần chưa thử được.
- [ ] Uyên duyệt cách tính sai số, mốc độ trễ, phạm vi FPS và kế hoạch dữ liệu.

**Trạng thái:** chờ Uyên duyệt. Đây là kế hoạch; báo cáo kết quả chính thức
được lập sau khi thực hiện đủ đợt đo. Mục tiêu trong SRS vẫn là ngưỡng tạm.
