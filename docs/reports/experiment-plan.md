# Kế hoạch thực nghiệm đối chiếu đếm tay

**SEAT-35 · Lê Văn Trí · 02/11/2026** 

Kế hoạch xác định cách đo sai số đếm, độ trễ hiển thị và tốc độ xử lý của
UTH-SeatSense, cùng [mẫu bảng ghi](experiment-record-template.md). Chưa có
số liệu thực nghiệm trong tài liệu này; các ngưỡng là mục tiêu, không phải
kết quả đã đạt. Công thức và quy trình hiệu chỉnh phải được xác nhận theo
câu 14–15 của SRS trước đợt đo chính thức

## 1. Căn cứ và phụ thuộc

| Nguồn                                                                                                                                | Nội dung áp dụng                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [SEAT-35](https://nhauyen70205.atlassian.net/browse/SEAT-35)                                                                           | 5–10 phiên × 30–60 phút, hai người đếm độc lập, mốc 5 phút, mẫu số 0, thống kê và phân tích lỗi.                          |
| [SRS 1.3](../requirements/UTH-SeatSense_SRS_v1.3.docx), mục 8.1                                                                       | AT-01: sai số ≤ 10%; AT-02: độ trễ ≤ 5 giây; AT-03: ≥ 5 FPS ở khoảng 416 px.                                                          |
| [Charter 1.2](../project-charter.md), mục 7, 15                                                                                       | Đối chiếu đếm tay, đo trên máy thực, xử lý hình tại chỗ và chỉ dùng video khi được phép.                                   |
| [SEAT-33](https://nhauyen70205.atlassian.net/browse/SEAT-33), [thuật toán CV](../../cv/README.md#thuật-toán-đếm-người--seat-33) | Đã merge qua PR #28; phân biệt số người nhìn thấy, IN/OUT tích lũy và hiện diện từ số đầu phiên.                             |
| [API contract](../architecture/api-contracts.md)                                                                                       | CountResult khác CrossingEvent; recorded_at là giờ xử lý, không phải giờ người qua cửa. Bộ gửi CV → Backend còn chờ tích hợp. |
| [SEAT-28](https://nhauyen70205.atlassian.net/browse/SEAT-28)                                                                           | Thu thập quyết định cho SRS câu 14 (môi trường, tải, công thức KPI) và 15 (hiệu chỉnh lệch đếm).                               |

## 2. Thiết kế phiên và phân công

Đề xuất bắt đầu với **5 phiên, mỗi phiên 30 phút**, mở rộng đến 10 phiên hoặc
60 phút/phiên để bổ sung điều kiện chưa đủ đại diện. Đây là lịch thiết kế,
chưa phải lịch được thư viện cho phép. Điền ngày, phòng và nhân sự vào mẫu
trước khi thực hiện; không suy diễn mức đông chỉ từ tên khung giờ.

| Phiên dự kiến | Thời lượng       | Điều kiện cần bao phủ                                | Khung giờ cần xác nhận                      |
| ---------------- | ------------------- | --------------------------------------------------------- | ----------------------------------------------- |
| P01              | 30 phút            | Ít người, vào/ra đơn lẻ, xác nhận hướng line   | Giờ vắng tại khu vực được phép          |
| P02              | 30 phút            | Mức sử dụng trung bình, hai chiều qua cửa           | Khung giờ thông thường                      |
| P03              | 30 phút            | Đông hơn, người đi gần nhau, che khuất tự nhiên | Giờ cao điểm được thư viện xác nhận   |
| P04              | 30 phút            | Điều kiện ánh sáng khác P01–P03                    | Buổi/điều kiện khác được phép          |
| P05              | 30 phút            | Lặp lại điều kiện để kiểm tra tính nhất quán   | Khung giờ tương đương một phiên trước |
| P06–P10         | 30–60 phút/phiên | Bổ sung mức đông, lặp lại hoặc điều kiện thiếu | Chỉ lên lịch sau rà soát 5 phiên đầu    |

Ghi mức đông thực tế bằng số tham chiếu và sức chứa nếu đã được xác nhận;
nhãn ít/trung bình/đông chỉ mô tả, chưa thay ngưỡng chính thức SRS câu 12.
Không cố gây tắc cửa hoặc vượt sức chứa để tạo tình huống thử nghiệm.

- **Người vận hành:** khóa cấu hình, chạy CV, đối chiếu log và
  tổng hợp; không thay hai người đếm tay bằng số CV.
- **Hai người đếm A/B:** điền tên khi được nhóm phân công, đếm độc lập,
  không xem kết quả CV và không trao đổi số trước khi nộp bảng gốc.
- **Uyên:** điều phối chấp thuận địa điểm/dữ liệu và duyệt kế hoạch. Các
  phương pháp KPI cần giảng viên xác nhận qua luồng SEAT-28.

## 3. Chuẩn bị và quy trình đếm tham chiếu

1. Có chấp thuận cho địa điểm, camera và video nếu cần; đặt biển thông báo.
   Ghi mã bằng chứng cho phép, người quản lý dữ liệu và hạn xóa cụ thể.
2. Ghi Git SHA, model/hash, Python/Ultralytics/Torch, CPU/GPU/RAM/OS, nguồn
   hình, vị trí/góc camera, độ phân giải/FPS nguồn, ảnh YOLO, confidence,
   line/hướng, deadband/cooldown/max-gap. Khóa cấu hình trong một phiên.
3. Chạy thử một lượt vào/ra đã biết để kiểm tra hướng, rồi bắt đầu phiên mới.
   Khởi động model và làm nóng khoảng 60 giây; ghi riêng, không đưa vào cửa
   sổ FPS chính thức. Cấu hình ảnh mục tiêu 416 chỉ được ghi khi thực sự dùng.
4. Hai người xác nhận số đầu phiên `N0` độc lập và thống nhất trước khi bắt
   đầu. Nếu không thể xác định, ghi chưa biết; không tự đặt 0. Chỉ đánh giá
   IN/OUT, chưa đánh giá hiện diện khi `N0` chưa biết.
5. Dùng cùng mốc bắt đầu `t0`, đồng bộ đồng hồ. A/B đếm IN/OUT tích lũy riêng
   theo người thực qua đường đã quy định; đi đến rồi quay lại cùng phía
   chưa qua line không phải một lượt. Không đếm ID tracker làm tham chiếu.
6. Tại t=0 và mỗi 5 phút, ghi số người hiện diện tham chiếu độc lập nếu quan
   sát toàn phòng được; nếu không, suy từ `N0 + IN_tay - OUT_tay` và đánh dấu
   là tham chiếu suy diễn. Không dùng people_count thay hiện diện toàn phòng.
7. Tại t=5,10,…,T phút, chốt counters cho khoảng `(mốc trước, mốc hiện tại]`.
   Giữ nhất quán quy tắc sự kiện đúng ranh giới. Lấy bản ghi CV cuối cùng
   không muộn hơn mốc, ghi frame_index/timestamp_ms và tuổi bản ghi. Đề xuất
   tuổi tối đa 1 giây, cần duyệt; vượt ngưỡng ghi thiếu mẫu thay vì điền 0.
8. Video offline dùng timeline video để căn mốc; webcam dùng thời gian từ
   đầu phiên. Không so UTC recorded_at của lúc xử lý offline với giờ quay.
9. Sau khi nộp bảng gốc, A/B đối soát mọi chênh lệch, ghi số đồng thuận, lý
   do và mã bằng chứng. Nếu chưa thống nhất thì giữ trạng thái unresolved,
   không lấy trung bình, không chọn số gần CV hơn. Không ghi đè bảng gốc.
10. Kết thúc, xuất dữ liệu và kiểm tra status completed/cancelled/failed.
    Dừng sớm, mất camera, restart hoặc đổi cấu hình phải ghi rõ; không trình
    bày phiên thiếu thời lượng như phiên chuẩn đủ 30–60 phút.

Nếu cần hiệu chỉnh trong khi chạy, giữ dữ liệu trước hiệu chỉnh, ghi thời
điểm/lý do/người thực hiện và bắt đầu đoạn hoặc phiên có baseline mới. Phân
tích riêng các đoạn; không xóa lỗi hoặc cộng counters tích lũy qua restart.
Quy trình hiệu chỉnh cuối cùng vẫn chờ câu 15 SRS được chốt.

## 4. AT-01 Sai số đếm

Tính riêng ba nhóm: **tổng IN mỗi phiên**, **tổng OUT mỗi phiên**, và **hiện
diện tại các mốc 5 phút**. T=0 dùng kiểm tra baseline, không đưa vào thống kê
hiện diện để tránh làm đẹp kết quả bằng số khởi tạo giống nhau.

```text
AE = abs(system - reference)                 # đơn vị: người hoặc lượt
RE_percent = 100 * AE / reference            # chỉ khi reference > 0
```

Với reference=0, RE là **N/A**, luôn báo AE: hệ thống 0 thì AE=0, hệ thống
2 thì AE=2. Không gán 0% hoặc 100%, không thay mẫu số bằng 1. Mẫu thiếu,
underflow, số đầu phiên chưa biết và tham chiếu unresolved có trạng thái
riêng; ô trống không có nghĩa là 0. Giữ và báo cờ underflow khi so ước tính
đã kẹp 0 để không che mất lỗi công thức/sự kiện.

Cho từng nhóm, báo **số mẫu tổng, hợp lệ, mẫu reference=0, thiếu/unresolved**;
trung bình, trung vị, lớn nhất của RE trên mẫu có reference>0; đồng thời báo
trung bình/trung vị/lớn nhất AE trên các cặp có tham chiếu hợp lệ, kể cả 0.
Tách kết quả theo phiên/điều kiện, chỉ tổng hợp cả đợt khi cùng định nghĩa.
Không gộp IN/OUT để lỗi hai chiều triệt tiêu; không cộng counters của từng
frame hoặc trung bình tỷ lệ với N/A được thay bằng 0.

Ví dụ kiểm tra công thức, **không phải kết quả đo**: tham chiếu 10, hệ thống
9 → AE=1, RE=10%; tham chiếu 0, hệ thống 2 → AE=2, RE=N/A.
Với RE=[10%,20%], trung bình/trung vị là 15%, xấu nhất 20%.

Ngưỡng SRS là ≤10%; **cần chốt dùng trung bình, trường hợp xấu nhất hay tiêu
chí khác, cho từng nhóm**, trước khi kết luận đạt/không đạt. Không chỉ chọn
chỉ số thuận lợi sau khi có kết quả.

## 5. AT-03 Tốc độ xử lý tại khoảng 416 px

Đo trên máy thực, ghi chế độ offline/live và cấu hình thực dùng. CLI hỗ trợ
`--image-size 416`; API/UI hiện mặc định 640, không tự coi là thử ở 416.
`--fallback-fps` là metadata nguồn, không phải tốc độ inference/lấy mẫu.

| Phép đo             | Cách đo và phạm vi                                                                                                                                                                                                                                                 |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FPS pipeline offline  | `N / T_wall`, N là frame hoàn tất; T_wall tính từ trước lần đọc frame đầu đến khi kết thúc đọc/xử lý/xuất và đóng file. Không gồm nạp model/làm nóng; báo riêng thời gian này. Dùng đồng hồ monotonic trên cùng tiến trình. |
| FPS pipeline live     | Trong cửa sổ 5 phút sau làm nóng, số frame hoàn tất chia thời gian monotonic thực; bao gồm chờ nguồn, giao tiếp trình duyệt/local CV và xử lý. Ghi số frame nguồn/bỏ qua nếu đo được; không tự suy số bỏ qua.                           |
| FPS từ processing_ms | `1000 * N / sum(processing_ms)`, chỉ trên các frame có giá trị hợp lệ. Đây là tốc độ của phạm vi được mã đo trong frame, không gồm toàn bộ pipeline; không lấy trung bình các `1000/processing_ms`.                                   |

Chia phiên thành cửa sổ 5 phút, báo N, thời lượng và FPS từng cửa sổ, giá trị
toàn phiên, trung vị và thấp nhất giữa cửa sổ. Nếu không đo được phạm vi
thời gian hoặc file hỏng, ghi không đo được, không gán FPS=0. Mục tiêu SRS
≥5 FPS ở khoảng 416 px; đề xuất lấy FPS toàn pipeline làm chỉ số chính,
cần xác nhận câu 14. Nếu live không đạt thì đánh giá offline và báo rõ,
không dùng kết quả offline để tuyên bố live đạt.

## 6. AT-02 Độ trễ từ sự kiện tới web hiển thị

Chỉ đo toàn luồng khi nguồn camera, CV sender, Backend/DB và Frontend đã
tích hợp; bản hiện tại chưa đủ để chứng minh AT-02. Có thể thử offline
AT-01/03 trước và ghi AT-02 **chưa đo được do thiếu tích hợp**, không thay
bằng thời gian inference hoặc thời gian POST.

- Đề xuất ít nhất 10 sự kiện/cập nhật đối chiếu được mỗi phiên live, có IN
  và OUT nếu thực tế xuất hiện; báo số thật, không tạo thêm số đo giả.
- Ghi `t_cross` là lúc người thực qua line, `t_cv` là lúc CV xác nhận sự
  kiện, `t_backend` là lúc lưu thành công và `t_render` là lúc web thật sự
  hiển thị bản ghi tương ứng. Báo cả `t_render - t_cross` theo cách hiểu
  Charter và `t_render - t_cv` theo mốc xác nhận; xin chốt mốc AT-02 ở câu 14.
- Cần mã tương quan từ sự kiện tới frame/session và bản ghi hiển thị; giá
  trị đếm giống nhau chưa chứng minh đúng bản ghi. Nếu pipeline chỉ gửi ảnh
  chụp số đếm, ghi rõ bản ghi phản ánh sự kiện và cách ánh xạ; không giả định
  event_id của CrossingEvent được API CountResult chấp nhận.
- Dùng UTC đã đồng bộ giữa các máy và kiểm tra lệch đồng hồ trước/sau phiên;
  ghi sai số thời gian. Chỉ lấy hiệu monotonic khi hai mốc cùng miền đồng hồ;
  không trừ trực tiếp Python monotonic với browser performance.now(). Thời
  điểm render cần đo tại UI, không thay bằng lúc HTTP trả về.
- Không dùng `recorded_at` làm t_cross. Với video, timestamp_ms là thời gian
  tương đối, không phải UTC để trừ với giờ web. Chưa có instrument/mã tương
  quan thì kết quả ghi không đo được. Không sửa số trễ âm về 0.
- Ghi retry, timeout, mất cập nhật, polling, mẫu không ghép được và sự kiện
  bị gộp giữa hai lần poll. Sự kiện không xuất hiện riêng trên web không có
  độ trễ riêng hợp lệ; báo thiếu mẫu, không loại âm thầm khỏi mẫu số.

Báo số sự kiện dự kiến/ghép được/mất/không ghép được, trung bình, trung vị,
lớn nhất độ trễ và số mẫu >5 giây. Nếu khoảng bất định do lệch đồng hồ chạm
ngưỡng thì ghi chưa đủ kết luận. Mục tiêu ≤5 giây không tự đồng nghĩa trung
bình ≤5 giây; cách tổng hợp/đánh giá cần duyệt trước.

## 7. Phân tích nguyên nhân và quản lý dữ liệu

| Nhóm lỗi            | Dấu hiệu cần ghi                                | Cách phân tích/đợt thử tiếp theo                                                             |
| --------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Detection             | Thiếu người/bbox, ánh sáng, che khuất        | Đối chiếu mốc/frame được phép; thử góc/ảnh/confidence khác trong phiên mới.           |
| Tracking              | ID đổi, hai người nhập track, track mất lâu | Ghi thời điểm và IN/OUT sai; phân biệt detection với nối track.                             |
| Line/cấu hình       | Sai hướng, ngoài đoạn, rung, cooldown/gap     | Kiểm tra vị trí và quy tắc line; không chỉnh giữa phiên mà không ghi log.                |
| Baseline/hiệu chỉnh | Hiện diện trôi, underflow, restart              | Đối soát N0 và lượt bỏ sót; giữ kết quả trước/sau hiệu chỉnh tách riêng.           |
| Truyền/hiển thị    | Retry, timeout, polling, bản ghi cũ              | Dùng timestamp/mã tương quan, kiểm tra kết nối; không quy tất cả cho model.               |
| Tham chiếu           | A/B lệch, ranh giới mốc không rõ              | Giữ bảng gốc, đối soát độc lập; unresolved không dùng làm ground truth đã xác nhận. |

Chỉ thu số liệu cần thiết, không nhận diện khuôn mặt/danh tính. Người quản lý
dữ liệu ghi danh sách được truy cập (nhóm thực nghiệm được phân công), nơi
lưu cục bộ được bảo vệ và hạn xóa theo chấp thuận. Video chỉ ghi khi được
phép, lưu tạm để đối soát/tính xong rồi xóa và ghi biên bản xóa; không lưu
lâu dài hoặc tải lên Git. Nếu việc đối soát kéo dài quá hạn, xin xác nhận
gia hạn trước, không tự giữ tiếp. Không tải video chỉ để minh họa PR.

File JSONL debug, bbox/track, ảnh chụp và log có đường dẫn/tài khoản/mã nguồn
camera phải rà soát trước chia sẻ; không đưa lên Git nguyên trạng. Trong
repo chỉ giữ mẫu trống và báo cáo tổng hợp ẩn danh được phép; bằng chứng
chấp thuận và dữ liệu gốc lưu tại nơi hạn chế truy cập, báo cáo chỉ dẫn mã.

## 8. Checklist duyệt và nghiệm thu kế hoạch

- [ ] Duyệt thiết kế phiên, nhân sự, địa điểm, lịch, cách thu/lưu/xóa dữ liệu.
- [ ] Câu 14 SRS được chốt: tham chiếu, mẫu số 0, tuổi mẫu tối đa, mốc độ trễ,
  số mẫu và cách tổng hợp/ngưỡng kết luận AT-01 đến AT-03.
- [ ] Câu 15 SRS được chốt: số đầu phiên, cách hiệu chỉnh và xử lý restart/lệch đếm.
- [ ] Mỗi AT có phương pháp và trường ghi tương ứng trong mẫu; hai người đếm
  hiểu quy tắc và giữ được bản gốc riêng.
- [ ] Ghi rõ hạn chế đo AT-02 và ảnh 416 trên UI; xác nhận môi trường đủ điều
  kiện trước khi lên lịch phần đo live.
- [ ] Review PR kế hoạch theo quy ước; không coi việc viết xong hoặc merge
  tài liệu là bằng chứng KPI đã đạt hay thực nghiệm đã thực hiện.

Sau đợt đo mới lập báo cáo kết quả: dữ liệu hợp lệ/thiếu, cấu hình, các thống
kê, đối chiếu ngưỡng đã duyệt, nguyên nhân sai và giới hạn.
