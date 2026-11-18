# Quy ước làm việc nhóm

Áp dụng theo quy trình hiện hành của kho mã và mẫu yêu cầu gộp (PR). Nếu Jira,
GitHub hoặc nhóm thay đổi quy trình, cập nhật tài liệu này cùng thay đổi.

## Jira và phạm vi công việc

- Mỗi nhánh, lần ghi Git (commit) và PR gắn với một công việc Jira đã được giao.
- Tiêu chí hoàn thành phải kiểm thử được. Cập nhật trạng thái Jira khi có bằng
  chứng tương ứng; không suy ra trạng thái từ commit hoặc tài liệu.
- Mỗi PR chỉ giải quyết một công việc; không gộp các nhiệm vụ không liên quan.

## Nhánh và commit

- Tạo nhánh từ `dev`; không đẩy trực tiếp lên `dev` hoặc `main`.
- Dạng tên nhánh: `<loại>/SEAT-<số>-<mô-tả-ngắn>`. Các loại thường dùng là
  `feat`, `fix`, `docs`; phần mô tả viết thường, không dấu và nối bằng dấu gạch
  ngang.
- Ví dụ: `feat/SEAT-51-gui-su-kien-cv`,
  `docs/SEAT-30-tieu-chi-nghiem-thu-sprint-4`.
- Dạng commit: `SEAT-<số> <loại>: <nội dung ngắn>`, ví dụ
  `SEAT-51 feat: gui su kien CV den API` hoặc
  `SEAT-30 docs: bo sung tieu chi nghiem thu`.
- Các loại commit thường dùng: `feat`, `fix`, `docs`, `refactor`, `test`,
  `chore`.
- Mỗi commit nên thể hiện một thay đổi có ý nghĩa. Không dùng `#done` hoặc
  `#in-progress` trong nội dung commit.

## PR và kiểm thử

- Mở PR vào `dev` theo [mẫu PR](../.github/pull_request_template.md).
- Cần ít nhất một người khác đánh giá PR; tác giả không tự duyệt PR của mình.
- PR có thay đổi tài liệu cần Uyên đánh giá theo yêu cầu trong mẫu PR.
- Ghi đúng lệnh kiểm tra đã chạy và kết quả đạt/không đạt. Nếu chưa chạy, ghi rõ
  việc đó và lý do. Không tuyên bố kiểm tra đạt khi chưa có kết quả.
- Chỉ chuyển công việc Jira sang cột Done (Hoàn thành) sau khi PR được đánh
  giá, gộp vào nhánh đích, đáp ứng định nghĩa hoàn thành và đã cập nhật công
  việc Jira.

## Dữ liệu không được commit

- Không commit `.env`, mật khẩu, khóa API, mã truy cập hoặc thông tin đăng nhập.
  Khi thêm cấu hình, cập nhật `.env.example` bằng giá trị giả.
- Không commit ảnh/video có thể nhận diện người, dữ liệu thử nghiệm thật hoặc
  mô hình/tệp dữ liệu lớn. Lưu trữ theo kênh nội bộ được nhóm phê duyệt.
- Ảnh kiểm thử giao diện không được để lộ mã OTP, email thật, thông tin bí mật
  hoặc dữ liệu cá nhân.

## Ghi nhận kết quả và quyết định

- Báo cáo kiểm thử ghi ngày, commit, lệnh, kết quả và giới hạn. Tài liệu kế
  hoạch không thay thế bằng chứng đã chạy kiểm thử.
- Chỉ lập biên bản sau cuộc họp, dựa trên nội dung và người tham dự thực tế.
  Không tạo biên bản hồi cứu khi thiếu nguồn xác thực.
- Chỉ ghi nhận trạng thái Jira, nhãn, bình luận xác nhận của lập trình viên,
  phê duyệt của thư viện hoặc quyết định của trường khi có bằng chứng tương
  ứng.
