import { afterEach, describe, expect, it, vi } from "vitest";
import {
  getApiHealth,
  getCurrentOccupancy,
  getRooms,
} from "../src/services/api.js";

afterEach(() => {
  vi.stubEnv("VITE_USE_MOCK", "false");
  vi.stubEnv("VITE_MOCK_OCCUPANCY_STATE", "fresh");
});

describe("API mock mode", () => {
  it("returns rooms using the API contract response shape", async () => {
    vi.stubEnv("VITE_USE_MOCK", "true");

    await expect(getRooms()).resolves.toMatchObject({
      items: [
        {
          id: 14,
          code: "A101",
          name: "Phòng A101",
          capacity: 40,
        },
      ],
      limit: 50,
      offset: 0,
      total: 1,
    });
  });

  it.each([
    ["fresh", 23, false, "online"],
    ["stale", 19, true, "online"],
    ["offline", null, true, "offline"],
  ])(
    "returns the %s occupancy fixture",
    async (status, count, isStale, deviceStatus) => {
      vi.stubEnv("VITE_USE_MOCK", "true");

      const data = await getCurrentOccupancy({ status });

      expect(data.count).toBe(count);
      expect(data.rooms[0].is_stale).toBe(isStale);
      expect(data.rooms[0].device_status).toBe(deviceStatus);
    },
  );

  it("uses the current timestamp for fresh occupancy data", async () => {
    vi.stubEnv("VITE_USE_MOCK", "true");
    const startedAt = Date.now();

    const data = await getCurrentOccupancy({ status: "fresh" });
    const updatedAt = Date.parse(data.updatedAt);

    expect(updatedAt).toBeGreaterThanOrEqual(startedAt);
    expect(updatedAt).toBeLessThanOrEqual(Date.now());
    expect(data.last_updated).toBe(data.rooms[0].updated_at);
    expect(data.rooms[0].is_stale).toBe(false);
  });

  it("does not call fetch when mock mode is enabled", async () => {
    vi.stubEnv("VITE_USE_MOCK", "true");
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await getRooms();
    await getCurrentOccupancy();

    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("uses mock health response instead of calling the backend", async () => {
    vi.stubEnv("VITE_USE_MOCK", "true");

    await expect(getApiHealth()).resolves.toEqual({
      status: "ok",
      service: "backend",
    });
  });
});
