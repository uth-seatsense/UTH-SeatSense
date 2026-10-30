"""Real PostgreSQL 16 migration checks in an isolated disposable container.

Set SEAT24_RUN_DB_TESTS=1 and run unittest discovery from the repo root.
No host ports, host data or existing Compose volumes are used.
"""
import os
from pathlib import Path
import subprocess
import time
import unittest
from uuid import uuid4

INIT = Path(__file__).resolve().parents[1] / 'init'


@unittest.skipUnless(os.environ.get('SEAT24_RUN_DB_TESTS') == '1', 'Set SEAT24_RUN_DB_TESTS=1 to run disposable PostgreSQL checks')
class MigrationTests(unittest.TestCase):
    @classmethod
    def command(cls, *args, input=None):
        return subprocess.run(['docker', *args], input=input, text=True, encoding='utf-8', capture_output=True, timeout=60)

    @classmethod
    def sql(cls, text, database='fresh', success=True):
        result = cls.command('exec','-i',cls.container,'psql','-X','-v','ON_ERROR_STOP=1','-At','-U','postgres','-d',database,input=text)
        if success and result.returncode:
            raise AssertionError(result.stderr)
        if not success and not result.returncode:
            raise AssertionError('Invalid record unexpectedly accepted')
        return result.stdout.strip()

    @classmethod
    def setUpClass(cls):
        cls.container = 'seatsense-seat24-test-' + uuid4().hex[:12]
        result = cls.command('run','--rm','--detach','--network','none','--name',cls.container,
                             '-e','POSTGRES_HOST_AUTH_METHOD=trust','postgres:16.6-alpine')
        if result.returncode:
            raise RuntimeError(result.stderr)
        try:
            for _ in range(60):
                # A real TCP connection avoids probing the temporary bootstrap server.
                ready = cls.command('exec',cls.container,'pg_isready','-h','127.0.0.1','-U','postgres')
                if ready.returncode == 0:
                    break
                time.sleep(0.5)
            else:
                raise RuntimeError('PostgreSQL did not become ready')
            cls.sql('CREATE DATABASE fresh;',database='postgres')
            cls.sql('CREATE DATABASE upgraded;',database='postgres')
            baseline = (INIT/'001_create_tables.sql').read_text(encoding='utf-8')
            migration = (INIT/'002_cv_count_records.sql').read_text(encoding='utf-8')
            cls.sql(baseline)
            cls.sql(migration)
            cls.sql(baseline,database='upgraded')
            cls.sql("INSERT INTO rooms (code,name,capacity) VALUES ('A101','Test room',40); INSERT INTO occupancy_records(room_id,occupied_count,observed_at) VALUES (1,5,'2026-10-30T07:00:00+07:00');",database='upgraded')
            cls.sql(migration,database='upgraded')
        except BaseException:
            cls.command('stop',cls.container)
            raise

    @classmethod
    def tearDownClass(cls):
        cls.command('stop',cls.container)

    def test_existing_rows_preserved_and_reapply_safe(self):
        self.assertEqual(self.sql('SELECT occupied_count FROM occupancy_records;',database='upgraded'),'5')
        self.sql((INIT/'002_cv_count_records.sql').read_text(encoding='utf-8'),database='upgraded')
        self.assertEqual(self.sql('SELECT count(*) FROM schema_migrations;',database='upgraded'),'1')
        self.assertEqual(self.sql('SELECT count(*) FROM rooms;',database='upgraded'),'1')

    def insert(self, **changes):
        fields = dict(schema_version="'1.0'",session_id=f"'{uuid4()}'",camera_id="'cam-01'",
                      source_type="'video'",frame_index='0',timestamp_ms='0',
                      recorded_at="'2026-10-30T07:00:00+07:00'",people_count='0',tracked_count='0',
                      line_enabled='false',occupancy_underflow='false')
        fields.update(changes)
        return f"INSERT INTO cv_count_records ({','.join(fields)}) VALUES ({','.join(fields.values())})"

    def test_zero_room_mapping_and_timezone_roundtrip(self):
        statement = self.insert(room_code="'unmapped-room'")
        result = self.sql("SET TIME ZONE 'UTC'; " + statement + " RETURNING people_count, room_id IS NULL, to_char(recorded_at,'YYYY-MM-DD HH24:MI:SSOF');")
        self.assertIn('0|t|2026-10-30 00:00:00+00',result)

    def test_constraints(self):
        invalid = [dict(people_count='-1'),dict(tracked_count='1'),dict(frame_index='-1'),
                   dict(timestamp_ms="'NaN'"),dict(timestamp_ms="'Infinity'"),
                   dict(recorded_at="'infinity'"),dict(camera_id="'  '"),
                   dict(source_type="'rtsp'"),dict(room_id='999999'),dict(line_enabled='true'),
                   dict(in_count='0'),dict(initial_occupancy='0'),
                   dict(line_enabled='true',in_count='0',out_count='1',initial_occupancy='0',estimated_occupancy='0',occupancy_underflow='false')]
        for changes in invalid:
            with self.subTest(changes=changes):
                self.sql(self.insert(**changes),success=False)

    def test_underflow_consistency_and_unique_frame(self):
        statement = self.insert(line_enabled='true',in_count='0',out_count='1',
                                initial_occupancy='0',estimated_occupancy='0',occupancy_underflow='true')
        self.sql(statement)
        self.sql(statement,success=False)
        self.sql(self.insert(line_enabled='true',in_count='0',out_count='0'))

    def test_indexes_exist(self):
        result = self.sql("SELECT indexname FROM pg_indexes WHERE tablename='cv_count_records';")
        for name in ['uq_cv_session_frame','idx_cv_camera_recorded','idx_cv_room_recorded']:
            self.assertIn(name,result)

    def test_failed_migration_rolls_back_all_new_tables(self):
        self.sql('CREATE DATABASE rollback_probe;',database='postgres')
        self.sql((INIT/'001_create_tables.sql').read_text(encoding='utf-8'),database='rollback_probe')
        migration = (INIT/'002_cv_count_records.sql').read_text(encoding='utf-8')
        migration = migration.replace('COMMIT;', 'SELECT missing_column FROM cv_count_records;\nCOMMIT;')
        self.sql(migration,database='rollback_probe',success=False)
        self.assertEqual(self.sql("SELECT to_regclass('cv_count_records') IS NULL, to_regclass('schema_migrations') IS NULL;",database='rollback_probe'),'t|t')


if __name__ == '__main__':
    unittest.main()
