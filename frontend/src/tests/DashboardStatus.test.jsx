import { describe, expect, it } from "vitest";
import { getOccupancyConnectionStatus } from "../pages/DashboardPage.jsx";

describe("getOccupancyConnectionStatus", () => {
  it("reports loading while the first request is pending", () => {
    expect(
      getOccupancyConnectionStatus({
        error: "",
        isLoading: true,
        occupancy: null,
      }),
    ).toEqual({ text: "Đang tải dữ liệu", className: "loading" });
  });

  it("distinguishes a successful response with no occupancy data", () => {
    expect(
      getOccupancyConnectionStatus({
        error: "",
        isLoading: false,
        occupancy: null,
      }),
    ).toEqual({ text: "Chưa có dữ liệu", className: "empty" });
  });

  it("reports API errors without describing them as connection errors", () => {
    expect(
      getOccupancyConnectionStatus({
        error: "API trả về lỗi HTTP 404",
        isLoading: false,
        occupancy: null,
      }),
    ).toEqual({ text: "Không thể cập nhật", className: "error" });
  });

  it("reports live updates when occupancy data is available", () => {
    expect(
      getOccupancyConnectionStatus({
        error: "",
        isLoading: false,
        occupancy: { count: 0 },
      }),
    ).toEqual({ text: "Cập nhật trực tiếp", className: "" });
  });
});
