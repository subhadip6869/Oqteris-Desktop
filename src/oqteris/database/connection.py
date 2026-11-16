"""SQLite database session and engine lifecycle management using SQLAlchemy."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from oqteris.models.entities import Base
from oqteris.platform.storage import get_storage_manager

logger = logging.getLogger(__name__)


# Enable foreign key enforcement for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for high concurrency
    cursor.close()


class DatabaseManager:
    """Manages SQLite connections, sessions, and schema initialization."""

    def __init__(self, db_path: Path | None = None) -> None:
        self._storage = get_storage_manager()
        self._db_path = db_path or self._storage.database_file
        self._db_url = f"sqlite:///{self._db_path.as_posix()}"

        # Initialize engine
        self._engine = create_engine(
            self._db_url,
            echo=False,
            future=True,
            connect_args={"check_same_thread": False},
        )
        self._session_factory = sessionmaker(
            bind=self._engine, autoflush=False, autocommit=False, expire_on_commit=False
        )
        self._scoped_session = scoped_session(self._session_factory)

        self.init_schema()

    @property
    def engine(self) -> Engine:
        return self._engine

    def init_schema(self) -> None:
        """Create all tables defined in Base models if they don't already exist."""
        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            Base.metadata.create_all(self._engine)
            logger.info("Database schema initialized at %s", self._db_path)
        except Exception as e:
            logger.error("Failed to initialize database schema: %s", e)
            raise

    def get_session(self) -> Session:
        """Return a new database session."""
        return self._scoped_session()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Database transaction rolled back: %s", e)
            raise
        finally:
            session.close()

    def close(self) -> None:
        """Close engine and scoped sessions."""
        self._scoped_session.remove()
        self._engine.dispose()


# Singleton database manager
_db_instance: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
