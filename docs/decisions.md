# Architecture decisions

## Quyết định kỹ thuật của SEAT-31

Các ngày trong bảng là ngày cập nhật tài liệu nguồn hoặc ngày ghi nhận vào nhật ký. [Project Charter v1.2](project-charter.md) và [SEAT-31](https://nhauyen70205.atlassian.net/browse/SEAT-31) cung cấp căn cứ cho các quyết định bên dưới.

| Mã    | Ngày                       | Quyết định                                                                              | Lý do                                                                                                                      | Phương án đã loại                                      | Người quyết                                                           | Ảnh hưởng                                                                                  |
| ------ | --------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| DEC-01 | 28/10/2026                  | Dùng FastAPI cho backend.                                                                 | Cùng hệ sinh thái Python với CV, thuận tiện tích hợp và demo.                                                      | Charter chưa ghi phương án backend bị loại.            | Nhóm dự án theo Charter mục 17, chưa ghi tên người duyệt.       | Backend cung cấp API và xử lý nghiệp vụ đặt phòng, check-in và số liệu đếm.     |
| DEC-02 | 28/10/2026                  | Dùng PostgreSQL làm cơ sở dữ liệu chính.                                            | Lưu tập trung dữ liệu nghiệp vụ và số liệu đếm theo kiến trúc đã chọn.                                      | Charter chưa ghi hệ quản trị bị loại.                  | Nhóm dự án theo Charter mục 6 và 17, chưa ghi tên người duyệt. | Backend dùng PostgreSQL. Docker Compose lưu dữ liệu trên volume.                         |
| DEC-03 | 28/10/2026                  | Dùng camera, YOLOv8n và ByteTrack.                                                       | YOLOv8n phù hợp hướng giảm tải. ByteTrack theo dõi người qua các khung hình để xác định lượt vào và ra. | Phương án A dùng phần cứng và cảm biến.             | Nhóm dự án theo Charter mục 5 và 17, chưa ghi tên người duyệt. | Phạm vi CV tập trung vào camera và video, với cấu hình hiệu năng cần kiểm chứng.  |
| DEC-04 | 28/10/2026                  | Đếm lượt vào và ra khi người cắt đường ảo.                                    | Hướng cắt đường ảo tại lối ra vào cho biết chiều di chuyển.                                                    | Nhận diện khuôn mặt và danh tính nằm ngoài phạm vi. | Nhóm dự án theo Charter mục 5 và 6, chưa ghi tên người duyệt.  | CV cần cấu hình đường và hướng đếm. Backend nhận số liệu đếm.                 |
| DEC-05 | 06/11/2026, ngày ghi nhận | Chạy CV trên máy host khi lấy hình trực tiếp từ camera laptop hoặc camera ngoài. | Charter mục 6 ghi nhận hạn chế truy cập webcam từ container.                                                          | Đưa luồng lấy hình trực tiếp từ camera vào Docker.  | Quyết định được nêu trong SEAT-31, chưa ghi tên người duyệt. | Host truy cập camera. Các dịch vụ còn lại tiếp tục dùng Docker Compose theo Charter. |

### Chờ chốt

Hạn 09/11/2026 lấy từ trường Due date trên Jira. Mốc 10/11 là mốc xử lý phương án tạm trong mô tả SEAT-28 nếu chưa nhận được trả lời.

| Mã     | Nội dung cần chốt                                                                                                                    | Chủ sở hữu và bên xác nhận                                                                                                              | Hạn theo Jira                                                                                            |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| OPEN-01 | Chọn framework web và đánh giá lựa chọn native.                                                                                  | Uyên phụ trách [SEAT-48](https://nhauyen70205.atlassian.net/browse/SEAT-48) và duyệt đề xuất.                                           | 09/11/2026.                                                                                               |
| OPEN-02 | Xác nhận có đưa app native vào phạm vi và phiên bản iOS/Android tối thiểu nếu được duyệt. Jira gọi đây là câu 17. | Trâm phụ trách [SEAT-28](https://nhauyen70205.atlassian.net/browse/SEAT-28), lấy xác nhận từ nhà trường. Uyên duyệt cập nhật SRS. | 09/11/2026. Ghi phương án tạm và người chịu trách nhiệm nếu chưa có trả lời trước 10/11. |
| OPEN-03 | Xác nhận Portal/SSO và loại email dùng để đăng ký, xác minh tài khoản theo câu 1.                                         | Trâm phụ trách SEAT-28, lấy xác nhận từ nhà trường. Uyên duyệt cập nhật SRS.                                                     | 09/11/2026. Ghi phương án tạm và người chịu trách nhiệm nếu chưa có trả lời trước 10/11. |
| OPEN-04 | Chốt thời gian chờ check-in trước khi đánh dấu no-show theo câu 6. SRS đang đề xuất 10–15 phút.                          | Trâm phụ trách SEAT-28, lấy xác nhận qua email từ thư viện. Uyên duyệt cập nhật SRS.                                              | 09/11/2026. Ghi phương án tạm và người chịu trách nhiệm nếu chưa có trả lời trước 10/11. |

## Phân chia dịch vụ ban đầu

- **Trạng thái.** Đã chấp thuận cho bộ khung dự án.
- **Quyết định.** Tách giao diện web, API nghiệp vụ và phần xử lý CV thành
  các thư mục dịch vụ riêng. Dùng PostgreSQL làm lớp lưu trữ dữ liệu chung.
- **Lý do.** Mỗi thành phần có trách nhiệm và yêu cầu môi trường chạy riêng.
- **Việc tiếp theo.** Cùng nhóm xác nhận các yêu cầu về triển khai, xác thực
  và giao tiếp giữa các dịch vụ.

## Đầu ra CV và quy tắc đếm của SEAT-17

- **Trạng thái.** Đã triển khai trong CV, đang chờ nhóm rà soát.
- **Ngày ghi nhận.** 30/10/2026.
- **Quyết định.** Đặt phiên bản 1.0 cho định dạng đầu ra CV, độc lập với
  phương thức truyền dữ liệu. Tách bản ghi số đếm tổng hợp khỏi bản ghi
  khung bao (bbox) dùng để gỡ lỗi cục bộ. Định nghĩa đầu ra trước khi
  backend triển khai phần tiếp nhận dữ liệu. Endpoint HTTP sẽ được xác định sau.
- **Cách đếm.** Số người nhìn thấy trong khung hình độc lập với tổng số lượt
  vào và ra (IN/OUT) qua đường ảo. Chỉ ước tính số người trong phòng khi
  đã cấu hình rõ số người ban đầu. Nếu kết quả ước tính âm, đưa về 0 và
  bật cờ báo thiếu hụt (underflow).
- **Theo dõi.** Dùng điểm giữa cạnh dưới của khung bao để xác định lượt cắt
  qua đoạn thẳng hữu hạn trong hệ tọa độ chuẩn hóa. Áp dụng vùng đệm,
  thời gian chờ giữa hai lần đếm và loại trạng thái theo dõi đã hết hạn.
  Đặt lại các bộ đếm khi bắt đầu phiên mới.
- **Việc tiếp theo.** Backend tiếp nhận dữ liệu, lưu trữ và hiển thị trên
  giao diện là ba bước riêng.
