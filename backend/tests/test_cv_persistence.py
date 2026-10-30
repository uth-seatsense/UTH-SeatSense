"""Real SQLAlchemy/PostgreSQL integration in a disposable localhost container."""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import subprocess
import sys
import time
import unittest
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor

from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.engine import URL
import psycopg
from app.db.session import build_engine, build_session_factory
from app.schemas.cv_count import CVCountInput
from app.services.cv_count_service import CVCountService
from app.repositories.cv_count_repository import CVRecordConflict

ROOT = Path(__file__).resolve().parents[2]


def payload(**changes):
    result = dict(session_id=str(uuid4()), camera_id='cam-test', room_id='A101',
                  source_type='video', frame_index=0, timestamp_ms=0,
                  recorded_at='2026-10-30T07:00:00+07:00',people_count=0,
                  tracked_count=0,line_enabled=False)
    result.update(changes)
    return result


class ValidationTests(unittest.TestCase):
    def test_component_configuration_preserves_special_characters(self):
        from app.core.config import Settings
        password='test@:/#?%'
        config=Settings(database_url=None,database_host='db',database_name='testdb',
                        database_user='testuser',database_password=password)
        self.assertEqual(config.connection_url().password,password)
        self.assertNotIn(password,repr(config))
    def test_invalid_inputs(self):
        for changes in [dict(recorded_at='2026-10-30T07:00:00'),dict(people_count=-1),
                        dict(tracked_count=1),dict(timestamp_ms=float('nan')),dict(camera_id=' '),
                        dict(session_id='invalid'),dict(line_enabled=True),dict(people_count=2147483648)]:
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                CVCountInput.model_validate(payload(**changes))

    def test_configuration_has_no_default_credential(self):
        from app.core.config import Settings
        self.assertIsNone(Settings(_env_file=None, database_url=None).database_url)
        with self.assertRaises(ValueError):
            build_engine(None)
        with self.assertRaises(ValueError):
            build_engine('sqlite://')


