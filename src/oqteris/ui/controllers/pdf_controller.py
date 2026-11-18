"""PDF controller exposing document operations, navigation, zoom, and search to QML."""

from __future__ import annotations

import logging
import platform
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QObject, Property, QUrl, Signal, Slot
from PySide6.QtGui import QClipboard, QGuiApplication

from oqteris.config.settings import get_settings_manager
from oqteris.core.constants import (
    DEFAULT_ZOOM_LEVEL,
    MAX_ZOOM_LEVEL,
    MIN_ZOOM_LEVEL,
    ZOOM_STEP,
)
from oqteris.core.exceptions import PDFCorruptedError, PDFEncryptedError, PDFError
from oqteris.pdf.document.document import PDFDocument
from oqteris.pdf.document.manager import DocumentManager, get_document_manager
from oqteris.pdf.document.models import DocumentMetadata, SearchMatch
from oqteris.pdf.rendering.image_provider import PDFPageImageProvider
from oqteris.ui.controllers.app_controller import AppController

logger = logging.getLogger(__name__)


class PDFController(QObject):
    """Coordinates PDF viewing, tab switching, zoom, rotation, and document search for QML."""

    documentChanged = Signal()
    pageChanged = Signal(int)
    zoomChanged = Signal(float)
    rotationChanged = Signal(int)
    displayModeChanged = Signal(str)
    tabsChanged = Signal()
    tocChanged = Signal()
    searchChanged = Signal()
    selectionRectsChanged = Signal()
    selectedTextChanged = Signal(str)
    selectedObjectChanged = Signal()
    selectAllTriggered = Signal()
    renderInvalidated = Signal(int)  # page_index (-1 for all pages)
    errorOccurred = Signal(str, str)  # title, message
    passwordPromptRequested = Signal(str)  # file_path

    def __init__(
        self,
        app_controller: Optional[AppController] = None,
        image_provider: Optional[PDFPageImageProvider] = None,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._doc_manager = get_document_manager()
        self._app_controller = app_controller
        self._image_provider = image_provider
        self._settings = get_settings_manager()

        self._current_page = 0
        self._zoom_level = self._settings.get("default_zoom", 1.0)
        self._display_mode = self._settings.get("page_display_mode", "continuous")
        self._render_nonce = 1

        # Search state
        self._search_query = ""
        self._search_results: list[SearchMatch] = []
        self._search_result_index = -1

        # Text & Object selection state
        self._selected_text = ""
        self._selection_page_index = -1
        self._selection_rects: list[dict[str, Any]] = []
        self._selected_object: dict[str, Any] = {}
        self._words_cache: dict[int, list[Any]] = {}
        self._objects_cache: dict[int, list[dict[str, Any]]] = {}

    def _reset_selection(self) -> None:
        self._selected_text = ""
        self._selection_page_index = -1
        self._selection_rects = []
        self._selected_object = {}
        self._words_cache.clear()
        self._objects_cache.clear()
        self.selectionRectsChanged.emit()
        self.selectedTextChanged.emit("")
        self.selectedObjectChanged.emit()

    # --- Document Properties ---

    @Property(int, notify=selectionRectsChanged)
    def selectionPageIndex(self) -> int:
        return self._selection_page_index

    @Property("QVariantList", notify=selectionRectsChanged)
    def selectionRects(self) -> list[dict[str, Any]]:
        return self._selection_rects

    @Property(str, notify=selectedTextChanged)
    def selectedText(self) -> str:
        return self._selected_text

    @Property("QVariantMap", notify=selectedObjectChanged)
    def selectedObject(self) -> dict[str, Any]:
        return self._selected_object

    @Property(bool, notify=selectedObjectChanged)
    def hasSelectedObject(self) -> bool:
        return bool(self._selected_object)

    @Property(bool, notify=documentChanged)
    def hasDocument(self) -> bool:
        doc = self._doc_manager.active_document
        return doc is not None and doc.is_open

    @Property(str, notify=documentChanged)
    def activeDocId(self) -> str:
        return self._doc_manager.active_doc_id or ""

    @Property(str, notify=documentChanged)
    def fileName(self) -> str:
        doc = self._doc_manager.active_document
        return doc.file_path.name if doc and doc.file_path else "No Document"

    @Property(str, notify=documentChanged)
    def filePath(self) -> str:
        doc = self._doc_manager.active_document
        return str(doc.file_path) if doc and doc.file_path else ""

    @Property(int, notify=documentChanged)
    def pageCount(self) -> int:
        doc = self._doc_manager.active_document
        return doc.page_count if doc else 0

    @Property(bool, notify=documentChanged)
    def isModified(self) -> bool:
        doc = self._doc_manager.active_document
        return doc.is_modified if doc else False

    @Property(int, notify=pageChanged)
    def currentPage(self) -> int:
        return self._current_page

    @currentPage.setter
    def currentPage(self, val: int) -> None:
        doc = self._doc_manager.active_document
        if not doc or doc.page_count == 0:
            val = 0
        else:
            val = max(0, min(val, doc.page_count - 1))

        if self._current_page != val:
            self._current_page = val
            self.pageChanged.emit(self._current_page)

    @Property(float, notify=zoomChanged)
    def zoomLevel(self) -> float:
        return self._zoom_level

    @zoomLevel.setter
    def zoomLevel(self, val: float) -> None:
        clamped = max(MIN_ZOOM_LEVEL, min(round(val, 2), MAX_ZOOM_LEVEL))
        if self._zoom_level != clamped:
            self._zoom_level = clamped
            self.zoomChanged.emit(self._zoom_level)

    @Property(int, notify=documentChanged)
    def rotation(self) -> int:
        doc = self._doc_manager.active_document
        if doc and 0 <= self._current_page < doc.page_count:
            return doc.get_page_geometry(self._current_page).rotation
        return 0

    @Property(str, notify=displayModeChanged)
    def displayMode(self) -> str:
        return self._display_mode

    @displayMode.setter
    def displayMode(self, mode: str) -> None:
        if mode in ("single", "continuous", "facing") and self._display_mode != mode:
            self._display_mode = mode
            self._settings.set("page_display_mode", mode)
            self.displayModeChanged.emit(self._display_mode)

    @Property(int, notify=renderInvalidated)
    def renderNonce(self) -> int:
        return self._render_nonce

    @Property("QVariantList", notify=tabsChanged)
    def openTabs(self) -> list[dict[str, Any]]:
        return self._doc_manager.list_open_documents()

    @Property("QVariantList", notify=tocChanged)
    def tableOfContents(self) -> list[dict[str, Any]]:
        doc = self._doc_manager.active_document
        if not doc:
            return []
        items = doc.get_table_of_contents()
        return [item.to_dict() for item in items]

    @Property("QVariantMap", notify=documentChanged)
    def metadata(self) -> dict[str, Any]:
        doc = self._doc_manager.active_document
        if not doc:
            return {}
        return doc.get_metadata().to_dict()

    @Property("QVariantList", notify=documentChanged)
    def pageGeometries(self) -> list[dict[str, Any]]:
        doc = self._doc_manager.active_document
        if not doc:
            return []
        geoms = []
        for i in range(doc.page_count):
            g = doc.get_page_geometry(i)
            geoms.append({
                "pageIndex": i,
                "width": g.width,
                "height": g.height,
                "rotation": g.rotation,
                "aspectRatio": g.aspect_ratio,
            })
        return geoms

    # --- Document Lifecycle Slots ---

    @Slot(str, str)
    @Slot(str)
    def openDocument(self, file_path: str, password: str = "") -> bool:
        """Open a PDF document, handling passwords and errors."""
        # Normalize file URI if given as file:///...
        if file_path.startswith("file:"):
            file_path = QUrl(file_path).toLocalFile()

        path = Path(file_path).resolve()
        if not path.is_file():
            self.errorOccurred.emit("File Not Found", f"The file '{path}' does not exist.")
            return False

        try:
            doc, meta = self._doc_manager.open_document(path, password=password)
            self._current_page = 0
            self._reset_selection()
            self.documentChanged.emit()
            self.pageChanged.emit(0)
            self.tabsChanged.emit()
            self.tocChanged.emit()

            if self._app_controller:
                self._app_controller.record_opened_file(
                    str(path),
                    size=meta.file_size_bytes,
                    pages=meta.page_count,
                )
            return True
        except PDFEncryptedError:
            self.passwordPromptRequested.emit(str(path))
            return False
        except PDFCorruptedError as e:
            self.errorOccurred.emit("Corrupted PDF", str(e))
            return False
        except Exception as e:
            logger.error("Failed to open %s: %s", path, e)
            self.errorOccurred.emit("Open Error", f"Unable to open document: {e}")
            return False

    @Slot(str)
    @Slot()
    def closeDocument(self, doc_id: str = "") -> None:
        target_id = doc_id or self.activeDocId
        if not target_id:
            return

        was_active = (target_id == self.activeDocId)

        if self._image_provider:
            self._image_provider.invalidate_document(target_id)

        self._doc_manager.close_document(target_id)
        if was_active:
            self._current_page = 0
            self._reset_selection()
            self.pageChanged.emit(0)

        self.documentChanged.emit()
        self.tabsChanged.emit()
        self.tocChanged.emit()

    @Slot(str)
    def switchTab(self, doc_id: str) -> None:
        if doc_id != self.activeDocId and self._doc_manager.get_document(doc_id):
            self._doc_manager.active_doc_id = doc_id
            self._current_page = 0
            self._reset_selection()
            self.documentChanged.emit()
            self.pageChanged.emit(0)
            self.tabsChanged.emit()
            self.tocChanged.emit()

    @Slot()
    def saveDocument(self) -> bool:
        doc = self._doc_manager.active_document
        if not doc:
            return False
        try:
            doc.save()
            self.documentChanged.emit()
            return True
        except Exception as e:
            self.errorOccurred.emit("Save Error", str(e))
            return False

    @Slot(str)
    def saveDocumentAs(self, target_path: str) -> bool:
        doc = self._doc_manager.active_document
        if not doc:
            return False

        if target_path.startswith("file:"):
            target_path = QUrl(target_path).toLocalFile()

        try:
            doc.save(target_path=target_path)
            self.documentChanged.emit()
            self.tabsChanged.emit()
            if self._app_controller:
                self._app_controller.record_opened_file(str(target_path), pages=doc.page_count)
            return True
        except Exception as e:
            self.errorOccurred.emit("Save As Error", str(e))
            return False

    # --- Navigation Slots ---

    @Slot(int)
    def goToPage(self, page_index: int) -> None:
        self.currentPage = page_index

    @Slot()
    def nextPage(self) -> None:
        self.currentPage += 1

    @Slot()
    def prevPage(self) -> None:
        self.currentPage -= 1

    @Slot()
    def firstPage(self) -> None:
        self.currentPage = 0

    @Slot()
    def lastPage(self) -> None:
        doc = self._doc_manager.active_document
        if doc:
            self.currentPage = doc.page_count - 1

    # --- Zoom & Rotation Slots ---

    @Slot(float)
    def setZoom(self, level: float) -> None:
        self.zoomLevel = level

    @Slot()
    def zoomIn(self) -> None:
        self.zoomLevel = self._zoom_level + ZOOM_STEP

    @Slot()
    def zoomOut(self) -> None:
        self.zoomLevel = self._zoom_level - ZOOM_STEP

    @Slot()
    def actualSize(self) -> None:
        self.zoomLevel = 1.0

    @Slot(float)
    def fitWidth(self, viewport_width: float) -> None:
        doc = self._doc_manager.active_document
        if not doc or viewport_width <= 50:
            return
        geom = doc.get_page_geometry(self._current_page)
        if geom.width > 0:
            # Leave 40px margin
            available = max(50.0, viewport_width - 40.0)
            self.zoomLevel = available / geom.width

    @Slot(float, float)
    def fitPage(self, viewport_width: float, viewport_height: float) -> None:
        doc = self._doc_manager.active_document
        if not doc or viewport_width <= 50 or viewport_height <= 50:
            return
        geom = doc.get_page_geometry(self._current_page)
        if geom.width > 0 and geom.height > 0:
            w_ratio = (viewport_width - 40.0) / geom.width
            h_ratio = (viewport_height - 40.0) / geom.height
            self.zoomLevel = min(w_ratio, h_ratio)

    @Slot(int)
    @Slot()
    def rotatePage(self, degrees: int = 90) -> None:
        doc = self._doc_manager.active_document
        if doc:
            doc.rotate_page(self._current_page, degrees)
            self.invalidateRender(self._current_page)
            self.documentChanged.emit()

    def invalidateRender(self, page_index: int = -1) -> None:
        doc = self._doc_manager.active_document
        if not doc:
            return
        if self._image_provider:
            if page_index >= 0:
                self._image_provider.invalidate_page(doc.doc_id, page_index)
            else:
                self._image_provider.invalidate_document(doc.doc_id)

        self._render_nonce += 1
        self.renderInvalidated.emit(page_index)

    # --- Search Slots & Properties ---

    @Property(str, notify=searchChanged)
    def searchQuery(self) -> str:
        return self._search_query

    @Property("QVariantList", notify=searchChanged)
    def searchResults(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self._search_results]

    @Property(int, notify=searchChanged)
    def currentSearchResultIndex(self) -> int:
        return self._search_result_index

    @Property(int, notify=searchChanged)
    def searchMatchCount(self) -> int:
        return len(self._search_results)

    @Slot(str, bool)
    @Slot(str)
    def search(self, query: str, case_sensitive: bool = False) -> int:
        self._search_query = query.strip()
        doc = self._doc_manager.active_document
        if not doc or not self._search_query:
            self._search_results = []
            self._search_result_index = -1
            self.searchChanged.emit()
            return 0

        self._search_results = doc.search_text(self._search_query, case_sensitive=case_sensitive)
        self._search_result_index = 0 if self._search_results else -1

        if self._search_results:
            # Navigate to first match
            self.currentPage = self._search_results[0].page_index

        self.searchChanged.emit()
        return len(self._search_results)

    @Slot()
    def nextSearchResult(self) -> None:
        if not self._search_results:
            return
        self._search_result_index = (self._search_result_index + 1) % len(self._search_results)
        self.currentPage = self._search_results[self._search_result_index].page_index
        self.searchChanged.emit()

    @Slot()
    def prevSearchResult(self) -> None:
        if not self._search_results:
            return
        self._search_result_index = (self._search_result_index - 1 + len(self._search_results)) % len(self._search_results)
        self.currentPage = self._search_results[self._search_result_index].page_index
        self.searchChanged.emit()

    @Slot()
    def clearSearch(self) -> None:
        self._search_query = ""
        self._search_results = []
        self._search_result_index = -1
        self.searchChanged.emit()

    @Slot(int, result=str)
    def extractText(self, page_index: int) -> str:
        doc = self._doc_manager.active_document
        if doc:
            return doc.extract_text_page(page_index)
        return ""

    @Slot(int, float, float, float, float)
    def updateSelection(self, page_index: int, start_x: float, start_y: float, cur_x: float, cur_y: float) -> None:
        doc = self._doc_manager.active_document
        if not doc or not doc.is_open or doc.raw_doc is None:
            self.clearSelection()
            return
        if not (0 <= page_index < len(doc.raw_doc)):
            self.clearSelection()
            return

        page = doc.raw_doc[page_index]
        if page_index not in self._words_cache:
            self._words_cache[page_index] = page.get_text("words")

        words = self._words_cache[page_index]
        if not words:
            self.clearSelection()
            return

        # Find word nearest to (start_x, start_y) and (cur_x, cur_y)
        def find_word_index(x: float, y: float) -> int:
            for i, w in enumerate(words):
                if w[0] <= x <= w[2] and w[1] <= y <= w[3]:
                    return i
            same_line = []
            for i, w in enumerate(words):
                if (w[1] - 4) <= y <= (w[3] + 4):
                    same_line.append((i, w))
            if same_line:
                return min(same_line, key=lambda it: min(abs(it[1][0] - x), abs(it[1][2] - x)))[0]
            return min(enumerate(words), key=lambda it: (it[1][0] + it[1][2] - 2 * x) ** 2 + (it[1][1] + it[1][3] - 2 * y) ** 2 * 9)[0]

        i1 = find_word_index(start_x, start_y)
        i2 = find_word_index(cur_x, cur_y)
        if i1 < 0 or i2 < 0:
            self.clearSelection()
            return

        start_idx = min(i1, i2)
        end_idx = max(i1, i2)
        sel_words = words[start_idx : end_idx + 1]

        # Group by (block, line) preserving reading order
        lines: list[list[Any]] = []
        curr_key = None
        curr_line: list[Any] = []
        for w in sel_words:
            key = (w[5], w[6])
            if key != curr_key:
                if curr_line:
                    lines.append(curr_line)
                curr_key = key
                curr_line = [w]
            else:
                curr_line.append(w)
        if curr_line:
            lines.append(curr_line)

        line_rects = []
        line_texts = []
        for l_words in lines:
            rx0 = min(w[0] for w in l_words)
            ry0 = min(w[1] for w in l_words)
            rx1 = max(w[2] for w in l_words)
            ry1 = max(w[3] for w in l_words)
            line_rects.append({"x0": rx0, "y0": ry0, "x1": rx1, "y1": ry1})
            line_texts.append(" ".join(w[4] for w in l_words))

        # Clear any object selection when selecting text
        if self._selected_object:
            self._selected_object = {}
            self.selectedObjectChanged.emit()

        self._selection_page_index = page_index
        self._selection_rects = line_rects
        self._selected_text = "\n".join(line_texts)
        self.selectionRectsChanged.emit()
        self.selectedTextChanged.emit(self._selected_text)

    @Slot(int, float, float, float, float, result=str)
    def extractTextInRect(self, page_index: int, x0: float, y0: float, x1: float, y1: float) -> str:
        self.updateSelection(page_index, x0, y0, x1, y1)
        return self._selected_text

    @Slot(int, result="QVariantList")
    def getPageObjects(self, page_index: int) -> list[dict[str, Any]]:
        """Return non-text objects (images and vector shapes) on the specified page."""
        doc = self._doc_manager.active_document
        if not doc or not doc.is_open or doc.raw_doc is None:
            return []
        if not (0 <= page_index < len(doc.raw_doc)):
            return []

        if page_index in self._objects_cache:
            return self._objects_cache[page_index]

        page = doc.raw_doc[page_index]
        page_rect = page.rect
        objects: list[dict[str, Any]] = []

        # 1. Embedded raster images
        try:
            for img_info in page.get_images():
                xref = img_info[0]
                for r in page.get_image_rects(xref):
                    if r.width >= 5 and r.height >= 5:
                        objects.append({
                            "type": "image",
                            "xref": xref,
                            "x0": float(r.x0),
                            "y0": float(r.y0),
                            "x1": float(r.x1),
                            "y1": float(r.y1),
                        })
        except Exception as e:
            logger.debug("Failed getting images for page %s: %s", page_index, e)

        # 2. Vector drawings / shapes
        try:
            for d in page.get_drawings():
                r = d.get("rect")
                if r:
                    if r.width >= page_rect.width - 2 and r.height >= page_rect.height - 2:
                        continue
                    if r.width < 6 or r.height < 6:
                        continue
                    objects.append({
                        "type": "shape",
                        "xref": 0,
                        "x0": float(r.x0),
                        "y0": float(r.y0),
                        "x1": float(r.x1),
                        "y1": float(r.y1),
                    })
        except Exception as e:
            logger.debug("Failed getting drawings for page %s: %s", page_index, e)

        self._objects_cache[page_index] = objects
        return objects

    @Slot(int, "QVariantMap")
    def selectObject(self, page_index: int, obj_data: dict[str, Any]) -> None:
        """Select a non-text object (image or shape)."""
        # Clear any text selection
        if self._selected_text or self._selection_rects:
            self._selected_text = ""
            self._selection_page_index = -1
            self._selection_rects = []
            self.selectionRectsChanged.emit()
            self.selectedTextChanged.emit("")

        sel = dict(obj_data)
        sel["pageIndex"] = page_index
        self._selected_object = sel
        self.selectedObjectChanged.emit()

    @Slot()
    def selectAll(self) -> None:
        doc = self._doc_manager.active_document
        if not doc or not doc.is_open or doc.raw_doc is None:
            return
        page_index = self._current_page
        if not (0 <= page_index < len(doc.raw_doc)):
            return

        page = doc.raw_doc[page_index]
        words = page.get_text("words")
        if not words:
            return

        lines: list[list[Any]] = []
        curr_key = None
        curr_line: list[Any] = []
        for w in words:
            key = (w[5], w[6])
            if key != curr_key:
                if curr_line:
                    lines.append(curr_line)
                curr_key = key
                curr_line = [w]
            else:
                curr_line.append(w)
        if curr_line:
            lines.append(curr_line)

        line_rects = []
        line_texts = []
        for l_words in lines:
            rx0 = min(w[0] for w in l_words)
            ry0 = min(w[1] for w in l_words)
            rx1 = max(w[2] for w in l_words)
            ry1 = max(w[3] for w in l_words)
            line_rects.append({"x0": rx0, "y0": ry0, "x1": rx1, "y1": ry1})
            line_texts.append(" ".join(w[4] for w in l_words))

        if self._selected_object:
            self._selected_object = {}
            self.selectedObjectChanged.emit()

        self._selection_page_index = page_index
        self._selection_rects = line_rects
        self._selected_text = "\n".join(line_texts)
        self.selectionRectsChanged.emit()
        self.selectedTextChanged.emit(self._selected_text)
        self.selectAllTriggered.emit()

    @Slot()
    def clearSelection(self) -> None:
        changed = False
        if self._selected_text or self._selection_rects:
            self._selected_text = ""
            self._selection_page_index = -1
            self._selection_rects = []
            self.selectionRectsChanged.emit()
            self.selectedTextChanged.emit("")
            changed = True
        if self._selected_object:
            self._selected_object = {}
            self.selectedObjectChanged.emit()
            changed = True

    @Slot()
    @Slot(str)
    def copyText(self, text: str = "") -> None:
        target_text = text if text else self._selected_text
        if target_text:
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(target_text)
            return

        # If a non-text object (image or shape) is selected, copy it to clipboard as an image
        if self._selected_object:
            doc = self._doc_manager.active_document
            if not doc or not doc.is_open or doc.raw_doc is None:
                return
            page_index = self._selected_object.get("pageIndex", -1)
            if not (0 <= page_index < len(doc.raw_doc)):
                return
            page = doc.raw_doc[page_index]
            try:
                import pymupdf
                from PySide6.QtGui import QImage
                xref = self._selected_object.get("xref", 0)
                if xref > 0 and self._selected_object.get("type") == "image":
                    pix = pymupdf.Pixmap(doc.raw_doc, xref)
                    if pix.n >= 5:
                        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                    fmt = QImage.Format_RGB888 if pix.n == 3 else (QImage.Format_RGBA8888 if pix.n == 4 else QImage.Format_Grayscale8)
                    qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
                else:
                    x0 = self._selected_object.get("x0", 0)
                    y0 = self._selected_object.get("y0", 0)
                    x1 = self._selected_object.get("x1", 0)
                    y1 = self._selected_object.get("y1", 0)
                    rect = pymupdf.Rect(x0, y0, x1, y1)
                    pix = page.get_pixmap(clip=rect, dpi=150)
                    qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)

                clipboard = QGuiApplication.clipboard()
                if clipboard and not qimg.isNull():
                    clipboard.setImage(qimg.copy())
            except Exception as e:
                logger.warning("Failed copying object to clipboard: %s", e)
