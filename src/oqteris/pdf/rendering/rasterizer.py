"""PDF page rasterizer converting PyMuPDF pixmaps to PySide6 QImage objects."""

from __future__ import annotations

import logging
from typing import Optional

import pymupdf
from PySide6.QtGui import QImage

from oqteris.pdf.document.document import PDFDocument
from oqteris.pdf.rendering.cache import PageRenderCache

logger = logging.getLogger(__name__)


class PDFRasterizer:
    """Rasterizes PDF pages into QImages at arbitrary zoom levels and rotations."""

    def __init__(self, cache: Optional[PageRenderCache] = None) -> None:
        self.cache = cache or PageRenderCache()

    def render_page_to_qimage(
        self,
        document: PDFDocument,
        page_index: int,
        zoom: float = 1.0,
        rotation: int = 0,
        use_cache: bool = True,
    ) -> Optional[QImage]:
        """Rasterize a page to a QImage, using the cache if enabled."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return None

        # Check cache
        if use_cache:
            cached_img = self.cache.get(document.doc_id, page_index, zoom, rotation)
            if cached_img is not None:
                return cached_img

        raw_doc = document.raw_doc
        if raw_doc is None:
            return None

        try:
            page = raw_doc[page_index]

            # Construct transformation matrix for DPI scaling and rotation
            total_rotation = (page.rotation + rotation) % 360
            matrix = pymupdf.Matrix(zoom, zoom).prerotate(total_rotation)

            # High quality pixmap
            pix = page.get_pixmap(matrix=matrix, alpha=False)

            # PyMuPDF samples are RGB (3 bytes per pixel)
            # Create QImage from byte buffer: QImage(data, width, height, bytesPerLine, format)
            # Note: We must make a deep copy (.copy()) so QImage owns the memory buffer after pixmap is garbage-collected!
            qimage = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                QImage.Format.Format_RGB888,
            ).copy()

            if use_cache:
                self.cache.put(document.doc_id, page_index, zoom, rotation, qimage)

            return qimage
        except Exception as e:
            logger.error(
                "Error rasterizing page %d for doc %s (zoom=%.2f, rot=%d): %s",
                page_index,
                document.doc_id,
                zoom,
                rotation,
                e,
            )
            return None
