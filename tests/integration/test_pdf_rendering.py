"""Integration tests for PDF page rasterization and bounded LRU cache."""

import os
import pytest
from pathlib import Path

# Use offscreen platform for Qt GUI tests
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtGui import QGuiApplication, QImage

from oqteris.pdf.document.document import PDFDocument
from oqteris.pdf.rendering.cache import PageRenderCache
from oqteris.pdf.rendering.rasterizer import PDFRasterizer


@pytest.fixture(scope="session")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication([])
    return app


def test_render_cache_lru_and_memory_limit(qapp):
    cache = PageRenderCache(max_items=3, max_memory_mb=10)

    img1 = QImage(100, 100, QImage.Format.Format_RGB888)
    img2 = QImage(100, 100, QImage.Format.Format_RGB888)
    img3 = QImage(100, 100, QImage.Format.Format_RGB888)
    img4 = QImage(100, 100, QImage.Format.Format_RGB888)

    cache.put("doc1", 0, 1.0, 0, img1)
    cache.put("doc1", 1, 1.0, 0, img2)
    cache.put("doc1", 2, 1.0, 0, img3)
    assert cache.item_count == 3

    # Adding 4th item evicts oldest (doc1, 0, 1.0, 0)
    cache.put("doc1", 3, 1.0, 0, img4)
    assert cache.item_count == 3
    assert cache.get("doc1", 0, 1.0, 0) is None
    assert cache.get("doc1", 3, 1.0, 0) is not None

    # Invalidate page
    cache.invalidate_page("doc1", 3)
    assert cache.get("doc1", 3, 1.0, 0) is None


def test_rasterizer_renders_qimage(qapp, sample_pdf_normal: Path):
    doc = PDFDocument(doc_id="raster_doc")
    doc.open(sample_pdf_normal)

    rasterizer = PDFRasterizer()
    qimage = rasterizer.render_page_to_qimage(doc, 0, zoom=1.0, rotation=0)

    assert qimage is not None
    assert not qimage.isNull()
    assert qimage.width() > 0
    assert qimage.height() > 0

    doc.close()
