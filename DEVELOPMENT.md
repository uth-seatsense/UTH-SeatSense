# Hướng Dẫn Phát Triển

## ⚠️ QUY TẮC QUAN TRỌNG

**TẤT CẢ DEV PHẢI CHẠY TRÊN DOCKER - PORT 3000**

- ❌ **KHÔNG** chạy `npm run dev` trực tiếp
- ❌ **KHÔNG** sử dụng port khác ngoài 3000
- ✅ **BẮT BUỘC** sử dụng Docker Compose

## Lý Do

- Đảm bảo môi trường đồng nhất cho cả team
- Tránh lỗi "works on my machine"
- Backend, database, CV service đều chạy trong Docker
- Volumes đã được mount để sync code

## Khởi Động Môi Trường Dev

### Lần Đầu Tiên

```bash
# 1. Copy file .env
cp .env.example .env

# 2. Cấu hình POSTGRES_PASSWORD trong .env
# POSTGRES_PASSWORD=your_secure_password

# 3. Build và khởi động tất cả services
docker-compose up --build
```

### Các Lần Sau

```bash
# Windows: Chạy script
.\start-dev.bat

# Linux/Mac: Chạy script
./start-dev.sh

# Hoặc dùng docker-compose trực tiếp
docker-compose up
```

## Truy Cập Ứng Dụng

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Adminer (DB)**: http://localhost:8080

## Hot Reload / Live Update

### ⚠️ Lưu Ý Quan Trọng

Do Windows/Docker limitations, hot reload có thể **KHÔNG** hoạt động tự động. 

**Giải pháp khi sửa code:**

```bash
# Sau khi sửa code frontend, restart container
docker-compose restart frontend

# Container restart rất nhanh (~3-5 giây)
# Refresh browser để thấy thay đổi
```

### Khi Nào Cần Rebuild?

```bash
# Thêm package mới trong package.json
docker-compose build frontend
docker-compose up -d frontend

# Thay đổi Dockerfile hoặc .env
docker-compose up --build

# Reset toàn bộ (khi có vấn đề)
docker-compose down
docker-compose up --build
```

## Workflow Phát Triển Thực Tế

### Quy Trình Chuẩn

1. **Khởi động Docker** (một lần mỗi ngày)
   ```bash
   docker-compose up -d
   ```

2. **Sửa code** trên editor yêu thích

3. **Restart để xem thay đổi**
   ```bash
   docker-compose restart frontend
   ```

4. **Refresh browser** (F5 hoặc Ctrl+R)

5. **Lặp lại bước 2-4**

### Tips Tăng Tốc

```bash
# Alias để restart nhanh (thêm vào ~/.bashrc hoặc PowerShell profile)
alias dcrf="docker-compose restart frontend"

# Windows PowerShell: thêm vào $PROFILE
function dcrf { docker-compose restart frontend }

# Sau đó chỉ cần gõ:
dcrf
```

## Dừng Services

```bash
# Dừng tất cả
docker-compose down

# Dừng và xóa volumes (reset database)
docker-compose down -v

# Dừng nhưng giữ containers (tiết kiệm thời gian khởi động)
docker-compose stop
```

## Xem Logs

```bash
# Xem tất cả logs
docker-compose logs -f

# Xem logs frontend
docker-compose logs -f frontend

# Xem logs backend  
docker-compose logs -f backend

# Xem 50 dòng cuối
docker-compose logs --tail=50 frontend
```

## Chạy Tests

```bash
# Frontend tests
docker-compose exec frontend npm test

# Backend tests
docker-compose exec backend pytest

# Lint
docker-compose exec frontend npm run lint

# Format check
docker-compose exec frontend npm run format:check
```

## Troubleshooting

### Hot reload không hoạt động

**Đây là hiện tượng bình thường trên Windows/Docker.**

✅ **Giải pháp**: Restart container sau mỗi lần sửa code
```bash
docker-compose restart frontend
```

### Port 3000 đã được sử dụng

