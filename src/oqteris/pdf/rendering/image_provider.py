"""Qt Quick QQuickImageProvider implementation serving rendered PDF pages to QML."""

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
    """

    def __init__(self, rasterizer: Optional[PDFRasterizer] = None) -> None:
        super().__init__(QQuickImageProvider.ImageType.Image)
        self._cache = PageRenderCache()
        self._rasterizer = rasterizer or PDFRasterizer(cache=self._cache)
        self._doc_manager = get_document_manager()

    @property
    def cache(self) -> PageRenderCache:
        return self._cache

    @property
    def rasterizer(self) -> PDFRasterizer:
        return self._rasterizer

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

            # Handle thumbnail mode
            is_thumb = "thumb" in query_params

            doc = self._doc_manager.get_document(doc_id)
            if not doc or not doc.is_open:
                return self._create_placeholder(200, 200)

            if is_thumb:
                # Fixed thumbnail resolution (e.g. 0.25 zoom)
                thumb_zoom = float(query_params.get("zoom", ["0.2"])[0])
                img = self._rasterizer.render_page_to_qimage(doc, page_index, zoom=thumb_zoom, rotation=rotation, dpi_scale=1.5)
            else:
                img = self._rasterizer.render_page_to_qimage(doc, page_index, zoom=zoom, rotation=rotation)

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
