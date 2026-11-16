"""Integration tests for PDF document opening, text extraction, search, and encryption."""

from pathlib import Path
import pytest

from oqteris.core.exceptions import PDFEncryptedError, PDFError
from oqteris.pdf.document.document import PDFDocument


def test_open_normal_pdf_and_metadata(sample_pdf_normal: Path):
    doc = PDFDocument(doc_id="test_doc_1")
    meta = doc.open(sample_pdf_normal)

    assert doc.is_open is True
    assert doc.page_count == 2
    assert meta.page_count == 2
    assert meta.can_print is True
    assert meta.is_encrypted is False

    doc.close()
    assert doc.is_open is False


def test_unicode_text_extraction(sample_pdf_normal: Path):
    doc = PDFDocument(doc_id="test_doc_unicode")
    doc.open(sample_pdf_normal)

    # Page 1 English text
    text_p1 = doc.extract_text_page(0)
    assert "Oqteris PDF Reader" in text_p1
    assert "Subhadip Dutta" in text_p1

    # Page 2 Unicode text
    text_p2 = doc.extract_text_page(1)
    if Path("C:/Windows/Fonts/vrinda.ttf").is_file():
        assert "স্বাগতম" in text_p2
    else:
        assert "Welcome" in text_p2

    doc.close()


def test_pdf_search_text(sample_pdf_normal: Path):
    doc = PDFDocument(doc_id="test_doc_search")
    doc.open(sample_pdf_normal)

    matches = doc.search_text("Oqteris")
    assert len(matches) >= 1
    assert matches[0].page_index == 0
    assert len(matches[0].rects) > 0

    doc.close()


def test_encrypted_pdf_handling(sample_pdf_encrypted: Path):
    doc = PDFDocument(doc_id="test_doc_enc")

    # Opening without password raises PDFEncryptedError
    with pytest.raises(PDFEncryptedError):
        doc.open(sample_pdf_encrypted, password="")

    # Opening with incorrect password raises PDFEncryptedError
    with pytest.raises(PDFEncryptedError):
        doc.open(sample_pdf_encrypted, password="wrong_password")

    # Opening with correct password succeeds
    meta = doc.open(sample_pdf_encrypted, password="secret123")
    assert doc.is_open is True
    assert meta.is_encrypted is True
    assert doc.page_count == 1

    doc.close()
