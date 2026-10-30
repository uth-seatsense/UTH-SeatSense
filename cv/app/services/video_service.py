"""Sequential offline video processing and bounded-memory exports."""
import csv
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import cv2

from app.counting.occupancy import count_people
from app.detection.tracker import PersonTracker


def process_video(source, output_root, detector, fallback_fps=None, annotate=False):
    source = Path(source)
    if not source.is_file():
        raise FileNotFoundError(f"Video not found: {source}")
    capture = cv2.VideoCapture(str(source))
    writer = None
    try:
        if not capture.isOpened():
            raise ValueError(f"Cannot open video: {source}")
        fps = capture.get(cv2.CAP_PROP_FPS)
        if not math.isfinite(fps) or fps <= 0:
            fps = fallback_fps
        if fps is None or not math.isfinite(fps) or fps <= 0:
            raise ValueError("Video FPS unavailable; provide --fallback-fps")
        tracker = PersonTracker(fps)
        session_id = str(uuid4())
        output = Path(output_root) / session_id
        output.mkdir(parents=True, exist_ok=False)
        fields = ["session_id", "frame_index", "timestamp_ms", "recorded_at", "people_count", "tracked_count", "processing_ms"]
        peak = 0
        index = 0
        with (output / "results.jsonl").open("w", encoding="utf-8") as jsonl, (output / "counts.csv").open("w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fields)
            csv_writer.writeheader()
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                started = time.perf_counter()
                boxes = detector.detect(frame)
                identities = tracker.update(boxes, frame)
                detections = []
                for position, (xyxy, score) in enumerate(zip(boxes.xyxy, boxes.conf)):
                    if float(score) < detector.confidence:
                        continue
                    detections.append({"track_id": identities.get(position), "confidence": round(float(score), 4), "bbox_xyxy": [round(float(v), 2) for v in xyxy]})
                record = {
                    "session_id": session_id, "frame_index": index,
                    "timestamp_ms": round(index * 1000 / fps, 3),
                    "recorded_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                    "people_count": count_people(detections),
                    "tracked_count": sum(d["track_id"] is not None for d in detections),
                    "processing_ms": round((time.perf_counter() - started) * 1000, 3),
                    "frame_width": frame.shape[1], "frame_height": frame.shape[0],
                    "detections": detections,
                }
                jsonl.write(json.dumps(record) + "\n")
                csv_writer.writerow({key: record[key] for key in fields})
                peak = max(peak, record["people_count"])
                if annotate:
                    if writer is None:
                        writer = cv2.VideoWriter(str(output / "annotated.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), fps, (frame.shape[1], frame.shape[0]))
                        if not writer.isOpened():
                            raise RuntimeError("Cannot create annotated MP4")
                    writer.write(annotate_frame(frame, record))
                index += 1
        if not index:
            raise ValueError("Video contains no decodable frames")
        summary = {"session_id": session_id, "frames_processed": index, "source_fps": fps, "peak_count": peak, "output_dir": str(output), "status": "completed"}
        (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary
    finally:
        capture.release()
        if writer is not None:
            writer.release()


def annotate_frame(frame, record):
    image = frame.copy()
    for item in record["detections"]:
        x1, y1, x2, y2 = map(int, item["bbox_xyxy"])
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 220, 100), 2)
        identity = item["track_id"] if item["track_id"] is not None else "new"
        cv2.putText(image, f"person #{identity} {item['confidence']:.0%}", (x1, max(20, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 220, 100), 1)
    cv2.putText(image, f"People: {record['people_count']} | {record['timestamp_ms']/1000:.2f}s", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, .65, (0, 255, 255), 2)
    return image
