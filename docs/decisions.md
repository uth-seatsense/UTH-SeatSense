# Architecture decisions

## Initial service boundaries

- **Status:** Accepted for the project scaffold
- **Decision:** Keep the web UI, business API, and CV processing in separate
  service directories, with PostgreSQL as the shared persistence layer.
- **Reason:** The components have distinct responsibilities and runtime needs.
- **Follow-up:** Validate deployment, authentication, and inter-service
  communication requirements with the team.

## SEAT-17 CV output and counting semantics

- **Status:** Implemented in CV, pending team review.
- **Date:** 2026-10-30.
- **Decision:** Version the transport-neutral CV output as 1.0. Keep aggregate
  count records separate from local bbox debug records. Define the output
  before Backend implements ingestion; no HTTP endpoint is assumed yet.
- **Counting:** Visible person count is independent of cumulative line IN/OUT.
  Only estimate room occupancy when an initial value is explicitly configured.
  Clamp negative estimates to zero while flagging underflow.
- **Tracking:** Bottom-center anchors cross a finite normalized segment, with
  deadband, cooldown and stale-state expiry. Counters reset for each session.
- **Follow-up:** Backend ingestion, storage and UI are separate stages.

## SEAT-33 thuat toan dem nguoi qua duong ao

- **Trạng thái:** Tài liệu hóa thuật toán đã có trong CV; chưa thay cho xác
  nhận bàn giao của Thắng và Khiêm.
- **Ngày rà soát:** 09/11/2026.
- **Nguồn:** [SEAT-33](https://nhauyen70205.atlassian.net/browse/SEAT-33),
  `cv/app/counting/line_counter.py` và `cv/app/schemas/count_result.py`.
- **Quyết định:** Dùng YOLOv8n và ByteTrack, lấy tâm cạnh dưới bbox của cùng
  track để xác định hướng khi cắt đoạn đường ảo hữu hạn. Dùng deadband,
  cooldown và hết hạn trạng thái mất dấu để giảm đếm lặp. Mỗi lần cắt hợp lệ
  sinh một sự kiện; track có thể quay lại sau cooldown.
- **Lý do:** Cần đếm lượt qua cửa theo hướng IN/OUT, tách số người đang thấy
  trong khung hình khỏi ước tính số người trong phòng. Track ID chỉ là ID
  tạm trong phiên, không dùng để nhận diện danh tính.
- **Phương án không dùng:** Không lấy `people_count` làm số người toàn phòng,
  không cộng counters tích lũy qua các frame, không giới hạn một ID chỉ được
  đếm một lần trong toàn phiên.
- **Công thức:** Khi biết số đầu phiên, hiện diện bằng
  `max(0, initial_occupancy + IN - OUT)`; số âm bật `occupancy_underflow`.
  Chỉ dùng IN trừ OUT khi đã xác nhận số đầu phiên bằng 0; chưa biết số đầu
  phiên thì hiện diện là `null`.
- **Ảnh hưởng:** Theo BR-02, số chỗ trống cần kẹp về 0 và đánh dấu khi vượt
  sức chứa; không kẹp số người xuống sức chứa. Kết hợp sức chứa và cảnh báo
  thuộc Backend/Frontend; `CountResult` hiện chưa có các trường này.
- **Giới hạn triển khai:** 416 px và 3–5 FPS là cấu hình mục tiêu, không phải
  hiệu năng đã đo. CLI mặc định 640, chưa lấy mẫu 3–5 FPS; CV xuất dữ liệu
  cục bộ, chưa có bộ gửi HTTP/retry đến Backend.
- **Bàn giao:** Chi tiết pipeline, tham số và giới hạn ở
  [Thuật toán đếm người](../cv/README.md#thuật-toán-đếm-người--seat-33).
  Thắng và Khiêm cần xác nhận giải thích đúng công thức và cách xử lý số âm
  theo tiêu chí SEAT-33; chưa ghi nhận xác nhận này khi rà soát.
