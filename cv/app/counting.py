"""SEAT-52: count crossings from a local video, host webcam or RTSP stream."""
import argparse
import math
import os
from pathlib import Path
from time import monotonic

# Keep app.counting.line_counter and app.counting.occupancy importable.
__path__ = [str(Path(__file__).with_suffix(""))]
from app.counting.line_counter import LineConfig, LineCounter


def count_source(source, config, model, device):
    import cv2
    from app.detection.detector import PersonDetector
    from app.detection.tracker import PersonTracker

    fps = float(config["target_fps"])
    if not 3 <= fps <= 5:
        raise ValueError("target_fps must be between 3 and 5")
    counter = LineCounter(LineConfig(**config["line"]))
    detector = PersonDetector(model, device, config["confidence"], config["image_size"])
    live = isinstance(source, int) or source.startswith(("rtsp://", "rtsps://"))
    capture = cv2.VideoCapture(source)
    try:
        if not capture.isOpened():
            raise OSError("Cannot open the selected video source")
        source_fps = capture.get(cv2.CAP_PROP_FPS)
        if not live and not (math.isfinite(source_fps) and source_fps > 0):
            raise ValueError("Video does not provide valid FPS")
        tracker = PersonTracker(fps if live else min(source_fps, fps))
        started = monotonic()
        frame_index = 0
        next_sample = 0
        while True:
            ok, frame = capture.read()
            if not ok:
                if live or frame_index == 0:
                    raise OSError("Source stopped delivering frames")
                break
            seconds = monotonic() - started if live else frame_index / source_fps
            frame_index += 1
            slot = math.floor(seconds * fps + 1e-9)
            if slot < next_sample:
                continue
            next_sample = slot + 1
            boxes = detector.detect(frame)
            ids = tracker.update(boxes, frame)
            detections = [
                dict(track_id=ids.get(i), confidence=float(score), bbox_xyxy=box)
                for i, (box, score) in enumerate(zip(boxes.xyxy, boxes.conf))
                if float(score) >= detector.confidence
            ]
            events = counter.update(detections, frame.shape[1], frame.shape[0], seconds * 1000)
            if events:
                print(f"IN={counter.in_count} OUT={counter.out_count}", flush=True)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        capture.release()
    print(f"Total IN={counter.in_count} OUT={counter.out_count}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/line_config.example.yaml"))
    parser.add_argument("--source", default="sample")
    parser.add_argument("--model", default=os.getenv("CV_MODEL_PATH", "models/best.pt"))
    args = parser.parse_args()
    import yaml  # Installed with the project's Ultralytics dependency.
    try:
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        source = config["sources"][args.source]
        count_source(source, config, args.model, os.getenv("CV_DEVICE", "cpu"))
    except (KeyError, OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        parser.exit(1, f"CV error: {exc}\n")


if __name__ == "__main__":
    main()
