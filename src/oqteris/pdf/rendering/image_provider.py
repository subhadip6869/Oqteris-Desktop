"""Qt Quick QQuickImageProvider implementation serving rendered PDF pages to QML.

Two separate caches are used to prevent thumbnail renders from evicting full-resolution
pages and vice-versa:

  _full_cache  : up to 8 full-resolution pages  / 64 MB  (what the user is reading)
  _thumb_cache : up to 20 thumbnail pages        / 24 MB  (side-panel strip)

The tight limits ensure RAM stays stable even when scrolling through a 500-page PDF.
"""

from __future__ import annotations

import logging
import urllib.parse
from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtGui import QImage
from PySide6.QtQuick import QQuickImageProvider

from oqteris.pdf.document.manager import get_document_manager
from oqteris.pdf.rendering.cache import PageRenderCache
from oqteris.pdf.rendering.rasterizer import PDFRasterizer

logger = logging.getLogger(__name__)


class PDFPageImageProvider(QQuickImageProvider):
    """Provides rasterized PDF pages directly to QML Image elements.

    URI format:
    image://pdf/<doc_id>/<page_index>?zoom=1.5&rot=0&v=123
    image://pdf/<doc_id>/<page_index>?thumb=1&v=123
    """

    def __init__(self, rasterizer: Optional[PDFRasterizer] = None) -> None:
        super().__init__(QQuickImageProvider.ImageType.Image)

        # Full-resolution cache: keep only 8 recently viewed pages (≤64 MB)
        self._full_cache = PageRenderCache(max_items=8, max_memory_mb=64)
        # Thumbnail cache: keep up to 20 small thumbnails (≤24 MB)
        self._thumb_cache = PageRenderCache(max_items=20, max_memory_mb=24)

        # Rasterizer uses the full-res cache by default; thumb renders pass their own
        self._rasterizer = rasterizer or PDFRasterizer(cache=self._full_cache)
        self._thumb_rasterizer = PDFRasterizer(cache=self._thumb_cache)
        self._doc_manager = get_document_manager()

    # ------------------------------------------------------------------
    # Back-compat: callers that reference .cache get the full-res cache
    # ------------------------------------------------------------------

    @property
    def cache(self) -> PageRenderCache:
        return self._full_cache

    @property
    def rasterizer(self) -> PDFRasterizer:
        return self._rasterizer

    # ------------------------------------------------------------------
    # Cache invalidation helpers (called from PDFController)
    # ------------------------------------------------------------------

    def invalidate_page(self, doc_id: str, page_index: int) -> None:
        self._full_cache.invalidate_page(doc_id, page_index)
        self._thumb_cache.invalidate_page(doc_id, page_index)

    def invalidate_document(self, doc_id: str) -> None:
        self._full_cache.invalidate_document(doc_id)
        self._thumb_cache.invalidate_document(doc_id)

    # ------------------------------------------------------------------
    # Qt Quick image request entry-point
    # ------------------------------------------------------------------

    def requestImage(self, id_str: str, size: QSize, requestedSize: QSize) -> QImage:
        """Invoked by Qt Quick whenever an image://pdf/... URL is requested."""
        try:
            # Parse query parameters if present
            if "?" in id_str:
                path_part, query_part = id_str.split("?", 1)
                query_params = urllib.parse.parse_qs(query_part)
            else:
                path_part = id_str
                query_params = {}

            segments = path_part.strip("/").split("/")
            if len(segments) < 2:
                logger.warning("Invalid image://pdf URI: %s", id_str)
                return self._create_placeholder(200, 200)

            doc_id = segments[0]
            page_index = int(segments[1])

            zoom = float(query_params.get("zoom", ["1.0"])[0])
            rotation = int(query_params.get("rot", ["0"])[0])
            is_thumb = "thumb" in query_params

            doc = self._doc_manager.get_document(doc_id)
            if not doc or not doc.is_open:
                return self._create_placeholder(200, 200)

            if is_thumb:
                # Thumbnails use a fixed low-resolution scale (dpi_scale=1.0 to keep them tiny)
                thumb_zoom = float(query_params.get("zoom", ["0.2"])[0])
                img = self._thumb_rasterizer.render_page_to_qimage(
                    doc, page_index, zoom=thumb_zoom, rotation=rotation, dpi_scale=1.0
                )
            else:
                img = self._rasterizer.render_page_to_qimage(
                    doc, page_index, zoom=zoom, rotation=rotation
                )

            if img is not None and not img.isNull():
                return img

            return self._create_placeholder(300, 400)
        except Exception as e:
            logger.error("Exception in requestImage for %s: %s", id_str, e)
            return self._create_placeholder(200, 200)

    def _create_placeholder(self, width: int, height: int) -> QImage:
        """Create an empty white placeholder image."""
        img = QImage(max(1, width), max(1, height), QImage.Format.Format_RGB888)
        img.fill(0xFFFFFF)
        return img
