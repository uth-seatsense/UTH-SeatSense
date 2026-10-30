"""Local verification CLI; not a replacement for SEAT-19 API endpoints."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.db.session import build_engine, build_session_factory
from app.services.cv_count_service import CVCountService


def main():
    parser = argparse.ArgumentParser(description='Verify CV persistence using DATABASE_URL')
    commands = parser.add_subparsers(dest='command',required=True)
    save = commands.add_parser('save')
    save.add_argument('file',type=Path,help='One CV schema 1.0 JSON record')
    history = commands.add_parser('history')
    history.add_argument('--camera-id')
    history.add_argument('--room-code')
    history.add_argument('--room-id',type=int)
    history.add_argument('--limit',type=int,default=20)
    history.add_argument('--offset',type=int,default=0)
    history.add_argument('--start',type=datetime.fromisoformat)
    history.add_argument('--end',type=datetime.fromisoformat)
    args = parser.parse_args()
    engine = None
    try:
        engine = build_engine(settings.connection_url())
        service = CVCountService(build_session_factory(engine))
        if args.command == 'save':
            result = service.save(json.loads(args.file.read_text(encoding='utf-8')))
            print(result.model_dump_json(indent=2))
        else:
            filters = vars(args).copy()
            filters.pop('command')
            print(json.dumps([row.model_dump(mode='json') for row in service.history(**filters)],indent=2))
        return 0
    except (OSError,ValueError):
        print('Invalid configuration, CV input, file or query; check README.',file=sys.stderr)
        return 1
    except SQLAlchemyError:
        print('Database operation failed; check connectivity and applied migrations.',file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
