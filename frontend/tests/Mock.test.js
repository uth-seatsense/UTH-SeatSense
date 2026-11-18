import { afterEach, describe, expect, it, vi } from "vitest";
import {
  getApiHealth,
  getCurrentOccupancy,
  isMockEnabled,
} from "../src/services/api.js";

afterEach(() => {
  vi.stubEnv("VITE_USE_MOCK", "false");
});

describe("API with mock toggle", () => {
  it("uses mock data when VITE_USE_MOCK is true", async () => {
    vi.stubEnv("VITE_USE_MOCK", "true");

    expect(isMockEnabled()).toBe(true);

    const data = await getCurrentOccupancy();
    expect(data).toBeDefined();
    expect(data.rooms).toBeDefined();
    expect(data.rooms.length).toBeGreaterThan(0);
    expect(data.rooms[0]).toHaveProperty("room_id");
    expect(data.rooms[0]).toHaveProperty("current_count");
  });

  it("mock health check returns ok status", async () => {
    vi.stubEnv("VITE_USE_MOCK", "true");

    const health = await getApiHealth();
    expect(health.status).toBe("ok");
    expect(health.service).toBe("backend");
  });
});
