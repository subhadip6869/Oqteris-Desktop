"""Unit tests for RecentFilesRepository and CertificatesRepository."""

from datetime import datetime, timezone
from pathlib import Path
from oqteris.database.connection import DatabaseManager
from oqteris.repositories.bookmarks_repo import CertificatesRepository
from oqteris.repositories.recent_files_repo import RecentFilesRepository


def test_recent_files_crud_and_trimming(test_db: DatabaseManager, temp_dir: Path):
    repo = RecentFilesRepository(db_manager=test_db)

    # Create dummy files
    p1 = temp_dir / "doc1.pdf"
    p2 = temp_dir / "doc2.pdf"
    p1.touch()
    p2.touch()

    repo.add_or_update(p1, file_size_bytes=100, page_count=2, max_limit=5)
    repo.add_or_update(p2, file_size_bytes=200, page_count=4, max_limit=5)

    recent = repo.get_recent()
    assert len(recent) == 2

    # Toggle pin
    is_pinned = repo.toggle_pinned(p1)
    assert is_pinned is True

    # Check pinned item is first
    recent_after_pin = repo.get_recent()
    assert recent_after_pin[0].file_path == str(p1.resolve())

    # Clear unpinned
    repo.clear(keep_pinned=True)
    assert len(repo.get_recent()) == 1
    assert repo.get_recent()[0].file_path == str(p1.resolve())


def test_certificates_repository(test_db: DatabaseManager):
    repo = CertificatesRepository(db_manager=test_db)

    now = datetime.now(timezone.utc)
    cert = repo.add_certificate(
        fingerprint_sha256="abc123sha256",
        common_name="OriginSD Root CA",
        issuer="OriginSD Trust Authority",
        valid_from=now,
        valid_to=now,
        certificate_pem="-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----",
        is_trusted=True,
    )
    assert cert.common_name == "OriginSD Root CA"

    all_certs = repo.get_all()
    assert len(all_certs) == 1

    repo.set_trust(cert.id, False)
    updated = repo.find_by_fingerprint("abc123sha256")
    assert updated is not None
    assert updated.is_trusted is False
