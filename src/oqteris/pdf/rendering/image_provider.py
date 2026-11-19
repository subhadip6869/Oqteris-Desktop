"""Qt Quick QQuickAsyncImageProvider implementation serving rendered PDF pages to QML.

Threading model
---------------
Qt's scene graph calls ``requestImageResponse()`` on a **Qt thread-pool thread**, NOT
on the main/UI thread.  This means MuPDF decoding, pixmap allocation, and store_shrink
all happen off the UI thread — the main thread stays free to handle scroll events,
delivering silky-smooth scrolling even on large scanned PDFs.

``QQuickImageResponse`` is returned immediately while rendering happens in the background.
Qt connects the ``finished`` signal to know when the image is ready, then uploads the
texture to the GPU without any UI stutter.

Two separate caches prevent thumbnails from evicting full-resolution pages:
  _full_cache  : up to 12 full-resolution pages  / 80 MB  (what the user is reading)
  _thumb_cache : up to 20 thumbnail pages         / 24 MB  (side-panel strip)
"""

from __future__ import annotations

import gc
import logging
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import pymupdf

from PySide6.QtCore import QSize, QThread
from PySide6.QtGui import QImage
from PySide6.QtQuick import QQuickAsyncImageProvider, QQuickImageResponse

from oqteris.pdf.document.manager import get_document_manager
from oqteris.pdf.rendering.cache import PageRenderCache
from oqteris.pdf.rendering.rasterizer import PDFRasterizer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Async image response
# ---------------------------------------------------------------------------

class _PDFImageResponse(QQuickImageResponse):
    """Wraps a single async page-render job and signals Qt when complete."""

    def __init__(self) -> None:
        super().__init__()
        self._image: Optional[QImage] = None
        self._error: str = ""

    # Called from the thread-pool worker thread
    def _deliver(self, image: Optional[QImage], error: str = "") -> None:
        self._image = image
        self._error = error
        # finished() must be emitted from any thread – Qt marshals it correctly.
        self.finished.emit()

    # Qt scene-graph calls this on the render thread to get the image
    def textureFactory(self):  # type: ignore[override]
        from PySide6.QtQuick import QQuickTextureFactory
        if self._image and not self._image.isNull():
            return QQuickTextureFactory.textureFactoryForImage(self._image)
        # Blank white placeholder
        placeholder = QImage(1, 1, QImage.Format.Format_RGB888)
        placeholder.fill(0xFFFFFF)
        return QQuickTextureFactory.textureFactoryForImage(placeholder)

    def errorString(self) -> str:
        return self._error


# ---------------------------------------------------------------------------
# Async image provider
# ---------------------------------------------------------------------------

class PDFPageImageProvider(QQuickAsyncImageProvider):
    """Provides rasterized PDF pages to QML on a background thread pool.

    URI format:
    image://pdf/<doc_id>/<page_index>?zoom=1.5&rot=0&v=123
    image://pdf/<doc_id>/<page_index>?thumb=1&v=123
    """

    def __init__(self, rasterizer: Optional[PDFRasterizer] = None) -> None:
        super().__init__()

        # Full-resolution cache: keep 12 recently viewed pages (≤80 MB)
        self._full_cache = PageRenderCache(max_items=12, max_memory_mb=80)
        # Thumbnail cache: keep up to 20 small thumbnails (≤24 MB)
        self._thumb_cache = PageRenderCache(max_items=20, max_memory_mb=24)
        # Print-preview cache: isolated so previewing does not evict document pages (≤16 MB)
        self._preview_cache = PageRenderCache(max_items=8, max_memory_mb=16)

        self._rasterizer = rasterizer or PDFRasterizer(cache=self._full_cache)
        self._thumb_rasterizer = PDFRasterizer(cache=self._thumb_cache)
        self._preview_rasterizer = PDFRasterizer(cache=self._preview_cache)
        self._doc_manager = get_document_manager()

        # Thread pool: 2 workers is enough — MuPDF is single-threaded per-document
        # anyway, and more threads just cause lock contention on the document lock.
        self._pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="pdf-render")

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
        self._preview_cache.invalidate_page(doc_id, page_index)

    def invalidate_document(self, doc_id: str) -> None:
        self._full_cache.invalidate_document(doc_id)
        self._thumb_cache.invalidate_document(doc_id)
        self._preview_cache.invalidate_document(doc_id)

    def clear_preview_cache(self) -> None:
        """Drop all cached preview images and free native MuPDF store memory immediately."""
        self._preview_cache.clear()
        pymupdf.TOOLS.store_shrink(100)
        gc.collect()

    # ------------------------------------------------------------------
    # QQuickAsyncImageProvider entry-point (called on Qt thread-pool thread)
    # ------------------------------------------------------------------

    def requestImageResponse(self, id_str: str, requestedSize: QSize) -> _PDFImageResponse:
        """Return an image response immediately; actual render happens on a pool thread."""
        response = _PDFImageResponse()
        # Submit render job to our own pool so we control concurrency
        self._pool.submit(self._render, response, id_str)
        return response

    # ------------------------------------------------------------------
    # Internal render (runs on thread-pool worker, NOT the UI thread)
    # ------------------------------------------------------------------

    def _render(self, response: _PDFImageResponse, id_str: str) -> None:
        try:
            if "?" in id_str:
                path_part, query_part = id_str.split("?", 1)
                query_params = urllib.parse.parse_qs(query_part)
            else:
                path_part = id_str
                query_params = {}

            segments = path_part.strip("/").split("/")
            if len(segments) < 2:
                logger.warning("Invalid image://pdf URI: %s", id_str)
                response._deliver(None, "Invalid URI")
                return

            doc_id = segments[0]
            page_index = int(segments[1])
            zoom = float(query_params.get("zoom", ["1.0"])[0])
            rotation = int(query_params.get("rot", ["0"])[0])
            is_thumb = "thumb" in query_params
            is_preview = "preview" in query_params
            is_gray = "gray" in query_params or "grayscale" in query_params

            doc = self._doc_manager.get_document(doc_id)
            if not doc or not doc.is_open:
                response._deliver(None, "Document not open")
                return

            if is_thumb:
                thumb_zoom = float(query_params.get("zoom", ["0.2"])[0])
                img = self._thumb_rasterizer.render_page_to_qimage(
                    doc, page_index, zoom=thumb_zoom, rotation=rotation, dpi_scale=1.0, grayscale=is_gray
                )
            elif is_preview:
                img = self._preview_rasterizer.render_page_to_qimage(
                    doc, page_index, zoom=zoom, rotation=rotation, dpi_scale=1.0, grayscale=is_gray
                )
            else:
                img = self._rasterizer.render_page_to_qimage(
                    doc, page_index, zoom=zoom, rotation=rotation, grayscale=is_gray
                )

            response._deliver(img)

        except Exception as e:
            logger.error("Exception rendering %s: %s", id_str, e)
            response._deliver(None, str(e))

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def shutdown(self) -> None:
        """Shut down the render thread pool gracefully."""
        self._pool.shutdown(wait=False, cancel_futures=True)
