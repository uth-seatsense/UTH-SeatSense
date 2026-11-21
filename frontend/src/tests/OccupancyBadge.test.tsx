/**
 * SEAT-63: Tests cho OccupancyBadge component
 *
 * Test ba mức hiển thị đúng nhãn.
 * Test icon hiển thị theo mức.
 * Test contrast (via CSS class presence).
 * Test tái sử dụng component (nhiều kích thước).
 */

import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { OccupancyBadge, getOccupancyLevel } from "../components/OccupancyBadge";

// Helper
function render(element: React.ReactElement): string {
  return renderToStaticMarkup(element);
}

// ── Ba mức hiển thị ────────────────────────────────────────────────────────

describe("OccupancyBadge — Mức 'empty' (Vắng)", () => {
  it("hiển thị nhãn 'Vắng'", () => {
    const html = render(createElement(OccupancyBadge, { level: "empty" }));
    expect(html).toContain("Vắng");
  });

  it("có class occupancy-badge--empty", () => {
    const html = render(createElement(OccupancyBadge, { level: "empty" }));
    expect(html).toContain("occupancy-badge--empty");
  });

  it("có aria-label mô tả trạng thái Vắng", () => {
    const html = render(createElement(OccupancyBadge, { level: "empty" }));
    expect(html).toContain("Còn nhiều chỗ trống");
  });

  it("hiển thị icon kèm nhãn theo mặc định (showIcon=true)", () => {
    const html = render(createElement(OccupancyBadge, { level: "empty" }));
    // Icon mức empty là "✓"
    expect(html).toContain("✓");
  });
});

describe("OccupancyBadge — Mức 'moderate' (Vừa)", () => {
  it("hiển thị nhãn 'Vừa'", () => {
    const html = render(createElement(OccupancyBadge, { level: "moderate" }));
    expect(html).toContain("Vừa");
  });

  it("có class occupancy-badge--moderate", () => {
    const html = render(createElement(OccupancyBadge, { level: "moderate" }));
    expect(html).toContain("occupancy-badge--moderate");
  });

  it("có aria-label mô tả trạng thái Vừa", () => {
    const html = render(createElement(OccupancyBadge, { level: "moderate" }));
    expect(html).toContain("Lấp đầy vừa phải");
  });

  it("hiển thị icon '~' cho mức vừa", () => {
    const html = render(createElement(OccupancyBadge, { level: "moderate" }));
    expect(html).toContain("~");
  });
});

describe("OccupancyBadge — Mức 'crowded' (Đông)", () => {
  it("hiển thị nhãn 'Đông'", () => {
    const html = render(createElement(OccupancyBadge, { level: "crowded" }));
    expect(html).toContain("Đông");
  });

  it("có class occupancy-badge--crowded", () => {
    const html = render(createElement(OccupancyBadge, { level: "crowded" }));
    expect(html).toContain("occupancy-badge--crowded");
  });

  it("có aria-label mô tả trạng thái Đông", () => {
    const html = render(createElement(OccupancyBadge, { level: "crowded" }));
    expect(html).toContain("Gần hết hoặc hết chỗ");
  });

  it("hiển thị icon '!' cho mức đông", () => {
    const html = render(createElement(OccupancyBadge, { level: "crowded" }));
    expect(html).toContain("!");
  });
});

// ── showIcon=false ─────────────────────────────────────────────────────────

describe("OccupancyBadge — showIcon=false", () => {
  it("ẩn icon khi showIcon=false nhưng vẫn hiển thị nhãn", () => {
    const html = render(
      createElement(OccupancyBadge, { level: "empty", showIcon: false }),
    );
    expect(html).toContain("Vắng");
    expect(html).not.toContain("✓");
  });

  it("ẩn icon crowded khi showIcon=false", () => {
    const html = render(
      createElement(OccupancyBadge, { level: "crowded", showIcon: false }),
    );
    expect(html).toContain("Đông");
    // icon "!" của crowded không được render
    // Note: "!" có thể xuất hiện trong HTML entities; kiểm tra không có span icon
    expect(html).not.toContain('<span aria-hidden="true"');
  });
});

// ── Nhiều kích thước (tái sử dụng) ────────────────────────────────────────

describe("OccupancyBadge — Tái sử dụng nhiều kích thước", () => {
  for (const size of ["sm", "md", "lg"] as const) {
    it(`có class occupancy-badge--${size} khi size="${size}"`, () => {
      const html = render(createElement(OccupancyBadge, { level: "empty", size }));
      expect(html).toContain(`occupancy-badge--${size}`);
    });
  }
});

// ── Accessibility ──────────────────────────────────────────────────────────

describe("OccupancyBadge — Accessibility", () => {
  it("có role='img' để screen reader đọc được", () => {
    const html = render(createElement(OccupancyBadge, { level: "empty" }));
    expect(html).toContain('role="img"');
  });

  it("icon có aria-hidden='true' để không đọc lại", () => {
    const html = render(createElement(OccupancyBadge, { level: "empty" }));
    expect(html).toContain('aria-hidden="true"');
  });
});

// ── getOccupancyLevel helper ───────────────────────────────────────────────

describe("getOccupancyLevel — Phân loại mức từ tỉ lệ lấp đầy", () => {
  it("trả về 'empty' khi tỉ lệ < 50%", () => {
    expect(getOccupancyLevel(10, 100)).toBe("empty");
    expect(getOccupancyLevel(49, 100)).toBe("empty");
    expect(getOccupancyLevel(0,  50)).toBe("empty");
  });

  it("trả về 'moderate' khi tỉ lệ 50%–85%", () => {
    expect(getOccupancyLevel(50,  100)).toBe("moderate");
    expect(getOccupancyLevel(85,  100)).toBe("moderate");
    expect(getOccupancyLevel(170, 200)).toBe("moderate");
  });

  it("trả về 'crowded' khi tỉ lệ > 85%", () => {
    expect(getOccupancyLevel(86,  100)).toBe("crowded");
    expect(getOccupancyLevel(100, 100)).toBe("crowded");
    expect(getOccupancyLevel(200, 100)).toBe("crowded");
  });

  it("trả về 'empty' khi số người = 0", () => {
    expect(getOccupancyLevel(0, 100)).toBe("empty");
  });
});