```bash
# Tìm process đang dùng port 3000
# Windows
netstat -ano | findstr :3000

# Linux/Mac
lsof -i :3000

# Dừng container cũ
docker-compose down
```

### Container không start

```bash
# Xem logs chi tiết
docker-compose logs frontend

# Rebuild từ đầu
docker-compose down
docker-compose build --no-cache frontend
docker-compose up
```

### Code thay đổi nhưng browser không cập nhật

```bash
# 1. Restart container
docker-compose restart frontend

# 2. Hard refresh browser
# Chrome/Firefox: Ctrl+Shift+R
# Windows: Ctrl+F5

# 3. Nếu vẫn không được, clear cache browser
```

### Lỗi "node_modules" hoặc dependencies

```bash
# Rebuild với clean install
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## Cấu Trúc Volumes

```yaml
volumes:
  - ./frontend:/app          # Code local → container
  - /app/node_modules        # node_modules ở trong container
```

**Lưu ý:**
- Code được sync real-time vào container
- `node_modules` không được sync (tránh xung đột OS)
- Sửa code local → phản ánh ngay trong container
- Cần restart container để browser nhận thay đổi

## Git Workflow

```bash
# 1. Pull code mới
git pull origin main

# 2. Nếu có thay đổi dependencies, rebuild
docker-compose up --build

# 3. Dev như bình thường
docker-compose up -d

# 4. Sửa code → restart → test
docker-compose restart frontend
```

## Checklist Trước Khi Commit

- [ ] Code chạy được trên Docker port 3000
- [ ] Không có lỗi trong browser console
- [ ] Không có lỗi trong container logs: `docker-compose logs frontend`
- [ ] Tests pass: `docker-compose exec frontend npm test`
- [ ] Lint pass: `docker-compose exec frontend npm run lint`
- [ ] Đã test trên cả Cơ sở 1 và Cơ sở 3

## So Sánh: Docker vs Local

| Tiêu chí | Docker (Bắt buộc) | Local `npm run dev` |
|----------|-------------------|---------------------|
| Port | 3000 | 5173 (không chuẩn) |
| Môi trường | Đồng nhất cho team | Khác nhau mỗi máy |
| Backend | Tích hợp sẵn | Phải chạy riêng |
| Database | Tích hợp sẵn | Phải setup riêng |
| Hot reload | Restart container | Tự động |
| Speed | Nhanh (~3s restart) | Nhanh hơn chút |

**Kết luận**: Restart 3s là trade-off nhỏ để có môi trường chuẩn.

## Tips & Tricks

### 1. Tăng tốc restart

Thêm vào PowerShell profile (`$PROFILE`):
```powershell
function dcrf { docker-compose restart frontend; Write-Host "✅ Frontend restarted!" }
function dcl { docker-compose logs -f frontend }
function dcs { docker-compose ps }
```

### 2. Kiểm tra containers đang chạy

```bash
docker-compose ps
```

### 3. Vào trong container để debug

```bash
docker-compose exec frontend sh
# Hoặc
docker-compose exec backend bash
```

### 4. Xem resource usage

```bash
docker stats
```

## FAQ

**Q: Tại sao không dùng `npm run dev` local?**  
A: Để đảm bảo tất cả dev có cùng môi trường. Backend, database, CV service đều trong Docker.

**Q: Hot reload có chậm không?**  
A: Restart container mất ~3s, là trade-off hợp lý.

**Q: Có thể dev trên port 5173 được không?**  
A: Không. Bắt buộc port 3000 để đồng bộ team.

**Q: Làm sao biết container đang chạy?**  
A: `docker-compose ps` - status phải là "Up"

**Q: Container bị crash liên tục?**  
A: Xem logs: `docker-compose logs frontend` và fix lỗi syntax

## Liên Hệ

Nếu có vấn đề:
1. Check logs: `docker-compose logs frontend`
2. Hỏi trên group chat
3. Tạo issue trên GitHub với logs đầy đủ
