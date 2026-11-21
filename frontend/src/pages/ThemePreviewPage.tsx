/**
 * SEAT-63: ThemePreviewPage — Trang xem thử theme và các mức đông
 *
 * CHỈ DÙNG KHI PHÁT TRIỂN — không xuất hiện trong điều hướng chính thức.
 * Truy cập: /theme-preview (thêm vào App.jsx tạm thời khi dev)
 *
 * Hiển thị:
 *  - Ba mức OccupancyBadge ở nhiều kích thước
 *  - Bảng màu theme
 *  - StaleWarning ở ba trạng thái
 */

import React from "react";
import { OccupancyBadge } from "../components/OccupancyBadge";
import { StaleWarning } from "../components/StaleWarning";
import theme from "../theme/theme";

// ── Helpers ────────────────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ marginBottom: 48 }}>
      <h2
        style={{
          marginBottom: 16,
          color: theme.colors.primary,
          fontSize: theme.typography.sizes.xl,
          fontWeight: theme.typography.weights.bold,
          borderBottom: `2px solid ${theme.colors.outline}`,
          paddingBottom: 8,
        }}
      >
        {title}
      </h2>
      {children}
    </section>
  );
}

function ColorSwatch({
  name,
  value,
}: {
  name: string;
  value: string;
}) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
      <span
        style={{
          display:      "inline-block",
          width:        40,
          height:       40,
          borderRadius: theme.radius.md,
          background:   value,
          border:       `1px solid ${theme.colors.outline}`,
          flexShrink:   0,
        }}
      />
      <span style={{ fontFamily: "monospace", fontSize: 13 }}>
        <strong>{name}</strong> — {value}
      </span>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────

export default function ThemePreviewPage() {
  const levels = ["empty", "moderate", "crowded"] as const;
  const sizes  = ["sm", "md", "lg"]              as const;

  return (
    <main
      style={{
        width:     "min(100% - 32px, 960px)",
        margin:    "0 auto",
        padding:   "32px 0 64px",
        fontFamily: theme.typography.fontFamily,
        color:     theme.colors.primary,
      }}
    >
      <h1
        style={{
          fontSize:      theme.typography.sizes["3xl"],
          fontWeight:    theme.typography.weights.bold,
          letterSpacing: "-0.035em",
          marginBottom:  8,
        }}
      >
        Theme Preview
      </h1>
      <p style={{ color: theme.colors.muted, marginBottom: 40 }}>
        Trang xem thử — chỉ dùng khi phát triển (SEAT-63)
      </p>

      {/* ── OccupancyBadge ──────────────────────────────────────────────── */}
      <Section title="OccupancyBadge — Ba mức mật độ">
        {sizes.map((size) => (
          <div
            key={size}
            style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 16 }}
          >
            <span
              style={{
                width:     60,
                fontSize:  theme.typography.sizes.sm,
                color:     theme.colors.muted,
                flexShrink: 0,
              }}
            >
              {size.toUpperCase()}
            </span>
            {levels.map((level) => (
              <OccupancyBadge key={level} level={level} size={size} />
            ))}
          </div>
        ))}

        {/* Không có icon */}
        <p style={{ marginTop: 16, fontSize: 13, color: theme.colors.muted }}>
          Không có icon (showIcon=false):
        </p>
        <div style={{ display: "flex", gap: 12 }}>
          {levels.map((level) => (
            <OccupancyBadge key={level} level={level} showIcon={false} />
          ))}
        </div>

        {/* Thang xám — kiểm tra tương phản */}
        <p
          style={{
            marginTop:  24,
            marginBottom: 8,
            fontSize:   13,
            color:      theme.colors.muted,
          }}
        >
          Thang xám (filter: grayscale) — kiểm tra độ tương phản AA:
        </p>
        <div
          style={{
            display: "flex",
            gap:     12,
            filter: "grayscale(100%)",
            padding: 12,
            borderRadius: theme.radius.md,
            background: "#f4f4f4",
          }}
        >
          {levels.map((level) => (
            <OccupancyBadge key={level} level={level} />
          ))}
        </div>
      </Section>

      {/* ── StaleWarning ────────────────────────────────────────────────── */}
      <Section title="StaleWarning — Ba trạng thái">
        <div style={{ display: "grid", gap: 16 }}>
          <StaleWarning
            status="stale"
            lastUpdatedAt="2026-11-20T08:30:00+07:00"
          />
          <StaleWarning status="disconnected" />
          <StaleWarning status="insufficient" />
        </div>
      </Section>

      {/* ── Bảng màu ────────────────────────────────────────────────────── */}
      <Section title="Bảng màu theme">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 24 }}>
          <div>
            <p style={{ fontWeight: 650, marginBottom: 8 }}>Màu thương hiệu</p>
            <ColorSwatch name="primary"   value={theme.colors.primary} />
            <ColorSwatch name="secondary" value={theme.colors.secondary} />
            <ColorSwatch name="muted"     value={theme.colors.muted} />
            <ColorSwatch name="outline"   value={theme.colors.outline} />
          </div>
          <div>
            <p style={{ fontWeight: 650, marginBottom: 8 }}>Mức mật độ — text</p>
            <ColorSwatch name="empty text"    value={theme.colors.occupancy.empty.text} />
            <ColorSwatch name="moderate text" value={theme.colors.occupancy.moderate.text} />
            <ColorSwatch name="crowded text"  value={theme.colors.occupancy.crowded.text} />
          </div>
          <div>
            <p style={{ fontWeight: 650, marginBottom: 8 }}>Mức mật độ — nền</p>
            <ColorSwatch name="empty bg"    value={theme.colors.occupancy.empty.background} />
            <ColorSwatch name="moderate bg" value={theme.colors.occupancy.moderate.background} />
            <ColorSwatch name="crowded bg"  value={theme.colors.occupancy.crowded.background} />
          </div>
        </div>
      </Section>
    </main>
  );
}
