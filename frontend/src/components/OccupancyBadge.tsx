/**
 * SEAT-63: OccupancyBadge — Huy hiệu mức mật độ chỗ ngồi
 *
 * Ba mức:
 *   empty    → Vắng   (xanh lá)
 *   moderate → Vừa    (vàng cam)
 *   crowded  → Đông   (đỏ)
 *
 * Mỗi mức có cả màu LẪN nhãn chữ và biểu tượng
 * → đọc được ngay cả khi chuyển sang thang xám (AA contrast).
 *
 * Phụ thuộc: SEAT-46 (bảng màu — đã Done).
 */

import { type OccupancyLevel } from "../theme/theme";

// ── Mapping nhãn & icon cho từng mức ──────────────────────────────────────

const LEVEL_CONFIG: Record<
  OccupancyLevel,
  { label: string; icon: string; ariaLabel: string }
> = {
  empty: {
    label:     "Vắng",
    icon:      "✓",   // dấu tích — còn nhiều chỗ
    ariaLabel: "Còn nhiều chỗ trống",
  },
  moderate: {
    label:     "Vừa",
    icon:      "~",   // dấu tilde — khoảng vừa
    ariaLabel: "Lấp đầy vừa phải, nên cân nhắc",
  },
  crowded: {
    label:     "Đông",
    icon:      "!",   // dấu chấm than — đông, chú ý
    ariaLabel: "Gần hết hoặc hết chỗ",
  },
};

// ── Hàm phân loại mức từ tỉ lệ lấp đầy ──────────────────────────────────

/**
 * Phân loại mức mật độ dựa trên tỉ lệ lấp đầy.
 *
 * @param occupiedCount  Số người đang có mặt
 * @param capacity       Sức chứa tối đa của phòng
 * @returns OccupancyLevel
 *
 * Ngưỡng (theo SEAT-46):
 *   < 50%  → empty
 *   50–85% → moderate
 *   > 85%  → crowded
 */
export function getOccupancyLevel(
  occupiedCount: number,
  capacity: number,
): OccupancyLevel {
  if (capacity <= 0) return "insufficient" as never;
  const ratio = occupiedCount / capacity;
  if (ratio < 0.5)  return "empty";
  if (ratio <= 0.85) return "moderate";
  return "crowded";
}

// ── Props ──────────────────────────────────────────────────────────────────

export interface OccupancyBadgeProps {
  /** Mức mật độ: "empty" | "moderate" | "crowded" */
  level: OccupancyLevel;
  /**
   * Kích thước badge.
   * - "sm" : nhỏ (12px) — dùng trong danh sách phòng
   * - "md" : mặc định (13px) — dùng mọi nơi
   * - "lg" : lớn (15px) — dùng trong dashboard card
   */
  size?: "sm" | "md" | "lg";
  /** Hiển thị icon kèm nhãn (mặc định: true) */
  showIcon?: boolean;
  /** CSS class thêm vào ngoài */
  className?: string;
}

// ── Inline styles theo mức (dùng CSS variable dự phòng) ───────────────────

const LEVEL_STYLES: Record<OccupancyLevel, React.CSSProperties> = {
  empty: {
    color:           "#176444",
    backgroundColor: "#effaf4",
    borderColor:     "#b8e3cc",
  },
  moderate: {
    color:           "#7a4100",
    backgroundColor: "#fff8e9",
    borderColor:     "#efd29d",
  },
  crowded: {
    color:           "#93000a",
    backgroundColor: "#fff2f0",
    borderColor:     "#f0c2bd",
  },
};

const SIZE_STYLES: Record<NonNullable<OccupancyBadgeProps["size"]>, React.CSSProperties> = {
  sm: { fontSize: "11px", padding: "3px 7px", gap: "4px" },
  md: { fontSize: "13px", padding: "4px 9px",  gap: "5px" },
  lg: { fontSize: "15px", padding: "5px 11px", gap: "6px" },
};

// ── Component ──────────────────────────────────────────────────────────────

import React from "react";

/**
 * OccupancyBadge
 *
 * Hiển thị mức mật độ chỗ ngồi với màu sắc, nhãn chữ và biểu tượng.
 * Component tái sử dụng được ở bất kỳ đâu trong ứng dụng.
 *
 * @example
 * <OccupancyBadge level="empty" />
 * <OccupancyBadge level="moderate" size="lg" />
 * <OccupancyBadge level="crowded" showIcon={false} />
 */
export function OccupancyBadge({
  level,
  size = "md",
  showIcon = true,
  className = "",
}: OccupancyBadgeProps) {
  const { label, icon, ariaLabel } = LEVEL_CONFIG[level];
  const levelStyle  = LEVEL_STYLES[level];
  const sizeStyle   = SIZE_STYLES[size];

  const baseStyle: React.CSSProperties = {
    display:        "inline-flex",
    alignItems:     "center",
    gap:            sizeStyle.gap,
    padding:        sizeStyle.padding,
    borderRadius:   "99px",
    border:         "1px solid",
    fontWeight:     650,
    whiteSpace:     "nowrap",
    lineHeight:     1.2,
    fontSize:       sizeStyle.fontSize,
    ...levelStyle,
  };

  return (
    <span
      aria-label={ariaLabel}
      className={`occupancy-badge occupancy-badge--${level} occupancy-badge--${size} ${className}`.trim()}
      role="img"
      style={baseStyle}
    >
      {showIcon && (
        <span aria-hidden="true" style={{ fontWeight: 700 }}>
          {icon}
        </span>
      )}
      {label}
    </span>
  );
}

export default OccupancyBadge;
