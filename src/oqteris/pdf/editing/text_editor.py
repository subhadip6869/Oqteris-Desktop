"""PDF direct text insertion and editing operations."""

from __future__ import annotations

import logging
from typing import Optional

import pymupdf

from oqteris.core.exceptions import PDFError
from oqteris.pdf.document.document import PDFDocument

logger = logging.getLogger(__name__)


class TextEditorService:
    """Handles text insertion and text replacement in PDF pages."""

    @staticmethod
    def insert_text(
        document: PDFDocument,
        page_index: int,
        point: tuple[float, float],
        text: str,
        font_size: float = 12.0,
        font_name: str = "helv",
        color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> bool:
        """Insert arbitrary text at coordinates (x, y)."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            pt = pymupdf.Point(point[0], point[1])
            page.insert_text(
                pt,
                text,
                fontsize=font_size,
                fontname=font_name,
                color=color,
            )
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to insert text at (%f, %f): %s", point[0], point[1], e)
            return False

    @staticmethod
    def replace_text(
        document: PDFDocument,
        page_index: int,
        rect: list[float],
        new_text: str,
        font_size: float = 12.0,
        font_name: str = "helv",
        color: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> bool:
        """Replace existing text within a bounding box using redaction and text insertion."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            r = pymupdf.Rect(rect[0], rect[1], rect[2], rect[3])

            # Step 1: Redact original content cleanly without black border
            page.add_redact_annot(r, fill=(1.0, 1.0, 1.0))
            page.apply_redactions()

            # Step 2: Insert replacement text starting at bottom-left baseline of rectangle
            baseline_y = r.y0 + font_size
            pt = pymupdf.Point(r.x0, min(baseline_y, r.y1))
            page.insert_text(
                pt,
                new_text,
                fontsize=font_size,
                fontname=font_name,
                color=color,
            )
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to replace text in rect %s: %s", rect, e)
            return False
