# Deployment Diagram

## Tổng quan triển khai

Hệ thống UTH-SeatSense được triển khai bằng Docker Compose với 5 dịch vụ chính:

```
┌──────────────────────────────────────────────────────────────────────┐
│                          Docker Host Machine                         │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │              Docker Compose - seatsense_network                 │ │
│  │                        (Bridge Network)                         │ │
│  │                                                                 │ │
│  │  ┌──────────────┐      ┌──────────────┐      ┌─────────────┐    │ │
│  │  │   Frontend   │      │   Backend    │      │      CV     │    │ │
│  │  │  React/Vite  │────▶│   FastAPI    │─────▶│   FastAPI   │    │ │
│  │  │  Port: 3000  │      │  Port: 8000  │      │ Port: 8001  │    │ │
│  │  └──────────────┘      └──────────────┘      └─────────────┘    │ │
│  │         │                      │                                │ │
│  │         │                      │                                │ │
│  │         │                      ▼                                │ │
│  │         │              ┌──────────────┐                         │ │
│  │         │              │  PostgreSQL  │                         │ │
│  │         │              │    16.6      │                         │ │
│  │         │              │  Port: 5432  │                         │ │
│  │         │              └──────────────┘                         │ │
│  │         │                      │                                │ │
│  │         │                      │                                │ │
│  │         └──────────────────────┴────────┐                       │ │
│  │                                         ▼                       │ │
│  │                                  ┌──────────────┐               │ │
│  │                                  │   Adminer    │               │ │
│  │                                  │  DB Manager  │               │ │
│  │                                  │  Port: 8080  │               │ │
│  │                                  └──────────────┘               │ │
│  │                                                                 │ │
│  │  ┌─────────────────────────────────────────────────────────┐    │ │
│  │  │              Volume: postgres_data                      │    │ │
│  │  │         (Persistent database storage)                   │    │ │
│  │  └─────────────────────────────────────────────────────────┘    │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  External Access:                                                    │
│  • localhost:3000  → Frontend Web UI                                 │
│  • localhost:8000  → Backend API (docs: /docs)                       │
│  • localhost:8001  → CV API (docs: /docs)                            │
│  • localhost:5432  → PostgreSQL (database clients)                   │
│  • localhost:8080  → Adminer (database web UI)                       │
└──────────────────────────────────────────────────────────────────────┘

                              ▲
                              │
                    ┌─────────┴─────────┐
                    │                   │
              ┌─────────┐         ┌──────────┐
              │   Web   │         │  Native  │
              │ Browser │         │  Mobile  │
              └─────────┘         └──────────┘
                    │                   │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Portal/Admin    │
                    │   Web Interface   │
                    └───────────────────┘
```

## Chi tiết các dịch vụ

### 1. PostgreSQL Database (db)
- **Image**: `postgres:16.6-alpine`
- **Port**: 5432 (host) → 5432 (container)
- **Vai trò**: Lưu trữ dữ liệu hệ thống
- **Volume**: `postgres_data` - dữ liệu persistent, không mất khi restart
- **Init scripts**: `/docker-entrypoint-initdb.d` để khởi tạo schema
- **Health check**: `pg_isready` kiểm tra 5s/lần, retry 10 lần
- **Dependencies**: Không phụ thuộc dịch vụ nào (khởi động đầu tiên)

**Lưu trữ**:
- Rooms (phòng đọc, phòng học nhóm)
- Reservations (đặt phòng)
- Occupancy events (sự kiện vào/ra)
- Users (sinh viên, thủ thư)

### 2. CV Service (cv)
- **Build**: `./cv/Dockerfile`
- **Port**: 8001 (host) → 8001 (container)
- **Vai trò**: Computer Vision - phát hiện và đếm người
- **Công nghệ**: YOLOv8n + ByteTrack
- **Volume mount**: `./cv/models:/app/models:ro` (read-only)
- **Health check**: HTTP GET `/health` mỗi 10s
- **Dependencies**: Không phụ thuộc dịch vụ nào

