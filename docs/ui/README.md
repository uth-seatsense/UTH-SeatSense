# UTH-SeatSense — Wireframes giao diện

Thư mục này lưu wireframe hiện có cho web và mobile. Đây là tài liệu thiết
kế, không phải bằng chứng giao diện đã được triển khai hoặc kiểm thử.

Nguồn yêu cầu giao diện là [SRS 1.9](../requirements/srs.md), còn mã UI-01–UI-08
được ánh xạ trong [test-plan.md](../test-plan.md) và
[screen-flow.md](screen-flow.md).

## Wireframes hiện có

| Tệp | Nội dung |
|---|---|
| `wireframes/Mobile/01-dang-nhap-sv.png` | Đăng nhập sinh viên |
| `wireframes/Mobile/02-tong-quan-cs1.png`, `03-tong-quan-cs3.png` | Tổng quan CS1 và CS3 |
| `wireframes/Mobile/04-dat-phong.png` | Đặt phòng chuyên đề |
| `wireframes/Mobile/05-lich-dat-và-ma-qr.png` | Lịch đặt và mã QR |
| `wireframes/Mobile/06-ho-so-sv.png` | Hồ sơ sinh viên |
| `wireframes/Mobile/LIB-01-dang-nhap-thu-thu.png` | Đăng nhập thủ thư |
| `wireframes/Mobile/LIB-02-mat-do-cs1.png`, `LIB-03-mat-do-cs3.png` | Mật độ CS1 và CS3 |
| `wireframes/Mobile/LIB-04-quan-ly-dat-phong.png` | Quản lý đặt phòng |
| `wireframes/Mobile/LIB-05-thong-ke-bao-cao-cs1.png`, `LIB-06-thong-ke-bao-cao-cs3.png` | Báo cáo CS1 và CS3 |
| `wireframes/Web/01-dang-nhap-sv.png` | Đăng nhập sinh viên |
| `wireframes/Web/02-tong-quan-cs1.png`, `03-tong-quan-cs3.png` | Tổng quan CS1 và CS3 |
| `wireframes/Web/04-dat-phong.png` | Đặt phòng chuyên đề |
| `wireframes/Web/05-lich-dat-va-ma-qr.png` | Lịch đặt và mã QR |
| `wireframes/Web/06-ho-so-sv.png` | Hồ sơ sinh viên |
| `wireframes/Web/LIB-01-dang-nhap-tt.png` | Đăng nhập thủ thư |
| `wireframes/Web/LIB-02-mat-do-cs1.png`, `LIB-03-mat-do-cs3.png` | Mật độ CS1 và CS3 |
| `wireframes/Web/LIB-04-quan-li-dat-phong-web.png` | Quản lý đặt phòng |
| `wireframes/Web/LIB-05-bao-cao-thong-ke.png` | Báo cáo; chưa có wireframe web riêng theo cơ sở |

## Nguyên tắc và trạng thái

- Dùng token và yêu cầu tương phản trong [ui-guideline.md](ui-guideline.md).
- Mỗi luồng phải xét loading, success, empty, error, stale và insufficient-data
  theo [screen-flow.md](screen-flow.md).
- Wireframe không thay thế tiêu chí responsive hoặc test; dùng
  [ui-test-plan.md](../ui-test-plan.md) cho các test case.
- Dữ liệu minh họa không được hiểu là dữ liệu thật từ Backend. Các API cần
  đối chiếu với [API contract](../architecture/api-contracts.md) trước tích hợp.
