# CV — Đếm người bằng camera

## Mục đích và trách nhiệm

Module CV phụ trách xử lý hình ảnh để đếm số người vào và ra khỏi phòng đọc.
Hướng triển khai là dùng YOLO để phát hiện người và theo dõi chuyển động qua
cửa. Số liệu được gửi cho Backend để cập nhật tình trạng chỗ trống, đồng thời
dùng để so sánh với phương án cảm biến và kết quả đếm tay.

## Cấu trúc thư mục dự kiến

```text
cv/
├── main.py          # Khởi động dịch vụ
├── config/          # Cấu hình xử lý hình ảnh
├── app/
│   ├── api/         # API của dịch vụ
│   ├── detection/   # Phát hiện và theo dõi người
│   ├── counting/    # Đếm lượt vào/ra
│   ├── services/    # Điều phối xử lý video
│   ├── schemas/     # Định dạng kết quả
│   └── utils/       # Các hàm hỗ trợ
├── models/          # Model dùng để nhận diện người
├── videos/          # Video thử nghiệm
└── tests/           # Kiểm thử phần CV
```

## Chuẩn bị trước khi chạy

### Giai đoạn 1 của SEAT-17

Đã có pipeline offline YOLOv8n + ByteTrack, đếm người đang thấy theo từng
frame, xuất JSONL/CSV và video có bbox/ID tùy chọn. Giai đoạn 2 bổ sung
IN/OUT qua đường kẻ và hợp đồng dữ liệu CV; chưa có giao diện, truyền HTTP
đến Backend hoặc PostgreSQL. Giai đoạn 3 bổ sung giao diện kiểm thử cục bộ.

