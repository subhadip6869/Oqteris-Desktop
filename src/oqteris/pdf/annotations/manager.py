"""Annotation service managing PDF annotations via PyMuPDF."""

from __future__ import annotations

import logging
from typing import Any, Optional

import pymupdf

from oqteris.core.exceptions import PDFError
from oqteris.pdf.annotations.models import AnnotationData, AnnotationType
from oqteris.pdf.document.document import PDFDocument

logger = logging.getLogger(__name__)


class AnnotationService:
    """Provides annotation operations (add, modify, delete) on PDF documents."""

    @staticmethod
    def get_annotations_for_page(document: PDFDocument, page_index: int) -> list[AnnotationData]:
        """Retrieve all annotations present on a page."""
        results: list[AnnotationData] = []
        if not document.is_open or not (0 <= page_index < document.page_count):
            return results

        raw_doc = document.raw_doc
        if raw_doc is None:
            return results

        try:
            page = raw_doc[page_index]
            for idx, annot in enumerate(page.annots()):
                annot_type_enum = AnnotationService._map_annot_type(annot.type[0])
                if annot_type_enum is None:
                    continue

                rect = [float(annot.rect.x0), float(annot.rect.y0), float(annot.rect.x1), float(annot.rect.y1)]
                colors = annot.colors
                stroke = colors.get("stroke", [1.0, 1.0, 0.0]) if colors else [1.0, 1.0, 0.0]
                fill = colors.get("fill", None) if colors else None

                results.append(
                    AnnotationData(
                        annot_id=str(idx),
                        page_index=page_index,
                        annot_type=annot_type_enum,
                        rect=rect,
                        content=annot.info.get("content", ""),
                        author=annot.info.get("title", ""),
                        color_rgb=list(stroke) if stroke else [1.0, 1.0, 0.0],
                        fill_rgb=list(fill) if fill else None,
                        opacity=annot.opacity,
                        stroke_width=annot.border.get("width", 1.5) if hasattr(annot, "border") and annot.border else 1.5,
                        creation_date=annot.info.get("creationDate", ""),
                        modification_date=annot.info.get("modDate", ""),
                    )
                )
        except Exception as e:
            logger.error("Failed to read annotations on page %d: %s", page_index, e)

        return results

    @staticmethod
    def _map_annot_type(raw_type: int) -> Optional[AnnotationType]:
        mapping = {
            pymupdf.PDF_ANNOT_HIGHLIGHT: AnnotationType.HIGHLIGHT,
            pymupdf.PDF_ANNOT_UNDERLINE: AnnotationType.UNDERLINE,
            pymupdf.PDF_ANNOT_STRIKE_OUT: AnnotationType.STRIKEOUT,
            pymupdf.PDF_ANNOT_TEXT: AnnotationType.NOTE,
            pymupdf.PDF_ANNOT_INK: AnnotationType.INK,
            pymupdf.PDF_ANNOT_SQUARE: AnnotationType.RECTANGLE,
            pymupdf.PDF_ANNOT_CIRCLE: AnnotationType.CIRCLE,
            pymupdf.PDF_ANNOT_LINE: AnnotationType.LINE,
            pymupdf.PDF_ANNOT_STAMP: AnnotationType.STAMP,
            pymupdf.PDF_ANNOT_FREE_TEXT: AnnotationType.TEXT,
            pymupdf.PDF_ANNOT_LINK: AnnotationType.LINK,
        }
        return mapping.get(raw_type)

    @staticmethod
    def add_highlight(
        document: PDFDocument,
        page_index: int,
        rects: list[list[float]],
        color: tuple[float, float, float] = (1.0, 0.9, 0.0),
        author: str = "",
    ) -> bool:
        """Add a text highlight annotation over given rectangles."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            for r in rects:
                annot = page.add_highlight_annot(pymupdf.Rect(r[0], r[1], r[2], r[3]))
                annot.set_colors(stroke=color)
                if author:
                    info = annot.info
                    info["title"] = author
                    annot.set_info(info)
                annot.update()

            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to add highlight: %s", e)
            return False

    @staticmethod
    def add_underline(
        document: PDFDocument,
        page_index: int,
        rects: list[list[float]],
        color: tuple[float, float, float] = (0.0, 0.4, 0.9),
    ) -> bool:
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            for r in rects:
                annot = page.add_underline_annot(pymupdf.Rect(r[0], r[1], r[2], r[3]))
                annot.set_colors(stroke=color)
                annot.update()
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to add underline: %s", e)
            return False

    @staticmethod
    def add_strikethrough(
        document: PDFDocument,
        page_index: int,
        rects: list[list[float]],
        color: tuple[float, float, float] = (0.9, 0.1, 0.1),
    ) -> bool:
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            for r in rects:
                annot = page.add_strikeout_annot(pymupdf.Rect(r[0], r[1], r[2], r[3]))
                annot.set_colors(stroke=color)
                annot.update()
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to add strikethrough: %s", e)
            return False

    @staticmethod
    def add_sticky_note(
        document: PDFDocument,
        page_index: int,
        point: tuple[float, float],
        text: str,
        author: str = "",
        color: tuple[float, float, float] = (1.0, 0.85, 0.2),
    ) -> bool:
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            annot = page.add_text_annot(pymupdf.Point(point[0], point[1]), text)
            annot.set_colors(stroke=color)
            if author:
                info = annot.info
                info["title"] = author
                annot.set_info(info)
            annot.update()
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to add sticky note: %s", e)
            return False

    @staticmethod
    def add_ink(
        document: PDFDocument,
        page_index: int,
        polylines: list[list[list[float]]],
        color: tuple[float, float, float] = (0.0, 0.0, 0.0),
        stroke_width: float = 2.0,
        opacity: float = 1.0,
    ) -> bool:
        """Add freehand drawing annotation."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            points_list = []
            for stroke in polylines:
                pt_stroke = [(float(pt[0]), float(pt[1])) for pt in stroke]
                if len(pt_stroke) >= 2:
                    points_list.append(pt_stroke)

            if not points_list:
                return False

            annot = page.add_ink_annot(points_list)
            annot.set_colors(stroke=color)
            annot.set_border(width=stroke_width)
            annot.set_opacity(opacity)
            annot.update()
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to add ink drawing: %s", e)
            return False

    @staticmethod
    def add_shape(
        document: PDFDocument,
        page_index: int,
        shape_type: str,  # "rectangle", "circle", "line", "arrow"
        rect: list[float],
        stroke_color: tuple[float, float, float] = (0.8, 0.0, 0.0),
        fill_color: Optional[tuple[float, float, float]] = None,
        stroke_width: float = 2.0,
        opacity: float = 1.0,
    ) -> bool:
        """Add geometric shape annotation."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            r = pymupdf.Rect(rect[0], rect[1], rect[2], rect[3])

            if shape_type == "rectangle":
                annot = page.add_rect_annot(r)
            elif shape_type == "circle":
                annot = page.add_circle_annot(r)
            elif shape_type == "line":
                p1 = pymupdf.Point(rect[0], rect[1])
                p2 = pymupdf.Point(rect[2], rect[3])
                annot = page.add_line_annot(p1, p2)
            elif shape_type == "arrow":
                p1 = pymupdf.Point(rect[0], rect[1])
                p2 = pymupdf.Point(rect[2], rect[3])
                annot = page.add_line_annot(p1, p2)
                annot.set_line_ends(pymupdf.PDF_ANNOT_LE_NONE, pymupdf.PDF_ANNOT_LE_CLOSED_ARROW)
            else:
                return False

            annot.set_colors(stroke=stroke_color, fill=fill_color)
            annot.set_border(width=stroke_width)
            annot.set_opacity(opacity)
            annot.update()
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to add shape annotation: %s", e)
            return False

    @staticmethod
    def add_stamp(
        document: PDFDocument,
        page_index: int,
        rect: list[float],
        stamp_text: str = "APPROVED",
        color: tuple[float, float, float] = (0.1, 0.6, 0.1),
    ) -> bool:
        """Add a text stamp annotation."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            r = pymupdf.Rect(rect[0], rect[1], rect[2], rect[3])

            # Map common standard stamps or draw custom stamp text
            stamp_id_map = {
                "APPROVED": pymupdf.STAMP_Approved,
                "CONFIDENTIAL": pymupdf.STAMP_Confidential,
                "DRAFT": pymupdf.STAMP_Draft,
                "FINAL": pymupdf.STAMP_Final,
                "COMPLETED": pymupdf.STAMP_Departmental,
            }
            stamp_val = stamp_id_map.get(stamp_text.upper(), pymupdf.STAMP_Approved)
            annot = page.add_stamp_annot(r, stamp=stamp_val)
            annot.set_colors(stroke=color)
            annot.update()
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to add stamp: %s", e)
            return False

    @staticmethod
    def delete_annotation(document: PDFDocument, page_index: int, annot_index: int) -> bool:
        """Delete an annotation by index on page."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            annots = list(page.annots())
            if 0 <= annot_index < len(annots):
                page.delete_annot(annots[annot_index])
                document.is_modified = True
                return True
        except Exception as e:
            logger.error("Failed to delete annotation %d on page %d: %s", annot_index, page_index, e)
        return False
