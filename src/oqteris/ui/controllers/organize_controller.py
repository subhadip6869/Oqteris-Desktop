"""Controllers for page organization, OCR processing, and application settings."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QObject, Property, Signal, Slot

from oqteris.config.settings import get_settings_manager
from oqteris.pdf.document.manager import get_document_manager
from oqteris.pdf.ocr.service import OCRService
from oqteris.pdf.optimisation.service import OptimizationService
from oqteris.ui.controllers.pdf_controller import PDFController

logger = logging.getLogger(__name__)


class OrganizeController(QObject):
    """Handles page organization: reorder, delete, extract, rotate, split, and merge."""

    operationCompleted = Signal(str, bool)  # message, is_success

    def __init__(self, pdf_controller: PDFController, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._pdf_controller = pdf_controller
        self._doc_manager = get_document_manager()

    @Slot(int, result=bool)
    def deletePage(self, page_index: int) -> bool:
        doc = self._doc_manager.active_document
        if not doc:
            return False
        try:
            doc.delete_page(page_index)
            self._pdf_controller.invalidateRender(-1)
            self._pdf_controller.documentChanged.emit()
            if self._pdf_controller.currentPage >= doc.page_count:
                self._pdf_controller.currentPage = max(0, doc.page_count - 1)
            self.operationCompleted.emit("Page deleted successfully.", True)
            return True
        except Exception as e:
            self.operationCompleted.emit(f"Failed to delete page: {e}", False)
            return False

    @Slot(int, int, result=bool)
    def movePage(self, from_index: int, to_index: int) -> bool:
        doc = self._doc_manager.active_document
        if not doc:
            return False
        try:
            doc.move_page(from_index, to_index)
            self._pdf_controller.invalidateRender(-1)
            self._pdf_controller.documentChanged.emit()
            return True
        except Exception as e:
            self.operationCompleted.emit(f"Failed to move page: {e}", False)
            return False

    @Slot("QVariantList", str, result=bool)
    def extractPages(self, page_indices: list[Any], output_path: str) -> bool:
        doc = self._doc_manager.active_document
        if not doc or not doc.file_path:
            return False
        try:
            indices = [int(p) for p in page_indices]
            OptimizationService.extract_pages(doc.file_path, output_path, indices)
            self.operationCompleted.emit(f"Extracted pages saved to {output_path}", True)
            return True
        except Exception as e:
            self.operationCompleted.emit(f"Extraction failed: {e}", False)
            return False

    @Slot(str, int, result=bool)
    def splitPdf(self, output_dir: str, pages_per_file: int = 1) -> bool:
        doc = self._doc_manager.active_document
        if not doc or not doc.file_path:
            return False
        try:
            parts = OptimizationService.split_pdf(doc.file_path, output_dir, pages_per_file)
            self.operationCompleted.emit(f"PDF split into {len(parts)} files in {output_dir}", True)
            return True
        except Exception as e:
            self.operationCompleted.emit(f"Split failed: {e}", False)
            return False

    @Slot("QVariantList", str, result=bool)
    def mergePdfs(self, input_paths: list[Any], output_path: str) -> bool:
        try:
            paths = [str(p) for p in input_paths]
            OptimizationService.merge_pdfs(paths, output_path)
            self.operationCompleted.emit(f"Merged PDF created at {output_path}", True)
            self._pdf_controller.openDocument(output_path)
            return True
        except Exception as e:
            self.operationCompleted.emit(f"Merge failed: {e}", False)
            return False

    @Slot(str, bool, int, bool, result="QVariantMap")
    def compressPdf(
        self,
        target_path: str,
        compress_images: bool = True,
        quality: int = 75,
        remove_metadata: bool = False,
    ) -> dict[str, Any]:
        doc = self._doc_manager.active_document
        if not doc or not doc.file_path:
            return {}
        try:
            result = OptimizationService.compress_pdf(
                doc.file_path,
                target_path,
                compress_images=compress_images,
                image_quality=quality,
                remove_metadata=remove_metadata,
            )
            self.operationCompleted.emit(
                f"PDF compressed: saved {result.get('compressionRatio', 0)}% of space.", True
            )
            return result
        except Exception as e:
            self.operationCompleted.emit(f"Compression failed: {e}", False)
            return {}


class OCRController(QObject):
    """Exposes OCR status, language models, and progress reporting to QML."""

    tesseractStatusChanged = Signal()
    ocrProgress = Signal(int, int, str)  # current, total, status_text
    ocrFinished = Signal(str, bool)  # output_path / message, success

    def __init__(self, pdf_controller: PDFController, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._pdf_controller = pdf_controller
        self._ocr_service = OCRService()
        self._is_cancelled = False

    @Property(bool, notify=tesseractStatusChanged)
    def isTesseractAvailable(self) -> bool:
        return self._ocr_service.is_tesseract_available()

    @Property("QVariantList", notify=tesseractStatusChanged)
    def availableLanguages(self) -> list[str]:
        return self._ocr_service.get_available_languages()

    @Slot(str, "QVariantList", bool, bool)
    def runOcr(
        self,
        output_path: str,
        languages: list[Any],
        deskew: bool = True,
        binarize: bool = False,
    ) -> None:
        doc = get_document_manager().active_document
        if not doc or not doc.file_path:
            self.ocrFinished.emit("No active document to process.", False)
            return

        self._is_cancelled = False
        lang_list = [str(l) for l in languages] if languages else ["eng"]

        def on_progress(cur: int, tot: int, msg: str) -> None:
            self.ocrProgress.emit(cur, tot, msg)

        def is_cancelled() -> bool:
            return self._is_cancelled

        try:
            out = self._ocr_service.ocr_pdf(
                source_path=doc.file_path,
                target_path=output_path,
                languages=lang_list,
                deskew=deskew,
                binarize=binarize,
                progress_callback=on_progress,
                is_cancelled=is_cancelled,
            )
            self.ocrFinished.emit(str(out), True)
            self._pdf_controller.openDocument(str(out))
        except Exception as e:
            logger.error("OCR job failed: %s", e)
            self.ocrFinished.emit(str(e), False)

    @Slot()
    def cancelOcr(self) -> None:
        self._is_cancelled = True


class SettingsController(QObject):
    """Reads, updates, and persists application settings for the Settings Dialog."""

    settingsChanged = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._settings = get_settings_manager()

    @Property(str, notify=settingsChanged)
    def defaultAuthor(self) -> str:
        return self._settings.get("default_author", "")

    @defaultAuthor.setter
    def defaultAuthor(self, val: str) -> None:
        self._settings.set("default_author", val)
        self.settingsChanged.emit()

    @Property(float, notify=settingsChanged)
    def defaultZoom(self) -> float:
        return self._settings.get("default_zoom", 1.0)

    @defaultZoom.setter
    def defaultZoom(self, val: float) -> None:
        self._settings.set("default_zoom", val)
        self.settingsChanged.emit()

    @Property(str, notify=settingsChanged)
    def pageDisplayMode(self) -> str:
        return self._settings.get("page_display_mode", "continuous")

    @pageDisplayMode.setter
    def pageDisplayMode(self, val: str) -> None:
        self._settings.set("page_display_mode", val)
        self.settingsChanged.emit()

    @Property(bool, notify=settingsChanged)
    def autosaveEnabled(self) -> bool:
        return self._settings.get("autosave_enabled", True)

    @autosaveEnabled.setter
    def autosaveEnabled(self, val: bool) -> None:
        self._settings.set("autosave_enabled", val)
        self.settingsChanged.emit()

    @Property(int, notify=settingsChanged)
    def autosaveInterval(self) -> int:
        return self._settings.get("autosave_interval_seconds", 300)

    @autosaveInterval.setter
    def autosaveInterval(self, val: int) -> None:
        self._settings.set("autosave_interval_seconds", val)
        self.settingsChanged.emit()

    @Property(str, notify=settingsChanged)
    def tesseractPath(self) -> str:
        return self._settings.get("ocr_tesseract_path", "")

    @tesseractPath.setter
    def tesseractPath(self, val: str) -> None:
        self._settings.set("ocr_tesseract_path", val)
        self.settingsChanged.emit()
