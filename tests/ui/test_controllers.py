"""Unit and integration tests for QObject controllers exposed to QML."""

import os
import pytest
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtGui import QGuiApplication

from oqteris.ui.controllers.app_controller import AppController
from oqteris.ui.controllers.pdf_controller import PDFController
from oqteris.ui.controllers.ribbon_controller import RibbonController
from oqteris.ui.controllers.organize_controller import SettingsController


@pytest.fixture(scope="session")
def qapp():
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication([])
    return app


def test_app_controller(qapp):
    ctrl = AppController()
    assert ctrl.appName == "Oqteris"
    assert ctrl.developerName == "Subhadip Dutta"

    initial_theme = ctrl.theme
    ctrl.toggleTheme()
    assert ctrl.theme != initial_theme
    ctrl.toggleTheme()


def test_pdf_controller_workflow(qapp, sample_pdf_normal: Path):
    app_ctrl = AppController()
    pdf_ctrl = PDFController(app_controller=app_ctrl)

    assert pdf_ctrl.hasDocument is False

    # Open document
    success = pdf_ctrl.openDocument(str(sample_pdf_normal))
    assert success is True
    assert pdf_ctrl.hasDocument is True
    assert pdf_ctrl.pageCount == 2
    assert pdf_ctrl.currentPage == 0

    # Navigation
    pdf_ctrl.nextPage()
    assert pdf_ctrl.currentPage == 1
    pdf_ctrl.prevPage()
    assert pdf_ctrl.currentPage == 0

    # Zoom
    pdf_ctrl.zoomIn()
    assert pdf_ctrl.zoomLevel > 1.0
    pdf_ctrl.actualSize()
    assert pdf_ctrl.zoomLevel == 1.0

    # Search
    count = pdf_ctrl.search("Oqteris")
    assert count >= 1

    pdf_ctrl.closeDocument()
    assert pdf_ctrl.hasDocument is False


def test_pdf_controller_multi_tabs_and_close(qapp, temp_dir: Path, sample_pdf_normal: Path):
    import pymupdf

    second_pdf = temp_dir / "sample_second.pdf"
    doc2 = pymupdf.open()
    doc2.new_page(width=595, height=842)
    doc2.save(str(second_pdf))
    doc2.close()

    app_ctrl = AppController()
    pdf_ctrl = PDFController(app_controller=app_ctrl)

    # 1. Open first document
    pdf_ctrl.openDocument(str(sample_pdf_normal))
    tabs = pdf_ctrl.openTabs
    assert len(tabs) == 1
    doc1_id = tabs[0]["docId"]
    assert tabs[0]["isActive"] is True

    # 2. Open second document
    pdf_ctrl.openDocument(str(second_pdf))
    tabs = pdf_ctrl.openTabs
    assert len(tabs) == 2
    doc2_id = pdf_ctrl.activeDocId
    assert doc2_id != doc1_id

    # 3. Switch tab back to first document
    pdf_ctrl.switchTab(doc1_id)
    assert pdf_ctrl.activeDocId == doc1_id

    # 4. Close the inactive tab (doc2) by docId
    pdf_ctrl.closeDocument(doc2_id)
    tabs = pdf_ctrl.openTabs
    assert len(tabs) == 1
    assert tabs[0]["docId"] == doc1_id
    assert pdf_ctrl.activeDocId == doc1_id
    assert pdf_ctrl.hasDocument is True

    # 5. Close the active tab (doc1) by docId
    pdf_ctrl.closeDocument(doc1_id)
    assert len(pdf_ctrl.openTabs) == 0
    assert pdf_ctrl.hasDocument is False


def test_ribbon_controller(qapp):
    ribbon = RibbonController()
    assert ribbon.currentTab == "Home"
    ribbon.selectTab("Comment")
    assert ribbon.currentTab == "Comment"

    ribbon.selectTool("highlight")
    assert ribbon.activeTool == "highlight"
