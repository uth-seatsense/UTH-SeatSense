import { useEffect, useState } from "react";
import { getApiHealth } from "../services/api.js";

export default function HealthPage() {
  const [result, setResult] = useState({ status: "checking" });

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    const timer = setTimeout(() => controller.abort(), 10_000);

    getApiHealth({ signal: controller.signal })
      .then((data) => {
        if (active) setResult({ status: "success", data });
      })
      .catch((error) => {
        if (active) {
          setResult({
            status: "error",
            message: controller.signal.aborted
              ? "Backend không phản hồi trong 10 giây."
              : error.message,
          });
        }
      })
      .finally(() => clearTimeout(timer));

    return () => {
      active = false;
      clearTimeout(timer);
      controller.abort();
    };
  }, []);

  return (
    <main className="skeleton-page">
      <h1>Health Check</h1>
      <div role="status" aria-live="polite">
        {result.status === "checking" && (
          <p>Đang kiểm tra kết nối backend...</p>
        )}
        {result.status === "success" && (
          <>
            <p>Kết nối backend thành công.</p>
            <pre>{JSON.stringify(result.data, null, 2)}</pre>
          </>
        )}
        {result.status === "error" && (
          <>
            <p>Không thể kết nối backend.</p>
            <p>{result.message}</p>
          </>
        )}
      </div>
    </main>
  );
}
