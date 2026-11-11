# UTH-SeatSense

## Mục lục

1. [Giới thiệu dự án](#1-giới-thiệu-dự-án)
2. [Kiến trúc tổng quan](#2-kiến-trúc-tổng-quan)
3. [Cấu trúc repository](#3-cấu-trúc-repository)
4. [Yêu cầu môi trường](#yêu-cầu-môi-trường)
5. [Cài đặt Git và Docker Desktop](#cài-đặt-git-và-docker-desktop)
6. [Cài đặt nhanh](#cài-đặt-nhanh-15-phút)
7. [Kiểm tra hệ thống](#kiểm-tra-hệ-thống)
8. [Cổng truy cập](#cổng-truy-cập)
9. [Chạy Computer Vision](#chạy-computer-vision)
10. [Chạy kiểm thử](#chạy-kiểm-thử)
11. [Cấu trúc thư mục](#cấu-trúc-thư-mục)
12. [Dừng và khởi động lại](#dừng-và-khởi-động-lại)
13. [Xử lý lỗi thường gặp](#xử-lý-lỗi-thường-gặp)
14. [Quy ước và tài liệu dự án](#quy-ước-làm-việc-nhóm)
15. [Liên hệ và hỗ trợ](#liên-hệ-và-hỗ-trợ)

---

## 1. Giới thiệu dự án

**UTH-SeatSense** (đề tài D6) là hệ thống hỗ trợ theo dõi mật độ sử dụng phòng đọc và đặt phòng học nhóm tại Thư viện UTH. Hệ thống kết hợp xử lý hình ảnh, API, cơ sở dữ liệu và giao diện web.

Mục tiêu của dự án:

- Phát hiện và đếm người từ camera hoặc video bằng Computer Vision.
- Tiếp nhận, xử lý và lưu số liệu đếm.
- Hiển thị tình trạng chỗ ngồi gần thời gian thực.
- Hỗ trợ đặt phòng học nhóm, check-in QR và nhả phòng khi quá hạn theo phạm vi chức năng được triển khai.
- Cung cấp dữ liệu thống kê phục vụ dashboard.
- Chạy các thành phần bằng Docker Compose để thống nhất môi trường phát triển.

## 2. Kiến trúc tổng quan

| Thành phần | Vai trò | Công nghệ |
|---|---|---|
| CV/AI (`cv/`) | Nhận video, phát hiện/theo dõi người và cung cấp dịch vụ CV | Python, FastAPI, YOLO/ByteTrack theo cấu hình CV |
| Backend (`backend/`) | API nghiệp vụ và kết nối cơ sở dữ liệu | Python, FastAPI, SQLAlchemy |
| Database (`db`) | Lưu trữ dữ liệu hệ thống | PostgreSQL 16.6 |
| Frontend (`frontend/`) | Giao diện web và proxy API | React, Vite, TypeScript |
| Adminer (`adminer`) | Giao diện quản trị database cho phát triển | Adminer 4.8.1 |
| Orchestration | Xây dựng và kết nối các dịch vụ | Docker Compose |

Luồng dữ liệu dự kiến: CV xử lý hình ảnh tại chỗ và gửi dữ liệu đếm cho Backend; Backend lưu dữ liệu vào PostgreSQL; Frontend gọi API để hiển thị. Cấu hình dịch vụ hiện tại được định nghĩa trong [`docker-compose.yml`](docker-compose.yml).

```text
[Camera/video] -> CV -> số liệu đếm -> Backend -> PostgreSQL -> Frontend
```

Thiết kế hướng tới giảm dữ liệu hình ảnh truyền/lưu trữ và không nhận diện khuôn mặt hay danh tính. Khả năng camera, mô hình và từng chức năng cụ thể phụ thuộc cấu hình/runtime hiện có; xem [README CV](cv/README.md) và [README từng thành phần](#readme-từng-thành-phần).

## 3. Cấu trúc repository

```text
UTH-SeatSense/
├── cv/                 # Computer Vision service
├── backend/            # FastAPI backend
├── frontend/           # React + Vite frontend
├── database/init/      # SQL khởi tạo PostgreSQL
├── docs/               # Tài liệu dự án và kiến trúc
├── tests/              # Integration tests
├── docker-compose.yml  # Compose ở thư mục gốc
└── .env.example        # Mẫu cấu hình môi trường
```

Mỗi thành phần có README riêng với hướng dẫn chi tiết. Không commit `.env`, model riêng tư hoặc dữ liệu video có thể nhận diện người.

## Yêu cầu môi trường

Trước khi bắt đầu, đảm bảo máy đã cài:

- **Git** - [Tải tại đây](https://git-scm.com/downloads)
- **Docker Desktop** - [Tải tại đây](https://www.docker.com/products/docker-desktop/)
  - Windows: Chọn WSL 2 khi cài đặt
  - Mở Docker Desktop và đợi Engine khởi động

Kiểm tra cài đặt thành công:

```bash
git --version
docker --version
docker compose version
```

Nếu các lệnh trả về số phiên bản, môi trường đã sẵn sàng.

## Cài đặt Git và Docker Desktop

1. Tải Git phù hợp với hệ điều hành tại [git-scm.com/downloads](https://git-scm.com/downloads) và cài đặt theo hướng dẫn.
2. Mở Terminal hoặc PowerShell mới, kiểm tra:

```bash
git --version
```

### Cài Docker Desktop

1. Tải Docker Desktop tại [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) và cài đặt.
2. Trên Windows, chọn **Use WSL 2 instead of Hyper-V** nếu trình cài đặt hỏi. Nếu máy chưa có WSL 2, mở PowerShell với quyền Administrator, chạy `wsl --install`, rồi khởi động lại máy khi được yêu cầu.
3. Mở Docker Desktop, chờ Docker Engine khởi động. Kiểm tra trong PowerShell/Terminal:

```bash
docker --version
docker compose version
docker info
```

Nếu `docker info` trả thông tin Engine mà không báo lỗi kết nối, Docker đã sẵn sàng.

### Thiết lập thông tin Git

Thiết lập tên và email một lần trên mỗi máy. Dùng email gắn với tài khoản GitHub/Jira của bạn:

```bash
git config --global user.name "Ho Ten"
git config --global user.email "email-cua-ban@example.com"
```

Kiểm tra lại:

```bash
git config --global --get user.name
git config --global --get user.email
```

Để tham gia repository riêng của nhóm, tài khoản GitHub cần được cấp quyền truy cập. Không đưa mật khẩu, token hoặc khóa truy cập vào repository.

### Cấu hình nâng cao

Khi cần tra cứu đầy đủ các biến môi trường, cấu hình dịch vụ, và quy trình clone/cập nhật nhánh, xem [README cài đặt đầy đủ](docs/README-full.md).

---

## Cài đặt nhanh (15 phút)

### Bước 1: Clone repository

```bash
# Clone về máy
git clone https://github.com/uth-seatsense/UTH-SeatSense.git
cd UTH-SeatSense

# Chuyển sang nhánh dev
git checkout dev
git pull origin dev
```

### Bước 2: Tạo file cấu hình `.env`

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

**Chỉnh sửa `.env`:**

Mở file `.env` bằng editor và **thay đổi dòng này** (bắt buộc):

```bash
# Đổi từ:
POSTGRES_PASSWORD=replace-with-a-local-development-password

# Thành (ví dụ):
POSTGRES_PASSWORD=dev123456
```

Dùng mật khẩu đơn giản gồm chữ và số, không dấu. Đây chỉ là mật khẩu phát triển cục bộ.

> **Lưu ý:** Không đổi các giá trị khác trừ khi port bị conflict với ứng dụng khác đang chạy.

### Bước 3: Khởi động hệ thống

```bash
docker compose up -d --build
```

Lần đầu chạy sẽ mất 3-5 phút để tải images và build. Chờ đến khi thấy:

```
✔ Container uth-seatsense-db-1       Healthy
✔ Container uth-seatsense-cv-1       Healthy  
✔ Container uth-seatsense-backend-1  Healthy
✔ Container uth-seatsense-frontend-1 Started
✔ Container uth-seatsense-adminer-1  Started
```

---

## Kiểm tra hệ thống

### Kiểm tra trạng thái containers

```bash
docker compose ps
```

Kết quả mong đợi:

```
NAME                      STATUS
uth-seatsense-db-1        Up (healthy)
uth-seatsense-cv-1        Up (healthy)
uth-seatsense-backend-1   Up (healthy)
uth-seatsense-frontend-1  Up
uth-seatsense-adminer-1   Up
```

### Kiểm tra health endpoints

```bash
# Backend health check (kết nối database)
curl http://localhost:8000/health/db

# CV service health check
curl http://localhost:8001/health
```

Nếu cả hai trả về status `200 OK`, hệ thống đã sẵn sàng.

### Xem logs

```bash
# Xem log tất cả services
docker compose logs -f

# Xem log một service cụ thể
docker compose logs -f backend
docker compose logs -f cv
docker compose logs -f frontend
```

Nhấn `Ctrl+C` để thoát.

---

## Cổng truy cập

Sau khi khởi động thành công, truy cập các địa chỉ sau:

| Thành phần | URL | Mô tả |
|-----------|-----|-------|
| **Frontend** | http://localhost:3000 | Giao diện web chính |
| **Backend API** | http://localhost:8000/docs | Swagger UI - tài liệu API |
| **CV Service** | http://localhost:8001 | Giao diện kiểm thử CV |
| **CV API Docs** | http://localhost:8001/docs | API tài liệu CV service |
| **Adminer** | http://localhost:8080 | Web UI quản lý PostgreSQL |

### Đăng nhập Adminer (quản lý database)

1. Mở http://localhost:8080
2. Điền thông tin (lấy từ file `.env`):
   - **System:** PostgreSQL
   - **Server:** `db`
   - **Username:** `seatsense` (hoặc giá trị `POSTGRES_USER`)
   - **Password:** Mật khẩu bạn đã đặt trong `POSTGRES_PASSWORD`
   - **Database:** `seatsense` (hoặc giá trị `POSTGRES_DB`)

---

## Chạy Computer Vision

Dịch vụ CV có **hai chế độ chạy**:

### Chế độ 1: Trong Docker với video mẫu (mặc định)

CV service đã chạy trong Docker khi bạn `docker compose up`.

- Truy cập: http://localhost:8001
- Upload video để kiểm thử
- Chọn "Uploaded File" → chọn video → "Start Test"

**Không hỗ trợ webcam trong Docker.**

### Chế độ 2: Ngoài Docker với camera thật

Để dùng camera laptop hoặc camera USB:

**1. Dừng CV container:**
```bash
docker compose stop cv
```

**2. Tải model (chỉ lần đầu):**
- Tải `best.pt` từ [Google Drive](https://drive.google.com/drive/folders/1q9-reDJxYw5hAdOfVUG4kNONaYuXL7j0)
- Đặt vào thư mục: `cv/models/best.pt`

**3. Cài môi trường Python:**

**Windows:**
```powershell
cd cv
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS/Linux:**
```bash
cd cv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**4. Khởi động CV service:**

**Windows:**
```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001
```

**macOS/Linux:**
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

**5. Truy cập và dùng camera:**
- Mở: http://127.0.0.1:8001
- Chọn "USB Webcam" → "Start Test" → cho phép camera trong browser

**Lưu ý:** 
- Backend vẫn chạy trong Docker và sẽ không kết nối được CV khi CV chạy ngoài Docker
- Để Backend kết nối CV ngoài Docker, sửa `CV_SERVICE_URL` thành `http://host.docker.internal:8001`

### CLI - Xử lý video offline (không cần API)

```powershell
cd cv
.\.venv\Scripts\python.exe run_video.py --video videos/sample.mp4 --annotate
```

Kết quả xuất ra thư mục `cv/outputs/`.

Chi tiết xem [cv/README.md](cv/README.md).

---

## Chạy kiểm thử

### Backend Tests

```bash
# Từ thư mục gốc
docker compose exec backend pytest

# Hoặc chạy trực tiếp trên máy
cd backend
python -m pytest
```

### CV Tests

```bash
# Cần tải model trước (xem phần "Chạy Computer Vision")
cd cv

# Windows
.\.venv\Scripts\python.exe -m pytest tests/

# macOS/Linux  
python -m pytest tests/
```

Chi tiết kiểm thử xem:
- [cv/tests/PHASE1_RESULTS.md](cv/tests/PHASE1_RESULTS.md)
- [cv/tests/PHASE3_RESULTS.md](cv/tests/PHASE3_RESULTS.md)

### Frontend Tests

```bash
cd frontend
npm test
```

---

## Cấu trúc thư mục

```
UTH-SeatSense/
├── cv/                     # Computer Vision - YOLOv8n + ByteTrack
│   ├── main.py            # CV API service (FastAPI)
│   ├── run_video.py       # CLI xử lý video offline
│   ├── app/               # Detection, tracking, counting logic
│   ├── models/            # Model files (best.pt) - KHÔNG trong Git
│   ├── videos/            # Video mẫu để test - KHÔNG trong Git
│   ├── tests/             # Unit tests và integration tests
│   └── README.md          # Hướng dẫn chi tiết CV
│
├── backend/               # FastAPI Backend
│   ├── main.py           # Entry point
│   ├── app/              
│   │   ├── api/          # REST API endpoints
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── db/           # Database connection
│   ├── tests/            # Backend tests
│   └── README.md         # Hướng dẫn chi tiết Backend
│
├── frontend/             # React + Vite Frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   └── App.tsx       # Main app
│   ├── tests/            # Frontend tests
│   └── README.md         # Hướng dẫn chi tiết Frontend
│
├── database/             # Database scripts
│   └── init/             # Init SQL scripts (chạy khi tạo DB lần đầu)
│
├── docs/                 # Tài liệu dự án
│   ├── architecture/     # Kiến trúc, deployment, ADR
│   │   ├── deployment-diagram.md
│   │   └── cv-data-contract.md
│   ├── README-full.md    # README phiên bản đầy đủ (quy ước Git/Jira chi tiết)
│   └── README.md
│
├── tests/                # Integration tests (cross-service)
│
├── docker-compose.yml    # Cấu hình Docker Compose
├── .env.example          # Mẫu file cấu hình (có chú thích)
├── .env                  # File cấu hình thực tế - KHÔNG commit
├── .gitignore            # Loại trừ .env, models, videos khỏi Git
└── README.md             # File này
```

### Quy tắc quan trọng

- Mỗi thư mục con có `README.md` riêng với hướng dẫn chi tiết
- **KHÔNG commit** các file sau:
  - `.env` (chứa mật khẩu)
  - `cv/models/*.pt` (model lớn, lưu trên Google Drive)
  - `cv/videos/*.mp4` (video mẫu có thể chứa người thật)
  - `__pycache__/`, `node_modules/`, `.venv/`

---

## Dừng và khởi động lại

### Dừng hệ thống (giữ dữ liệu)

```bash
docker compose down
```

Lệnh này dừng và xóa containers, nhưng **GIỮ volume `postgres_data`**.

**TC-12 compliant:** Dữ liệu PostgreSQL vẫn còn khi khởi động lại.

### Khởi động lại

```bash
docker compose up -d
```

Dữ liệu database từ lần chạy trước vẫn còn nguyên.

### Reset toàn bộ (XÓA dữ liệu)

```bash
# Dừng và xóa containers + volumes
docker compose down -v

# Khởi động lại với database trống
docker compose up -d --build
```

> **Cảnh báo:** `-v` xóa toàn bộ dữ liệu PostgreSQL. Chỉ dùng khi muốn reset hệ thống.

### Rebuild sau khi sửa code

```bash
# Rebuild tất cả
docker compose up -d --build

# Rebuild một service
docker compose up -d --build backend
```

### Xem resource usage

```bash
docker compose stats
```

---

## Xử lý lỗi thường gặp

### Lỗi: Port đã được sử dụng

```
Error: bind: address already in use
```

**Giải pháp:**
1. Tìm ứng dụng đang dùng port:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # macOS/Linux
   lsof -i :8000
   ```

2. Đổi port trong `.env`:
   ```bash
   BACKEND_PORT=8001
   ```

3. Restart:
   ```bash
   docker compose up -d --build
   ```

### Lỗi: Thiếu POSTGRES_PASSWORD

```
Error: Set POSTGRES_PASSWORD in .env
```

**Giải pháp:**
1. Kiểm tra file `.env` tồn tại:
   ```bash
   ls -la .env
   ```

2. Nếu chưa có, tạo từ `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Mở `.env` và điền `POSTGRES_PASSWORD=dev123456`

### Lỗi: Service không healthy

```bash
# Xem log để tìm lỗi
docker compose logs db
docker compose logs backend
docker compose logs cv

# Restart service
docker compose restart backend
```

### Lỗi: Cannot connect to Docker daemon

**Giải pháp:**
1. Mở Docker Desktop
2. Đợi Engine khởi động (icon Docker trên taskbar không còn loading)
3. Chạy lại `docker compose up -d`

### Lỗi: Camera không hoạt động trong Docker

**Nguyên nhân:** Docker container không truy cập được webcam.

**Giải pháp:** Chạy CV ngoài Docker (xem phần [Chạy Computer Vision](#chạy-computer-vision)).

### Database connection refused

```bash
# Kiểm tra db container
docker compose ps db

# Restart db
docker compose restart db

# Kiểm tra kết nối từ backend
docker compose exec backend python -c "import psycopg2; print('OK')"
```

---

## Quy ước làm việc nhóm

### Quy tắc ngắn gọn

1. **Nhánh:**
   - `main` - Bản ổn định (cấm push trực tiếp)
   - `dev` - Nhánh phát triển (cấm push trực tiếp)
   - `feature/SEAT-X-ten-ngan` - Làm tính năng mới
   - `fix/SEAT-X-ten-ngan` - Sửa lỗi

2. **Commit message:**
   ```bash
   SEAT-12 feat: them endpoint nhan su kien
   SEAT-12 fix: sua loi dem trung
   ```

3. **Pull Request:**
   - Tạo PR vào `dev`
   - Cần ít nhất 1 người review
   - Merge bằng "Squash and merge"

4. **KHÔNG commit:**
   - File `.env` (password)
   - Video/ảnh người dùng thật
   - Model files (`*.pt`)
   - API keys, tokens

**Quy ước đầy đủ (Git, Jira, Sprint):** Xem [docs/README-full.md](docs/README-full.md)

---

## Tài liệu chi tiết

### Kiến trúc và thiết kế

- [docs/architecture/deployment-diagram.md](docs/architecture/deployment-diagram.md) - Sơ đồ triển khai Docker
- [docs/architecture/cv-data-contract.md](docs/architecture/cv-data-contract.md) - Hợp đồng dữ liệu CV → Backend
- [docs/decisions.md](docs/decisions.md) - Các quyết định kiến trúc (ADR)

### README từng thành phần

- [cv/README.md](cv/README.md) - Computer Vision service
- [backend/README.md](backend/README.md) - Backend API
- [frontend/README.md](frontend/README.md) - Frontend web
- [database/README.md](database/README.md) - Database schema

### Quy ước và quy trình

- [docs/README-full.md](docs/README-full.md) - Quy ước Git/Jira, Sprint, Review, Checklist đầy đủ

### Kiểm thử

- [cv/tests/PHASE1_RESULTS.md](cv/tests/PHASE1_RESULTS.md) - Kết quả test CV giai đoạn 1
- [cv/tests/PHASE3_RESULTS.md](cv/tests/PHASE3_RESULTS.md) - Kết quả test CV giai đoạn 3
- [tests/README.md](tests/README.md) - Integration tests

---

## Liên hệ và hỗ trợ

- **GitHub:** https://github.com/uth-seatsense/UTH-SeatSense
- **Jira:** Liên hệ nhóm trưởng để được mời vào workspace

### Báo lỗi hoặc đề xuất

Tạo issue trên GitHub hoặc Jira task với:
- Mô tả vấn đề
- Các bước tái hiện
- Logs liên quan (`docker compose logs`)
- Screenshots nếu có

---

**Cập nhật lần cuối:** 2026-11-09  
**Phiên bản README:** 2.0 (Streamlined for quick start)
