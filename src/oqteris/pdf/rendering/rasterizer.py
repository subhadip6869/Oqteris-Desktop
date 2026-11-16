"""PDF page rasterizer converting PyMuPDF pixmaps to PySide6 QImage objects with High-DPI support."""

from __future__ import annotations

import logging
from typing import Optional

import pymupdf
from PySide6.QtGui import QGuiApplication, QImage

from oqteris.pdf.document.document import PDFDocument
from oqteris.pdf.rendering.cache import PageRenderCache

logger = logging.getLogger(__name__)


def get_screen_scale_factor() -> float:
    """Detect screen DPI scaling factor and device pixel ratio.

    Standard PDF resolution is 72 DPI (1 pt = 1 pixel). Standard desktop screens
    are 96 DPI (1.33x scale). Modern High-DPI screens (Windows 125%, 150%, 200% Retina/4K)
    require higher pixel density so that text and vector graphics render pin-sharp
    instead of appearing blurry or pixelated.
    """
    try:
        app = QGuiApplication.instance()
        if app and hasattr(app, "primaryScreen"):
            screen = app.primaryScreen()
            if screen:
                dpr = float(screen.devicePixelRatio())
                # Base ratio: 96 DPI screen / 72 pt PDF = 1.33333333
                # Multiplied by DPR (e.g. 1.25 on Windows gives ~1.67)
                # Minimum 2.0 (144 DPI) ensures retina-sharp text across all display scales
                return max(2.0, min(3.0, round(dpr * (96.0 / 72.0), 2)))
    except Exception:
        pass
    return 2.0


class PDFRasterizer:
    """Rasterizes PDF pages into QImages at arbitrary zoom levels and rotations with High-DPI supersampling."""

    def __init__(self, cache: Optional[PageRenderCache] = None) -> None:
        self.cache = cache or PageRenderCache()

    def render_page_to_qimage(
        self,
        document: PDFDocument,
        page_index: int,
        zoom: float = 1.0,
        rotation: int = 0,
        use_cache: bool = True,
        dpi_scale: Optional[float] = None,
    ) -> Optional[QImage]:
        """Rasterize a page to a high-DPI QImage, using the cache if enabled."""
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

            scale = get_screen_scale_factor() if dpi_scale is None else max(1.0, dpi_scale)
            effective_zoom = zoom * scale

            # Guard against exceeding maximum GPU texture dimensions (e.g. 4096 px)
            max_pt = max(float(page.rect.width), float(page.rect.height), 1.0)
            if max_pt * effective_zoom > 4096:
                effective_zoom = 4096.0 / max_pt

            # Construct transformation matrix for DPI scaling and rotation
            total_rotation = (page.rotation + rotation) % 360
            matrix = pymupdf.Matrix(effective_zoom, effective_zoom).prerotate(total_rotation)

            # High quality pixmap with anti-aliasing
            pix = page.get_pixmap(matrix=matrix, alpha=False)

            # PyMuPDF samples are RGB (3 bytes per pixel)
            # Create QImage from byte buffer: QImage(data, width, height, bytesPerLine, format)
            # Note: We must make a deep copy (.copy()) so QImage owns the memory buffer
            qimage = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                QImage.Format.Format_RGB888,
            ).copy()

            # Set Device Pixel Ratio on QImage so Qt Quick handles High-DPI correctly
            qimage.setDevicePixelRatio(scale)

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
