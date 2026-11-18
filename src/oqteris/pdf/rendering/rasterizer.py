"""PDF page rasterizer converting PyMuPDF pixmaps to PySide6 QImage objects with High-DPI support.

Memory management
-----------------
MuPDF (the C library behind PyMuPDF) maintains an internal *store* that caches decoded
images, fonts, and other resources for every page it touches.  For image-heavy PDFs
(e.g. scanned magazine pages at 4–5 MB/page) this store grows by ~5 MB per page even
after the Python pixmap object is deleted, because MuPDF keeps the decoded image in C
heap for potential reuse.

The fix is to call ``pymupdf.TOOLS.store_shrink(100)`` after every render.  This tells
MuPDF to discard everything it can from its internal cache.  In practice this keeps RSS
completely flat (< 5 MB drift over hundreds of pages) with no measurable render-speed
penalty, since the dominant cost is JPEG/PNG decoding and rasterisation, not the cache
lookup.
"""

from __future__ import annotations

import gc
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


def _flush_mupdf_store() -> None:
    """Release MuPDF's internal decoded-resource store.

    MuPDF caches decoded images, fonts, CMaps, etc. in a process-global C-heap store.
    After rendering a page we no longer need any of that cached data, so evicting 100 %
    of it immediately keeps native (non-Python) RAM flat even when scrolling through
    hundreds of large scanned pages.
    """
    try:
        pymupdf.TOOLS.store_shrink(100)
    except Exception:
        pass  # Defensive – should never fail, but never crash the renderer for it


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

        # Return cached image immediately — no MuPDF work needed.
        if use_cache:
            cached_img = self.cache.get(document.doc_id, page_index, zoom, rotation)
            if cached_img is not None:
                return cached_img

        raw_doc = document.raw_doc
        if raw_doc is None:
            return None

        page = None
        pix = None
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

            # Deep-copy pixel bytes into QImage so it fully owns the buffer, then
            # immediately release both the pixmap and the page reference so MuPDF
            # can drop any page-local resources as soon as possible.
            qimage = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                QImage.Format.Format_RGB888,
            ).copy()

            # --- Critical: free native MuPDF memory before returning ---
            # 1. Release the C pixmap buffer (RGB pixel data).
            del pix
            pix = None
            # 2. Release the page reference so MuPDF can free page-local structures.
            del page
            page = None
            # 3. Flush MuPDF's internal decoded-resource store (decoded JPEG/PNG images,
            #    fonts, CMaps, etc.).  Without this, native RSS grows ~5 MB per page on
            #    image-heavy PDFs (e.g. scanned books) even after del pix / del page.
            _flush_mupdf_store()

            # Set Device Pixel Ratio so Qt Quick handles High-DPI correctly.
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
        finally:
            # Belt-and-suspenders: ensure native resources are always freed even on error.
            if pix is not None:
                del pix
            if page is not None:
                del page
            gc.collect(0)  # generation-0 only – fast, frees short-lived objects immediately
