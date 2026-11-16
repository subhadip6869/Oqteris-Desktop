"""Hyperlink and internal page link creation and manipulation."""

from __future__ import annotations

import logging
from typing import Any

import pymupdf

from oqteris.pdf.document.document import PDFDocument

logger = logging.getLogger(__name__)


class LinkEditorService:
    """Handles adding and inspecting links in PDF pages."""

    @staticmethod
    def get_links(document: PDFDocument, page_index: int) -> list[dict[str, Any]]:
        if not document.is_open or not (0 <= page_index < document.page_count):
            return []

        try:
            page = document.raw_doc[page_index]
            links = page.get_links()
            return [
                {
                    "kind": l.get("kind"),
                    "uri": l.get("uri", ""),
                    "page": l.get("page", -1),
                    "from": [float(l["from"].x0), float(l["from"].y0), float(l["from"].x1), float(l["from"].y1)],
                }
                for l in links
            ]
        except Exception as e:
            logger.error("Failed to get links on page %d: %s", page_index, e)
            return []

    @staticmethod
    def add_uri_link(document: PDFDocument, page_index: int, rect: list[float], uri: str) -> bool:
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            r = pymupdf.Rect(rect[0], rect[1], rect[2], rect[3])
            link_dict = {
                "kind": pymupdf.LINK_URI,
                "from": r,
                "uri": uri,
            }
            page.insert_link(link_dict)
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to insert URI link: %s", e)
            return False

    @staticmethod
    def add_page_link(document: PDFDocument, page_index: int, rect: list[float], target_page: int) -> bool:
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            r = pymupdf.Rect(rect[0], rect[1], rect[2], rect[3])
            link_dict = {
                "kind": pymupdf.LINK_GOTO,
                "from": r,
                "page": target_page,
            }
            page.insert_link(link_dict)
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to insert goto page link: %s", e)
            return False