Chạy các lệnh sau từ thư mục `cv/`. Khuyến nghị Python 3.12 và môi trường
ảo riêng; bản hiện tại đã kiểm chứng với Ultralytics 8.4.191, Torch 2.11.0
và CPU. Cài Torch phù hợp thiết bị nếu cần GPU, truyền `--device 0` khi chạy.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Tải file `best.pt` từ [thư mục model trên Google Drive](https://drive.google.com/drive/folders/1q9-reDJxYw5hAdOfVUG4kNONaYuXL7j0?usp=sharing).
Đặt file vào `cv/models/best.pt` tính từ thư mục gốc repo. Model được lưu
trên Drive, không commit lên Git.

Khi chạy từ thư mục `cv/`, đường dẫn model là `models/best.pt`.
Đặt video được phép sử dụng vào
`videos/sample.mp4`. Model phải có lớp `person`; hỗ trợ cả checkpoint
person-only và checkpoint COCO. Không tự tải model khi thiếu file.

```powershell
.\.venv\Scripts\python.exe run_video.py --video videos/sample.mp4 --annotate
```

Tham số: `--model` (mặc định `CV_MODEL_PATH` hoặc `models/best.pt`),
`--device` (mặc định `CV_DEVICE` hoặc `cpu`), `--confidence` (0.1–1, mặc định
0.32), `--image-size` (mặc định 640), `--output` (mặc định `outputs`),
`--fallback-fps` (dùng khi metadata FPS thiếu), `--annotate` (ghi MP4).
Đường dẫn tương đối được tính từ thư mục đang chạy lệnh.

Mỗi lần chạy tạo thư mục UUID riêng trong `outputs/` gồm:

- `results.jsonl`: một dòng mỗi frame, có số đếm, thời gian và bbox/ID.
- `counts.csv`: số đếm và thời gian dạng bảng, không chứa bbox.
- `summary.json`: ghi khi hoàn tất hoặc dừng có kiểm soát; kiểm tra `status`
  để phân biệt `completed` và `cancelled` (kết quả một phần).
- `annotated.mp4`: có khi truyền `--annotate`, phục vụ kiểm tra cục bộ.

`people_count` đếm bbox người vượt ngưỡng, kể cả người mới chưa có ID.
`tracked_count` là phần trong đó đã có ID được xác nhận. Track mất dấu không
được cộng vào số hiện tại. Đây không phải số khách duy nhất hoặc số người
toàn phòng khi camera chỉ thấy một phần phòng.

`frame_index` bắt đầu từ 0. `timestamp_ms = frame_index * 1000 / source_fps`
là thời gian tương đối, dành cho video FPS cố định. `recorded_at` là UTC
lúc xử lý frame, không phải thời gian quay gốc. `processing_ms` đo detector
và tracker, không gồm đọc/ghi file. ByteTrack được tạo mới mỗi video.

CLI trả mã thoát 1 khi lỗi. Nếu chạy bị lỗi, file trong thư mục UUID có thể
chỉ chứa một phần video; không sử dụng như kết quả hoàn tất khi thiếu
`summary.json` có status completed. OpenCV không luôn phân biệt được EOF và video hỏng giữa chừng.

### Kiểm thử pipeline

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_video_pipeline.py -v
```

Để chạy cả kiểm thử inference thật, đặt hai biến trước khi chạy lệnh trên:

```powershell
$env:CV_TEST_MODEL = (Resolve-Path models/best.pt).Path
$env:CV_TEST_VIDEO = (Resolve-Path videos/sample.mp4).Path
```

Video kiểm thử inference phải có ít nhất 16 frame đầu chứa người được model
nhận diện. Test tạo video tạm gồm 16 frame chuyển động và 4 frame đen, kiểm
tra số 0, tracking, thời gian, CSV, MP4 và hai phiên độc lập. Thiếu biến môi
trường thì test inference được ghi rõ là bỏ qua; không đồng nghĩa đã test AI.

Xem [kết quả kiểm thử giai đoạn 1](tests/PHASE1_RESULTS.md).

### Giai đoạn 2 của SEAT-17

```powershell
.\.venv\Scripts\python.exe run_video.py --video videos/sample.mp4 --camera-id cam-01 --room-id room-a --line 0.5 0 0.5 1 --in-direction positive-to-negative --initial-occupancy 0 --annotate
```

`--line X1 Y1 X2 Y2` là hai đầu đoạn thẳng chuẩn hóa [0,1], gốc tọa độ ở
góc trên trái. Với đường dọc từ trên xuống, phía phải có dấu âm, phía trái
có dấu dương. Ví dụ trên đếm IN khi đi từ trái sang phải. Mũi tên trên video
chỉ chiều từ đầu tới cuối đoạn thẳng, không phải chiều IN.

Điểm theo dõi dùng tâm cạnh dưới bbox. Mỗi ID phải được thấy ổn định ở hai
phía ngoài vùng đệm mới có thể phát sinh sự kiện. Giao điểm phải nằm trong
đoạn thẳng. `--deadband` mặc định 0.01 trong không gian chuẩn hóa;
`--cooldown-ms` mặc định 500 chống đảo chiều quá nhanh;
`--max-gap-ms` mặc định 1000 hủy trạng thái ID mất dấu quá lâu.
Đây là biện pháp giảm đếm lặp, không bảo đảm loại bỏ mọi lỗi tracking.

Không bật line thì IN/OUT là `null`. Bật line nhưng chưa có lượt qua thì là
`0`. Chỉ truyền `--initial-occupancy` khi biết số người ban đầu; nếu không,
`estimated_occupancy` là `null`. Ước tính bằng số ban đầu + IN - OUT; nếu âm,
giá trị xuất là 0 và `occupancy_underflow=true` để báo cần kiểm tra.
Mỗi phiên bắt đầu lại counters; không cộng giữa các phiên hoặc camera.

Đầu ra bổ sung `backend_counts.jsonl` (không có bbox/ID) và `events.jsonl`
(chỉ sự kiện qua line, có ID cục bộ). JSONL và CSV dùng schema phiên bản 1.0;
CSV để trống ô có giá trị null. `results.jsonl` là bản debug có thêm bbox.
Đây là thay đổi cột CSV so với giai đoạn 1.

Xem [hợp đồng dữ liệu](../docs/architecture/cv-data-contract.md), JSON Schema
và ví dụ đi kèm. Tải model theo link Google Drive ở phần chuẩn bị phía trên.

Chạy toàn bộ kiểm thử với hai biến model/video đã cấu hình:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### Giai đoạn 3 của SEAT-17

Sau khi cài thư viện và đặt model, chạy từ thư mục `cv/`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Mở `http://127.0.0.1:8001`.

Script `static/lab.js` nối các nút trên bản mẫu với API xử lý thật:

1. Chọn USB Webcam, bấm Start Test và cho phép camera trong trình duyệt.
   Chỉ lấy hình, không lấy âm thanh; webcam cần localhost hoặc HTTPS.
2. Hoặc chọn Uploaded File, chọn video rồi bấm Start Test (tối đa 200 MB).
3. Cấu hình confidence/camera, bật IN/OUT nếu cần. Đường đếm mặc định dọc
   giữa khung hình; chọn chiều IN và số người ban đầu nếu biết.
4. Bật/tắt Boxes, Tracking IDs, Conf %, Virtual Line; Pause chỉ giữ hình
   xem, không dừng inference. Snapshot tải ảnh frame đang thấy.
5. Nhập số đếm tay rồi Compare Accuracy để giữ frame và tính sai số đếm.
   Không suy ra F1 từ số đếm; số đếm tay 0 cho sai số tương đối N/A.
6. Stop Test tắt webcam và kết thúc phiên; tải CSV/JSONL/summary ở thanh
   kết quả. Reset Count dùng sau khi dừng để chuẩn bị phiên mới.

RTSP chưa hỗ trợ và được vô hiệu hóa. FPS là nghịch đảo thời gian detector
+ tracker, không phải FPS camera hoặc toàn pipeline. Số đầu tiên là số người
đang thấy, không phải số người ngồi trong toàn phòng. Webcam gửi từng frame
JPEG (tối đa khoảng 10 frame/giây, phụ thuộc thiết bị) và không tạo hàng đợi
inference; file kết quả lưu theo các frame thực sự được xử lý.
API cũng có thể sử dụng qua `/docs`; CLI giai đoạn 1–2 không đổi.

Có thể cấu hình `CV_MODEL_PATH`, `CV_DEVICE`, `CV_OUTPUT_DIR` qua biến môi
trường trước khi khởi động. Mặc định dùng `models/best.pt`, CPU và outputs
trong module CV. Không ghi đường dẫn máy cá nhân vào tài liệu chia sẻ.

Video được tải tới dịch vụ CV và xóa bản đầu vào sau xử lý/dừng/lỗi.
Webcam gửi frame tới dịch vụ local, không ghi video; kết quả bbox/đếm lưu
cục bộ. Bấm Stop Test trước khi đóng trang; nếu tab bị crash, restart dịch
vụ CV để giải phóng phiên còn treo.
Kết quả debug giữ trong outputs; chủ máy tự quản lý và xóa khi không cần.
Mỗi lần chỉ chạy một video, giữ tối đa 20 metadata phiên trong RAM. Restart
làm mất danh sách tải qua UI; file kết quả vẫn còn trên đĩa. Không có tài
khoản hoặc DB; hiện chỉ phục vụ kiểm thử local, chưa dùng để public.

Kiểm thử API/UI (hai biến model/video cấu hình như phần trên):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test tests/ui.test.cjs
npm install --no-save --package-lock=false jsdom
node --test tests/lab.test.cjs
```

Xem [báo cáo giai đoạn 3](tests/PHASE3_RESULTS.md).


Có thể khởi động dịch vụ bằng Docker Compose từ thư mục gốc dự án:

```sh
docker compose up --build -d cv
```

## Quản lý model, video và dữ liệu nhạy cảm

- Lưu model trong `models/`, video thử nghiệm trong `videos/`; không đưa các
  file này lên Git. Ghi lại nguồn và phiên bản model để nhóm dễ dùng chung.
- Chỉ quay và dùng video khi được cho phép. Camera tại thư viện cần có sự
  đồng ý và biển thông báo.
- Xử lý hình ảnh tại chỗ, không nhận diện khuôn mặt và chỉ gửi số đếm lên server.
- Không lưu video khi chạy trực tiếp. Video đánh giá chỉ lưu tạm trong nhóm
  và xóa sau khi sử dụng xong.
- Không đưa ảnh người dùng, mật khẩu hay thông tin đăng nhập camera vào mã
  nguồn, log hoặc tài liệu chia sẻ.
