# UI Guideline — UTH-SeatSense 

Quy chuẩn gọn dùng chung cho web responsive và Android native. Dùng token theo tên ngữ nghĩa; không tự chọn màu theo từng màn. Chuẩn áp dụng: **WCAG AA** (chữ thường ≥4.5:1, chữ lớn ≥3:1, điều khiển ≥3:1).

## 1. Bảng màu chuẩn hóa

### 1.1 Bảng màu chính

| Vai trò | Màu hex | Chữ/Icon | Nền | Tương phản | Dùng cho |
|---|---|---|---|---|---|
| **Chính** | #006B5D | #FFFFFF | #006B5D | 6.44:1 | Nút hành động, nhận diện |
| **Nền trang** | #F5FBF8 | — | #F5FBF8 | — | Nền chính |
| **Bề mặt** | #FFFFFF | — | #FFFFFF | — | Thẻ, hộp thoại |
| **Chữ chính** | #171D1B | #171D1B | #F5FBF8 | 16.32:1 | Nội dung chính |
| **Chữ phụ** | #3D4946 | #3D4946 | #F5FBF8 | 8.95:1 | Mô tả, label |
| **Vắng** | #047857 | #FFFFFF | #047857 | 5.21:1 | Badge ≤50% |
| **Vừa** | #92400E | #FFFFFF | #92400E | 6.84:1 | Badge 50–85% |
| **Đông** | #9F1239 | #FFFFFF | #9F1239 | 7.30:1 | Badge ≥85% |
| **Lỗi** | #BA1A1A | #FFFFFF | #BA1A1A | 5.00:1 | Lỗi, nguy hiểm |
| **Cảnh báo** | #92400E | #92400E | #FFFBEB | 6.84:1 | Dữ liệu cũ |
| **Viền** | #B8D9D3 | — | — | — | Điều khiển |

### 1.2 Nền bổ sung
- Badge Vắng: #ECFDF5
- Badge Vừa: #FFFBEB
- Badge Đông: #FFF1F2
- Nền lỗi: #FFDAD6
- Viền nhạt: #E8F1EE

### 1.3 Quy tắc mật độ — luôn có chữ + số

| Mức | Ngưỡng | Hiển thị | Badge |
|---|---|---|---|
| **Vắng** | <50% | "Vắng · 40%" | Nền #ECFDF5, chữ #047857 |
| **Vừa** | 50–85% | "Vừa · 73%" | Nền #FFFBEB, chữ #92400E |
| **Đông** | ≥85% | "Đông · 92%" | Nền #FFF1F2, chữ #9F1239 |

**Bắt buộc:** Luôn có nhãn chữ + số lượng/phần trăm; không chỉ màu. Khi dữ liệu thiếu hoặc cũ, hiển thị "Chưa có dữ liệu mới" chứ không suy diễn trạng thái.

---

## 2. Chữ và khoảng cách

### 2.1 Font
- **Font chính:** Inter (đã dùng phần lớn)
- **Dự phòng:** -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
- **Android:** sans-serif hệ thống tương ứng
- Không nhúng font; giữ cùng trọng lượng và phân cấp

### 2.2 Thang cỡ chữ

| Vai trò | Cỡ chữ | Chiều cao dòng | Độ đậm | Ví dụ |
|---|---|---|---|---|
| Tiêu đề trang desktop | 32 px | 40 px | 700 | "Tổng quan Thư viện UTH" |
| Tiêu đề tpage mobile | 24 px | 32 px | 700 | "Tổng quan Thư viện" |
| Tiêu đề khu vực | 20 px | 28 px | 600 | "Mật độ các khu vực" |
| Tiêu đề thẻ | 16 px | 24 px | 600 | Tên phòng |
| Nội dung chính | 16 px | 24 px | 400–500 | Chữ ô nhập, mô tả |
| Nhãn, nút, bảng | 14 px | 20 px | 500–600 | Button, label, cell |
| Chú thích, thời gian | 12 px | 16 px | 400–500 | "Cập nhật 10:40" |
| Số liệu nổi bật | 32 px | 40 px | 700 | "254 người" |

**Quy tắc:** Không dùng 10–11 px; luôn ≥12 px. Không ép line-height; cho native phóng to chữ.

### 2.3 Thang khoảng cách (bội số 4 hoặc 8)

Chuỗi: **4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 · 64 px**

- **8 px:** Biểu tượng ↔ nhãn
- **16 px:** Label ↔ ô nhập; giữa trường; padding thẻ mobile
- **24 px:** Giữa thẻ/section; padding thẻ desktop
- **32 px:** Giữa khu vực lớn; lề trang desktop

### 2.4 Bo góc (border-radius)
- Nút, ô nhập: **8 px**
- Thẻ, bảng: **12 px**
- Viên thuốc (badge): **999 px**

