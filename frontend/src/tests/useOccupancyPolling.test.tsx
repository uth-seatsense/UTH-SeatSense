import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  getPollingIntervalMs,
  useOccupancyPolling,
} from "../hooks/useOccupancyPolling";

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllEnvs();
});

describe("useOccupancyPolling", () => {
  it("uses the configured polling interval", () => {
    vi.stubEnv("VITE_POLL_INTERVAL_MS", "3000");
    expect(getPollingIntervalMs()).toBe(3000);
  });

  it("falls back when the configured interval is outside the 3–5 second range", () => {
    vi.stubEnv("VITE_POLL_INTERVAL_MS", "6000");
    expect(getPollingIntervalMs()).toBe(3000);
  });

  it("polls automatically and stops interval on unmount", async () => {
    vi.useFakeTimers();
    vi.stubEnv("VITE_POLL_INTERVAL_MS", "3000");
    const fetchSnapshot = vi.fn(async () => ({ count: 48 }));

    const { result, unmount } = renderHook(() =>
      useOccupancyPolling(fetchSnapshot),
    );

    await act(async () => {
      await vi.advanceTimersByTimeAsync(3000);
    });

    expect(fetchSnapshot).toHaveBeenCalledTimes(2);
    expect(result.current.data).toEqual({ count: 48 });

    unmount();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(6000);
    });
    expect(fetchSnapshot).toHaveBeenCalledTimes(2);
  });

  it("does not start another request while the previous poll is pending", async () => {
    vi.useFakeTimers();
    vi.stubEnv("VITE_POLL_INTERVAL_MS", "3000");
    let resolveSnapshot!: (value: { count: number }) => void;
    const fetchSnapshot = vi.fn(
      () =>
        new Promise<{ count: number }>((resolve) => {
          resolveSnapshot = resolve;
        }),
    );

    const { unmount } = renderHook(() => useOccupancyPolling(fetchSnapshot));
    await act(async () => {
      await vi.advanceTimersByTimeAsync(9000);
    });
    expect(fetchSnapshot).toHaveBeenCalledTimes(1);

    await act(async () => {
      resolveSnapshot({ count: 48 });
    });
    unmount();
  });
});
