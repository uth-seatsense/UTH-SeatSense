import unittest
from pydantic import ValidationError
from app.counting.line_counter import LineConfig, LineCounter
from app.schemas.count_result import CountResult


def detection(x, y=0.5, identity=1):
    return {"track_id": identity, "confidence": 0.9, "bbox_xyxy": [x * 100 - 2, y * 100 - 10, x * 100 + 2, y * 100]}


class LineTests(unittest.TestCase):
    def setUp(self):
        # Downward vertical line: right is negative, left is positive.
        self.counter = LineCounter(LineConfig((0.5, 0.2), (0.5, 0.8)))

    def move(self, x, time, y=0.5, identity=1):
        return self.counter.update([detection(x, y, identity)], 100, 100, time)

    def test_both_directions_and_cooldown(self):
        self.assertEqual(self.move(0.6, 0), [])
        self.assertEqual(self.move(0.4, 100)[0]["direction"], "IN")
        self.assertEqual(self.move(0.6, 200), [])
        self.move(0.4, 700)
        self.assertEqual(self.move(0.6, 1300)[0]["direction"], "OUT")
        self.assertEqual((self.counter.in_count, self.counter.out_count), (2, 1))

    def test_deadband_does_not_count_jitter(self):
        self.move(0.6, 0)
        for time, x in enumerate([0.505, 0.495, 0.501, 0.6], 1):
            self.assertEqual(self.move(x, time * 100), [])
        self.assertEqual(self.counter.in_count, 0)

    def test_crossing_beyond_endpoint_is_ignored(self):
        self.move(0.6, 0, y=0.95)
        self.assertEqual(self.move(0.4, 100, y=0.95), [])

    def test_missing_track_expires_and_new_identity_does_not_cross(self):
        self.move(0.6, 0)
        self.assertEqual(self.move(0.4, 1100), [])
        self.assertEqual(self.move(0.6, 1200, identity=2), [])
        self.assertEqual(self.move(0.4, 1300, identity=None), [])

    def test_reverse_direction(self):
        counter = LineCounter(LineConfig((0.5, 0), (0.5, 1), in_direction="positive-to-negative"))
        counter.update([detection(0.6)], 100, 100, 0)
        events = counter.update([detection(0.4)], 100, 100, 100)
        self.assertEqual(events[0]["direction"], "OUT")

    def test_config_validation(self):
        for start, end in [((0, 0), (0, 0)), ((-1, 0), (1, 1)), ((float('nan'), 0), (1, 1))]:
            with self.assertRaises(ValueError):
                LineConfig(start, end)


class ContractTests(unittest.TestCase):
    def payload(self, **changes):
        data = dict(session_id="test", camera_id="cam-01", frame_index=0, timestamp_ms=0,
                    recorded_at="2026-10-30T00:00:00Z", people_count=0, tracked_count=0, line_enabled=False)
        data.update(changes)
        return data

    def test_zero_and_no_line_are_valid(self):
        data = CountResult(**self.payload()).model_dump(mode="json")
        self.assertEqual(data["people_count"], 0)
        self.assertIsNone(data["estimated_occupancy"])

    def test_invalid_payloads(self):
        for changes in [dict(people_count=-1), dict(tracked_count=1), dict(recorded_at="2026-10-30T00:00:00"), dict(timestamp_ms=float('nan')), dict(line_enabled=True), dict(in_count=0), dict(camera_id=""), dict(unknown=1)]:
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                CountResult(**self.payload(**changes))

    def test_underflow_is_flagged_and_clamped(self):
        CountResult(**self.payload(line_enabled=True, in_count=0, out_count=1,
                                  initial_occupancy=0, estimated_occupancy=0, occupancy_underflow=True))
        with self.assertRaises(ValidationError):
            CountResult(**self.payload(line_enabled=True, in_count=0, out_count=1,
                                      initial_occupancy=0, estimated_occupancy=0))


if __name__ == "__main__":
    unittest.main()
