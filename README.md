# UTH-SeatSense

> Các mục đánh dấu **`[CHƯA CÓ DỮ KIỆN]`** cần được cập nhật sau khi nhóm xác nhận thông tin thực tế. Không điền suy đoán vào các mục này.

## Mục lục

1. [Giới thiệu dự án](#1-giới-thiệu-dự-án)
2. [Kiến trúc tổng quan](#2-kiến-trúc-tổng-quan)
3. [Cấu trúc repository](#3-cấu-trúc-repository)
4. [Yêu cầu môi trường](#4-yêu-cầu-môi-trường)
5. [Cài đặt Git và Docker Desktop](#5-cài-đặt-git-và-docker-desktop)
6. [Thiết lập Git cho thành viên](#6-thiết-lập-git-cho-thành-viên)
7. [Clone repository](#7-clone-repository)
8. [Cấu hình biến môi trường](#8-cấu-hình-biến-môi-trường)
9. [Khởi chạy dự án bằng Docker Compose](#9-khởi-chạy-dự-án-bằng-docker-compose)
10. [Cổng truy cập](#10-cổng-truy-cập)
11. [Trạng thái chức năng](#11-trạng-thái-chức-năng)
12. [Quy ước làm việc nhóm (Git và Jira)](#12-quy-ước-làm-việc-nhóm-git-và-jira)
13. [Xử lý lỗi thường gặp](#13-xử-lý-lỗi-thường-gặp)
14. [Kiểm tra README trên máy phát triển](#14-kiểm-tra-readme-trên-máy-phát-triển)
15. [Lịch sử thay đổi](#15-lịch-sử-thay-đổi)

---

## 1. Giới thiệu dự án

**UTH-SeatSense** (đề tài D6) là hệ thống theo dõi mật độ sử dụng phòng đọc và đặt phòng học nhóm tại Thư viện UTH, dựa trên xử lý hình ảnh và hệ thống quản lý dữ liệu.

Mục tiêu của dự án:

- Phát hiện và đếm số người từ camera hoặc video bằng Computer Vision.
- Tiếp nhận, xử lý và lưu trữ dữ liệu đếm người.
- Hiển thị số chỗ trống và mức độ đông của phòng đọc gần thời gian thực trên web.
- Cho phép sinh viên đặt phòng học nhóm theo khung giờ, check-in bằng QR, tự động nhả phòng khi quá hạn.
- Cung cấp dashboard thống kê cho thủ thư (mật độ theo giờ/ngày, tỷ lệ sử dụng phòng, tỷ lệ no-show).
- Chạy các thành phần bằng Docker để chuẩn hóa môi trường phát triển và triển khai.

## 2. Kiến trúc tổng quan

| Thành phần | Vai trò | Công nghệ |
|---|---|---|
| CV/AI (`cv/`) | Phát hiện và theo dõi người, đếm vào/ra qua đường ảo | Camera + YOLOv8n + ByteTrack |
| Backend (`backend/`) | Tiếp nhận dữ liệu đếm, xử lý nghiệp vụ (đặt phòng, check-in, nhả phòng), cung cấp API | FastAPI |
| PostgreSQL | Lưu trữ dữ liệu hệ thống | PostgreSQL (phiên bản: **`[CHƯA CÓ DỮ KIỆN]`**) |
| Frontend (`frontend/`) | Hiển thị chỗ trống, đặt phòng, check-in QR, dashboard thủ thư | Web responsive (framework: **`[CHƯA CÓ DỮ KIỆN]`**) |
| Docker | Đóng gói và chạy các dịch vụ | Docker Compose |

**Phương án đã chốt:** nhóm chọn **Phương án B** (phương án hai trong Project Charter): đếm người bằng camera + YOLOv8n + ByteTrack, đếm khi người cắt đường ảo. Toàn bộ hệ thống chạy kèm Docker. Phương án A (cảm biến) không nằm trong phạm vi của repository này.

Luồng xử lý:

1. Thành phần CV/AI nhận hình ảnh từ camera (hoặc video quay sẵn khi đánh giá), đếm người vào/ra.
2. CV/AI chỉ gửi **con số** (không gửi hình ảnh/video) lên Backend.
3. Backend tiếp nhận và xử lý dữ liệu.
4. PostgreSQL lưu trữ dữ liệu.
5. Frontend gọi API Backend để lấy dữ liệu và hiển thị.

```text
[Camera + YOLOv8n + ByteTrack] -> (số lượng vào/ra) -> Backend (FastAPI) -> PostgreSQL -> Frontend (web)
```

Cách CV/AI gửi dữ liệu đến Backend (giao thức, endpoint, định dạng dữ liệu): **`[CHƯA CÓ DỮ KIỆN]`**

**Nguyên tắc giảm tải cho CV/AI** (theo Project Charter):

- Dùng YOLOv8n, độ phân giải đầu vào 320–416 px, xử lý 3–5 khung hình/giây.
- Cắt vùng quan tâm quanh cửa; có thể xuất sang ONNX/OpenVINO.
- Phần đánh giá chạy offline trên video quay sẵn; phần demo trực tiếp chạy ở mức nhẹ.

**Quyền riêng tư:**

- Camera đặt trên cao nhìn xuống, xử lý ngay trên máy, **không lưu video**, không nhận diện khuôn mặt hay danh tính.
- Chỉ lưu số liệu tổng hợp ẩn danh. Dữ liệu đặt phòng gắn với mã sinh viên được thu thập tối thiểu.

Cách CV/AI truy cập camera hoặc video bên trong Docker (thiết bị, đường dẫn, cấu hình): **`[CHƯA CÓ DỮ KIỆN]`**

> Các thành phần được triển khai và tích hợp theo tiến độ phát triển thực tế.

## 3. Cấu trúc repository

```text
UTH-SeatSense/
  cv/         thị giác máy tính (YOLO), đánh giá
  backend/    FastAPI, CSDL
  frontend/   web, dashboard
  docs/       tài liệu, quyết định kiến trúc, báo cáo
```

Vị trí file Docker Compose (thư mục gốc hay thư mục khác): **`[CHƯA CÓ DỮ KIỆN]`**

Quy tắc:

- Mỗi thư mục có `README.md` hướng dẫn chạy ngắn gọn.
- Mỗi người chủ yếu sửa thư mục của mảng mình. Muốn sửa thư mục của người khác phải qua Pull Request và báo chủ mảng đó.
- Quyết định kiến trúc ghi vào `docs/decisions.md`.

## 4. Yêu cầu môi trường

- Git.
- Docker Desktop.
- Docker Compose (thường được tích hợp trong Docker Desktop).
- Visual Studio Code hoặc IDE tương đương.
- Kết nối Internet khi clone repository và tải Docker images.

Sau khi cài đặt, mở Terminal hoặc PowerShell và kiểm tra:

```bash
git --version
docker --version
docker compose version
```

Nếu các lệnh trả về phiên bản tương ứng, môi trường đã nhận diện được các công cụ cần thiết.

## 5. Cài đặt Git và Docker Desktop

### Git

1. Truy cập https://git-scm.com/downloads
2. Tải phiên bản phù hợp với hệ điều hành và cài đặt theo hướng dẫn.
3. Kiểm tra: `git --version`

### Docker Desktop

1. Truy cập https://www.docker.com/products/docker-desktop/
2. Tải Docker Desktop phù hợp với hệ điều hành, cài đặt và khởi động.
3. Chờ Docker khởi động hoàn tất, sau đó kiểm tra:

```bash
docker --version
docker compose version
docker info
```

Nếu `docker info` hoạt động bình thường, Docker Engine đã sẵn sàng.

## 6. Thiết lập Git cho thành viên

Thực hiện một lần cho mỗi thành viên.

1. Có tài khoản GitHub, được mời vào organization `uth-seatsense` (quyền Write) và vào Jira site của nhóm.
2. Cấu hình Git bằng **đúng email của tài khoản Jira**:

```bash
git config --global user.name 'Ho Ten'
git config --global user.email 'email-jira-cua-ban@gmail.com'
```

Sai email thì tên và ảnh không hiện trong Jira, smart commit cũng không chạy.

## 7. Clone repository

Clone vào thư mục riêng (không clone vào thư mục đang chứa file khác):

```bash
git clone https://github.com/uth-seatsense/UTH-SeatSense.git
cd UTH-SeatSense
```

Chuyển sang nhánh `dev`:

```bash
git fetch origin
git checkout dev
git pull origin dev
```

Nếu máy chưa có nhánh `dev` ở local:

```bash
git checkout -b dev origin/dev
```

Kiểm tra:

```bash
git branch -a
git status
```

> **Lưu ý:** `dev` là nhánh tích hợp để phát triển. Không push trực tiếp lên `dev` hoặc `main`. Mọi thay đổi làm trên nhánh công việc riêng và gửi Pull Request (xem [mục 12](#12-quy-ước-làm-việc-nhóm-git-và-jira)).

## 8. Cấu hình biến môi trường

File `.env` chứa các biến cấu hình ứng dụng. File `.env.example` là mẫu ban đầu.

1. Kiểm tra thư mục gốc có file `.env.example`.
2. Tạo file `.env`:

   Windows PowerShell:
   ```powershell
   Copy-Item .env.example .env
   ```

   macOS/Linux:

   ```bash
   cp .env.example .env
   ```

3. Mở `.env` và cập nhật giá trị phù hợp với môi trường phát triển.

| Biến | Dịch vụ sử dụng | Ý nghĩa | Giá trị mẫu |
|---|---|---|---|
| `POSTGRES_DB` | PostgreSQL, Backend | Tên cơ sở dữ liệu | `seatsense` |
| `POSTGRES_USER` | PostgreSQL, Backend | Tên người dùng cơ sở dữ liệu | `seatsense` |
| `POSTGRES_PASSWORD` | PostgreSQL, Backend | Mật khẩu phát triển cục bộ | Thay bằng mật khẩu riêng |
| `POSTGRES_PORT` | PostgreSQL | Cổng trên máy host | `5432` |
| `BACKEND_PORT` | Backend | Cổng API trên máy host | `8000` |
| `CV_PORT` | CV/AI | Cổng API trên máy host | `8001` |
| `FRONTEND_PORT` | Frontend | Cổng web trên máy host | `3000` |
| `VITE_API_BASE_URL` | Frontend | Đường dẫn API | `/api/v1` |
| `VITE_BACKEND_PROXY_TARGET` | Frontend | URL Backend trong Docker network | `http://backend:8000` |

**Lưu ý bảo mật:**

- Không commit file `.env`. File này đã nằm trong `.gitignore`.
- Không đưa mật khẩu Wi-Fi, API key, token, thông tin đăng nhập cơ sở dữ liệu lên GitHub.
- Khi thêm biến mới, cập nhật `.env.example` (không chứa giá trị thật) để các thành viên khác cấu hình được.
- Các biến phải thống nhất với cấu hình Docker Compose và từng dịch vụ.

## 9. Khởi chạy dự án bằng Docker Compose

Thực hiện tại thư mục chứa file `compose.yaml`, `compose.yml`, `docker-compose.yaml` hoặc `docker-compose.yml`.

### 9.0. Các dịch vụ chạy bằng Docker

| Thành phần | Thư mục mã nguồn | Tên dịch vụ trong Compose | Ghi chú |
|---|---|---|---|
| CV/AI | `cv/` | `cv` | API scaffold; camera/video chưa được tích hợp |
| Backend (FastAPI) | `backend/` | `backend` | API scaffold; chờ PostgreSQL và CV healthy |
| PostgreSQL | Image `postgres:16.6-alpine` | `db` | Chờ healthcheck; dữ liệu lưu ở volume `postgres_data` |
| Frontend | `frontend/` | `frontend` | Dashboard đang phát triển; chờ Backend healthy |

Các service giao tiếp nội bộ qua network bridge `seatsense_network`. Backend kết
nối PostgreSQL bằng hostname `db`; Frontend proxy đường dẫn `/api` tới hostname
`backend`.

### 9.1. Kiểm tra cấu hình

```bash
docker compose config
```

Nếu có lỗi, kiểm tra file Compose và biến môi trường trước khi tiếp tục.

### 9.2. Khởi chạy

```bash
docker compose up --build
```

- `up`: tạo và khởi chạy các dịch vụ.
- `--build`: build lại image khi cần.
- Lệnh chạy foreground và hiển thị log trong terminal. Muốn chạy nền, dùng `docker compose up -d --build`.

Lần chạy đầu có thể mất thêm thời gian để tải image.

Các dịch vụ hiện cung cấp PostgreSQL, health check và API scaffold; chức năng đặt phòng, check-in, phát hiện mật độ, xác thực và dashboard chưa được triển khai.

### 9.3. Kiểm tra trạng thái

```bash
docker compose ps
```

### 9.4. Xem log

```bash
docker compose logs                  # tất cả dịch vụ
docker compose logs -f               # theo dõi liên tục
docker compose logs -f <service_name>  # một dịch vụ cụ thể
```

Tên dịch vụ trong file Compose: `db`, `backend`, `cv`, `frontend`.

### 9.5. Khởi động lại

```bash
docker compose restart
docker compose restart <service_name>
```

### 9.6. Dừng dự án

```bash
docker compose down
```

Lệnh này dừng và xóa container cùng network `seatsense_network`. Dữ liệu trong volume thường vẫn được giữ.

> **Không dùng `docker compose down -v` nếu chưa chắc chắn**, vì lệnh này có thể xóa volume chứa dữ liệu cơ sở dữ liệu.

## 10. Cổng truy cập

| Thành phần | Cổng | Địa chỉ truy cập |
|---|---|---|
| Frontend | `3000` | <http://localhost:3000> |
| Backend API | `8000` | <http://localhost:8000/docs> |
| PostgreSQL | `5432` | Không truy cập bằng trình duyệt |
| CV/AI | `8001` | <http://localhost:8001/docs> |

Để xác định cổng thực tế, chạy `docker compose ps` và kiểm tra phần `ports` trong file Compose cùng các biến môi trường liên quan.

## 11. Trạng thái chức năng

Chỉ đánh dấu "Hoàn thành" khi đã được kiểm thử hoặc xác nhận trong môi trường phát triển.

| Nhóm | Nội dung cần làm | Trạng thái |
|---|---|---|
| CV/AI | Kiểm thử và hoàn thiện phát hiện, theo dõi, đếm người | **`[CHƯA CÓ DỮ KIỆN]`** |
| Backend | Hoàn thiện API tiếp nhận và truy xuất dữ liệu | **`[CHƯA CÓ DỮ KIỆN]`** |
| Backend | Đặt phòng theo khung giờ, kiểm tra trùng lịch | **`[CHƯA CÓ DỮ KIỆN]`** |
| Backend | Check-in QR và tự động nhả phòng khi quá 10–15 phút | **`[CHƯA CÓ DỮ KIỆN]`** |
| Database | Hoàn thiện cấu trúc bảng và cơ chế lưu trữ | **`[CHƯA CÓ DỮ KIỆN]`** |
| Frontend | Hiển thị chỗ trống gần thời gian thực, đặt phòng | **`[CHƯA CÓ DỮ KIỆN]`** |
| Frontend | Dashboard thống kê cho thủ thư | **`[CHƯA CÓ DỮ KIỆN]`** |
| Tích hợp | Kiểm thử luồng dữ liệu CV/AI, Backend, PostgreSQL, Frontend | **`[CHƯA CÓ DỮ KIỆN]`** |
| Docker | Chạy đủ các dịch vụ bằng `docker compose up -d --build` | Đã kiểm tra: PostgreSQL, CV và Backend healthy; Frontend truy cập Backend qua proxy `/api`. |
| Thực nghiệm | Đối chiếu với đếm tay, thử nghiệm người dùng (SUS) | **`[CHƯA CÓ DỮ KIỆN]`** |

### Chỉ tiêu mục tiêu (theo Project Charter)

| Chỉ số | Mục tiêu | Kết quả đo được |
|---|---|---|
| Sai số đếm | ≤ 10% so với đếm tay (5–10 phiên × 30–60 phút) | **`[CHƯA CÓ DỮ KIỆN]`** |
| Độ trễ cập nhật | ≤ 5 giây, từ lúc có người vào đến lúc web hiển thị | **`[CHƯA CÓ DỮ KIỆN]`** |
| Tốc độ xử lý CV/AI | ≥ 5 FPS ở 416 px (hoặc chạy offline nếu thấp hơn) | **`[CHƯA CÓ DỮ KIỆN]`** |
| Trải nghiệm người dùng | Điểm SUS ≥ 70 (15–30 sinh viên dùng thử) | **`[CHƯA CÓ DỮ KIỆN]`** |

Các chỉ tiêu này sẽ được rà soát lại sau khảo sát thực địa.

## 12. Quy ước làm việc nhóm (Git và Jira)

Áp dụng cho mọi thành viên. Muốn đổi quy ước phải thống nhất trong buổi họp tuần và ghi vào [mục 15](#15-lịch-sử-thay-đổi).

### 12.1. Quy ước Jira

**Ba cấp công việc**

| Cấp | Dùng cho | Ví dụ |
|---|---|---|
| Epic | Một mảng lớn của dự án | CV/AI (phát hiện và đếm người) |
| Story | Một kết quả có giá trị, làm xong trong 1 sprint | Phát hiện được người trong video mẫu |
| Task (sub-task) | Một bước nhỏ, một người làm, 1–2 ngày | Viết hàm đọc khung hình từ video |

Nhánh Git và Pull Request luôn gắn với mã của Task đang làm. Story và Epic do nhóm trưởng chuyển Done sau khi mọi Task con xong và đã demo.

**Tiêu đề và mô tả**

- Tiêu đề bắt đầu bằng động từ, nêu rõ đối tượng, dưới 80 ký tự. Ví dụ: *Viết endpoint POST /events nhận sự kiện vào/ra*.
- Mô tả ghi mục tiêu và **tiêu chí hoàn thành** dạng gạch đầu dòng.
- Mỗi issue có đúng **một người phụ trách** (Assignee).

**Ý nghĩa các cột trên bảng**

| Cột | Ý nghĩa | Ai chuyển |
|---|---|---|
| To Do | Đã vào sprint, chưa bắt đầu | Nhóm trưởng |
| In Progress | Đang làm | Tự động khi tạo nhánh có mã issue |
| In Review | Đã mở Pull Request, chờ review | Tự động khi mở PR |
| Done | PR đã merge | Tự động khi merge PR |

**Ước lượng và nhãn**

- Story point theo dãy **1, 2, 3, 5, 8**: 1 là dưới nửa ngày, 2 khoảng một ngày, 3 một đến hai ngày, 5 khoảng ba ngày. Việc lớn hơn 5 cố gắng tách nhỏ; lớn hơn 8 bắt buộc tách.
- Nhãn vai trò: `PM`, `CV`, `BE`, `FE`. Nhãn sprint: `Sprint-0`, `Sprint-1`, ...

**Nguyên tắc làm việc**

- Không làm việc không có issue. Việc phát sinh thì tạo issue trước.
- Mỗi người tối đa **2 việc In Progress** cùng lúc.
- Vướng quá một ngày: comment trên issue, gắn tên người liên quan và báo trong standup.
- **Definition of Ready:** có tiêu đề rõ, tiêu chí hoàn thành, ước lượng, người nhận.
- **Definition of Done:** code đã review và merge, chạy được, có bằng chứng (ảnh, video ngắn hoặc bảng số liệu), có ghi chú tài liệu nếu thay đổi cách dùng.

### 12.2. Quy ước Git

**Nhánh**

| Nhánh | Mục đích | Quy tắc |
|---|---|---|
| `main` | Bản ổn định để demo và nộp | Cấm push trực tiếp. Chỉ merge từ `dev` qua PR do nhóm trưởng duyệt |
| `dev` | Nơi gộp công việc hằng ngày | Cấm push trực tiếp, chỉ merge qua PR |
| `feature/SEAT-x-ten-ngan` | Làm tính năng | Tạo từ `dev` |
| `fix/SEAT-x-ten-ngan` | Sửa lỗi | Tạo từ `dev` |
| `docs/SEAT-x-ten-ngan` | Tài liệu, báo cáo | Tạo từ `dev` |

Đặt tên nhánh: chữ thường, không dấu, nối bằng gạch ngang, bắt đầu bằng loại nhánh và mã issue. Ví dụ: `feature/SEAT-12-api-nhan-su-kien`. Mã issue phải **viết hoa đúng** (`SEAT-12`), nếu không Jira không nhận ra.

**Commit**

Dạng: `SEAT-x loai: noi dung ngan`

| Loại | Dùng khi |
|---|---|
| `feat` | Thêm tính năng |
| `fix` | Sửa lỗi |
| `docs` | Sửa tài liệu |
| `refactor` | Sắp xếp lại code, không đổi chức năng |
| `test` | Thêm hoặc sửa kiểm thử |
| `chore` | Việc lặt vặt (cấu hình, thư viện) |

```bash
git commit -m 'SEAT-12 feat: them endpoint nhan su kien vao ra'
git commit -m 'SEAT-12 fix: sua loi dem trung khi 2 nguoi di sat nhau'
```

- Viết tiếng Việt không dấu hoặc tiếng Anh, tối đa khoảng 72 ký tự.
- Mỗi commit một thay đổi có ý nghĩa; commit thường xuyên.
- Có thể ghi chú lên Jira từ commit: `SEAT-12 #comment da xong phan luu CSDL #time 2h`.
- **Không** dùng `#done` hay `#in-progress` trong commit, vì trạng thái do tự động hóa quản lý.

**Không đưa vào Git**

- Mật khẩu Wi-Fi, API key, token: để trong `.env` (đã có trong `.gitignore`), kèm `.env.example` không chứa giá trị thật.
- **Video và ảnh quay trong thư viện:** không commit vì liên quan quyền riêng tư. Lưu cục bộ, xóa sau khi xử lý xong.
- File lớn (model `.pt`, dữ liệu thô trên 50 MB): để trên Google Drive, ghi link trong `docs/`.
- File sinh tự động: `__pycache__`, `node_modules`, `.venv`, thư mục build.

### 12.3. Quy trình cho mỗi công việc

1. Nhận Task trên Jira, gán tên mình, đảm bảo thẻ đang ở **To Do**.
2. Cập nhật `dev`:

   ```bash
   git checkout dev
   git pull
   ```

3. Tạo nhánh có mã issue (Jira tự chuyển thẻ sang **In Progress**):

   ```bash
   git checkout -b feature/SEAT-12-api-nhan-su-kien
   ```

4. Làm việc, commit thường xuyên theo quy ước ở trên.
5. Trước khi push, lấy `dev` mới nhất để giảm xung đột:

   ```bash
   git fetch origin
   git merge origin/dev
   ```

6. Push nhánh:

   ```bash
   git push -u origin feature/SEAT-12-api-nhan-su-kien
   ```

7. Mở Pull Request vào `dev` (Jira tự chuyển thẻ sang **In Review**).
8. Sau khi được duyệt, bấm **Squash and merge**, xóa nhánh (Jira tự chuyển thẻ sang **Done**). Về máy:

   ```bash
   git checkout dev
   git pull
   ```

### 12.4. Pull Request

- **Tiêu đề** có mã issue: `SEAT-12 Them endpoint nhan su kien`.
- **Base** là `dev` (riêng PR từ `dev` vào `main` do nhóm trưởng tạo khi chốt mốc).
- **Mô tả** theo mẫu:

  ```markdown
  ## Lam gi
  (1-2 cau)

  ## Cach kiem tra
  (cac buoc de nguoi review chay thu)

  ## Anh / ket qua
  (anh chup, bang so lieu neu co)

  ## Lien quan
  SEAT-12
  ```

- Một PR chỉ giải quyết **một issue** và nên nhỏ (khoảng dưới 300 dòng thay đổi nếu có thể).
- Cần **ít nhất một người khác** review. Tác giả không tự merge PR của mình.
- Người được nhờ review trả lời trong vòng **24 giờ**.
- **Checklist review:** chạy được theo mục "Cách kiểm tra", đúng yêu cầu issue, không lộ bí mật hay dữ liệu cá nhân, tên rõ ràng, không có file thừa.
- Merge bằng **Squash and merge**, giữ mã issue ở đầu thông điệp commit gộp.

### 12.5. Tự động hóa Jira và GitHub

| Sự kiện trên GitHub | Jira tự chuyển | Điều kiện |
|---|---|---|
| Tạo nhánh có mã issue | To Do -> In Progress | Thẻ đang ở To Do |
| Mở Pull Request có mã issue | In Progress hoặc To Do -> In Review | Thẻ đang ở một trong hai cột này |
| Merge Pull Request | In Review hoặc In Progress -> Done | Thẻ đang ở một trong hai cột này |

- Chỉ chạy khi tên nhánh hoặc tiêu đề PR chứa **mã issue đúng, viết hoa**.
- Tự động hóa chỉ phản ứng với sự kiện **mới**. Tạo issue **trước** khi tạo nhánh.
- Thẻ không tự chuyển: kiểm tra mã, kiểm tra thẻ có đang ở đúng cột điều kiện không, rồi xem **Space settings -> Automation -> Audit log**.
- Chỉ kéo thẻ tay khi cần, ví dụ PR bị từ chối thì kéo về In Progress.

### 12.6. Nhịp làm việc theo sprint (1 tuần)

| Buổi | Thời gian | Nội dung |
|---|---|---|
| Sprint Planning | Thứ Hai, 30 phút | Chọn việc từ Backlog, giao người, ước lượng |
| Daily Standup | 15 phút mỗi ngày (hoặc nhắn trong nhóm chat) | Hôm qua làm gì, hôm nay làm gì, đang vướng gì |
| Sprint Review và Retro | Cuối tuần, 45 phút | Demo kết quả thật, rút kinh nghiệm |

### 12.7. Checklist trước khi push

- [ ] Tên nhánh và commit có đúng mã issue, viết hoa.
- [ ] Code chạy được trên máy mình.
- [ ] Không có bí mật, video, ảnh thư viện hay file lớn trong thay đổi (`git status`).
- [ ] Đã `git merge origin/dev` và xử lý xung đột.
- [ ] Issue Jira đã gán tên mình và có tiêu chí hoàn thành.

### 12.8. Ứng xử trong nhóm

- Review code để cải thiện sản phẩm, không để chê người. Góp ý cụ thể, lịch sự.
- Báo sớm khi trễ hoặc vướng.
- Tôn trọng quyền riêng tư: không chia sẻ dữ liệu khảo sát có thông tin cá nhân ra ngoài nhóm.

## 13. Xử lý lỗi thường gặp

### Docker và môi trường

| Tình huống | Cách xử lý |
|---|---|
| Docker không chạy | Kiểm tra Docker Desktop đã khởi động, chạy `docker info`, khởi động lại Docker Desktop nếu cần |
| Không tìm thấy file `.env` | Kiểm tra đang ở đúng thư mục dự án và đã tạo `.env` từ `.env.example` |
| Không khởi chạy được Compose | Chạy `docker compose config`, `docker compose logs`, `docker compose ps`; kiểm tra biến môi trường, tên dịch vụ, cấu hình cổng |
| Cổng đã được sử dụng | Tìm ứng dụng khác đang dùng cổng. Nếu đổi cổng, giữ cấu hình Frontend, Backend và Compose nhất quán |
| Cần cập nhật mã nguồn mới nhất | `git checkout dev` rồi `git pull origin dev`. Nếu đang ở nhánh cá nhân, lưu hoặc commit thay đổi trước khi chuyển nhánh |

### Git và Jira

| Tình huống | Cách xử lý |
|---|---|
| Quên mã issue ở commit cuối, **chưa push** | `git commit --amend -m 'SEAT-12 feat: noi dung'` |
| Lỡ commit trực tiếp trên `dev`, chưa push | Tạo nhánh giữ lại công việc: `git branch feature/SEAT-12-ten`, rồi đưa `dev` về đồng bộ: `git reset --hard origin/dev`. Nếu không chắc, hỏi nhóm trưởng trước |
| Xung đột khi merge | Mở file có dấu `<<<<<<<`, giữ đoạn đúng, xóa các dấu, rồi `git add` và `git commit`. Không chắc thì hỏi người viết đoạn đó |
| Jira không hiện commit hoặc nhánh | Kiểm tra mã issue, email Git, repo đã được cấp quyền cho app GitHub for Atlassian |
| Thẻ không tự chuyển | Xem [mục 12.5](#125-tự-động-hóa-jira-và-github) |
| Commit sai email | Sửa `git config user.email` rồi commit mới. Commit cũ sai email có thể bỏ qua |
| Lỡ đẩy mật khẩu hoặc API key lên repo | Báo nhóm trưởng ngay và **đổi mật khẩu hoặc key lập tức**. Xóa file là chưa đủ vì lịch sử vẫn còn |

Các lỗi riêng của từng thành phần (CV/AI, Backend, Frontend): **`[CHƯA CÓ DỮ KIỆN]`**

## 14. Kiểm tra README trên máy phát triển

Sau khi hoàn thành hướng dẫn, kiểm tra theo trình tự:

1. Clone repository trên máy phát triển.
2. Checkout và cập nhật nhánh `dev`.
3. Tạo `.env` từ `.env.example`.
4. Chạy `docker compose config`.
5. Chạy `docker compose up -d --build`.
6. Kiểm tra trạng thái bằng `docker compose ps`.
7. Kiểm tra log bằng `docker compose logs`.
8. Xác nhận các dịch vụ khởi động đúng và truy cập được tại các cổng đã công bố.
9. Kiểm tra chức năng đã triển khai và ghi nhận chức năng còn thiếu.
10. Cập nhật README nếu phát hiện bước nào không chính xác hoặc chưa đầy đủ.

**Trạng thái kiểm thử hướng dẫn:** Chưa xác nhận. Chỉ cập nhật thành "Đã kiểm tra" sau khi thực hiện thành công trên ít nhất một máy phát triển.

## 15. Lịch sử thay đổi

| Phiên bản | Ngày | Thay đổi | Người cập nhật |
|---|---|---|---|
| 1.0 | 26/10/2026 | Bản quy ước làm việc nhóm đầu tiên | [LD] |
| 1.1 | 28/10/2026 | Gộp README và quy ước Git/Jira thành một tài liệu; để trống các mục chưa có dữ kiện | **`** |
| 1.2 | 28/10/2026 | Bỏ phần cứng; chốt Phương án B (camera + YOLOv8n + ByteTrack) kèm Docker theo Project Charter; bổ sung đặt phòng, dashboard, chỉ tiêu | **`** |
