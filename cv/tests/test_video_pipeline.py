"""Real model integration tests. Set CV_TEST_MODEL and CV_TEST_VIDEO to run."""
import csv
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from pathlib import Path

import cv2
import numpy as np

from app.detection.detector import PersonDetector
from app.services.video_service import process_video
from app.counting.line_counter import LineConfig
from app.schemas.count_result import CountResult, CrossingEvent


class InputTests(unittest.TestCase):
    def test_crossing_events_are_exported_end_to_end(self):
        class Detector:
            confidence = 0.32
            def __init__(self):
                self.positions = iter([60, 40, 40, 60])
            def detect(self, frame):
                x = next(self.positions)
                return SimpleNamespace(xyxy=np.array([[x-2, 30, x+2, 50]]), conf=np.array([0.9]))
        with tempfile.TemporaryDirectory() as folder:
            video = Path(folder) / "crossing.mp4"
            writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"mp4v"), 2, (100, 100))
            self.assertTrue(writer.isOpened())
            for _ in range(4):
                writer.write(np.zeros((100, 100, 3), dtype=np.uint8))
            writer.release()
            with patch("app.services.video_service.PersonTracker") as tracker:
                tracker.return_value.update.return_value = {0: 1}
                run = process_video(video, folder, Detector(), line_config=LineConfig((0.5, 0), (0.5, 1)), initial_occupancy=2)
            output = Path(run["output_dir"])
            events = [CrossingEvent.model_validate_json(line) for line in (output / "events.jsonl").read_text().splitlines()]
            self.assertEqual([e.direction for e in events], ["IN", "OUT"])
            self.assertEqual([e.timestamp_ms for e in events], [500, 1500])
            self.assertEqual(len({e.event_id for e in events}), 2)
            self.assertEqual((run["in_count"], run["out_count"], run["estimated_occupancy"]), (1, 1, 2))

    def test_missing_model(self):
        with self.assertRaises(FileNotFoundError):
            PersonDetector("missing-model.pt")

    def test_missing_video(self):
        with self.assertRaises(FileNotFoundError):
            process_video("missing-video.mp4", "unused", None)

    def test_invalid_video(self):
        with tempfile.TemporaryDirectory() as folder:
            video = Path(folder) / "invalid.mp4"
            video.write_bytes(b"not a video")
            with self.assertRaises(ValueError):
                process_video(video, folder, None)


@unittest.skipUnless(os.environ.get("CV_TEST_MODEL") and os.environ.get("CV_TEST_VIDEO"), "Set CV_TEST_MODEL and CV_TEST_VIDEO for real inference")
class RealPipelineTests(unittest.TestCase):
    def test_detection_tracking_exports_and_fresh_session(self):
        detector = PersonDetector(os.environ["CV_TEST_MODEL"])
        capture = cv2.VideoCapture(os.environ["CV_TEST_VIDEO"])
        frames = []
        try:
            for _ in range(16):
                ok, frame = capture.read()
                self.assertTrue(ok)
                frames.append(frame)
        finally:
            capture.release()
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "input.mp4"
            height, width = frames[0].shape[:2]
            writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"mp4v"), 10, (width, height))
            self.assertTrue(writer.isOpened())
            for frame in frames + [np.zeros_like(frames[0])] * 4:
                writer.write(frame)
            writer.release()
            runs = [process_video(source, folder, detector, annotate=True,
                                  camera_id="test-cam", room_id="test-room",
                                  line_config=LineConfig((0.5, 0), (0.5, 1)), initial_occupancy=0) for _ in range(2)]
            self.assertNotEqual(runs[0]["session_id"], runs[1]["session_id"])
            all_records = []
            for run in runs:
                output = Path(run["output_dir"])
                records = [json.loads(line) for line in (output / "results.jsonl").read_text().splitlines()]
                all_records.append(records)
                backend = [CountResult.model_validate_json(line) for line in (output / "backend_counts.jsonl").read_text().splitlines()]
                self.assertEqual(len(backend), 20)
                self.assertEqual(backend[0].in_count, 0)
                self.assertEqual(backend[0].out_count, 0)
                self.assertTrue(all("detections" not in item.model_dump() for item in backend))
                events = [CrossingEvent.model_validate_json(line) for line in (output / "events.jsonl").read_text().splitlines()]
                self.assertEqual(run["in_count"], sum(event.direction == "IN" for event in events))
                self.assertEqual(run["out_count"], sum(event.direction == "OUT" for event in events))
                self.assertEqual(len(records), 20)
                self.assertTrue(any(r["people_count"] > 0 for r in records[:16]))
                self.assertTrue(any(r["tracked_count"] > 0 for r in records[:16]))
                self.assertTrue(all(r["people_count"] == 0 for r in records[-4:]))
                self.assertEqual(records[0]["timestamp_ms"], 0)
                self.assertEqual(records[-1]["timestamp_ms"], 1900)
                self.assertTrue(all(r["tracked_count"] <= r["people_count"] for r in records))
                self.assertTrue(all(r["people_count"] == len(r["detections"]) for r in records))
                with (output / "counts.csv").open(newline="") as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual([int(r["people_count"]) for r in rows], [r["people_count"] for r in records])
                annotated = cv2.VideoCapture(str(output / "annotated.mp4"))
                count = 0
                while annotated.read()[0]:
                    count += 1
                annotated.release()
                self.assertEqual(count, 20)
            self.assertEqual([r["people_count"] for r in all_records[0]], [r["people_count"] for r in all_records[1]])


if __name__ == "__main__":
    unittest.main()
