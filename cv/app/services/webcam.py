"""Browser JPEG frames with a per-session tracker and streaming exports."""
import csv
import json
import time
from datetime import datetime, timezone
from threading import Lock
import cv2
import numpy as np
from app.detection.detector import PersonDetector
from app.detection.tracker import PersonTracker
from app.counting.line_counter import LineCounter
from app.schemas.count_result import CountResult, CrossingEvent


class WebcamSession:
    def __init__(self, manager, job):
        self.lock = Lock()
        self.job = job
        self.options = job['options']
        self.detector = PersonDetector(manager.model, manager.device, self.options['confidence'])
        self.tracker = PersonTracker(10)
        self.counter = LineCounter(self.options['line_config']) if self.options['line_config'] else None
        self.started = time.monotonic()
        self.index = 0
        self.peak = 0
        self.streams = {}
        try:
            for name in ['counts.csv','backend_counts.jsonl','results.jsonl','events.jsonl']:
                self.streams[name] = (job['directory']/name).open('w',encoding='utf-8',newline='')
            self.csv = csv.DictWriter(self.streams['counts.csv'],fieldnames=list(CountResult.model_fields))
            self.csv.writeheader()
        except BaseException:
            for stream in self.streams.values():
                stream.close()
            raise

    def process(self, content):
        frame = cv2.imdecode(np.frombuffer(content,np.uint8),cv2.IMREAD_COLOR)
        if frame is None or max(frame.shape[:2]) > 1920:
            raise ValueError('Frame JPEG khong hop le hoac vuot 1920 pixel')
        start = time.perf_counter()
        timestamp = round((time.monotonic()-self.started)*1000,3)
        boxes = self.detector.detect(frame)
        ids = self.tracker.update(boxes,frame)
        detections = [dict(track_id=ids.get(i),confidence=round(float(score),4),bbox_xyxy=[round(float(v),2) for v in xyxy]) for i,(xyxy,score) in enumerate(zip(boxes.xyxy,boxes.conf)) if float(score)>=self.detector.confidence]
        events = self.counter.update(detections,frame.shape[1],frame.shape[0],timestamp) if self.counter else []
        initial = self.options['initial_occupancy']
        raw = None if initial is None else initial+self.counter.in_count-self.counter.out_count
        payload = CountResult(session_id=self.job['id'],camera_id=self.options['camera_id'],room_id=self.options['room_id'],source_type='webcam',frame_index=self.index,timestamp_ms=timestamp,recorded_at=datetime.now(timezone.utc),people_count=len(detections),tracked_count=sum(d['track_id'] is not None for d in detections),line_enabled=self.counter is not None,in_count=self.counter.in_count if self.counter else None,out_count=self.counter.out_count if self.counter else None,initial_occupancy=initial,estimated_occupancy=None if raw is None else max(0,raw),occupancy_underflow=raw is not None and raw<0).model_dump(mode='json')
        record = dict(payload,detections=detections,frame_width=frame.shape[1],frame_height=frame.shape[0],processing_ms=round((time.perf_counter()-start)*1000,3))
        self.csv.writerow(payload)
        self.streams['backend_counts.jsonl'].write(json.dumps(payload)+'\n')
        self.streams['results.jsonl'].write(json.dumps(record)+'\n')
        for event in events:
            item = CrossingEvent(**event,event_id=f"{self.job['id']}:{self.index}:{event['track_id']}:{event['direction']}",**{key:payload[key] for key in ['session_id','camera_id','room_id','frame_index','timestamp_ms','recorded_at']})
            self.streams['events.jsonl'].write(item.model_dump_json()+'\n')
        self.index += 1
        self.peak = max(self.peak,len(detections))
        return record, events

    def close(self):
        for stream in self.streams.values():
            stream.close()
        summary = dict(session_id=self.job['id'],status='completed',source_type='webcam',frames_processed=self.index,peak_count=self.peak)
        summary.update(camera_id=self.options['camera_id'], room_id=self.options['room_id'],
                       in_count=self.counter.in_count if self.counter else None,
                       out_count=self.counter.out_count if self.counter else None)
        (self.job['directory']/'summary.json').write_text(json.dumps(summary),encoding='utf-8')
        self.detector = None
        self.tracker = None
        return summary
