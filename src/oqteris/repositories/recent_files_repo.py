"""Repository for recent files tracking and persistence."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import delete, desc, select

from oqteris.database.connection import DatabaseManager, get_db_manager
from oqteris.models.entities import RecentFile

logger = logging.getLogger(__name__)


class RecentFilesRepository:
    """Handles CRUD operations for recent file records."""

    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        self._db = db_manager or get_db_manager()

    def add_or_update(
        self,
        file_path: str | Path,
        file_size_bytes: int = 0,
        page_count: int = 0,
        max_limit: int = 20,
    ) -> RecentFile:
        """Add a recent file or update its last opened timestamp and metadata."""
        norm_path = str(Path(file_path).resolve())
        file_name = Path(norm_path).name

        with self._db.session_scope() as session:
            stmt = select(RecentFile).where(RecentFile.file_path == norm_path)
            record = session.execute(stmt).scalar_one_or_none()

            now = datetime.now(timezone.utc)
            if record:
                record.last_opened_at = now
                record.is_missing = not Path(norm_path).exists()
                if file_size_bytes > 0:
                    record.file_size_bytes = file_size_bytes
                if page_count > 0:
                    record.page_count = page_count
            else:
                record = RecentFile(
                    file_path=norm_path,
                    file_name=file_name,
                    file_size_bytes=file_size_bytes,
                    page_count=page_count,
                    last_opened_at=now,
                    is_missing=not Path(norm_path).exists(),
                    is_pinned=False,
                )
                session.add(record)

            session.flush()

            # Enforce max_limit for unpinned items
            self._trim_unpinned_entries(session, max_limit)
            session.refresh(record)
            return record

    def _trim_unpinned_entries(self, session, max_limit: int) -> None:
        """Trim oldest unpinned files if count exceeds max_limit."""
        stmt = (
            select(RecentFile)
            .where(RecentFile.is_pinned == False)  # noqa: E712
            .order_by(desc(RecentFile.last_opened_at))
        )
        unpinned = list(session.execute(stmt).scalars().all())

        if len(unpinned) > max_limit:
            to_delete = unpinned[max_limit:]
            for item in to_delete:
                session.delete(item)

    def get_recent(self, limit: int = 20) -> list[RecentFile]:
        """Fetch list of recent files, pinned first then newest opened."""
        with self._db.session_scope() as session:
            stmt = (
                select(RecentFile)
                .order_by(desc(RecentFile.is_pinned), desc(RecentFile.last_opened_at))
                .limit(limit)
            )
            results = list(session.execute(stmt).scalars().all())
            # Check existence and update flag if necessary
            for r in results:
                exists = Path(r.file_path).exists()
                if r.is_missing != (not exists):
                    r.is_missing = not exists
            return results

    def remove(self, file_path: str | Path) -> bool:
        """Remove a recent file by path."""
        norm_path = str(Path(file_path).resolve())
        with self._db.session_scope() as session:
            stmt = delete(RecentFile).where(RecentFile.file_path == norm_path)
            res = session.execute(stmt)
            return res.rowcount > 0

    def clear(self, keep_pinned: bool = True) -> int:
        """Clear recent files list, optionally keeping pinned items."""
        with self._db.session_scope() as session:
            if keep_pinned:
                stmt = delete(RecentFile).where(RecentFile.is_pinned == False)  # noqa: E712
            else:
                stmt = delete(RecentFile)
            res = session.execute(stmt)
            return res.rowcount

    def toggle_pinned(self, file_path: str | Path) -> bool:
        """Toggle pinned status for a recent file."""
        norm_path = str(Path(file_path).resolve())
        with self._db.session_scope() as session:
            stmt = select(RecentFile).where(RecentFile.file_path == norm_path)
            record = session.execute(stmt).scalar_one_or_none()
            if record:
                record.is_pinned = not record.is_pinned
                return record.is_pinned
        return False
