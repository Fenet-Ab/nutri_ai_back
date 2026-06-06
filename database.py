from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import get_settings

settings = get_settings()

_connect_args = {}
if settings.database_url.startswith("sqlite"):
    # Local development SQLite
    _connect_args = {"check_same_thread": False}
elif settings.database_url.startswith("postgresql"):
    # Ensure TLS/SSL for hosted Postgres (Supabase, managed PG providers)
    _connect_args = {"sslmode": "require"}

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    pool_pre_ping=True,  # reconnect after idle timeouts
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """All ORM models inherit from this"""

    pass


def get_db():
    """FastAPI dependency — yields a DB session and always closes it"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
