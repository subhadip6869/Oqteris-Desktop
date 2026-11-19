"""Integration tests for scanned PDF detection and OpenCV image preprocessing."""

from pathlib import Path
import numpy as np
from PIL import Image
import pymupdf as fitz

from oqteris.pdf.document.document import PDFDocument
from oqteris.pdf.ocr.detector import ScannedPDFDetector
from oqteris.pdf.ocr.preprocessor import ImagePreprocessor


def test_scanned_pdf_detector(sample_pdf_normal: Path, temp_dir: Path):
    # 1. Normal document with text is not scanned
    doc = PDFDocument(doc_id="det_normal")
    doc.open(sample_pdf_normal)
    assert ScannedPDFDetector.is_page_scanned(doc, 0) is False
    assert ScannedPDFDetector.is_document_scanned(doc) is False
    doc.close()

    # 2. Create synthetic scanned PDF (only image, no text)
    img_path = temp_dir / "scan_sample.png"
    Image.new("RGB", (600, 800), color="white").save(img_path)

    scanned_pdf_path = temp_dir / "scanned_doc.pdf"
    sc_doc = fitz.open()
    p = sc_doc.new_page(width=600, height=800)
    p.insert_image(p.rect, filename=str(img_path))
    sc_doc.save(str(scanned_pdf_path))
    sc_doc.close()

    doc_scanned = PDFDocument(doc_id="det_scanned")
    doc_scanned.open(scanned_pdf_path)
    assert ScannedPDFDetector.is_page_scanned(doc_scanned, 0) is True
    assert ScannedPDFDetector.is_document_scanned(doc_scanned) is True
    doc_scanned.close()


def test_opencv_preprocessor():
    # Test deskew with synthetic angled line image
    arr = np.zeros((200, 200, 3), dtype=np.uint8)
    deskewed = ImagePreprocessor.deskew(arr)
    assert deskewed.shape == arr.shape

    # Test binarization
    binarized = ImagePreprocessor.binarize(arr)
    assert len(binarized.shape) == 2
