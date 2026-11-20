/**
 * SEAT-63: Theme — Màu, font, khoảng cách theo SEAT-46
 *
 * Thang khoảng cách: bội số 4px (compact) và 8px (layout).
 * Màu sắc:
 *   - Vắng  (empty)   : xanh lá  — thoải mái, nhiều chỗ trống
 *   - Vừa  (moderate) : vàng cam — bắt đầu đông, nên cân nhắc
 *   - Đông  (crowded) : đỏ       — gần hết hoặc hết chỗ
 *
 * Thang xám (kiểm tra tương phản):
 *   empty    → #18a36e  → gray #5a9  → đủ sáng để đọc trên trắng (AA)
 *   moderate → #b76b00  → gray #777  → đủ sáng (AA)
 *   crowded  → #ba1a1a  → gray #5c5  → đủ sáng (AA)
 */

// ── Màu sắc cốt lõi ────────────────────────────────────────────────────────

export const colors = {
  // Màu thương hiệu (kế thừa từ main.css :root)
  primary:   "#002452",
  secondary: "#0055c7",
  muted:     "#747781",
  outline:   "#d7dce8",
  surface:   "#f7f8ff",
  surfaceLow:   "#eff4ff",
  surfaceCard:  "#ffffff",
  surfaceContainer: "#e7efff",

  // Màu trạng thái chung
  green:  "#07875c",
  amber:  "#b76b00",
  error:  "#ba1a1a",

  // ── Mức mật độ chỗ ngồi ────────────────────────────────────────────────
  occupancy: {
    empty: {
      /** Màu chữ / icon */
      text:       "#176444",
      /** Màu nền huy hiệu */
      background: "#effaf4",
      /** Màu viền huy hiệu */
      border:     "#b8e3cc",
      /** Dot màu (progress bar / status dot) */
      dot:        "#18a36e",
    },
    moderate: {
      text:       "#7a4100",
      background: "#fff8e9",
      border:     "#efd29d",
      dot:        "#d4860a",
    },
    crowded: {
      text:       "#93000a",
      background: "#fff2f0",
      border:     "#f0c2bd",
      dot:        "#ba1a1a",
    },
  },
} as const;

// ── Typography ─────────────────────────────────────────────────────────────

export const typography = {
  fontFamily:
    "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  sizes: {
    xs:   "9px",
    sm:   "11px",
    base: "14px",
    md:   "16px",
    lg:   "18px",
    xl:   "22px",
    "2xl": "30px",
    "3xl": "34px",
  },
  weights: {
    regular:  400,
    medium:   500,
    semibold: 650,
    bold:     700,
  },
} as const;

// ── Thang khoảng cách (bội số 4px) ─────────────────────────────────────────

export const spacing = {
  0:  "0px",
  1:  "4px",
  2:  "8px",
  3:  "12px",
  4:  "16px",
  5:  "20px",
  6:  "24px",
  7:  "28px",
  8:  "32px",
  10: "40px",
  12: "48px",
  14: "56px",
  16: "64px",
} as const;

// ── Border radius ───────────────────────────────────────────────────────────

export const radius = {
  sm:   "6px",
  md:   "8px",
  lg:   "12px",
  pill: "99px",
} as const;

// ── Shadows ─────────────────────────────────────────────────────────────────

export const shadows = {
  card: "0 2px 6px rgb(11 28 48 / 4%)",
  sm:   "0 1px 3px rgb(11 28 48 / 8%)",
} as const;

// ── Export gom ──────────────────────────────────────────────────────────────

const theme = { colors, typography, spacing, radius, shadows } as const;
export default theme;

// ── Types ───────────────────────────────────────────────────────────────────

export type OccupancyLevel = keyof typeof colors.occupancy;