## 3. Thành phần dùng chung

### 3.1 Nút (Button)

| Kiểu | Bối cảnh | Nền | Chữ | Viền |
|---|---|---|---|---|
| **Primary** | Hành động chính | #006B5D | #FFFFFF | — |
| **Secondary** | Phụ / Quay lại | #FFFFFF | #006B5D | #B8D9D3 |
| **Text** | Liên kết | #FFFFFF | #006B5D | — |
| **Danger** | Xóa / Hủy quan trọng | #BA1A1A | #FFFFFF | — |

**Trạng thái:** Default → Hover (tối 10%) → Active (tối 20%) → Focus (ring 2px) → Loading ("Đang...") → Disabled (mờ 50%)

**Yêu cầu:**
- Web: 40 px cao, vùng chạm ≥44×44 px
- Android: 48 dp cao, ≥48×48 dp
- Padding ngang: 16 px desktop, 12 px mobile
- Nhãn: Động từ + danh từ ("Gửi mã", "Xác nhận", "Đặt phòng")
- Tải: Giữ chiều rộng, đổi nhãn thành "Đang [hành động]…"

### 3.2 Ô nhập (Input)

**Cấu trúc:**
1. Label (14 px, 500 đậm) — luôn hiện
2. Trường (16 px, 48 px cao)
3. Hỗ trợ/Lỗi (12 px, 400 đậm, cách 8 px dưới)

**Trạng thái:**
- Default: Viền #B8D9D3, nền #FFFFFF
- Focus: Viền #006B5D (2 px), shadow nhẹ
- Lỗi: Viền #BA1A1A, nền #FFDAD6
- Disabled: Nền #F5FBF8, chữ mờ

**Yêu cầu:** Placeholder là gợi ý, không thay thế label. Lỗi nằm sát dưới, giữ dữ liệu đã nhập.

### 3.3 Thẻ phòng (Room Card)

**Thứ tự thông tin (từ trên xuống):**
1. Tên phòng (16 px, 600 đậm)
2. Cơ sở/Tầng (12 px, secondary, "B.301A · Lầu 1")
3. Badge trạng thái (Vắng/Vừa/Đông hoặc "Hết chỗ")
4. Sức chứa & chỗ trống ("100 chỗ · Còn 27")
5. Tiện ích (icon + nhãn nếu có)
6. Thời gian cập nhật (12 px, muted, "Cập nhật 10:40")
7. Nút hành động (Primary)

**Quy tắc:** Padding 16px mobile / 24px desktop. **Không hiện nút đặt cho khu tự học tự do.**

### 3.4 Huy hiệu trạng thái (Badge)

**Ba nhóm:**
- **Mật độ:** Vắng (xanh) / Vừa (cam) / Đông (đỏ)
- **Đặt phòng:** Đã đặt / Check-in / Hủy
- **Kết nối:** Đang tải / Lỗi / Cập nhật

**Cấu trúc:** Nền nhạt + chữ token, 12–14 px, 600 đậm, padding 4×8 px, 16 px bo góc.

**Bắt buộc:** Luôn có nhãn chữ, không chỉ biểu tượng. Mỗi nhóm dùng nhãn riêng rõ ràng.

### 3.5 Thanh dữ liệu cũ (Stale Data Bar)

```
⚠️ Dữ liệu chưa được cập nhật
Cập nhật lần cuối lúc 10:40. Số chỗ trống có thể đã thay đổi.
[ Thử cập nhật ]
```

**Yêu cầu:**
- Nền #FFFBEB, chữ #92400E, padding 16 px, bo góc 8 px
- Vị trí: Ngay trên số liệu, không tự biến mất
- Icon warning + thời điểm cập nhật + nút "Thử lại"
- Ngưỡng cũ: Cấu hình theo chu kỳ thực tế

### 3.6 Bảng (Table)

**Yêu cầu:**
- Cao hàng ≥48 px web, 56 dp Android
- Tiêu đề: Rõ ràng, căn trái (chữ) / căn phải (số)
- Padding: 12 px ô, 16 px giữa cột
- Responsive: Mobile → thẻ; tablet+ → bảng; nếu cuộn ngang, chỉ trong bảng

**Trạng thái:** Loading (skeleton) / Rỗng (icon + chữ) / Lỗi (thông báo + "Thử lại") / Sắp xếp / Phân trang

### 3.7 Biểu đồ (Chart)

**Bắt buộc:**
- Tiêu đề + đơn vị + khoảng thời gian
- Chú giải (legend): Màu + ký hiệu + nhãn
- Giá trị tooltip khi hover
- **Cũng cung cấp bảng dữ liệu**
- Phân biệt chuỗi: Màu + ký hiệu + nhãn, không chỉ màu

