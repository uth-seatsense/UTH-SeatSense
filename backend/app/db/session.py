"""Lazy PostgreSQL connection; DATABASE_URL comes from environment only."""
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


def build_engine(database_url):
    if not database_url:
        raise ValueError('DATABASE_URL is required for database operations')
    url = make_url(database_url)
    if url.drivername != 'postgresql+psycopg':
        raise ValueError('DATABASE_URL must use postgresql+psycopg')
    return create_engine(url, pool_pre_ping=True, hide_parameters=True,
                         connect_args={'options': '-c timezone=UTC', 'connect_timeout': 10})


def build_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)


@lru_cache(maxsize=1)
def get_session_factory():
    return build_session_factory(build_engine(settings.database_url))


def get_db():
    """Read/use a session; services own explicit transaction boundaries."""
    with get_session_factory()() as session:
        yield session
