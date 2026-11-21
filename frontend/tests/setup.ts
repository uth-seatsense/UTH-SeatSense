import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

vi.stubEnv("VITE_USE_MOCK", "false");
vi.stubEnv("VITE_MOCK_OCCUPANCY_STATE", "fresh");

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  vi.unstubAllGlobals();
  vi.stubEnv("VITE_USE_MOCK", "false");
  vi.stubEnv("VITE_MOCK_OCCUPANCY_STATE", "fresh");
});
