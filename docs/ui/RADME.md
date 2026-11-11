# UTH-SeatSense – Tài liệu thiết kế giao diện UI/UX

## 1. Giới thiệu

Thư mục này lưu trữ các bản thiết kế giao diện người dùng (UI/UX) của dự án **UTH-SeatSense – Hệ thống đặt chỗ và theo dõi mật độ sử dụng phòng đọc**.

Các giao diện được thiết kế bằng Figma và Google Stitch, phục vụ quá trình xây dựng Frontend cho hai nền tảng Web và Mobile.

Hệ thống hỗ trợ hai nhóm người dùng chính:
- **Sinh viên:** Đăng ký, đăng nhập, xem tình trạng phòng, đặt phòng, check-in QR và quản lý hồ sơ cá nhân.
- **Thủ thư:** Theo dõi mật độ phòng, quản lý đặt phòng và xem thống kê, báo cáo.

## 2. Cấu trúc thư mục

```text
docs/
└── ui/
    ├── README.md
    └── wireframes/
        ├── Mobile/
        │   ├── 01-dang-ky-sv.png
        │   ├── 02-dang-nhap-sv.png
        │   ├── 03-tong-quan-cs1.png
        │   ├── 04-tong-quan-cs3.png
        │   ├── 05-dat-phong.png
        │   ├── 06-lich-dat-va-ma-qr.png
        │   ├── 07-ho-so-sv.png
        │   ├── LIB-01-dang-nhap-thu-thu.png
        │   ├── LIB-02-mat-do-cs1.png
        │   ├── LIB-03-mat-do-cs3.png
        │   ├── LIB-04-quan-ly-dat-phong.png
        │   ├── LIB-05-thong-ke-bao-cao-cs1.png
        │   └── LIB-06-thong-ke-bao-cao-cs3.png
        │
        └── Web/
            ├── 01-dang-ky-sv.png
            ├── 02-dang-nhap-sv.png
            ├── 03-tong-quan-cs1.png
            ├── 04-tong-quan-cs3.png
            ├── 05-dat-phong.png
            ├── 06-lich-dat-va-ma-qr.png
            ├── 07-ho-so-sv.png
            ├── LIB-01-dang-nhap-tt.png
            ├── LIB-02-mat-do-cs1.png
            ├── LIB-03-mat-do-cs3.png
            ├── LIB-04-quan-ly-dat-phong-web.png
            └── LIB-05-bao-cao-thong-ke.png
```

## 3. Danh sách giao diện

### 3.1. Giao diện sinh viên

| Mã | Tên giao diện | Mô tả |
|---|---|---|
| 01 | Đăng ký sinh viên | Cho phép sinh viên tạo tài khoản. |
| 02 | Đăng nhập sinh viên | Cho phép sinh viên đăng nhập hệ thống. |
| 03 | Tổng quan Cơ sở 1 | Hiển thị tình trạng sử dụng phòng tại Cơ sở 1. |
| 04 | Tổng quan Cơ sở 3 | Hiển thị tình trạng sử dụng phòng tại Cơ sở 3. |
| 05 | Đặt phòng | Xem phòng trống và thực hiện đặt phòng chuyên đề. |
| 06 | Lịch đặt và mã QR | Xem lịch đặt phòng và mã QR check-in. |
| 07 | Hồ sơ sinh viên | Xem thông tin cá nhân và lịch sử hoạt động. |

### 3.2. Giao diện thủ thư

| Mã | Tên giao diện | Mô tả |
|---|---|---|
| LIB-01 | Đăng nhập thủ thư | Giao diện đăng nhập dành cho thủ thư. |
| LIB-02 | Mật độ Cơ sở 1 | Theo dõi số lượng người và mật độ sử dụng tại Cơ sở 1. |
| LIB-03 | Mật độ Cơ sở 3 | Theo dõi số lượng người và mật độ sử dụng tại Cơ sở 3. |
| LIB-04 | Quản lý đặt phòng | Theo dõi và xử lý các yêu cầu đặt phòng chuyên đề. |
| LIB-05 | Thống kê, báo cáo Cơ sở 1 | Theo dõi các chỉ số sử dụng không gian tại Cơ sở 1. |
| LIB-06 (Mobile) / LIB-05 (Web) | Thống kê, báo cáo Cơ sở 3 | Theo dõi các chỉ số sử dụng không gian tại Cơ sở 3. |

## 4. Nguyên tắc thiết kế

- Giao diện đơn giản, trực quan và dễ sử dụng.
- Thống nhất màu sắc, font chữ, nút bấm, biểu tượng và thành phần giao diện.
- Thiết kế phù hợp với kích thước màn hình của Web và Mobile.
- Ưu tiên khả năng hiển thị thông tin số lượng người và tình trạng sử dụng phòng.
- Bố trí các thao tác đặt phòng, xem lịch đặt và check-in QR rõ ràng.
- Xây dựng các trạng thái giao diện phù hợp: Loading, Success, Empty, Error và Stale.

## 5. Quy ước đặt tên file

- Các giao diện được phân chia thành hai thư mục: `Mobile` và `Web`.
- Giao diện sinh viên sử dụng số thứ tự từ `01` đến `07`.
- Giao diện thủ thư sử dụng tiền tố `LIB-` để phân biệt.
- Tên file viết thường, không dấu và sử dụng dấu gạch ngang để phân tách từ.
- Định dạng hình ảnh: PNG.

## 6. Công cụ và công nghệ

| Công cụ / Công nghệ | Mục đích |
|---|---|
| Figma | Thiết kế giao diện và xây dựng prototype. |
| Google Stitch | Hỗ trợ tạo và phát triển giao diện bằng AI. |
| React + Vite | Công nghệ triển khai Frontend Web. |
| GitHub | Quản lý mã nguồn và lưu trữ tài liệu thiết kế. |

## 7. Ghi chú

- Hình ảnh trong thư mục `wireframes/` là tài liệu tham khảo cho quá trình triển khai Frontend.
- Dữ liệu trên giao diện có thể là dữ liệu minh họa, chưa phải dữ liệu thực tế từ Backend.
- Các API cần được đối chiếu với tài liệu Backend trước khi tích hợp.
- Các chức năng chưa được xác nhận về nghiệp vụ cần được nhóm dự án rà soát trước khi triển khai.

## 8. Liên kết thiết kế

**Figma:** https://www.figma.com/design/XAnsuHf2lZ3ftoSaxD2dWp/UTH-SeatSense?node-id=0-1&t=EujMb6BT6SjKAVhm-1

**Trạng thái:** Đang hoàn thiện và rà soát thiết kế giao diện.