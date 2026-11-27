/**
 * SEAT-55: Thông báo tiếng Việt đã thống nhất (SEAT-45)
 * Dùng chung cho StaleWarning và các component cảnh báo trạng thái dữ liệu.
 */

export const STALE_MESSAGES = {
  /** Dữ liệu cũ: nhận được từ nguồn nhưng quá hạn */
  stale: {
    title: "Dữ liệu có thể không còn chính xác",
    description:
      "Số liệu hiển thị đã được cập nhật cách đây khá lâu và có thể không phản ánh tình trạng thực tế hiện tại.",
    hint: "Vui lòng kiểm tra lại trước khi sử dụng.",
  },

  /** Nguồn mất kết nối: CV service không phản hồi */
  disconnected: {
    title: "Nguồn dữ liệu mất kết nối",
    description:
      "Hệ thống không nhận được dữ liệu mới từ camera. Số liệu hiển thị là lần cập nhật gần nhất.",
    hint: "Đội quản lý đã được thông báo. Thử lại sau ít phút.",
  },

  /** Chưa đủ dữ liệu: mới khởi động hoặc chưa có frame nào */
  insufficient: {
    title: "Chưa đủ dữ liệu",
    description:
      "Hệ thống đang khởi động hoặc chưa nhận được đủ dữ liệu để hiển thị số liệu chính xác.",
    hint: "Vui lòng đợi vài giây để hệ thống cập nhật.",
  },
} as const;

export type StaleStatus = keyof typeof STALE_MESSAGES;

/** Nhãn hiển thị cho từng trạng thái (dùng trong badge/pill) */
export const STALE_STATUS_LABELS: Record<StaleStatus, string> = {
  stale: "Dữ liệu cũ",
  disconnected: "Mất kết nối",
  insufficient: "Chưa đủ dữ liệu",
};
