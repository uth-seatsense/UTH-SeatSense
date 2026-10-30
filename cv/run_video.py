"""Run from cv/: python run_video.py --model ... --video ..."""
import argparse
import json
import os
import sys

os.environ.setdefault("YOLO_AUTOINSTALL", "false")

from app.detection.detector import PersonDetector
from app.services.video_service import process_video


def main():
    parser = argparse.ArgumentParser(description="Offline YOLOv8 + ByteTrack person counting")
    parser.add_argument("--model", default=os.environ.get("CV_MODEL_PATH", "models/best.pt"))
    parser.add_argument("--video", required=True)
    parser.add_argument("--output", default="outputs")
    parser.add_argument("--device", default=os.environ.get("CV_DEVICE", "cpu"))
    parser.add_argument("--confidence", type=float, default=0.32)
    parser.add_argument("--image-size", type=int, default=640)
    parser.add_argument("--fallback-fps", type=float)
    parser.add_argument("--annotate", action="store_true")
    args = parser.parse_args()
    try:
        detector = PersonDetector(args.model, args.device, args.confidence, args.image_size)
        result = process_video(args.video, args.output, detector, args.fallback_fps, args.annotate)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"CV error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