**Hai chế độ chạy**:
1. **Trong Docker (mặc định)**: Xử lý video mẫu, không cần camera thật
2. **Ngoài Docker**: Chạy trực tiếp trên host với camera laptop hoặc camera USB
   ```bash
   # Ví dụ chạy ngoài Docker với camera
   cd cv
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py --camera 0  # Camera laptop
   python main.py --camera 1  # Camera USB ngoài
   ```

**Gửi dữ liệu**: POST `/events` → Backend API (chỉ gửi số liệu, không gửi hình ảnh)

### 3. Backend (backend)
- **Build**: `./backend/Dockerfile`
- **Port**: 8000 (host) → 8000 (container)
- **Vai trò**: API chính, xử lý nghiệp vụ, orchestration
- **Công nghệ**: FastAPI + SQLAlchemy + asyncpg
- **Health check**: HTTP GET `/health/db` mỗi 10s (kiểm tra kết nối DB)
- **Dependencies**: 
  - Chờ `db` healthy
  - Chờ `cv` healthy

**Kết nối**:
- Database: `postgresql://seatsense:password@db:5432/seatsense`
- CV Service: `http://cv:8001` (internal network)

**API Endpoints**:
- `/api/v1/rooms` - Quản lý phòng
- `/api/v1/reservations` - Đặt phòng
- `/api/v1/events` - Nhận dữ liệu đếm người từ CV
- `/api/v1/occupancy` - Truy vấn mật độ hiện tại
- `/health/db` - Health check

### 4. Frontend (frontend)
- **Build**: `./frontend/Dockerfile`
- **Port**: 3000 (host) → 3000 (container)
- **Vai trò**: Web UI cho sinh viên và thủ thư
- **Công nghệ**: React + Vite + TypeScript
- **Dependencies**: Chờ `backend` healthy

**Proxy**:
- Frontend proxy `/api/*` → `http://backend:8000/api/*` (không cần CORS)
- Cấu hình trong Vite: `VITE_BACKEND_PROXY_TARGET`

**Giao diện**:
- Dashboard: Hiển thị chỗ trống real-time
- Booking: Đặt phòng học nhóm
- QR Check-in: Quét QR để check-in
- Admin: Thống kê cho thủ thư

### 5. Adminer (adminer)
- **Image**: `adminer:4.8.1`
- **Port**: 8080 (host) → 8080 (container)
- **Vai trò**: Web UI quản lý PostgreSQL (development tool)
- **Dependencies**: Chờ `db` healthy

**Chỉ dùng cho môi trường phát triển**, không deploy production.

## Luồng dữ liệu

### Luồng 1: Đếm người (Real-time occupancy)
```
[Camera] → [CV Service] → [POST /api/v1/events] → [Backend] → [PostgreSQL]
                                                         ↓
[Web Browser] ← [GET /api/v1/occupancy/current] ← [Backend]
```

### Luồng 2: Đặt phòng (Room booking)
```
[User Web] → [POST /api/v1/reservations] → [Backend] → [PostgreSQL]
                                                 ↓
                                        [Check conflicts]
                                                 ↓
                                        [Generate QR code]
                                                 ↓
[User Web] ← [Return reservation + QR] ← [Backend]
```

### Luồng 3: Check-in QR
```
[User scans QR] → [POST /api/v1/reservations/{id}/checkin] → [Backend]
                                                                   ↓
                                                    [Update status in PostgreSQL]
                                                                   ↓
                                      [Schedule auto-release job (10-15 min)]
```

## Network và Communication

### Internal Network: seatsense_network (Bridge)
Tất cả containers giao tiếp qua Docker network nội bộ:
- Backend → DB: `postgresql://seatsense:password@db:5432/seatsense`
- Backend → CV: `http://cv:8001`
- Frontend → Backend: `http://backend:8000` (internal proxy)
- Adminer → DB: `db:5432`

### External Access (Host ports)
| Service | Internal Port | Host Port | URL |
|---------|--------------|-----------|-----|
| Frontend | 3000 | 3000 | http://localhost:3000 |
| Backend | 8000 | 8000 | http://localhost:8000 |
| CV | 8001 | 8001 | http://localhost:8001 |
| PostgreSQL | 5432 | 5432 | localhost:5432 |
| Adminer | 8080 | 8080 | http://localhost:8080 |

## Persistent Storage

