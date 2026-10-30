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
from app.counting.line_counter import LineCounter
from app.schemas.count_result import CountResult, CrossingEvent


def process_video(source, output_root, detector, fallback_fps=None, annotate=False,
                  camera_id="camera-01", room_id=None, line_config=None, initial_occupancy=None):
    if initial_occupancy is not None and (initial_occupancy < 0 or line_config is None):
        raise ValueError("Nonnegative initial occupancy requires a counting line")
    CountResult(session_id="validation", camera_id=camera_id, room_id=room_id,
                frame_index=0, timestamp_ms=0, recorded_at=datetime.now(timezone.utc),
                people_count=0, tracked_count=0, line_enabled=False)
    counter = LineCounter(line_config) if line_config else None
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
        fields = list(CountResult.model_fields)
        peak = 0
        index = 0
        with (output / "results.jsonl").open("w", encoding="utf-8") as jsonl, (output / "counts.csv").open("w", newline="", encoding="utf-8") as csv_file, (output / "backend_counts.jsonl").open("w", encoding="utf-8") as backend_file, (output / "events.jsonl").open("w", encoding="utf-8") as event_file:
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
                events = counter.update(detections, frame.shape[1], frame.shape[0], record["timestamp_ms"]) if counter else []
                raw = None if initial_occupancy is None else initial_occupancy + counter.in_count - counter.out_count
                payload = CountResult(
                    **{key: record[key] for key in ("session_id", "frame_index", "timestamp_ms", "recorded_at", "people_count", "tracked_count")},
                    camera_id=camera_id, room_id=room_id, line_enabled=counter is not None,
                    in_count=counter.in_count if counter else None,
                    out_count=counter.out_count if counter else None,
                    initial_occupancy=initial_occupancy,
                    estimated_occupancy=None if raw is None else max(0, raw),
                    occupancy_underflow=raw is not None and raw < 0,
                ).model_dump(mode="json")
                record.update(payload)
                backend_file.write(json.dumps(payload) + "\n")
                for event in events:
                    event_payload = CrossingEvent(
                        **event, event_id=f"{session_id}:{index}:{event['track_id']}:{event['direction']}",
                        **{key: payload[key] for key in ("session_id", "camera_id", "room_id", "frame_index", "timestamp_ms", "recorded_at")},
                    )
                    event_file.write(event_payload.model_dump_json() + "\n")
                jsonl.write(json.dumps(record) + "\n")
                csv_writer.writerow({key: record[key] for key in fields})
                peak = max(peak, record["people_count"])
                if annotate:
                    if writer is None:
                        writer = cv2.VideoWriter(str(output / "annotated.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), fps, (frame.shape[1], frame.shape[0]))
                        if not writer.isOpened():
                            raise RuntimeError("Cannot create annotated MP4")
                    writer.write(annotate_frame(frame, record, line_config))
                index += 1
        if not index:
            raise ValueError("Video contains no decodable frames")
        summary = {"session_id": session_id, "frames_processed": index, "source_fps": fps, "peak_count": peak, "output_dir": str(output), "status": "completed"}
        from dataclasses import asdict
        summary.update(schema_version="1.0", camera_id=camera_id, room_id=room_id,
                       line_config=asdict(line_config) if line_config else None,
                       in_count=counter.in_count if counter else None,
                       out_count=counter.out_count if counter else None,
                       initial_occupancy=initial_occupancy,
                       estimated_occupancy=payload["estimated_occupancy"],
                       occupancy_underflow=payload["occupancy_underflow"])
        (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary
    finally:
        capture.release()
        if writer is not None:
            writer.release()


def annotate_frame(frame, record, line_config=None):
    image = frame.copy()
    if line_config:
        height, width = image.shape[:2]
        start, end = [tuple(int(v * scale) for v, scale in zip(point, (width, height))) for point in (line_config.start, line_config.end)]
        cv2.arrowedLine(image, start, end, (255, 200, 0), 2)
        cv2.putText(image, f"IN: {record['in_count']} OUT: {record['out_count']}", (15, 55), cv2.FONT_HERSHEY_SIMPLEX, .6, (255, 200, 0), 2)
    for item in record["detections"]:
        x1, y1, x2, y2 = map(int, item["bbox_xyxy"])
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 220, 100), 2)
        identity = item["track_id"] if item["track_id"] is not None else "new"
        cv2.putText(image, f"person #{identity} {item['confidence']:.0%}", (x1, max(20, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 220, 100), 1)
    cv2.putText(image, f"People: {record['people_count']} | {record['timestamp_ms']/1000:.2f}s", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, .65, (0, 255, 255), 2)
    return image
