# Báo cáo kiểm tra skeleton frontend và Dockerfile

- Mã công việc: SEAT-50.

- Ngày kiểm tra: 13/11/2026 (Asia/Bangkok).
- Mã nền: nhánh `dev` tại commit `d1e0b60`.
- Nhánh thực hiện: `feature/SEAT-50-frontend-skeleton-dockerfile`.

## 1. Kết quả hiện tại

Phần này là kết quả mới nhất, thay thế các giới hạn về kết nối và kiểm tra
trình duyệt trong lịch sử bên dưới.

- Skeleton React/Vite đã có đủ sáu trang yêu cầu, cùng Home, Health và trang 404.
- Sidebar “Đặt phòng học” đã dùng React Router để mở `/reservation`,
  thay cho liên kết `#rooms` không điều hướng đến trang đặt phòng.
- Nhãn cơ sở được khai báo tập trung, bảo đảm nút chọn và tiêu đề khu vực
  cùng hiển thị “Cơ sở 3 (Tòa K - Lầu 2)”. Đây là sửa tính nhất quán giao diện,
  chưa phải xác minh vị trí phòng thực tế.
- Đã bổ sung kiểm thử liên kết sidebar, ẩn Health khỏi menu và vị trí Đăng nhập:
  **39/39 ca đạt trên máy**. Lượt kiểm thử container trước đó đạt 37/37 ca.
- Menu đã dùng tiếng Việt có dấu; Đăng nhập nằm ngoài cùng bên phải.
  Health không xuất hiện trong menu nhưng vẫn truy cập được tại `/health`.
- Docker loại `.env` và `.env.*` khỏi image, giữ lại `.env.example`.
- ESLint: không có lỗi, còn 14 cảnh báo kiểm tra props của Dashboard hiện có.
- Kiểm tra định dạng Prettier và bản build production: đạt trên máy.
  Bản build production trong container cũng đạt.
- Đã build lại image và tạo lại riêng container frontend bằng `--no-deps`.
- Đã dùng Chrome chạy không giao diện để mở trực tiếp và tải lại cả tám route
  cùng trang 404 tại các chiều rộng 1440, 768, 390 và 320 px.
  Menu điều hướng phía trên hoạt động ở mọi kích thước; không ghi nhận lỗi
  JavaScript chưa xử lý hoặc tràn ngang. Đã xem ảnh chụp desktop và mobile.
- Sau khi sửa, đã kiểm tra lại liên kết sidebar và tải lại trang đặt phòng
  trên desktop; nhãn Cơ sở 3, độ rộng nội dung và Health đạt ở cả bốn kích thước.
- Trang Health hiển thị kết nối thành công với backend qua proxy frontend,
  nhận phản hồi thật: `{"status":"ok","service":"backend"}`.
- Trong lượt hoàn thiện này, không thay đổi mã backend/CV, dữ liệu DB
  hoặc container backend/CV. Chưa tạo commit hay push.

## 2. Phạm vi thực hiện

- Khởi tạo cấu trúc `src/`: `pages`, `components`, `services`, `hooks`,
  `assets`, `styles`.
- Khởi tạo `BrowserRouter` trong `main.jsx`; kiểm thử route dùng `StaticRouter`.
- Cấu hình các route `/`, `/login`, `/rooms`, `/reservation`, `/my-bookings`,
  `/checkin`, `/dashboard`, `/health` và trang 404.
- Giữ giao diện Dashboard hiện có; khắc phục phần điều hướng bị sidebar che
  và bỏ header thừa trên Home.
- Bổ sung ESLint, Prettier, npm scripts và cài dependency Docker bằng `npm ci`.
- Tích hợp frontend vào Compose với `VITE_API_BASE_URL`
  và `VITE_BACKEND_PROXY_TARGET`.
- Trang Health hiển thị trạng thái đang kiểm tra, thành công hoặc lỗi thật;
  hủy yêu cầu sau 10 giây hoặc khi rời trang.

Đăng nhập, danh sách phòng, đặt phòng, lịch đặt của tôi và check-in vẫn là
trang khung, chưa triển khai nghiệp vụ. Docker đang chạy Vite dev server,
không phải cấu hình phục vụ production.

## 3. Các lệnh kiểm tra

Tại thư mục `frontend/`:

