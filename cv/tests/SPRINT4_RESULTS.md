# SEAT-52 — Đối chiếu đếm qua đường ảo

| Nguồn | IN tay | OUT tay | IN máy | OUT máy | Nhận xét |
|---|---:|---:|---:|---:|---|
| `sample` (annotated.mp4) | 0 | 0 | 0 | 1 | Số lượt vào khớp đếm tay. Máy đếm thừa 1 lượt ra. |
| `test.mp4` (video test lặp liên tục đủ 10 phút) | 5 | 3 | 5 | 3 | Tổng từng chiều khớp ở lượt phát đầu, trước khi video lặp. |

## Clip mẫu ngày 18/11/2026

Ngày 18/11/2026, lệnh `python -m app.counting --source sample` chạy trên host Windows với clip `outputs/c3056f66-938a-4ab9-abb3-3b7a0d12598d/annotated.mp4` và in ra `Total IN=0 OUT=1`. CV Testing Lab cũng ghi nhận 0 lượt vào và 1 lượt ra trên cùng clip.

Lần chạy bằng dòng lệnh dùng `config/line_config.example.yaml` với vạch dọc giữa khung hình, chiều IN từ phải sang trái, ảnh 416 px, ngưỡng tin cậy 0.32 và mục tiêu 5 FPS.


## Phiên video 10 phút ngày 20/11/2026

Video `test.mp4` dài 110,899 giây. Vạch dọc đặt tại cửa góc dưới phải, từ `(0.84, 0.66)` đến `(0.84, 1.00)` theo tọa độ chuẩn hóa từ góc trên trái. Đi từ phải sang trái tính IN, chiều ngược lại tính OUT. Host Windows dùng CPU, ảnh 416 px, ngưỡng tin cậy 0,32 và mục tiêu 5 FPS. [Thư mục Drive dành cho video kiểm thử](https://drive.google.com/drive/u/1/folders/1q9-reDJxYw5hAdOfVUG4kNONaYuXL7j0)

Ngay trước lần phát lại đầu tiên, máy ghi **5 IN, 3 OUT**, khớp tổng đếm tay ở cả hai chiều. Host tiếp tục xử lý cùng video đến đủ 600 giây. Tổng cuối phiên là 31 IN, 17 OUT, trong đó 26 IN và 14 OUT phát sinh khi phát lại và được loại khỏi bảng đối chiếu.

| Phút | RAM tiến trình CV (MiB) | FPS xử lý trong phút |
|---:|---:|---:|
| 1 | 435,8 | 5,00 |
| 2 | 435,3 | 5,00 |
| 3 | 438,7 | 5,00 |
| 4 | 437,2 | 5,00 |
| 5 | 439,6 | 5,00 |
| 6 | 438,9 | 5,00 |
| 7 | 441,0 | 5,00 |
| 8 | 416,7 | 5,01 |
| 9 | 418,0 | 5,00 |
| 10 | 436,2 | 5,01 |

Host xử lý 3.000 khung hình trong 600 giây và kết thúc bình thường. FPS duy trì khoảng 5, RAM dao động từ 416,7 đến 441,0 MiB. Phiên webcam 10 phút theo Jira vẫn chờ kiểm thử.

<!-- Chờ Khiêm chạy lại theo README và ghi nhận kết quả. -->
