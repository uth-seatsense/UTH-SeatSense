import json
import os
import unittest
from unittest.mock import patch
from urllib.error import URLError

from app.services.backend_ingest import BackendCountSender, BackendIngestError


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def read(self):
        return b'{}'


class BackendCountSenderTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(
            os.environ,
            {
                "BACKEND_URL": "http://backend:8000/",
                "CV_API_KEY": "test-key",
            },
        )
        self.environment.start()

    def tearDown(self):
        self.environment.stop()

    def record(self, frame_index):
        return {
            "source_type": "webcam",
            "room_id": "A101",
            "frame_index": frame_index,
            "estimated_occupancy": 3,
        }

    @patch("app.services.backend_ingest.urlopen", return_value=FakeResponse())
    def test_sends_live_batches_with_api_key(self, urlopen):
        sender = BackendCountSender()

        sender.add(self.record(1))
        self.assertEqual(urlopen.call_count, 0)
        sender.add(self.record(2))

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://backend:8000/api/v1/cv/count-records")
        self.assertEqual(request.get_header("X-api-key"), "test-key")
        self.assertEqual(
            json.loads(request.data),
            {"records": [self.record(1), self.record(2)]},
        )
        self.assertEqual(sender.pending, [])

    @patch("app.services.backend_ingest.urlopen", side_effect=URLError("offline"))
    def test_keeps_batch_and_surfaces_backend_failure(self, urlopen):
        sender = BackendCountSender(batch_size=1)

        with self.assertRaisesRegex(BackendIngestError, "Could not send occupancy"):
            sender.add(self.record(1))

        self.assertEqual(len(sender.pending), 1)
        self.assertEqual(urlopen.call_count, 1)

    def test_requires_matching_backend_api_key(self):
        with patch.dict(os.environ, {"CV_API_KEY": ""}):
            with self.assertRaisesRegex(
                RuntimeError, "CV_API_KEY must match the backend"
            ):
                BackendCountSender()
