import { useEffect, useState } from "react";

export function getPollingIntervalMs(): number {
  const configured = Number(import.meta.env.VITE_POLL_INTERVAL_MS);
  return Number.isInteger(configured) &&
    configured >= 3000 &&
    configured <= 5000
    ? configured
    : 3000;
}

export function useOccupancyPolling<T>(
  fetchSnapshot: (signal: AbortSignal) => Promise<T>,
) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    let intervalId: number | null = null;
    let hasLoaded = false;
    let requestInFlight = false;

    async function poll() {
      if (!active || requestInFlight) return;
      requestInFlight = true;
      if (active) {
        setIsLoading(!hasLoaded);
        setIsRefreshing(hasLoaded);
      }
      try {
        const result = await fetchSnapshot(controller.signal);
        if (active) {
          setData(result);
          setError("");
        }
      } catch (pollError) {
        if (active && (pollError as { name?: string }).name !== "AbortError") {
          setError(
            (pollError as { message?: string }).message ||
              "Không thể kết nối đến máy chủ.",
          );
        }
      } finally {
        requestInFlight = false;
        if (active) {
          hasLoaded = true;
          setIsLoading(false);
          setIsRefreshing(false);
        }
      }
    }

    poll();
    intervalId = window.setInterval(poll, getPollingIntervalMs());

    return () => {
      active = false;
      controller.abort();
      if (intervalId !== null) window.clearInterval(intervalId);
    };
  }, [fetchSnapshot]);

  return { data, isLoading, isRefreshing, error };
}
