"""Application-level QObject controller exposed to Qt Quick/QML."""

from __future__ import annotations

import logging
import os
import platform
import sys
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QObject, Property, Signal, Slot, QUrl

from oqteris.config.settings import get_settings_manager
from oqteris.core.constants import (
    APP_DESCRIPTION,
    APP_DISPLAY_NAME,
    APP_NAME,
    APP_VERSION,
    DEVELOPER_GITHUB_USERNAME,
    DEVELOPER_NAME,
    ISSUES_URL,
    ORGANIZATION_NAME,
    ORGANIZATION_URL,
    REPOSITORY_URL,
    get_assets_dir,
)
from oqteris.platform.integration import get_platform_integration
from oqteris.repositories.bookmarks_repo import BookmarksRepository
from oqteris.repositories.recent_files_repo import RecentFilesRepository

logger = logging.getLogger(__name__)


class AppController(QObject):
    """Main application controller managing metadata, themes, recent files, and global actions."""

    themeChanged = Signal(str)
    recentFilesChanged = Signal()
    isDefaultViewerChanged = Signal(bool)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._settings = get_settings_manager()
        self._recent_repo = RecentFilesRepository()
        self._bookmark_repo = BookmarksRepository()
        self._platform = get_platform_integration()

        self._theme = self._settings.get("theme", "light")
        self._is_default = self._platform.is_default_viewer()

    # --- Application Metadata Properties ---

    @Property(str, constant=True)
    def appName(self) -> str:
        return APP_NAME

    @Property(str, constant=True)
    def appDisplayName(self) -> str:
        return APP_DISPLAY_NAME

    @Property(str, constant=True)
    def appVersion(self) -> str:
        return APP_VERSION

    @Property(str, constant=True)
    def appDescription(self) -> str:
        return APP_DESCRIPTION

    @Property(str, constant=True)
    def organizationName(self) -> str:
        return ORGANIZATION_NAME

    @Property(str, constant=True)
    def organizationUrl(self) -> str:
        return ORGANIZATION_URL

    @Property(str, constant=True)
    def developerName(self) -> str:
        return DEVELOPER_NAME

    @Property(str, constant=True)
    def repositoryUrl(self) -> str:
        return REPOSITORY_URL

    @Property(str, constant=True)
    def issuesUrl(self) -> str:
        return ISSUES_URL

    @Property(str, constant=True)
    def osName(self) -> str:
        return platform.system()

    @Property(str, constant=True)
    def logoPath(self) -> str:
        assets_dir = get_assets_dir()
        logo_file = assets_dir / "icons" / "app" / "oqteris-logo.png"
        return QUrl.fromLocalFile(str(logo_file)).toString()

    @Property(str, constant=True)
    def uiIconsPath(self) -> str:
        assets_dir = get_assets_dir() / "icons" / "ui"
        return QUrl.fromLocalFile(str(assets_dir)).toString()

    @Property(str, constant=True)
    def ribbonIconsPath(self) -> str:
        return self.uiIconsPath

    # --- Theme Management ---

    @Property(str, notify=themeChanged)
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, value: str) -> None:
        if self._theme != value:
            self._theme = value
            self._settings.set("theme", value)
            self.themeChanged.emit(self._theme)

    @Property(bool, notify=themeChanged)
    def isDarkMode(self) -> bool:
        return self._theme == "dark"

    @Slot(str)
    def setTheme(self, theme_name: str) -> None:
        self.theme = theme_name

    @Slot()
    def toggleTheme(self) -> None:
        self.theme = "dark" if self._theme == "light" else "light"

    # --- Default Viewer Integration ---

    @Property(bool, notify=isDefaultViewerChanged)
    def isDefaultViewer(self) -> bool:
        return self._is_default

    @Slot()
    def requestMakeDefaultViewer(self) -> None:
        success = self._platform.request_set_default()
        self._is_default = self._platform.is_default_viewer()
        self.isDefaultViewerChanged.emit(self._is_default)

    # --- Recent Files ---

    @Property("QVariantList", notify=recentFilesChanged)
    def recentFiles(self) -> list[dict[str, Any]]:
        records = self._recent_repo.get_recent(limit=self._settings.get("recent_files_limit", 20))
        return [
            {
                "filePath": r.file_path,
                "fileName": r.file_name,
                "fileSize": r.file_size_bytes,
                "pageCount": r.page_count,
                "lastOpened": r.last_opened_at.strftime("%b %d, %Y %H:%M"),
                "isPinned": r.is_pinned,
                "isMissing": r.is_missing,
            }
            for r in records
        ]

    @Slot(str)
    def removeRecentFile(self, file_path: str) -> None:
        self._recent_repo.remove(file_path)
        self.recentFilesChanged.emit()

    @Slot(str)
    def togglePinRecentFile(self, file_path: str) -> None:
        self._recent_repo.toggle_pinned(file_path)
        self.recentFilesChanged.emit()

    @Slot()
    def clearRecentFiles(self) -> None:
        self._recent_repo.clear(keep_pinned=False)
        self.recentFilesChanged.emit()

    def record_opened_file(self, file_path: str, size: int = 0, pages: int = 0) -> None:
        self._recent_repo.add_or_update(
            file_path,
            file_size_bytes=size,
            page_count=pages,
            max_limit=self._settings.get("recent_files_limit", 20),
        )
        self.recentFilesChanged.emit()
