# Android — Ứng dụng UTH SeatSense

Ứng dụng Android gốc viết bằng **Kotlin + Jetpack Compose**, dùng chung API Backend (`FastAPI`) với giao diện web để đăng nhập OTP, lưu phiên đăng nhập an toàn (AES-GCM qua Android Keystore), xem tình trạng chỗ trống, đặt phòng chuyên đề và check-in bằng QR.

## 1. Cấu trúc chính (SEAT-78)

| Thành phần | Vai trò |
|---|---|
| `app/build.gradle.kts` | Cấu hình Android SDK 35 (`minSdk = 26`), Compose và biến `BuildConfig.API_BASE_URL` |
| `data/ApiClient.kt` | Lớp gọi REST API (`auth/register`, `auth/login`, `auth/me`, `auth/logout`, ...) lấy URL từ cấu hình |
| `data/TokenStore.kt` | Lưu access token mã hóa AES-256-GCM bằng `AndroidKeyStore` (hỗ trợ tùy chọn *Ghi nhớ thiết bị*) |
| `ui/LoginScreen.kt` | Màn hình đăng nhập OTP 2 bước theo thiết kế Figma (đếm ngược OTP 5 phút, gửi lại sau 60s) |
| `ui/SeatSenseApp.kt` | Điều phối phiên đăng nhập, trạng thái lỗi/mạng và màn hình chính sau đăng nhập |

## 2. Yêu cầu môi trường

- **Android Studio** (khuyên dùng phiên bản hỗ trợ AGP 8.9.2 / Kotlin 2.1.20).
- **JDK 17**.
- **Android SDK Platform 35** (Build-Tools tương ứng).
- Thiết bị thật hoặc máy ảo chạy **Android 8.0 (API 26)** trở lên.

## 3. Cấu hình Backend chạy trong Docker

Trước khi thử đăng nhập trên Android, đảm bảo hệ thống Backend + PostgreSQL đang chạy (`docker compose up -d`) và file `.env` ở thư mục gốc đã cấu hình OTP (theo SEAT-65 & SEAT-70):

1. Đặt `ALLOWED_EMAIL_DOMAINS=ut.edu.vn` (hoặc tên miền thử nghiệm phù hợp).
2. Đặt `OTP_HASH_SECRET` là chuỗi ngẫu nhiên tối thiểu 32 ký tự.
3. Cấu hình biến `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` (dùng SMTP Gmail hoặc SMTP giả lập khi chạy local theo SEAT-70).
4. Khởi động lại backend nếu vừa sửa `.env`:

```powershell
docker compose up -d --force-recreate backend
```

> **Lưu ý mạng trên Windows khi test bằng điện thoại thật:** Máy tính chạy Docker và điện thoại phải cùng mạng Wi-Fi, đồng thời mở inbound port `8000` trên Windows Firewall để điện thoại gọi được tới `http://<IP_MAY_TINH>:8000/api/v1/`.

## 4. Đổi địa chỉ API (không ghi cứng)

Ứng dụng đọc địa chỉ máy chủ mặc định vào `BuildConfig.API_BASE_URL` theo thứ tự ưu tiên:
1. Gradle property `-PseatsenseApiBaseUrl=...` lúc build
2. Khóa `seatsense.api.base.url=...` trong `android/local.properties`
3. Biến môi trường `SEATSENSE_API_BASE_URL`
4. Mặc định cho Android Emulator: `http://10.0.2.2:8000/api/v1/`

Ngoài ra, trên màn hình đăng nhập có nút cấu hình nhỏ ở góc trên bên phải cho phép đổi URL máy chủ khi kiểm thử trực tiếp trên máy ảo hoặc điện thoại thật.

> Chỉ bản `debug` bật `usesCleartextTraffic="true"` để gọi HTTP nội bộ; bản phát hành (`release`) yêu cầu HTTPS.

## 5. Cách build APK và chạy unit test

### Cách A: Tải APK build tự động từ GitHub Actions (không cần cài Android Studio)
1. Mở tab **Actions** trên repo GitHub → chọn workflow **Android Build & Test**.
2. Chọn lần chạy mới nhất của nhánh `feat/SEAT-78-android-otp-login` (hoặc bấm **Run workflow** nếu muốn truyền sẵn `-PseatsenseApiBaseUrl` / `api_base_url`).
3. Cuộn xuống mục **Artifacts** và tải `seatsense-debug-apk` → giải nén lấy `app-debug.apk`.
4. Khi mở app trên điện thoại thật cùng Wi-Fi với máy chạy Docker, bấm nút tròn ở góc trên bên phải màn hình đăng nhập để đổi `API Base URL` sang `http://<IP_MAY_TINH>:8000/api/v1/`.

### Cách B: Build trực tiếp bằng Android Studio / dòng lệnh
Mở terminal tại thư mục gốc repository (`UTH-SeatSense/`):

### Chạy unit test + build APK cho Emulator:
```powershell
.\android\gradlew.bat testDebugUnitTest assembleDebug
```

### Build APK kết nối Backend từ điện thoại thật (cùng Wi-Fi):
Tìm IPv4 máy tính chạy Docker bằng `ipconfig` (ví dụ `192.168.1.25`), sau đó build:
```powershell
.\android\gradlew.bat assembleDebug "-PseatsenseApiBaseUrl=http://192.168.1.25:8000/api/v1/"
```

Sau khi build thành công, file APK nằm tại:
```text
android/app/build/outputs/apk/debug/app-debug.apk
```

*(Hoặc mở thư mục `android/` trong **Android Studio**, đợi Gradle sync xong rồi chọn **Build → Build Bundle(s) / APK(s) → Build APK(s)**).*

## 6. Cài đặt APK lên điện thoại thật

### Cách 1: Cài trực tiếp qua file APK
1. Copy file `android/app/build/outputs/apk/debug/app-debug.apk` sang điện thoại (qua cáp USB, Zalo/Drive nội bộ).
2. Mở file `.apk` trên điện thoại Android, cho phép **Cài đặt ứng dụng không xác định nguồn gốc** nếu hệ thống hỏi và bấm **Cài đặt**.

### Cách 2: Cài bằng `adb` (khi bật USB Debugging)
```powershell
adb install -r android\app\build\outputs\apk\debug\app-debug.apk
```

## 7. Kiểm thử xác nhận (SEAT-78)
1. Mở app **UTH SeatSense** trên điện thoại hoặc emulator.
2. Nhập email được phép trong `ALLOWED_EMAIL_DOMAINS` (VD: `2151050123@ut.edu.vn`) và bấm **Gửi mã OTP**.
3. Nhập mã OTP 6 chữ số nhận được từ email/SMTP test, chọn **Ghi nhớ thiết bị này** nếu muốn giữ phiên, rồi bấm **Xác thực OTP & Đăng nhập**.
4. Xác nhận vào được màn hình chính (`Xin chào, ...` với các tab `Chỗ trống`, `Đặt phòng`, `Lịch đặt`) và đóng mở lại app vẫn giữ phiên đăng nhập hợp lệ.