### Volume: postgres_data
- **Mục đích**: Lưu trữ database files của PostgreSQL
- **Vị trí**: Docker managed volume (không lưu trực tiếp trong project)
- **Lifecycle**: 
  - `docker compose down` → Volume **vẫn tồn tại** (TC-12)
  - `docker compose down -v` → Volume **bị xóa** (reset database)
  - `docker compose up` lại → Dữ liệu cũ vẫn còn nếu không dùng `-v`

```bash
# Kiểm tra volumes
docker volume ls

# Xem chi tiết volume
docker volume inspect uth-seatsense_postgres_data

# Backup database
docker compose exec db pg_dump -U seatsense seatsense > backup.sql

# Restore database
docker compose exec -T db psql -U seatsense seatsense < backup.sql
```

## Health Checks và Dependencies

### Startup Order (dependencies)
```
1. db (PostgreSQL)          → Health: pg_isready
   ↓
2. cv (CV Service)          → Health: GET /health
   ↓
3. backend (Backend)        → Health: GET /health/db
   ↓
4. frontend (Frontend)      → No health check
5. adminer (Adminer)        → Depends on db
```

### Health Check Intervals
- **db**: 5s interval, 10 retries, 5s start period
- **cv**: 10s interval, 5 retries, 10s start period
- **backend**: 10s interval, 5 retries, 10s start period

Docker Compose tự động chờ các service phụ thuộc healthy trước khi khởi động service tiếp theo.

## Environment Variables Flow

```
.env file (host)
    ↓
docker-compose.yml reads variables
    ↓
    ├─→ db: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    ├─→ backend: DATABASE_HOST, DATABASE_NAME, CV_SERVICE_URL
    ├─→ cv: (currently none, future: MODEL_PATH, CAMERA_ID)
    ├─→ frontend: VITE_API_BASE_URL, VITE_BACKEND_PROXY_TARGET
    └─→ adminer: ADMINER_DEFAULT_SERVER
```

## Security Considerations

### Development (hiện tại)
- Passwords trong `.env` (không commit)
- Database port exposed để debug (5432)
- Adminer exposed (8080)
- Không có authentication/authorization

### Production (tương lai)
- [ ] Secrets management (Docker secrets hoặc vault)
- [ ] Database không expose port ra ngoài
- [ ] Tắt Adminer
- [ ] HTTPS/TLS cho tất cả services
- [ ] API authentication (JWT tokens)
- [ ] Rate limiting
- [ ] Network policies

## Client Applications

### Web Browser
- URL: http://localhost:3000
- Người dùng: Sinh viên, thủ thư
- Chức năng: Xem chỗ trống, đặt phòng, check-in, dashboard

### Native Mobile (future)
- Platform: React Native hoặc Flutter
- API: Gọi trực tiếp Backend API (http://api-server:8000)
- Chức năng tương tự Web

### Admin Portal
- URL: http://localhost:3000/admin (hoặc subdomain riêng)
- Người dùng: Thủ thư, quản trị viên
- Chức năng: Dashboard thống kê, quản lý phòng, xem logs

## Testing với Docker Compose

### Test file: docker-compose.test.yml
```bash
# Chạy tests trong isolated environment
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

Test containers có thể override configurations để:
- Sử dụng test database riêng
- Mock external services
- Run integration tests
- Generate test reports

## Troubleshooting

### Kiểm tra trạng thái
```bash
docker compose ps
docker compose logs <service>
docker compose top
```

### Restart một service
```bash
docker compose restart backend
docker compose up -d --no-deps --build backend
```

### Kiểm tra network connectivity
```bash
# Vào container backend
docker compose exec backend bash

# Ping other services
ping db
ping cv
curl http://cv:8001/health
```

### Database connection test
```bash
# Từ host machine
psql -h localhost -p 5432 -U seatsense -d seatsense

# Từ backend container
docker compose exec backend python -c "from database import engine; engine.connect()"
```

## Notes

- Tất cả services chạy trong Docker, không cần cài Python/Node.js trên host
- CV service có thể chạy ngoài Docker để truy cập camera thật
- Volume `postgres_data` đảm bảo dữ liệu không mất khi restart (TC-12)
- Health checks đảm bảo startup order đúng
- Internal network names (db, backend, cv) dùng làm hostname trong Docker
