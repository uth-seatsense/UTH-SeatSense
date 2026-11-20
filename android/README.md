# Android — Ứng dụng UTH SeatSense

Ứng dụng Kotlin/Jetpack Compose dùng chung API Backend để đăng nhập OTP,
xem tình trạng chỗ, đặt phòng chuyên đề, xem lịch đặt và check-in bằng QR.
Mã truy cập được mã hóa AES-GCM bằng Android Keystore.

## Yêu cầu

- Android Studio và Android SDK Platform 35.
- JDK 17.
- Thiết bị hoặc emulator Android 8.0 (API 26) trở lên. API 26 hiện là giả
  định tạm thời, cần xác nhận theo đặc tả thiết bị của dự án.

## Cấu hình Backend

Tạo `.env` từ `.env.example`, sau đó cấu hình `ALLOWED_EMAIL_DOMAINS`,
`OTP_HASH_SECRET` (chuỗi ngẫu nhiên tối thiểu 32 ký tự), SMTP và địa chỉ gửi
email. Không commit `.env` hoặc bí mật SMTP. Quy tắc đặt phòng trong mẫu môi
trường hiện là giá trị tạm theo SRS 1.9.

Migration `009_add_email_otp_auth.sql` chỉ chạy tự động khi tạo PostgreSQL
volume mới. Với volume đã tồn tại, hãy sao lưu dữ liệu rồi áp migration theo
hướng dẫn trong [README Database](../database/README.md) trước khi dùng OTP,
booking hoặc check-in.

## Build và chạy

Từ thư mục gốc:

```powershell
.\android\gradlew.bat testDebugUnitTest assembleDebug
```

Mặc định emulator gọi `http://10.0.2.2:8000/api/v1/`. Để gọi Backend từ thiết
bị thật hoặc địa chỉ khác, truyền URL API khi build:

```powershell
.\android\gradlew.bat assembleDebug "-PseatsenseApiBaseUrl=http://<DIA_CHI_MAY>:8000/api/v1/"
```

HTTP chỉ được cho phép trong bản debug. Bản phát hành cần HTTPS. Cần cài
Android SDK Platform 35 để Gradle biên dịch ứng dụng; chưa có APK/runtime
evidence cho đến khi build và kiểm thử trên emulator hoặc thiết bị thành công.
