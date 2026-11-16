"""Repository for visual saved signatures (drawings/scans)."""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import delete, select

from oqteris.database.connection import DatabaseManager, get_db_manager
from oqteris.models.entities import SavedSignature

logger = logging.getLogger(__name__)


class SavedSignaturesRepository:
    def __init__(self, db_manager: DatabaseManager | None = None) -> None:
        self._db = db_manager or get_db_manager()

    def add_signature(
        self,
        title: str,
        image_rel_path: str,
        signature_type: str = "drawn",
        is_default: bool = False,
    ) -> SavedSignature:
        with self._db.session_scope() as session:
            if is_default:
                # Reset previous default
                stmt = select(SavedSignature).where(SavedSignature.is_default == True)  # noqa: E712
                prev_defaults = session.execute(stmt).scalars().all()
                for p in prev_defaults:
                    p.is_default = False

            sig = SavedSignature(
                title=title,
                image_rel_path=image_rel_path,
                signature_type=signature_type,
                is_default=is_default,
            )
            session.add(sig)
            session.flush()
            session.refresh(sig)
            return sig

    def get_all(self) -> list[SavedSignature]:
        with self._db.session_scope() as session:
            stmt = select(SavedSignature).order_by(SavedSignature.id.desc())
            return list(session.execute(stmt).scalars().all())

    def get_default(self) -> Optional[SavedSignature]:
        with self._db.session_scope() as session:
            stmt = select(SavedSignature).where(SavedSignature.is_default == True)  # noqa: E712
            return session.execute(stmt).scalar_one_or_none()

    def delete_signature(self, sig_id: int) -> bool:
        with self._db.session_scope() as session:
            stmt = delete(SavedSignature).where(SavedSignature.id == sig_id)
            return session.execute(stmt).rowcount > 0
