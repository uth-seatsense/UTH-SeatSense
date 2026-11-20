import unittest

from app.counting import LineConfig, LineCounter


def test_counting_modules_are_importable() -> None:
    from app.counting import line_counter, occupancy

    assert line_counter is not None
    assert occupancy is not None


class HostLineCountingTests(unittest.TestCase):
    def test_two_tracks_cross_while_one_lingers_at_line(self):
        counter = LineCounter(LineConfig((0.5, 0), (0.5, 1)))
        frames = [
            (0, (60, 30)),
            (200, (50.5, 40)),
            (400, (49.5, 60)),
            (600, (55, 65)),
            (800, (40, 70)),
            (1000, (35, 70)),
        ]
        crossings = []
        for timestamp, centers in frames:
            detections = [
                {"track_id": track, "confidence": 0.9, "bbox_xyxy": [x-2, 20, x+2, 60]}
                for track, x in enumerate(centers, start=1)
            ]
            crossings.extend(counter.update(detections, 100, 100, timestamp))
        self.assertEqual([(e["track_id"], e["direction"]) for e in crossings],
                         [(2, "OUT"), (1, "IN")])
        self.assertEqual((counter.in_count, counter.out_count), (1, 1))
