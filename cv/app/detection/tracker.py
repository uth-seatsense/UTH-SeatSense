"""A fresh ByteTrack instance is created for each video."""
from types import SimpleNamespace


class PersonTracker:
    def __init__(self, fps):
        from ultralytics.trackers.byte_tracker import BYTETracker

        self.tracker = BYTETracker(SimpleNamespace(
            track_high_thresh=0.25, track_low_thresh=0.1,
            new_track_thresh=0.25, track_buffer=max(1, round(fps)),
            match_thresh=0.8, fuse_score=True,
        ))

    def update(self, boxes, frame):
        tracks = self.tracker.update(boxes, frame)
        return {int(track[-1]): int(track[4]) for track in tracks}
