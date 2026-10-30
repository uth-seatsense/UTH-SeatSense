import io
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"CV_OUTPUT_DIR": self.temp.name, "CV_MODEL_PATH": str(Path(self.temp.name) / "missing.pt")})
        self.environment.start()
        self.context = TestClient(app)
        self.client = self.context.__enter__()

    def tearDown(self):
        self.context.__exit__(None, None, None)
        self.environment.stop()
        self.temp.cleanup()

    def test_static_health_validation_and_origin(self):
        self.assertEqual(self.client.get('/health').status_code, 200)
        self.assertIn('CV Testing Lab', self.client.get('/').text)
        self.assertEqual(self.client.get('/static/app.js').status_code, 200)
        self.assertFalse(self.client.get('/api/config').json()['model_available'])
        self.assertEqual(self.client.get('/api/jobs/unknown').status_code, 404)
        for options in [dict(confidence=0), dict(line=[0,0,0,0]), dict(initial_occupancy=0), dict(camera_id='')]:
            response=self.client.post('/api/jobs', files={'file':('test.mp4', b'x')}, data={'options':json.dumps(options)})
            self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.post('/api/jobs', files={'file':('x.txt',b'x')}).status_code, 415)
        self.assertEqual(self.client.post('/api/jobs', files={'file':('x.mp4',b'x')}).status_code, 503)
        self.assertEqual(self.client.post('/api/jobs/x/stop',headers={'Origin':'https://other.example'}).status_code,403)

    def test_cancel_busy_and_no_local_path_in_summary(self):
        model=Path(self.temp.name)/'model.pt';model.touch()
        app.state.jobs.model=model
        def processing(source, output, detector, should_stop, **options):
            while not should_stop():
                time.sleep(0.01)
            directory=Path(output)/'result';directory.mkdir()
            for filename in ['counts.csv','backend_counts.jsonl','events.jsonl','results.jsonl']:
                (directory/filename).write_text('')
            return dict(status='cancelled',output_dir=str(directory),frames_processed=0)
        with patch('app.services.jobs.PersonDetector'), patch('app.services.jobs.process_video',side_effect=processing):
            start=self.client.post('/api/jobs',files={'file':('x.mp4',b'video')})
            self.assertEqual(start.status_code,202)
            identity=start.json()['id']
            self.assertEqual(self.client.post('/api/jobs',files={'file':('x.mp4',b'video')}).status_code,409)
            self.assertEqual(self.client.get(f'/api/jobs/{identity}/files/csv').status_code,409)
            self.assertEqual(self.client.post(f'/api/jobs/{identity}/stop').status_code,200)
            state=self.wait(identity)
            self.assertEqual(state['status'],'cancelled')
            self.assertNotIn('output_dir',state['summary'])
            self.assertEqual(self.client.get(f'/api/jobs/{identity}/files/summary').json()['status'],'cancelled')
            self.assertEqual(self.client.get(f'/api/jobs/{identity}/files/csv').status_code,200)
            self.assertEqual(self.client.get(f'/api/jobs/{identity}/files/unknown').status_code,404)
        self.assertFalse(any(Path(self.temp.name).glob('*/input.*')))

    def wait(self, identity):
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            state=self.client.get(f'/api/jobs/{identity}').json()
            if state['status'] in {'completed','cancelled','failed'}:
                return state
            time.sleep(0.03)
        self.fail('Job timed out')

    @unittest.skipUnless(os.environ.get('CV_TEST_MODEL') and os.environ.get('CV_TEST_VIDEO'),'Needs real model/video')
    def test_browser_webcam_frames_and_stop(self):
        import cv2
        app.state.jobs.model=Path(os.environ['CV_TEST_MODEL'])
        start=self.client.post('/api/webcam',json={'camera_id':'test-camera','line':[0.5,0,0.5,1]})
        self.assertEqual(start.status_code,202,start.text)
        identity=start.json()['id']
        self.assertEqual(self.client.post('/api/webcam',json={}).status_code,409)
        self.assertEqual(self.client.post(f'/api/webcam/{identity}/frame',content=b'bad').status_code,422)
        capture=cv2.VideoCapture(os.environ['CV_TEST_VIDEO']);ok,frame=capture.read();capture.release()
        self.assertTrue(ok)
        ok,jpeg=cv2.imencode('.jpg',frame);self.assertTrue(ok)
        for index in range(2):
            response=self.client.post(f'/api/webcam/{identity}/frame',content=jpeg.tobytes())
            self.assertEqual(response.status_code,200,response.text)
            record=response.json()
            self.assertEqual(record['source_type'],'webcam')
            self.assertEqual(record['frame_index'],index)
            self.assertGreater(record['people_count'],0)
        self.assertEqual(self.client.post(f'/api/jobs/{identity}/stop').status_code,200)
        self.assertEqual(self.client.post(f'/api/jobs/{identity}/stop').status_code,200)
        self.assertEqual(self.client.post(f'/api/webcam/{identity}/frame',content=jpeg.tobytes()).status_code,409)
        rows=self.client.get(f'/api/jobs/{identity}/files/jsonl').text.splitlines()
        self.assertEqual(len(rows),2)
        self.assertEqual(json.loads(rows[0])['source_type'],'webcam')

    @unittest.skipUnless(os.environ.get('CV_TEST_MODEL') and os.environ.get('CV_TEST_VIDEO'),'Needs real model/video')
    def test_real_video_upload_preview_and_exports(self):
        app.state.jobs.model=Path(os.environ['CV_TEST_MODEL'])
        with Path(os.environ['CV_TEST_VIDEO']).open('rb') as video:
            start=self.client.post('/api/jobs',files={'file':('sample.mp4',video,'video/mp4')},data={'options':json.dumps(dict(line=[0.5,0,0.5,1],initial_occupancy=0))})
        self.assertEqual(start.status_code,202,start.text)
        identity=start.json()['id'];state=self.wait(identity)
        self.assertEqual(state['status'],'completed',state)
        self.assertEqual(state['frames_processed'],50)
        self.assertTrue(state['frame_image'])
        self.assertEqual(state['latest']['frame_index'],49)
        self.assertEqual(self.client.get(f'/api/jobs/{identity}/preview').headers['content-type'],'image/jpeg')
        for kind in ['csv','jsonl','debug','events','summary']:
            response=self.client.get(f'/api/jobs/{identity}/files/{kind}')
            self.assertEqual(response.status_code,200)
        records=self.client.get(f'/api/jobs/{identity}/files/jsonl').text.splitlines()
        self.assertEqual(len(records),50)
        self.assertNotIn('detections',json.loads(records[0]))
        self.assertFalse(any(Path(self.temp.name).glob('*/input.*')))


if __name__=='__main__':
    unittest.main()
