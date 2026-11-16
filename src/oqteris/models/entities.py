"""SQLAlchemy declarative base and models for Oqteris."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class RecentFile(Base):
    """Tracks recently opened PDF documents."""

    __tablename__ = "recent_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String(1024), unique=True, index=True, nullable=False)
    file_name: Mapped[str] = mapped_column(String(256), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    last_opened_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_missing: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<RecentFile id={self.id} path={self.file_path!r} last_opened={self.last_opened_at}>"


class UserBookmark(Base):
    """User-created bookmarks for pages in a PDF document."""

    __tablename__ = "user_bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String(1024), index=True, nullable=False)
    page_index: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    __table_args__ = (
        UniqueConstraint("file_path", "page_index", name="uq_bookmark_file_page"),
    )


class WorkspaceTab(Base):
    """Persists open document tabs in the application workspace."""

    __tablename__ = "workspace_tabs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    current_page: Mapped[int] = mapped_column(Integer, default=0)
    zoom_level: Mapped[float] = mapped_column(Float, default=1.0)
    scroll_x: Mapped[float] = mapped_column(Float, default=0.0)
    scroll_y: Mapped[float] = mapped_column(Float, default=0.0)
    tab_index: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class SavedSignature(Base):
    """Metadata for saved visual user signatures (drawings, scanned images)."""

    __tablename__ = "saved_signatures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    signature_type: Mapped[str] = mapped_column(String(32), default="drawn")  # drawn, image, text
    image_rel_path: Mapped[str] = mapped_column(String(512), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class TrustedCertificate(Base):
    """Trusted X.509 certificates and CA metadata for digital signature verification."""

    __tablename__ = "trusted_certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fingerprint_sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    common_name: Mapped[str] = mapped_column(String(256), nullable=False)
    organization: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    issuer: Mapped[str] = mapped_column(String(512), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=True)
    is_root_ca: Mapped[bool] = mapped_column(Boolean, default=False)
    certificate_pem: Mapped[str] = mapped_column(Text, nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class OCRJobHistory(Base):
    """Audit log of OCR processing tasks."""

    __tablename__ = "ocr_job_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    target_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    language: Mapped[str] = mapped_column(String(64), default="eng")
    page_count: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="completed")  # completed, failed, cancelled
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class RecoveryRecord(Base):
    """Crash recovery tracking for unsaved or interrupted documents."""

    __tablename__ = "recovery_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    recovery_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    document_title: Mapped[str] = mapped_column(String(256), default="Untitled")
    last_saved_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    is_recovered: Mapped[bool] = mapped_column(Boolean, default=False)
