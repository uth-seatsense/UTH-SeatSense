"""Run from cv/: python run_video.py --model ... --video ..."""
import argparse
import json
import os
import sys

os.environ.setdefault("YOLO_AUTOINSTALL", "false")

from app.detection.detector import PersonDetector
from app.services.video_service import process_video
from app.counting.line_counter import LineConfig


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
    parser.add_argument("--camera-id", default="camera-01")
    parser.add_argument("--room-id")
    parser.add_argument("--line", type=float, nargs=4, metavar=("X1", "Y1", "X2", "Y2"))
    parser.add_argument("--in-direction", choices=["negative-to-positive", "positive-to-negative"], default="negative-to-positive")
    parser.add_argument("--deadband", type=float, default=0.01)
    parser.add_argument("--max-gap-ms", type=float, default=1000)
    parser.add_argument("--cooldown-ms", type=float, default=500)
    parser.add_argument("--initial-occupancy", type=int)
    args = parser.parse_args()
    try:
        line = LineConfig(tuple(args.line[:2]), tuple(args.line[2:]), args.in_direction, args.deadband, args.max_gap_ms, args.cooldown_ms) if args.line else None
        detector = PersonDetector(args.model, args.device, args.confidence, args.image_size)
        result = process_video(args.video, args.output, detector, args.fallback_fps, args.annotate,
                               args.camera_id, args.room_id, line, args.initial_occupancy)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"CV error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
