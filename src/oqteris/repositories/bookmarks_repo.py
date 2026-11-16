"""Repositories for bookmarks, workspace state, certificates, and recovery records."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import delete, desc, select

from oqteris.database.connection import DatabaseManager, get_db_manager
from oqteris.models.entities import (
    OCRJobHistory,
    RecoveryRecord,
    SavedSignature,
    TrustedCertificate,
    UserBookmark,
    WorkspaceTab,
)

logger = logging.getLogger(__name__)


class BookmarksRepository:
    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        self._db = db_manager or get_db_manager()

    def add_bookmark(self, file_path: str, page_index: int, title: str) -> UserBookmark:
        norm_path = str(Path(file_path).resolve())
        with self._db.session_scope() as session:
            stmt = select(UserBookmark).where(
                UserBookmark.file_path == norm_path,
                UserBookmark.page_index == page_index,
            )
            existing = session.execute(stmt).scalar_one_or_none()
            if existing:
                existing.title = title
                return existing

            bookmark = UserBookmark(file_path=norm_path, page_index=page_index, title=title)
            session.add(bookmark)
            session.flush()
            session.refresh(bookmark)
            return bookmark

    def get_bookmarks_for_file(self, file_path: str) -> list[UserBookmark]:
        norm_path = str(Path(file_path).resolve())
        with self._db.session_scope() as session:
            stmt = (
                select(UserBookmark)
                .where(UserBookmark.file_path == norm_path)
                .order_by(UserBookmark.page_index)
            )
            return list(session.execute(stmt).scalars().all())

    def remove_bookmark(self, bookmark_id: int) -> bool:
        with self._db.session_scope() as session:
            stmt = delete(UserBookmark).where(UserBookmark.id == bookmark_id)
            return session.execute(stmt).rowcount > 0


class WorkspaceRepository:
    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        self._db = db_manager or get_db_manager()

    def save_tabs(self, tabs: list[dict[str, Any]]) -> None:
        with self._db.session_scope() as session:
            session.execute(delete(WorkspaceTab))
            for idx, tab_data in enumerate(tabs):
                tab = WorkspaceTab(
                    file_path=str(Path(tab_data["file_path"]).resolve()),
                    current_page=tab_data.get("current_page", 0),
                    zoom_level=tab_data.get("zoom_level", 1.0),
                    scroll_x=tab_data.get("scroll_x", 0.0),
                    scroll_y=tab_data.get("scroll_y", 0.0),
                    tab_index=idx,
                    is_active=tab_data.get("is_active", False),
                )
                session.add(tab)

    def get_tabs(self) -> list[WorkspaceTab]:
        with self._db.session_scope() as session:
            stmt = select(WorkspaceTab).order_by(WorkspaceTab.tab_index)
            return list(session.execute(stmt).scalars().all())

    def clear(self) -> None:
        with self._db.session_scope() as session:
            session.execute(delete(WorkspaceTab))


class CertificatesRepository:
    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        self._db = db_manager or get_db_manager()

    def add_certificate(
        self,
        fingerprint_sha256: str,
        common_name: str,
        issuer: str,
        valid_from: datetime,
        valid_to: datetime,
        certificate_pem: str,
        organization: str | None = None,
        is_trusted: bool = True,
        is_root_ca: bool = False,
    ) -> TrustedCertificate:
        with self._db.session_scope() as session:
            stmt = select(TrustedCertificate).where(
                TrustedCertificate.fingerprint_sha256 == fingerprint_sha256
            )
            existing = session.execute(stmt).scalar_one_or_none()
            if existing:
                existing.is_trusted = is_trusted
                existing.common_name = common_name
                return existing

            cert = TrustedCertificate(
                fingerprint_sha256=fingerprint_sha256,
                common_name=common_name,
                organization=organization,
                issuer=issuer,
                valid_from=valid_from,
                valid_to=valid_to,
                certificate_pem=certificate_pem,
                is_trusted=is_trusted,
                is_root_ca=is_root_ca,
            )
            session.add(cert)
            session.flush()
            session.refresh(cert)
            return cert

    def get_all(self) -> list[TrustedCertificate]:
        with self._db.session_scope() as session:
            stmt = select(TrustedCertificate).order_by(TrustedCertificate.common_name)
            return list(session.execute(stmt).scalars().all())

    def find_by_fingerprint(self, fingerprint: str) -> TrustedCertificate | None:
        with self._db.session_scope() as session:
            stmt = select(TrustedCertificate).where(
                TrustedCertificate.fingerprint_sha256 == fingerprint
            )
            return session.execute(stmt).scalar_one_or_none()

    def set_trust(self, cert_id: int, is_trusted: bool) -> bool:
        with self._db.session_scope() as session:
            stmt = select(TrustedCertificate).where(TrustedCertificate.id == cert_id)
            cert = session.execute(stmt).scalar_one_or_none()
            if cert:
                cert.is_trusted = is_trusted
                return True
        return False

    def remove(self, cert_id: int) -> bool:
        with self._db.session_scope() as session:
            stmt = delete(TrustedCertificate).where(TrustedCertificate.id == cert_id)
            return session.execute(stmt).rowcount > 0


class RecoveryRepository:
    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        self._db = db_manager or get_db_manager()

    def create_record(self, original_path: str, recovery_path: str, title: str) -> RecoveryRecord:
        with self._db.session_scope() as session:
            rec = RecoveryRecord(
                original_path=original_path,
                recovery_path=recovery_path,
                document_title=title,
                is_recovered=False,
            )
            session.add(rec)
            session.flush()
            session.refresh(rec)
            return rec

    def get_unresolved(self) -> list[RecoveryRecord]:
        with self._db.session_scope() as session:
            stmt = select(RecoveryRecord).where(RecoveryRecord.is_recovered == False)  # noqa: E712
            return list(session.execute(stmt).scalars().all())

    def mark_resolved(self, record_id: int) -> None:
        with self._db.session_scope() as session:
            stmt = select(RecoveryRecord).where(RecoveryRecord.id == record_id)
            record = session.execute(stmt).scalar_one_or_none()
            if record:
                record.is_recovered = True
