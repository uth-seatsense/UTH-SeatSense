# SEAT-52 — Đối chiếu đếm qua đường ảo

| Nguồn | IN tay | OUT tay | IN máy | OUT máy | Nhận xét |
|---|---:|---:|---:|---:|---|
| `sample` (annotated.mp4) | 0 | 0 | 0 | 1 | Số lượt vào khớp đếm tay. Máy đếm thừa 1 lượt ra. |

Dữ liệu test tạm thời, chưa test liên tục 10 phút.
Ngày 18/11/2026, lệnh `python -m app.counting --source sample` chạy trên host Windows với clip `outputs/c3056f66-938a-4ab9-abb3-3b7a0d12598d/annotated.mp4` và in ra `Total IN=0 OUT=1`. CV Testing Lab cũng ghi nhận 0 lượt vào và 1 lượt ra trên cùng clip.

Lần chạy bằng dòng lệnh dùng `config/line_config.example.yaml` với vạch dọc giữa khung hình, chiều IN từ phải sang trái, ảnh 416 px, ngưỡng tin cậy 0.32 và mục tiêu 5 FPS.


<!-- Chờ Khiêm chạy lại theo README và ghi nhận kết quả. -->
