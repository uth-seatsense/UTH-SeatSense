"""One local inference job at a time; bounded UI snapshots, disk exports."""
import logging
import base64
import os
import threading
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor

import cv2

from app.detection.detector import PersonDetector
from app.services.video_service import process_video

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]


class Jobs:
    def __init__(self):
        self.root = Path(os.environ.get("CV_OUTPUT_DIR", ROOT / "outputs"))
        self.model = Path(os.environ.get("CV_MODEL_PATH", ROOT / "models/best.pt"))
        self.device = os.environ.get("CV_DEVICE", "cpu")
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.lock = threading.Lock()
        self.slot = threading.Lock()
        self.jobs = {}

    def reserve(self, options):
        if not self.model.is_file():
            raise FileNotFoundError("Chua co model. Tai best.pt va dat vao cv/models/.")
        if not self.slot.acquire(blocking=False):
            raise RuntimeError("Mot video dang xu ly. Hay dung hoac cho hoan tat.")
        try:
            identity = str(uuid4())
            directory = self.root / identity
            directory.mkdir(parents=True, exist_ok=False)
            job = dict(id=identity, status="uploading", latest=None, events=[], preview=None,
                       summary=None, error=None, stop=threading.Event(), directory=directory,
                       options=options, frames_processed=0)
            with self.lock:
                if len(self.jobs) >= 20:
                    # Only metadata is evicted; completed files remain local.
                    self.jobs.pop(next(iter(self.jobs)))
                self.jobs[identity] = job
            return job
        except BaseException:
            self.slot.release()
            raise

    def snapshot(self, identity):
        with self.lock:
            job = self.jobs[identity]
            snapshot = {key: job[key] for key in ("id", "status", "latest", "events", "summary", "error", "frames_processed")}
            snapshot["frame_image"] = base64.b64encode(job["preview"]).decode("ascii") if job["preview"] else None
            return snapshot

    def submit(self, job, source):
        self.pool.submit(self.run, job, source)

    def run(self, job, source):
        try:
            with self.lock:
                job["status"] = "loading"
            detector = PersonDetector(self.model, self.device, job["options"].pop("confidence"))
            def frame_ready(record, frame, events):
                # Unannotated JPEG lets UI independently toggle bbox, IDs and line.
                scale = min(1, 1280 / max(frame.shape[:2]))
                preview = cv2.resize(frame, None, fx=scale, fy=scale) if scale < 1 else frame
                ok, jpeg = cv2.imencode(".jpg", preview, [cv2.IMWRITE_JPEG_QUALITY, 80])
                with self.lock:
                    job.update(status="processing", latest=record, frames_processed=record["frame_index"] + 1)
                    job["events"] = (job["events"] + [dict(event, timestamp_ms=record["timestamp_ms"]) for event in events])[-100:]
                    if ok:
                        job["preview"] = jpeg.tobytes()
            summary = process_video(source, job["directory"], detector,
                                    on_frame=frame_ready, should_stop=job["stop"].is_set,
                                    **job["options"])
            output = Path(summary.pop("output_dir"))
            with self.lock:
                job.update(status=summary["status"], summary=summary, output=output)
        except Exception:
            logger.exception("CV job failed")
            with self.lock:
                job.update(status="failed", error="Khong xu ly duoc video. Kiem tra model, video va cau hinh; xem log dich vu de biet chi tiet.")
        finally:
            source.unlink(missing_ok=True)
            self.slot.release()

    def shutdown(self):
        with self.lock:
            for job in self.jobs.values():
                job["stop"].set()
        self.pool.shutdown(wait=True)
        for job in self.jobs.values():
            if job.get('live') and job['status'] not in {'completed','failed'}:
                with job['live'].lock:
                    job['live'].close()
