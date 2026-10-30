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
frame, xuất JSONL/CSV và video có bbox/ID tùy chọn. Chưa triển khai đếm
IN/OUT, giao diện kiểm thử, hợp đồng API Backend hoặc PostgreSQL.

Chạy các lệnh sau từ thư mục `cv/`. Khuyến nghị Python 3.12 và môi trường
ảo riêng; bản hiện tại đã kiểm chứng với Ultralytics 8.4.191, Torch 2.11.0
và CPU. Cài Torch phù hợp thiết bị nếu cần GPU, truyền `--device 0` khi chạy.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Đặt checkpoint YOLOv8n vào `models/best.pt` và video được phép sử dụng vào
`videos/sample.mp4`. Model phải có lớp `person`; hỗ trợ cả checkpoint
person-only và checkpoint COCO. Không tự tải model khi thiếu file.

```powershell
.\.venv\Scripts\python.exe run_video.py --video videos/sample.mp4 --annotate
```

Trong workspace của Lê Văn Trí, có thể dùng trực tiếp môi trường, model và
video đã có, không cần sao chép chúng vào repo:

```powershell
& D:/hkdn/yolov8/.venv/Scripts/python.exe run_video.py --model D:/hkdn/yolov8/artifacts/cctv_yolov8n_v5/weights/best.pt --video D:/hkdn/yolov8/samples/people-walking.mp4 --annotate
```

Tham số: `--model` (mặc định `CV_MODEL_PATH` hoặc `models/best.pt`),
`--device` (mặc định `CV_DEVICE` hoặc `cpu`), `--confidence` (0.1–1, mặc định
0.32), `--image-size` (mặc định 640), `--output` (mặc định `outputs`),
`--fallback-fps` (dùng khi metadata FPS thiếu), `--annotate` (ghi MP4).
Đường dẫn tương đối được tính từ thư mục đang chạy lệnh.

Mỗi lần chạy tạo thư mục UUID riêng trong `outputs/` gồm:

- `results.jsonl`: một dòng mỗi frame, có số đếm, thời gian và bbox/ID.
- `counts.csv`: số đếm và thời gian dạng bảng, không chứa bbox.
- `summary.json`: chỉ được ghi sau khi xử lý thành công.
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
`summary.json`. OpenCV không luôn phân biệt được EOF và video hỏng giữa chừng.

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

Lệnh Docker Compose bên dưới chỉ khởi động API health hiện có; không tự chạy
video. Chạy CLI cục bộ theo hướng dẫn trên để kiểm tra pipeline giai đoạn 1.

Cần môi trường Python và các thư viện trong `requirements.txt`. Chuẩn bị
model phù hợp, camera hoặc video được phép sử dụng và cấu hình khu vực đếm.
Khi kết nối với hệ thống, thống nhất định dạng số liệu gửi sang Backend.

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
