"""SEAT-24: original Compose + isolated overrides, real Backend/PostgreSQL.

Requires Docker Compose >=2.24.4 (!override support). No CV/GPU build needed.
Set SEAT24_RUN_COMPOSE_TESTS=1; temporary projects/volumes are removed afterward.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.environ.get('SEAT24_RUN_COMPOSE_TESTS')=='1','Set SEAT24_RUN_COMPOSE_TESTS=1')
class ComposePersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='seat24-compose-')
        cls.password = uuid4().hex + '@:/#?%'
        cls.environment = dict(os.environ,POSTGRES_PASSWORD=cls.password,
                               POSTGRES_DB='seatsense',POSTGRES_USER='seatsense')
        cls.envfile = Path(cls.temp.name)/'empty.env'
        cls.envfile.write_text('',encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setup_project(self, legacy):
        self.project = 'seat24-check-' + uuid4().hex[:12]
        overlay = Path(self.temp.name)/(self.project+'.yaml')
        volume = ''
        if legacy:
            baseline = (ROOT/'database/init/001_create_tables.sql').as_posix()
            migration = (ROOT/'database/init/002_cv_count_records.sql').as_posix()
            volume = '\n    volumes: !override\n      - postgres_data:/var/lib/postgresql/data\n      - '+json.dumps(baseline+':/docker-entrypoint-initdb.d/001_create_tables.sql:ro')+'\n      - '+json.dumps(migration+':/migrations/002.sql:ro')
        overlay.write_text('services:\n  db:\n    ports: !reset []\n    restart: "no"'+volume+'\n  backend:\n    ports: !reset []\n',encoding='utf-8')
        self.command = ['docker','compose','--project-name',self.project,'--env-file',str(self.envfile),
                        '-f',str(ROOT/'docker-compose.yml'),'-f',str(overlay)]
        self.addCleanup(self.cleanup_project)

    def compose(self,*args,input=None,success=True):
        result = subprocess.run(self.command+list(args),cwd=ROOT,env=self.environment,
                                input=input,text=True,encoding='utf-8',capture_output=True,timeout=900)
        if success and result.returncode:
            message=(result.stderr or result.stdout).replace(self.password,'[redacted]')
            self.fail(message)
        if not success:
            self.assertNotEqual(result.returncode,0)
        return result.stdout.strip()

    def cleanup_project(self):
        # This is exclusively our generated project, never the user's project.
        if not self.project.startswith('seat24-check-'):
            raise RuntimeError('Unsafe cleanup project')
        self.compose('down','--volumes','--remove-orphans')

    def sql(self, statement):
        return self.compose('exec','-T','db','sh','-c',
                            'psql -X -v ON_ERROR_STOP=1 -At -U "$POSTGRES_USER" -d "$POSTGRES_DB"',input=statement)

    def test_fresh_database_bootstrap(self):
        self.setup_project(legacy=False)
        self.compose('up','-d','--wait','--wait-timeout','120','db')
        self.assertEqual(self.sql("SELECT version FROM schema_migrations WHERE version='002_cv_count_records';"),'002_cv_count_records')
        self.assertEqual(self.sql("SELECT version FROM schema_migrations WHERE version='009_add_email_otp_auth';"),'009_add_email_otp_auth')
        self.assertEqual(self.sql("SELECT version FROM schema_migrations WHERE version='010_cv_count_event_uuid';"),'010_cv_count_event_uuid')
        self.assertEqual(self.sql("SELECT version FROM schema_migrations WHERE version='011_normalize_room_types';"),'011_normalize_room_types')
        self.assertEqual(self.sql("SELECT version FROM schema_migrations WHERE version='012_seed_campuses_and_rooms';"),'012_seed_campuses_and_rooms')
        self.assertEqual(self.sql("SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('email_otp_challenges','auth_sessions');"),'2')
        self.assertEqual(self.sql("SELECT count(*) FROM cv_count_records;"),'0')
        self.assertEqual(self.sql("SELECT count(*) FROM campuses WHERE code IN ('CS1','CS3');"),'2')
        self.assertEqual(self.sql("SELECT count(*) FROM rooms WHERE code LIKE 'DEMO-%';"),'4')
        self.assertEqual(self.sql("SELECT count(DISTINCT room_type) FROM rooms WHERE code LIKE 'DEMO-%' AND room_type IN ('free_area','topic_room');"),'2')
        self.assertEqual(self.sql("SELECT count(*) FROM rooms WHERE code LIKE 'DEMO-%' AND campus_id IS NOT NULL;"),'4')
        self.sql("""
            ALTER TABLE rooms DROP CONSTRAINT ck_rooms_type;
            UPDATE rooms SET room_type = CASE room_type
                WHEN 'free_area' THEN 'reading_room'
                WHEN 'topic_room' THEN 'group_study_room'
            END
            WHERE code LIKE 'DEMO-%';
            ALTER TABLE rooms ADD CONSTRAINT ck_rooms_type
                CHECK (room_type IN ('reading_room', 'group_study_room'));
        """)
        for filename in ('011_normalize_room_types.sql', '012_seed_campuses_and_rooms.sql'):
            script = (ROOT/'database'/'init'/filename).read_text(encoding='utf-8')
            self.compose('exec','-T','db','sh','-c',
                         'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"',
                         input=script)
        self.assertEqual(self.sql("SELECT count(*) FROM rooms WHERE code LIKE 'DEMO-%' AND room_type IN ('free_area','topic_room');"),'4')
        self.assertEqual(self.sql("SELECT count(*) FROM rooms WHERE code LIKE 'DEMO-%';"),'4')
        self.assertEqual(self.sql("SELECT indexdef LIKE '%UNIQUE%' FROM pg_indexes WHERE schemaname='public' AND tablename='count_events' AND indexname='count_events_pkey';"),'t')
        self.assertEqual(self.sql("SELECT count(*) FROM pg_indexes WHERE schemaname='public' AND indexname='idx_occupancy_room_recorded';"),'1')
        self.sql("""
            INSERT INTO occupancy_records
                (room_id, current_count, available_seats, recorded_at, source, device_status)
            SELECT id, 7, capacity - 7, '2026-11-20T14:00:00Z', 'cv', 'online'
            FROM rooms
            WHERE code = 'DEMO-CS1-FREE-01';
        """)
        self.assertEqual(self.sql("""
            SELECT count(*)
            FROM occupancy_records AS occupancy
            JOIN rooms ON rooms.id = occupancy.room_id
            WHERE rooms.code = 'DEMO-CS1-FREE-01'
              AND occupancy.current_count = 7
              AND occupancy.available_seats = 53
              AND occupancy.recorded_at = '2026-11-20T14:00:00Z';
        """),'1')
        self.compose('down')
        self.compose('up','-d','--wait','--wait-timeout','120','db')
        self.assertEqual(self.sql("SELECT count(*) FROM rooms WHERE code LIKE 'DEMO-%';"),'4')
        self.assertEqual(self.sql("""
            SELECT count(*)
            FROM occupancy_records AS occupancy
            JOIN rooms ON rooms.id = occupancy.room_id
            WHERE rooms.code = 'DEMO-CS1-FREE-01'
              AND occupancy.current_count = 7
              AND occupancy.available_seats = 53
              AND occupancy.recorded_at = '2026-11-20T14:00:00Z';
        """),'1')
        migration = (ROOT/'database/init/009_add_email_otp_auth.sql').read_text(encoding='utf-8')
        self.compose('exec','-T','db','sh','-c',
                     'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"',
                     input=migration)
        self.assertEqual(self.sql("SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('email_otp_challenges','auth_sessions');"),'2')

    def test_upgrade_backend_write_read_and_restart(self):
        self.setup_project(legacy=True)
        self.compose('up','-d','--wait','--wait-timeout','120','db')
        self.assertEqual(self.sql("SELECT to_regclass('cv_count_records') IS NULL;"),'t')
        self.sql("INSERT INTO rooms(code,name,capacity) VALUES ('A101','Test room',40); INSERT INTO occupancy_records(room_id,occupied_count) VALUES (1,5);")
        for _ in range(2):
            self.compose('exec','-T','db','sh','-c','psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /migrations/002.sql')
        self.assertEqual(self.sql('SELECT occupied_count FROM occupancy_records;'),'5')
        self.compose('build','backend')
        self.compose('up','-d','--no-deps','--wait','--wait-timeout','120','backend')
        health = self.compose('exec','-T','backend','python','-c',
                              "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health/db').read().decode())")
        self.assertEqual(json.loads(health)['status'],'ok')
        sample = json.loads((ROOT/'docs/examples/cv-count-v1.json').read_text(encoding='utf-8'))
        sample.update(room_id='A101',people_count=0,tracked_count=0,recorded_at='2026-10-30T07:00:00+07:00')
        self.compose('exec','-T','backend','python','-c',
                     "import sys; from pathlib import Path; Path('/tmp/cv-input.json').write_text(sys.stdin.read())",input=json.dumps(sample))
        first = json.loads(self.compose('exec','-T','backend','python','-m','app.cv_store','save','/tmp/cv-input.json'))
        second = json.loads(self.compose('exec','-T','backend','python','-m','app.cv_store','save','/tmp/cv-input.json'))
        self.assertEqual(first['id'],second['id'])
        self.assertEqual(first['room_id'],1)
        self.assertEqual(first['people_count'],0)
        self.assertEqual(first['recorded_at'],'2026-10-30T00:00:00Z')
        rows = json.loads(self.compose('exec','-T','backend','python','-m','app.cv_store','history','--camera-id','cam-01'))
        self.assertEqual(len(rows),1)
        self.compose('stop','db')
        unavailable = self.compose('exec','-T','backend','python','-c',
            "import urllib.request, urllib.error\ntry:\n urllib.request.urlopen('http://localhost:8000/health/db')\nexcept urllib.error.HTTPError as error:\n print(error.code)")
        self.assertEqual(unavailable,'503')
        self.compose('stop','backend','db')
        self.compose('up','-d','--wait','--wait-timeout','120','db')
        self.compose('up','-d','--no-deps','--wait','--wait-timeout','120','backend')
        again = json.loads(self.compose('exec','-T','backend','python','-m','app.cv_store','history','--camera-id','cam-01'))
        self.assertEqual(again[0]['id'],first['id'])
        self.assertEqual(self.sql('SELECT occupied_count FROM occupancy_records;'),'5')


if __name__=='__main__':
    unittest.main()
