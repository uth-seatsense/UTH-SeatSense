/**
 * SEAT-55: Tests cho StaleWarning component
 *
 * Test ba trạng thái hiển thị đúng nội dung.
 * Test dữ liệu cũ không hiển thị như số chính thức.
 * Test hiển thị thời điểm cập nhật gần nhất.
 */

import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { StaleWarning } from "../components/StaleWarning";
import { STALE_MESSAGES, STALE_STATUS_LABELS } from "../constants/messages";

// Helper
function render(element: React.ReactElement): string {
  return renderToStaticMarkup(element);
}

// ── Trạng thái: stale ─────────────────────────────────────────────────────

describe("StaleWarning — trạng thái stale (dữ liệu cũ)", () => {
  it("hiển thị đúng tiêu đề và mô tả cho trạng thái stale", () => {
    const html = render(createElement(StaleWarning, { status: "stale" }));
    expect(html).toContain(STALE_MESSAGES.stale.title);
    expect(html).toContain(STALE_MESSAGES.stale.description);
    expect(html).toContain(STALE_MESSAGES.stale.hint);
  });

  it("hiển thị nhãn badge 'Dữ liệu cũ'", () => {
    const html = render(createElement(StaleWarning, { status: "stale" }));
    expect(html).toContain(STALE_STATUS_LABELS.stale);
  });

  it("có class CSS stale-warning--stale", () => {
    const html = render(createElement(StaleWarning, { status: "stale" }));
    expect(html).toContain("stale-warning--stale");
  });

  it("có data-stale-status='stale' để component cha kiểm soát ẩn số", () => {
    const html = render(createElement(StaleWarning, { status: "stale" }));
    expect(html).toContain('data-stale-status="stale"');
  });

  it("hiển thị thời điểm cập nhật gần nhất khi được truyền vào", () => {
    const html = render(
      createElement(StaleWarning, {
        status:        "stale",
        lastUpdatedAt: "2026-11-20T08:30:00+07:00",
      }),
    );
    // Phải có phần tử <time> với thuộc tính dateTime
    expect(html).toContain("<time");
    expect(html).toContain("Cập nhật lần cuối");
  });

  it("không hiển thị thời điểm khi lastUpdatedAt không được truyền", () => {
    const html = render(createElement(StaleWarning, { status: "stale" }));
    expect(html).not.toContain("Cập nhật lần cuối");
  });

  /**
   * Dữ liệu cũ KHÔNG được hiển thị như số chính thức.
   * StaleWarning tự mình không render số — nó chỉ cung cấp data-attribute
   * để component cha ẩn/mờ số.  Test này xác nhận component không render
   * số chiếm chỗ trực tiếp bên trong StaleWarning.
   */
  it("không tự render số chiếm chỗ chính thức bên trong component", () => {
    const html = render(
      createElement(StaleWarning, { status: "stale", lastUpdatedAt: null }),
    );
    // Không được render số như "80 chỗ" hay "50 người" trong warning box
    expect(html).not.toMatch(/\d+\s*(chỗ|người|chỗ trống)/);
  });
});

// ── Trạng thái: disconnected ───────────────────────────────────────────────

describe("StaleWarning — trạng thái disconnected (mất kết nối)", () => {
  it("hiển thị đúng tiêu đề và mô tả cho trạng thái disconnected", () => {
    const html = render(createElement(StaleWarning, { status: "disconnected" }));
    expect(html).toContain(STALE_MESSAGES.disconnected.title);
    expect(html).toContain(STALE_MESSAGES.disconnected.description);
    expect(html).toContain(STALE_MESSAGES.disconnected.hint);
  });

  it("hiển thị nhãn badge 'Mất kết nối'", () => {
    const html = render(createElement(StaleWarning, { status: "disconnected" }));
    expect(html).toContain(STALE_STATUS_LABELS.disconnected);
  });

  it("có class CSS stale-warning--disconnected", () => {
    const html = render(createElement(StaleWarning, { status: "disconnected" }));
    expect(html).toContain("stale-warning--disconnected");
  });

  it("có data-stale-status='disconnected'", () => {
    const html = render(createElement(StaleWarning, { status: "disconnected" }));
    expect(html).toContain('data-stale-status="disconnected"');
  });
});

// ── Trạng thái: insufficient ───────────────────────────────────────────────

describe("StaleWarning — trạng thái insufficient (chưa đủ dữ liệu)", () => {
  it("hiển thị đúng tiêu đề và mô tả cho trạng thái insufficient", () => {
    const html = render(createElement(StaleWarning, { status: "insufficient" }));
    expect(html).toContain(STALE_MESSAGES.insufficient.title);
    expect(html).toContain(STALE_MESSAGES.insufficient.description);
    expect(html).toContain(STALE_MESSAGES.insufficient.hint);
  });

  it("hiển thị nhãn badge 'Chưa đủ dữ liệu'", () => {
    const html = render(createElement(StaleWarning, { status: "insufficient" }));
    expect(html).toContain(STALE_STATUS_LABELS.insufficient);
  });

  it("có class CSS stale-warning--insufficient", () => {
    const html = render(createElement(StaleWarning, { status: "insufficient" }));
    expect(html).toContain("stale-warning--insufficient");
  });
});

// ── Accessibility ──────────────────────────────────────────────────────────

describe("StaleWarning — Accessibility", () => {
  it("có role='status' và aria-live='polite'", () => {
    const html = render(createElement(StaleWarning, { status: "stale" }));
    expect(html).toContain('role="status"');
    expect(html).toContain('aria-live="polite"');
  });
});
