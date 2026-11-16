"""PDF controller exposing document operations, navigation, zoom, and search to QML."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QObject, Property, Signal, Slot
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

    # --- Document Properties ---

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
        if file_path.startswith("file:///"):
            file_path = file_path[8:]
            if platform.system() == "Windows" and file_path.startswith("/") and len(file_path) > 2 and file_path[2] == ":":
                file_path = file_path[1:]

        path = Path(file_path).resolve()
        if not path.is_file():
            self.errorOccurred.emit("File Not Found", f"The file '{path}' does not exist.")
            return False

        try:
            doc, meta = self._doc_manager.open_document(path, password=password)
            self._current_page = 0
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

        if self._image_provider:
            self._image_provider.cache.invalidate_document(target_id)

        self._doc_manager.close_document(target_id)
        self._current_page = 0
        self.documentChanged.emit()
        self.pageChanged.emit(0)
        self.tabsChanged.emit()
        self.tocChanged.emit()

    @Slot(str)
    def switchTab(self, doc_id: str) -> None:
        if doc_id != self.activeDocId and self._doc_manager.get_document(doc_id):
            self._doc_manager.active_doc_id = doc_id
            self._current_page = 0
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

        if target_path.startswith("file:///"):
            target_path = target_path[8:]
            if platform.system() == "Windows" and target_path.startswith("/") and len(target_path) > 2 and target_path[2] == ":":
                target_path = target_path[1:]

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
                self._image_provider.cache.invalidate_page(doc.doc_id, page_index)
            else:
                self._image_provider.cache.invalidate_document(doc.doc_id)

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

    @Slot(str)
    def copyText(self, text: str) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
