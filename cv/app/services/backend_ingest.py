"""Send live webcam occupancy batches to the SeatSense backend."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class BackendIngestConfigurationError(RuntimeError):
    pass


class BackendIngestError(RuntimeError):
    pass


class BackendCountSender:
    def __init__(self, *, batch_size: int = 2, timeout: float = 3.0):
        self.backend_url = os.environ.get("BACKEND_URL", "").strip().rstrip("/")
        self.api_key = os.environ.get("CV_API_KEY", "").strip()
        self.batch_size = batch_size
        self.timeout = timeout
        self.pending: list[dict] = []
        if self.backend_url and not self.api_key:
            raise BackendIngestConfigurationError(
                "CV_API_KEY must match the backend CV_INGEST_API_KEY"
            )

    @property
    def enabled(self) -> bool:
        return bool(self.backend_url)

    def add(self, record: dict) -> None:
        if not self.enabled:
            return
        if record.get("source_type") != "webcam":
            raise ValueError("Only webcam records can update live occupancy")
        if not record.get("room_id"):
            raise ValueError("Enter a room code to sync live occupancy")
        if record.get("estimated_occupancy") is None:
            raise ValueError("Enter the verified initial occupancy to sync live data")
        self.pending.append(record)
        if len(self.pending) >= self.batch_size:
            self.flush()

    def flush(self) -> None:
        if not self.enabled or not self.pending:
            return
        request = Request(
            f"{self.backend_url}/api/v1/cv/count-records",
            data=json.dumps({"records": self.pending}).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                if response.status != 200:
                    raise BackendIngestError(
                        f"Backend rejected occupancy data (HTTP {response.status})"
                    )
                response.read()
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise BackendIngestError(
                f"Backend rejected occupancy data (HTTP {exc.code}): {detail}"
            ) from exc
        except URLError as exc:
            raise BackendIngestError(
                f"Could not send occupancy data to backend: {exc.reason}"
            ) from exc
        self.pending.clear()
