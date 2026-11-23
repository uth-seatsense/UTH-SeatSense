import json
import logging
import os
from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)


def send_count_record(payload: dict) -> bool:
    backend_url = os.getenv("BACKEND_URL", "").strip()
    if not backend_url:
        return False

    url = f"{backend_url.rstrip('/')}/api/v1/cv/count-records"
    allowed = {
        "schema_version", "session_id", "camera_id", "room_id", "source_type",
        "frame_index", "timestamp_ms", "recorded_at", "people_count",
        "tracked_count", "line_enabled", "in_count", "out_count",
        "initial_occupancy", "estimated_occupancy", "occupancy_underflow",
    }
    record = {key: value for key, value in payload.items() if key in allowed}
    body = json.dumps({"records": [record]}).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    api_key = os.getenv("CV_API_KEY", "").strip()
    if api_key:
        headers["X-API-Key"] = api_key

    try:
        request = Request(url, data=body, headers=headers, method="POST")
        with urlopen(request, timeout=2) as response:
            return 200 <= response.status < 300
    except Exception as exc:
        logger.warning("Could not send CV count to Backend: %s", exc)
        return False