```sh
npm test
npm run lint
npm run format:check
npm run build
```

Trên PowerShell, có thể dùng `npm.cmd` nếu `npm.ps1` bị chặn.

Tại thư mục gốc dự án, chỉ build và khởi động frontend:

```sh
docker compose build frontend
docker compose up --no-build --no-deps -d frontend
docker compose exec -T frontend npm test
docker compose exec -T frontend npm run build
```

Dashboard hiện được loại khỏi kiểm tra định dạng Prettier để tránh định dạng
lại toàn bộ mã ngoài phạm vi skeleton; ESLint vẫn kiểm tra tệp này.

## 4. Vấn đề còn lại ngoài phạm vi SEAT-50

`GET /api/v1/occupancy/current` vẫn trả HTTP 503 từ backend đang chạy.
Container đang dùng truy vấn cũ với `occupied_count`, `observed_at`, trong khi
mã backend trên máy đã chuyển sang `current_count`, `recorded_at`.
Việc build lại backend và kiểm tra schema được tách khỏi lượt nghiệm thu frontend.

Health thành công chỉ xác nhận kết nối và phản hồi của endpoint health,
không đồng nghĩa tất cả API nghiệp vụ đã hoạt động.

## 5. Lịch sử kiểm tra trước đó

Các ghi chú sau phản ánh những lượt chạy trước, không thay thế kết quả hiện tại:

- Lượt kiểm tra trước có 35 ca đạt trong bốn tệp; lượt đầu trong container có
  29 ca đạt. Bản build trên máy và trong container đều đạt.
- Các route dev trả HTTP 200. Có thời điểm chưa hoàn tất kiểm tra HTTP trong
  container do Docker Desktop mất kết nối với Linux engine; không tự khởi động
  lại Docker.
- Sau khi Docker phục hồi, frontend chạy độc lập và `/`, `/health` trả HTTP 200;
  ảnh chụp trình duyệt xác nhận các trang khung hiển thị.
- Khi backend chưa chạy, kết nối backend chưa được nghiệm thu; trạng thái
  502/lỗi khi đó là kết quả dự kiến, không dùng dữ liệu giả để che lỗi.
- Kiểm tra HTTP và render tĩnh khi đó chưa thay thế kiểm tra trình duyệt.
  Giới hạn này đã được bổ sung bằng lượt kiểm tra Chrome ở mục 1.
- Ghi chú ban đầu cho biết phần việc chưa hoàn tất được giữ trong hai Git stash;
  đây là thông tin lịch sử, chưa xác minh lại trạng thái stash hiện tại.

## 6. Lịch sử sửa backend cục bộ — không thuộc SEAT-50

Theo yêu cầu trước đó, đã sửa cục bộ
`backend/app/repositories/cv_count_repository.py`, bổ sung kiểm thử hồi quy
trong `backend/tests/test_cv_api.py`. Trong lượt sửa đó, không thay đổi endpoint CV,
schema hay dịch vụ CV; không tạo commit, push hoặc PR.

Repository xuất `CVRecordConflict`, giữ bản ghi cũ khi gửi lại, trả cờ trùng lặp
và từ chối nội dung xung đột. So sánh khi gửi lại chuẩn hóa thời gian UTC
và giữ cách xác định phòng ban đầu.

- Kiểm thử backend: 33 ca đạt; sáu ca PostgreSQL được bỏ qua trong lượt mặc định.
- Sau đó sáu ca lưu trữ đều đạt trên container PostgreSQL tạm riêng, gồm gửi lại
  đồng thời và rollback. Đã xóa DB/network tạm; không sửa dữ liệu DB ứng dụng.
- Chỉ backend được build và khởi động lại; CV không được build hay khởi động lại.
- `/health`, `/health/db` và `/api/v1/health` qua frontend trả HTTP 200.
- Lỗi occupancy lúc đó là HTTP 503 do lệch tên cột, không còn là lỗi
  kết nối/proxy 502. Lượt sửa CV đó không thay đổi endpoint occupancy hay schema.

Trước lần pull tiếp theo, cần bảo toàn thay đổi frontend/backend bằng commit
hoặc stash có tên rõ ràng, rồi đối chiếu với mã đã merge. Không áp lại máy móc
bản sửa cục bộ nếu task khác đã giải quyết cùng vấn đề.
