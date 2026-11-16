"""Image insertion and replacement operations for PDF pages."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pymupdf

from oqteris.core.exceptions import PDFError
from oqteris.pdf.document.document import PDFDocument

logger = logging.getLogger(__name__)


class ImageEditorService:
    """Handles inserting images onto pages or replacing existing image XObjects."""

    @staticmethod
    def insert_image(
        document: PDFDocument,
        page_index: int,
        rect: list[float],
        image_path: str | Path,
    ) -> bool:
        """Insert an external image file onto a page within the given rectangle."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        img_path = Path(image_path).resolve()
        if not img_path.exists():
            logger.error("Image file not found: %s", img_path)
            return False

        try:
            page = document.raw_doc[page_index]
            r = pymupdf.Rect(rect[0], rect[1], rect[2], rect[3])
            page.insert_image(r, filename=str(img_path), keep_proportion=True)
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to insert image %s: %s", img_path, e)
            return False

    @staticmethod
    def insert_image_bytes(
        document: PDFDocument,
        page_index: int,
        rect: list[float],
        image_bytes: bytes,
    ) -> bool:
        """Insert in-memory image bytes (e.g. signature drawing) onto a page."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            r = pymupdf.Rect(rect[0], rect[1], rect[2], rect[3])
            page.insert_image(r, stream=image_bytes, keep_proportion=True)
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to insert image stream: %s", e)
            return False
