"""Main application entry point for Oqteris."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QObject, Qt, QUrl
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

from oqteris.application.single_instance import SingleInstanceCoordinator
from oqteris.config.settings import get_settings_manager
from oqteris.core.constants import (
    APP_DISPLAY_NAME,
    APP_IDENTIFIER,
    APP_NAME,
    APP_VERSION,
    ORGANIZATION_DOMAIN,
    ORGANIZATION_NAME,
    get_assets_dir,
)
from oqteris.core.logging import setup_logging
from oqteris.database.connection import get_db_manager
from oqteris.pdf.rendering.image_provider import PDFPageImageProvider
from oqteris.platform.storage import get_storage_manager
from oqteris.ui.icon_provider import IconImageProvider
from oqteris.ui.controllers.annotation_controller import AnnotationController
from oqteris.ui.controllers.app_controller import AppController
from oqteris.ui.controllers.organize_controller import (
    OCRController,
    OrganizeController,
    SettingsController,
)
from oqteris.ui.controllers.pdf_controller import PDFController
from oqteris.ui.controllers.ribbon_controller import RibbonController
from oqteris.ui.controllers.signature_controller import SignatureController
from oqteris.ui.controllers.update_controller import UpdateController

logger = logging.getLogger("oqteris.main")


class _FileOpenEventFilter(QObject):
    """Event filter to capture macOS Finder open-file requests (QFileOpenEvent)."""

    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self._callback = callback

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.FileOpen:
            file_path = ""
            if hasattr(event, "file") and event.file():
                file_path = event.file()
            elif hasattr(event, "url") and event.url().isLocalFile():
                file_path = event.url().toLocalFile()
            if file_path:
                self._callback(file_path)
                return True
        return super().eventFilter(watched, event)


def main() -> int:
    """Launch Oqteris desktop application."""
    # Step 1: Storage and Logging initialization
    storage = get_storage_manager()
    setup_logging()
    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)

    # Step 2: High DPI scaling and native desktop style
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QQuickStyle.setStyle("Fusion")

    # Step 3: Initialize Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_DISPLAY_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setOrganizationDomain(ORGANIZATION_DOMAIN)
    app.setApplicationVersion(APP_VERSION)
    if hasattr(app, "setDesktopFileName"):
        app.setDesktopFileName(APP_IDENTIFIER)

    # Step 4: Application Icon
    assets_dir = get_assets_dir()
    icon_ico = assets_dir / "icons" / "app" / "oqteris-logo.ico"
    icon_png = assets_dir / "icons" / "app" / "oqteris-logo.png"

    if icon_ico.is_file():
        app.setWindowIcon(QIcon(str(icon_ico)))
    elif icon_png.is_file():
        app.setWindowIcon(QIcon(str(icon_png)))

    # Step 5: Single-Instance Enforcement & Local IPC
    coordinator = SingleInstanceCoordinator(app_id=APP_IDENTIFIER, parent=app)
    is_primary = coordinator.handle_startup(sys.argv[1:])
    if not is_primary:
        logger.info("Forwarded request to running instance. Exiting secondary process.")
        return 0

    # Step 6: Database initialization
    db = get_db_manager()

    # Step 7: QML Engine and Image Providers
    engine = QQmlApplicationEngine()
    image_provider = PDFPageImageProvider()
    engine.addImageProvider("pdf", image_provider)
    icon_provider = IconImageProvider()
    engine.addImageProvider("icon", icon_provider)

    # Step 8: Controllers setup
    app_controller = AppController(parent=app)
    pdf_controller = PDFController(
        app_controller=app_controller,
        image_provider=image_provider,
        parent=app,
    )
    ribbon_controller = RibbonController(parent=app)
    annotation_controller = AnnotationController(pdf_controller=pdf_controller, parent=app)
    signature_controller = SignatureController(pdf_controller=pdf_controller, parent=app)
    organize_controller = OrganizeController(pdf_controller=pdf_controller, parent=app)
    ocr_controller = OCRController(pdf_controller=pdf_controller, parent=app)
    settings_controller = SettingsController(parent=app)
    update_controller = UpdateController(parent=app)

    # Hook IPC file opening to pdf_controller
    def on_files_received(file_paths: list[str]) -> None:
        if file_paths:
            logger.info("Opening files received from IPC: %s", file_paths)
            for path in file_paths:
                pdf_controller.openDocument(path)

    coordinator.files_received.connect(on_files_received)

    # Listen for macOS Finder file open events (QFileOpenEvent)
    file_open_filter = _FileOpenEventFilter(pdf_controller.openDocument, parent=app)
    app.installEventFilter(file_open_filter)

    # Step 9: Register Controllers into QML Context
    root_context = engine.rootContext()
    root_context.setContextProperty("appController", app_controller)
    root_context.setContextProperty("pdfController", pdf_controller)
    root_context.setContextProperty("ribbonController", ribbon_controller)
    root_context.setContextProperty("annotationController", annotation_controller)
    root_context.setContextProperty("signatureController", signature_controller)
    root_context.setContextProperty("organizeController", organize_controller)
    root_context.setContextProperty("ocrController", ocr_controller)
    root_context.setContextProperty("settingsController", settings_controller)
    root_context.setContextProperty("updateController", update_controller)

    # Step 10: Load initial file argument if passed
    initial_files = [a for a in sys.argv[1:] if Path(a).is_file() and a.lower().endswith(".pdf")]
    if initial_files:
        pdf_controller.openDocument(initial_files[0])

    # Step 11: Load QML Main UI
    qml_file = Path(__file__).resolve().parent / "ui" / "qml" / "Main.qml"
    if not qml_file.exists():
        logger.critical("Main QML file not found at %s", qml_file)
        return 1

    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        logger.critical("Failed to load QML root objects from %s", qml_file)
        return 1

    logger.info("QML UI loaded successfully. Entering event loop.")
    exit_code = app.exec()

    # Cleanup on exit
    coordinator.close()
    image_provider.shutdown()
    storage.clean_temp_directory()
    db.close()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
