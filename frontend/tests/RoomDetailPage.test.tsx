import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import RoomDetailPage from "../src/pages/RoomDetailPage";
import {
  getRoomDetails,
  getRoomOccupancyDetail,
} from "../src/services/roomApi";

vi.mock("../src/services/roomApi", () => ({
  getRoomDetails: vi.fn(),
  getRoomOccupancyDetail: vi.fn(),
}));

const room = {
  id: 14,
  code: "A101",
  name: "Phòng A101",
  capacity: 40,
  campus_code: "CS1",
  building: "Cơ sở 1",
  is_active: true,
};

function occupancy(count: number, recordedAt = "2026-11-24T05:00:00Z") {
  return {
    estimated_occupancy: count,
    recorded_at: recordedAt,
    received_at: recordedAt,
    is_stale: false,
  };
}

function renderRoomDetail() {
  return render(
    <MemoryRouter initialEntries={["/rooms/14"]}>
      <Routes>
        <Route path="/rooms/:roomId" element={<RoomDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.useFakeTimers();
  vi.stubEnv("VITE_POLL_INTERVAL_MS", "3000");
  vi.mocked(getRoomDetails).mockResolvedValue(room);
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllEnvs();
  vi.clearAllMocks();
});

describe("RoomDetailPage", () => {
  it("updates occupancy when the polling API returns a new count", async () => {
    vi.mocked(getRoomOccupancyDetail)
      .mockResolvedValueOnce(occupancy(23))
      .mockResolvedValueOnce(occupancy(24, "2026-11-24T05:00:03Z"));

    renderRoomDetail();
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(screen.getByText("23 người")).toBeTruthy();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(3000);
    });

    expect(screen.getByText("24 người")).toBeTruthy();
    expect(getRoomOccupancyDetail).toHaveBeenCalledTimes(2);
  });

  it("shows zero available seats and an over-capacity warning", async () => {
    vi.mocked(getRoomOccupancyDetail).mockResolvedValue(occupancy(42));

    renderRoomDetail();
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(screen.getByText("0 chỗ")).toBeTruthy();
    expect(screen.getByRole("alert").textContent).toContain("Vượt sức chứa");
  });

  it("shows the shared stale warning and hides stale counts", async () => {
    vi.mocked(getRoomOccupancyDetail).mockResolvedValue({
      ...occupancy(23),
      is_stale: true,
    });

    renderRoomDetail();
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(document.querySelector('[data-stale-status="stale"]')).toBeTruthy();
    expect(screen.queryByText("23 người")).toBeNull();
  });

  it("shows insufficient-data warning when the capacity is unconfirmed", async () => {
    vi.mocked(getRoomDetails).mockResolvedValue({
      ...room,
      capacity_confirmed: false,
    });
    vi.mocked(getRoomOccupancyDetail).mockResolvedValue(occupancy(23));

    renderRoomDetail();
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(
      document.querySelector('[data-stale-status="insufficient"]'),
    ).toBeTruthy();
    expect(screen.queryByText("23 người")).toBeNull();
  });

  it("stops polling after the page unmounts", async () => {
    vi.mocked(getRoomOccupancyDetail).mockResolvedValue(occupancy(23));

    const { unmount } = renderRoomDetail();
    await act(async () => {
      await Promise.resolve();
      await Promise.resolve();
    });
    expect(getRoomOccupancyDetail).toHaveBeenCalledTimes(1);

    unmount();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(6000);
    });

    expect(getRoomOccupancyDetail).toHaveBeenCalledTimes(1);
  });
});
