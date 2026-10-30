"""Real model integration tests. Set CV_TEST_MODEL and CV_TEST_VIDEO to run."""
import csv
import json
import os
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from app.detection.detector import PersonDetector
from app.services.video_service import process_video


class InputTests(unittest.TestCase):
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
            runs = [process_video(source, folder, detector, annotate=True) for _ in range(2)]
            self.assertNotEqual(runs[0]["session_id"], runs[1]["session_id"])
            all_records = []
            for run in runs:
                output = Path(run["output_dir"])
                records = [json.loads(line) for line in (output / "results.jsonl").read_text().splitlines()]
                all_records.append(records)
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
