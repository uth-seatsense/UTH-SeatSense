/**
 * SEAT-55: StaleWarning — Component cảnh báo trạng thái nguồn dữ liệu
 *
 * Ba trạng thái:
 *  - stale        : Dữ liệu cũ (quá hạn)
 *  - disconnected : Nguồn mất kết nối (CV service không phản hồi)
 *  - insufficient : Chưa đủ dữ liệu (mới khởi động)
 *
 * Khi dữ liệu cũ, không hiển thị số như số chính thức.
 * Hiển thị thời điểm cập nhật gần nhất nếu có.
 *
 * Phụ thuộc: SEAT-62 (mock), SEAT-57 (nối API thật)
 */

import { STALE_MESSAGES, STALE_STATUS_LABELS, type StaleStatus } from "../constants/messages";

// ── Icon SVG nội tuyến (không cần thư viện ngoài) ─────────────────────────

function IconWarning() {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      height={20}
      viewBox="0 0 24 24"
      width={20}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
      />
    </svg>
  );
}

function IconDisconnected() {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      height={20}
      viewBox="0 0 24 24"
      width={20}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M18.36 6.64a9 9 0 010 10.72M6.64 6.64a9 9 0 000 10.72M4.93 4.93a13 13 0 000 14.14M19.07 4.93a13 13 0 010 14.14M12 12h.01"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
      />
    </svg>
  );
}

function IconInfo() {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      height={20}
      viewBox="0 0 24 24"
      width={20}
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx={12} cy={12} r={10} stroke="currentColor" strokeWidth={2} />
      <path
        d="M12 16v-4m0-4h.01"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
      />
    </svg>
  );
}

// ── Helpers ────────────────────────────────────────────────────────────────

function formatLastUpdated(value: Date | string | null | undefined): string | null {
  if (!value) return null;
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(date);
}

function iconForStatus(status: StaleStatus) {
  switch (status) {
    case "disconnected":
      return <IconDisconnected />;
    case "insufficient":
      return <IconInfo />;
    default:
      return <IconWarning />;
  }
}

// ── Props ──────────────────────────────────────────────────────────────────

export interface StaleWarningProps {
  /** Trạng thái nguồn dữ liệu hiện tại */
  status: StaleStatus;
  /**
   * Thời điểm cập nhật gần nhất.
   * Truyền null/undefined nếu chưa có lần cập nhật nào.
   */
  lastUpdatedAt?: Date | string | null;
  /** CSS class thêm vào ngoài để tuỳ chỉnh layout */
  className?: string;
}

// ── Component ──────────────────────────────────────────────────────────────

/**
 * StaleWarning
 *
 * Hiển thị cảnh báo khi dữ liệu chiếm chỗ không đáng tin cậy.
 * Khi `status` là "stale" hoặc "disconnected", component ẩn hoặc làm mờ
 * số liệu chính thức — việc ẩn/mờ số do component cha kiểm soát;
 * StaleWarning chỉ cung cấp data-attribute `data-stale-status` để cha
 * dễ truy vấn trạng thái.
 *
 * @example
 * // Dữ liệu cũ, có thời điểm cập nhật
 * <StaleWarning status="stale" lastUpdatedAt="2026-11-20T09:00:00Z" />
 *
 * @example
 * // Nguồn mất kết nối, chưa có lần cập nhật nào
 * <StaleWarning status="disconnected" />
 *
 * @example
 * // Chưa đủ dữ liệu
 * <StaleWarning status="insufficient" />
 */
export function StaleWarning({ status, lastUpdatedAt, className = "" }: StaleWarningProps) {
  const { title, description, hint } = STALE_MESSAGES[status];
  const formattedTime = formatLastUpdated(lastUpdatedAt);
  const label = STALE_STATUS_LABELS[status];

  return (
    <div
      aria-live="polite"
      className={`stale-warning stale-warning--${status} ${className}`.trim()}
      data-stale-status={status}
      role="status"
    >
      {/* Icon + tiêu đề */}
      <div className="stale-warning__header">
        <span className="stale-warning__icon">{iconForStatus(status)}</span>
        <span className="stale-warning__badge">{label}</span>
        <strong className="stale-warning__title">{title}</strong>
      </div>

      {/* Mô tả chi tiết */}
      <p className="stale-warning__description">{description}</p>

      {/* Gợi ý xử lý */}
      <p className="stale-warning__hint">{hint}</p>

      {/* Thời điểm cập nhật gần nhất */}
      {formattedTime && (
        <p className="stale-warning__timestamp">
          Cập nhật lần cuối:{" "}
          <time dateTime={new Date(lastUpdatedAt as string | Date).toISOString()}>
            {formattedTime}
          </time>
        </p>
      )}
    </div>
  );
}

export default StaleWarning;