---

## 4. Responsive & Native

### 4.1 Breakpoint & bố trí

| Chiều rộng | Bố trí |
|---|---|
| **<600 px** | Một cột; nav đáy; bộ lọc trượt từ đáy; nút xác nhận cố định dưới |
| **600–1023 px** | Hai cột khi thẻ đủ rộng; nav thu gọn; form giữ thứ tự đọc |
| **≥1024 px** | Sidebar; lưới 12 cột; danh sách + chi tiết cạnh nhau |

### 4.2 Kiểm tra responsive

Kiểm tra tại: **320, 390, 600, 768, 1024, 1280 px** + **chữ phóng to +200%**

### 4.3 Quy tắc mobile

- Ưu tiên: cơ sở → dữ liệu mới → chỗ trống → phòng → hành động
- Không thu nhỏ desktop vào mobile
- Bảng → thẻ; cuộn ngang chỉ trong bảng, không toàn trang
- Biểu đồ: Giảm mật độ nhãn, không dùng chữ <12 px
- Nút đáy: Chừa vùng an toàn (notch, home bar)

### 4.4 Native Android

- **Vùng chạm:** ≥48 × 48 dp
- **Phóng to chữ:** Hỗ trợ system font scaling; không khóa line-height
- **Làm mới:** Kéo xuống bổ sung; vẫn có nút cập nhật
- **Back:** Tôn trọng điều hướng hệ điều hành; giữ bộ lọc/cuộn
- **Vuốt:** Vuốt đóng bảng trượt được phép nếu không mất dữ liệu
- **Focus:** Không tự chuyển focus khi dữ liệu cập nhật

---

## 5. Giọng điệu thông báo

Ngắn, bình tĩnh, cụ thể. Nêu trạng thái và bước tiếp theo. Không đổ lỗi.

### 5.1 Mẫu thông báo

| Tình huống | Nội dung | Hành động |
|---|---|---|
| **Đặt thành công** | “Đã đặt Phòng Chuyên đề 1, 13:30–15:30 hôm nay.” | Xem mã QR |
| **Khung giờ hết** | “Khung giờ này vừa được đặt. Vui lòng chọn giờ khác.” | Chọn giờ khác |
| **Lỗi kết nối** | “Chưa thể cập nhật số chỗ trống. Dữ liệu gần nhất lúc 10:40.” | Thử lại |
| **OTP sai** | “Mã xác thực chưa đúng. Vui lòng kiểm tra và nhập lại.” | — |
| **OTP hết hạn** | “Mã đã hết hạn (5 phút). Vui lòng xin mã mới.” | Gửi lại |
| **Vượt 5 lần sai** | “Bạn đã nhập sai quá nhiều lần. Vui lòng xin mã mới.” | Gửi lại |
| **Chờ gửi lại** | “Vui lòng chờ 60 giây trước khi gửi lại mã.” | [Bộ đếm] |
| **Xác nhận hủy** | “Hủy lịch Phòng Chuyên đề 1, 13:30–15:30?” | Giữ lịch / Hủy |
| **Chưa có lịch** | “Bạn chưa có lịch đặt phòng.” | Tìm phòng |
| **Dữ liệu cũ** | “Dữ liệu đã cũ — thử cập nhật lại.” | Thử lại |
| **Không quyền** | “Bạn không có quyền truy cập trang này.” | Quay lại |
| **Chưa đủ dữ liệu** | “Chưa có dữ liệu mật độ. Vui lòng kiểm tra lại sau.” | — |
| **Email không hợp lệ** | “Email không được hỗ trợ. Vui lòng kiểm tra lại.” | — |
| **Email cần đợi 60s** | “Vui lòng chờ 60 giây trước khi gửi email mới.” | [Bộ đếm] |

### 5.2 Quy tắc viết

1. **Chủ động, không đổ lỗi:** ✅ “Chưa thể cập nhật” vs ❌ “Cập nhật thất bại”
2. **Nêu rõ bước tiếp theo:** ✅ “Vui lòng chọn giờ khác” vs ❌ “Không được”
3. **Cụ thể, không chung chung:** ✅ “Khung giờ này đã được đặt” vs ❌ “Lỗi”
4. **Không tiết lộ kỹ thuật:** Không stack trace, mã lỗi, hay thông tin cá nhân
5. **Giữ dữ liệu:** Không xóa gì khi thông báo lỗi

---

## Dùng chung trên nền tảng

Token names và màu hex ở trên là nguồn chuẩn cho CSS variables (web) và `colors.xml`/Compose theme (Android). Kiểm tra tương phản trên mọi cặp chữ/nền thực tế và ở trạng thái disabled/focus trước khi phát hành.