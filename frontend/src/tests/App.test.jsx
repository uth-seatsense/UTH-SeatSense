import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../App.jsx";
import { StaticRouter } from "react-router-dom";
import { getCurrentOccupancy, normalizeOccupancy } from "../services/api.js";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("Dashboard", () => {
  it("renders the loading state without presenting sample occupancy data", () => {
    const markup = renderToStaticMarkup(
      createElement(StaticRouter, { location: "/" }, createElement(App)),
    );

    expect(markup).toContain("Đang có mặt");
    expect(markup).toContain("Đang tải dữ liệu");
    expect(markup).not.toContain(">80<");
  });
});

describe("normalizeOccupancy", () => {
  it("reads a current count, timestamp, and location from the API", () => {
    expect(
      normalizeOccupancy({
        data: {
          current_count: 24,
          updated_at: "2026-11-03T10:45:12+07:00",
          location: "Thư viện UTH",
        },
      }),
    ).toEqual({
      count: 24,
      updatedAt: "2026-11-03T10:45:12+07:00",
      location: "Thư viện UTH",
    });
  });

  describe("getCurrentOccupancy", () => {
    it("requests the versioned endpoint without an unsupported campus filter", async () => {
      vi.stubGlobal("window", {
        location: { origin: "http://localhost:3000" },
      });
      const fetchMock = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ current_count: 7 }),
      });
      vi.stubGlobal("fetch", fetchMock);
      const controller = new AbortController();

      await getCurrentOccupancy({ signal: controller.signal });

      expect(fetchMock).toHaveBeenCalledWith(
        new URL("/api/v1/occupancy/current", "http://localhost:3000"),
        { signal: controller.signal },
      );
    });
  });

  it("preserves a valid zero count and treats missing data as empty", () => {
    expect(normalizeOccupancy({ count: 0 })).toEqual({
      count: 0,
      updatedAt: null,
      location: null,
    });
    expect(normalizeOccupancy({})).toBeNull();
    expect(normalizeOccupancy(null)).toBeNull();
  });

  it("rejects invalid counts instead of displaying them", () => {
    expect(() => normalizeOccupancy({ current_count: -1 })).toThrow(
      "API trả về số người không hợp lệ",
    );
    expect(() => normalizeOccupancy({ current_count: "24" })).toThrow(
      "API trả về số người không hợp lệ",
    );
  });
});