@unittest.skipUnless(os.environ.get('SEAT24_RUN_DB_TESTS')=='1','Set SEAT24_RUN_DB_TESTS=1 for real PostgreSQL')
class PersistenceTests(unittest.TestCase):
    @classmethod
    def docker(cls,*args):
        result = subprocess.run(['docker',*args],capture_output=True,text=True,timeout=60)
        if result.returncode:
            raise RuntimeError(result.stderr)
        return result.stdout.strip()

    @classmethod
    def setUpClass(cls):
        cls.container = 'seatsense-seat24-backend-' + uuid4().hex[:12]
        password = uuid4().hex
        cls.docker('run','--rm','--detach','--name',cls.container,'-p','127.0.0.1::5432',
                   '-e',f'POSTGRES_PASSWORD={password}','postgres:16.6-alpine')
        try:
            port = int(cls.docker('port',cls.container,'5432/tcp').split(':')[-1])
            for _ in range(60):
                try:
                    with psycopg.connect(host='127.0.0.1',port=port,user='postgres',password=password,dbname='postgres',connect_timeout=1,autocommit=True) as connection:
                        for name in ['001_create_tables.sql','002_cv_count_records.sql']:
                            connection.execute((ROOT/'database/init'/name).read_text(encoding='utf-8'))
                    break
                except psycopg.OperationalError:
                    time.sleep(0.5)
            else:
                raise RuntimeError('PostgreSQL unavailable')
            cls.engine = build_engine(URL.create('postgresql+psycopg',username='postgres',password=password,host='127.0.0.1',port=port,database='postgres'))
            cls.service = CVCountService(build_session_factory(cls.engine))
        except BaseException:
            cls.docker('stop',cls.container)
            raise

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()
        cls.docker('stop',cls.container)

    def setUp(self):
        with self.engine.begin() as connection:
            connection.execute(text('TRUNCATE cv_count_records, rooms RESTART IDENTITY CASCADE'))
            connection.execute(text("INSERT INTO rooms(code,name,capacity) VALUES ('A101','Test room',40)"))

    def test_roundtrip_zero_and_room_mapping(self):
        row = self.service.save(payload())
        self.assertEqual((row.people_count,row.room_id,row.room_code),(0,1,'A101'))
        self.assertEqual(row.recorded_at,datetime(2026,10,30,tzinfo=timezone.utc))
        self.assertEqual(row.received_at.utcoffset().total_seconds(),0)
        self.assertEqual(self.service.latest(camera_id='cam-test').id,row.id)
        self.assertIsNone(self.service.latest(camera_id='missing'))
        for code in ['unknown','1',None]:
            saved = self.service.save(payload(room_id=code))
            self.assertIsNone(saved.room_id)
            self.assertEqual(saved.room_code,code)

    def test_retry_conflict_and_batch_rollback(self):
        original = payload()
        first = self.service.save(original)
        self.assertEqual(first.id,self.service.save(original).id)
        with self.assertRaises(CVRecordConflict):
            self.service.save(dict(original,people_count=2))
        before = len(self.service.history())
        with self.assertRaises(CVRecordConflict):
            self.service.save_many([payload(),dict(original,people_count=3)])
        self.assertEqual(len(self.service.history()),before)
        self.assertEqual(self.service.save(payload()).people_count,0)

    def test_history_filters_ranges_and_pagination(self):
        older = self.service.save(payload(recorded_at='2026-10-29T23:59:00Z'))
        first = self.service.save(payload())
        second = self.service.save(payload())
        self.service.save(payload(camera_id='other',room_id='unknown'))
        self.assertEqual([r.id for r in self.service.history(camera_id='cam-test')],[second.id,first.id,older.id])
        self.assertEqual(self.service.history(camera_id='cam-test',limit=1,offset=1)[0].id,first.id)
        self.assertEqual(len(self.service.history(room_id=1)),3)
        self.assertEqual(len(self.service.history(room_code='unknown')),1)
        self.assertEqual(len(self.service.history(session_id=older.session_id)),1)
        start=datetime(2026,10,29,23,59,tzinfo=timezone.utc)
        end=datetime(2026,10,30,tzinfo=timezone.utc)
        self.assertEqual([r.id for r in self.service.history(start=start,end=end)],[older.id])
        for filters in [dict(limit=0),dict(limit=501),dict(offset=-1),dict(start=datetime(2026,1,1)),dict(start=end,end=start)]:
            with self.assertRaises(ValueError):
                self.service.history(**filters)

    def test_concurrent_identical_retry(self):
        data = payload()
        with ThreadPoolExecutor(max_workers=2) as pool:
            rows = list(pool.map(self.service.save,[data,data]))
        self.assertEqual(rows[0].id,rows[1].id)
        self.assertEqual(len(self.service.history()),1)

    def test_cv_example_and_unknown_room_retry(self):
        sample = json.loads((ROOT/'docs/examples/cv-count-v1.json').read_text(encoding='utf-8'))
        row = self.service.save(sample)
        self.assertEqual(row.people_count,sample['people_count'])
        self.assertEqual(row.estimated_occupancy,sample['estimated_occupancy'])
        self.assertIsNone(row.room_id)
        with self.engine.begin() as connection:
            connection.execute(text('INSERT INTO rooms(code,name,capacity) VALUES (:code,:name,40)'),dict(code=sample['room_id'],name='New room'))
        retry = self.service.save(sample)
        self.assertEqual(retry.id,row.id)
        self.assertIsNone(retry.room_id)

    def test_cli_save_and_history(self):
        environment = dict(os.environ, DATABASE_URL=self.engine.url.render_as_string(hide_password=False))
        saved = subprocess.run([sys.executable,'-m','app.cv_store','save','../docs/examples/cv-count-v1.json'],
                               cwd=ROOT/'backend',env=environment,capture_output=True,text=True,timeout=30)
        self.assertEqual(saved.returncode,0,'CLI save failed')
        row = json.loads(saved.stdout)
        read = subprocess.run([sys.executable,'-m','app.cv_store','history','--camera-id','cam-01'],
                              cwd=ROOT/'backend',env=environment,capture_output=True,text=True,timeout=30)
        self.assertEqual(read.returncode,0,'CLI query failed')
        self.assertEqual(json.loads(read.stdout)[0]['id'],row['id'])


if __name__=='__main__':
    unittest.main()
