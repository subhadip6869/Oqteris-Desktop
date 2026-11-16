"""Pytest test fixtures and synthetic test PDF generators for Oqteris test suite."""

from __future__ import annotations

import datetime
import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import fitz  # PyMuPDF
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from oqteris.config.settings import SettingsManager
from oqteris.database.connection import DatabaseManager
from oqteris.platform.storage import StorageManager
from oqteris.repositories.recent_files_repo import RecentFilesRepository


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Temporary scratch directory for test isolation."""
    td = tempfile.mkdtemp(prefix="oq_test_")
    yield Path(td)
    shutil.rmtree(td, ignore_errors=True)


@pytest.fixture
def test_storage(temp_dir: Path) -> StorageManager:
    """Storage manager pointing to temporary directory."""
    storage = StorageManager(app_name="OqterisTest", org_name="OriginSDTest")
    storage._data_dir = temp_dir / "data"
    storage._config_dir = temp_dir / "config"
    storage._cache_dir = temp_dir / "cache"
    storage._logs_dir = temp_dir / "logs"
    storage._temp_dir = temp_dir / "temp"
    storage._recovery_dir = temp_dir / "recovery"
    storage._backups_dir = temp_dir / "backups"
    storage._ipc_dir = temp_dir / "ipc"
    storage.ensure_directories()
    return storage


@pytest.fixture
def test_db(temp_dir: Path) -> DatabaseManager:
    """Isolated SQLite database manager."""
    db_path = temp_dir / "test_oqteris.db"
    mgr = DatabaseManager(db_path=db_path)
    yield mgr
    mgr.close()


@pytest.fixture
def test_settings(temp_dir: Path) -> SettingsManager:
    """Isolated settings manager."""
    settings_file = temp_dir / "test_settings.json"
    return SettingsManager(file_path=settings_file)


@pytest.fixture
def sample_pdf_normal(temp_dir: Path) -> Path:
    """Creates a valid multi-page PDF with English and Bengali Unicode text."""
    pdf_path = temp_dir / "sample_normal.pdf"
    doc = fitz.open()

    # Page 1: Standard text
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text(fitz.Point(50, 100), "Oqteris PDF Reader and Editor", fontsize=18)
    p1.insert_text(fitz.Point(50, 140), "OriginSD - Subhadip Dutta", fontsize=14)
    p1.insert_text(fitz.Point(50, 180), "This is a clean synthetic test PDF document.", fontsize=12)

    # Page 2: Non-Latin Unicode (Bengali where supported, or extended Unicode)
    p2 = doc.new_page(width=595, height=842)
    p2.insert_text(fitz.Point(50, 100), "Unicode Support Test", fontsize=16)
    vrinda = Path("C:/Windows/Fonts/vrinda.ttf")
    if vrinda.is_file():
        p2.insert_text(fitz.Point(50, 140), "Welcome to Oqteris / স্বাগতম", fontfile=str(vrinda), fontname="bengali", fontsize=12)
    else:
        p2.insert_text(fitz.Point(50, 140), "Welcome to Oqteris / café / España", fontsize=12)

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def sample_pdf_encrypted(temp_dir: Path) -> Path:
    """Creates a password-protected PDF (password: 'secret123')."""
    pdf_path = temp_dir / "sample_encrypted.pdf"
    doc = fitz.open()
    p = doc.new_page(width=595, height=842)
    p.insert_text(fitz.Point(50, 100), "Confidential Encrypted Document", fontsize=14)
    doc.save(
        str(pdf_path),
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw="secret123",
        owner_pw="owner123",
    )
    doc.close()
    return pdf_path


@pytest.fixture
def sample_pdf_form(temp_dir: Path) -> Path:
    """Creates a PDF containing AcroForm widgets."""
    pdf_path = temp_dir / "sample_form.pdf"
    doc = fitz.open()
    p = doc.new_page(width=595, height=842)

    # Add text field
    widget = fitz.Widget()
    widget.rect = fitz.Rect(50, 100, 250, 125)
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.field_name = "fullName"
    widget.field_value = "John Doe"
    p.add_widget(widget)

    # Add checkbox field
    cb_widget = fitz.Widget()
    cb_widget.rect = fitz.Rect(50, 150, 70, 170)
    cb_widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
    cb_widget.field_name = "agreeTerms"
    cb_widget.field_value = "Yes"
    p.add_widget(cb_widget)

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def test_p12_certificate(temp_dir: Path) -> tuple[Path, str]:
    """Generates a synthetic self-signed test PKCS#12 certificate."""
    cert_path = temp_dir / "test_identity.p12"
    passphrase = "testpassword"

    # Generate RSA private key
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Self-signed certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "Test Signer"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "OriginSD Test"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )

    # Serialize to PKCS#12
    p12_bytes = serialization.pkcs12.serialize_key_and_certificates(
        name=b"test_signer",
        key=key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode("utf-8")),
    )

    with open(cert_path, "wb") as f:
        f.write(p12_bytes)

    return cert_path, passphrase
