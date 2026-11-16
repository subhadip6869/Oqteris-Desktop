"""Controller exposing PDF annotation tools to QML."""

from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Property, Signal, Slot

from oqteris.pdf.annotations.manager import AnnotationService
from oqteris.pdf.document.manager import get_document_manager
from oqteris.ui.controllers.pdf_controller import PDFController

logger = logging.getLogger(__name__)


class AnnotationController(QObject):
    """Bridges QML markup interactions (highlights, ink, sticky notes, shapes) with AnnotationService."""

    annotationsChanged = Signal(int)  # page_index

    def __init__(self, pdf_controller: PDFController, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._pdf_controller = pdf_controller
        self._doc_manager = get_document_manager()

    @Slot(int, "QVariantList", str, result=bool)
    @Slot(int, "QVariantList", result=bool)
    def addHighlight(self, page_index: int, rects: list[Any], color_hex: str = "#FFEB3B") -> bool:
        doc = self._doc_manager.active_document
        if not doc:
            return False

        color_rgb = self._hex_to_rgb(color_hex)
        rect_list = [[float(r[0]), float(r[1]), float(r[2]), float(r[3])] for r in rects]
        success = AnnotationService.add_highlight(doc, page_index, rect_list, color=color_rgb)
        if success:
            self._pdf_controller.invalidateRender(page_index)
            self.annotationsChanged.emit(page_index)
        return success

    @Slot(int, "QVariantList", str, result=bool)
    @Slot(int, "QVariantList", result=bool)
    def addUnderline(self, page_index: int, rects: list[Any], color_hex: str = "#2196F3") -> bool:
        doc = self._doc_manager.active_document
        if not doc:
            return False

        color_rgb = self._hex_to_rgb(color_hex)
        rect_list = [[float(r[0]), float(r[1]), float(r[2]), float(r[3])] for r in rects]
        success = AnnotationService.add_underline(doc, page_index, rect_list, color=color_rgb)
        if success:
            self._pdf_controller.invalidateRender(page_index)
            self.annotationsChanged.emit(page_index)
        return success

    @Slot(int, "QVariantList", str, result=bool)
    @Slot(int, "QVariantList", result=bool)
    def addStrikethrough(self, page_index: int, rects: list[Any], color_hex: str = "#F44336") -> bool:
        doc = self._doc_manager.active_document
        if not doc:
            return False

        color_rgb = self._hex_to_rgb(color_hex)
        rect_list = [[float(r[0]), float(r[1]), float(r[2]), float(r[3])] for r in rects]
        success = AnnotationService.add_strikethrough(doc, page_index, rect_list, color=color_rgb)
        if success:
            self._pdf_controller.invalidateRender(page_index)
            self.annotationsChanged.emit(page_index)
        return success

    @Slot(int, float, float, str, str, str, result=bool)
    def addStickyNote(
        self,
        page_index: int,
        x: float,
        y: float,
        text: str,
        author: str = "",
        color_hex: str = "#FFD54F",
    ) -> bool:
        doc = self._doc_manager.active_document
        if not doc or not text.strip():
            return False

        color_rgb = self._hex_to_rgb(color_hex)
        success = AnnotationService.add_sticky_note(
            doc,
            page_index,
            point=(x, y),
            text=text,
            author=author,
            color=color_rgb,
        )
        if success:
            self._pdf_controller.invalidateRender(page_index)
            self.annotationsChanged.emit(page_index)
        return success

    @Slot(int, "QVariantList", str, float, result=bool)
    def addInkDrawing(
        self,
        page_index: int,
        polylines: list[Any],
        color_hex: str = "#000000",
        stroke_width: float = 2.0,
    ) -> bool:
        doc = self._doc_manager.active_document
        if not doc or not polylines:
            return False

        color_rgb = self._hex_to_rgb(color_hex)
        success = AnnotationService.add_ink(
            doc,
            page_index,
            polylines=polylines,
            color=color_rgb,
            stroke_width=stroke_width,
        )
        if success:
            self._pdf_controller.invalidateRender(page_index)
            self.annotationsChanged.emit(page_index)
        return success

    @Slot(int, str, "QVariantList", str, float, result=bool)
    def addShape(
        self,
        page_index: int,
        shape_type: str,
        rect: list[Any],
        color_hex: str = "#E53935",
        stroke_width: float = 2.0,
    ) -> bool:
        doc = self._doc_manager.active_document
        if not doc or len(rect) < 4:
            return False

        color_rgb = self._hex_to_rgb(color_hex)
        r = [float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])]
        success = AnnotationService.add_shape(
            doc,
            page_index,
            shape_type=shape_type,
            rect=r,
            stroke_color=color_rgb,
            stroke_width=stroke_width,
        )
        if success:
            self._pdf_controller.invalidateRender(page_index)
            self.annotationsChanged.emit(page_index)
        return success

    @Slot(int, "QVariantList", str, result=bool)
    def addStamp(self, page_index: int, rect: list[Any], stamp_text: str = "APPROVED") -> bool:
        doc = self._doc_manager.active_document
        if not doc or len(rect) < 4:
            return False

        r = [float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3])]
        success = AnnotationService.add_stamp(doc, page_index, r, stamp_text=stamp_text)
        if success:
            self._pdf_controller.invalidateRender(page_index)
            self.annotationsChanged.emit(page_index)
        return success

    @Slot(int, result="QVariantList")
    def getAnnotations(self, page_index: int) -> list[dict[str, Any]]:
        doc = self._doc_manager.active_document
        if not doc:
            return []
        annots = AnnotationService.get_annotations_for_page(doc, page_index)
        return [a.to_dict() for a in annots]

    @Slot(int, int, result=bool)
    def deleteAnnotation(self, page_index: int, annot_index: int) -> bool:
        doc = self._doc_manager.active_document
        if not doc:
            return False
        success = AnnotationService.delete_annotation(doc, page_index, annot_index)
        if success:
            self._pdf_controller.invalidateRender(page_index)
            self.annotationsChanged.emit(page_index)
        return success

    @staticmethod
    def _hex_to_rgb(hex_str: str) -> tuple[float, float, float]:
        hex_str = hex_str.lstrip("#")
        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16) / 255.0
            g = int(hex_str[2:4], 16) / 255.0
            b = int(hex_str[4:6], 16) / 255.0
            return (r, g, b)
        return (0.0, 0.0, 0.0)
