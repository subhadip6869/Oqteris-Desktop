"""Application settings management with atomic persistence and validation.

Stores user preferences in %LOCALAPPDATA%/OriginSD/Oqteris/settings.json (Windows),
~/Library/Application Support/OriginSD/Oqteris/settings.json (macOS),
or ~/.config/oqteris/settings.json (Linux).
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from oqteris.platform.storage import get_storage_manager

logger = logging.getLogger(__name__)


@dataclass
class SettingsModel:
    """Strongly typed application settings schema."""

    # UI & Appearance
    theme: str = "light"  # "light", "dark", "system"
    ui_scale: float = 1.0
    font_family: str = "Segoe UI"
    font_size: int = 12
    show_ribbon: bool = True
    show_thumbnails_panel: bool = False
    show_bookmarks_panel: bool = False
    show_annotations_panel: bool = False
    show_signatures_panel: bool = False
    show_properties_panel: bool = False
    show_status_bar: bool = True

    # Document & Viewer defaults
    default_author: str = ""
    default_zoom: float = 1.0
    page_display_mode: str = "continuous"  # "single", "continuous", "facing"
    fit_mode: str = "fit_width"  # "actual_size", "fit_page", "fit_width"
    restore_workspace_on_startup: bool = True
    recent_files_limit: int = 20

    # Autosave & Recovery
    autosave_enabled: bool = True
    autosave_interval_seconds: int = 300

    # OCR Settings
    ocr_languages: list[str] = field(default_factory=lambda: ["eng"])
    ocr_deskew: bool = True
    ocr_clean_images: bool = True
    ocr_preserve_geometry: bool = True
    ocr_tesseract_path: str = ""

    # Digital Signatures & Security
    auto_validate_signatures: bool = True
    check_revocation_online: bool = False
    strict_chain_validation: bool = False
    warn_before_destructive_edits: bool = True

    # Updates & System
    check_updates_on_startup: bool = True
    prompt_make_default_viewer: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SettingsModel:
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


class SettingsManager:
    """Manages application settings lifecycle and atomic disk serialization."""

    def __init__(self, file_path: Path | None = None) -> None:
        self._storage = get_storage_manager()
        self._file_path = file_path or self._storage.settings_file
        self._settings = SettingsModel()
        self.load()

    @property
    def current(self) -> SettingsModel:
        return self._settings

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self._settings, key, default)

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        if hasattr(self._settings, key):
            setattr(self._settings, key, value)
            if auto_save:
                self.save()
        else:
            logger.warning("Attempted to set unknown setting '%s'", key)

    def update(self, updates: dict[str, Any], auto_save: bool = True) -> None:
        for k, v in updates.items():
            if hasattr(self._settings, k):
                setattr(self._settings, k, v)
        if auto_save:
            self.save()

    def load(self) -> None:
        """Load settings from JSON file with fallback to defaults."""
        if not self._file_path.exists():
            logger.info("Settings file not found. Creating with defaults at %s", self._file_path)
            self.save()
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self._settings = SettingsModel.from_dict(data)
                logger.debug("Settings successfully loaded from %s", self._file_path)
            else:
                logger.warning("Invalid settings format in %s. Using defaults.", self._file_path)
        except Exception as e:
            logger.error("Failed to load settings file %s: %e. Falling back to defaults.", self._file_path, e)
            self._settings = SettingsModel()

    def save(self) -> None:
        """Atomically persist settings to disk."""
        data = self._settings.to_dict()
        parent_dir = self._file_path.parent
        parent_dir.mkdir(parents=True, exist_ok=True)

        # Atomic write: write to temp file in same directory then os.replace
        temp_file = parent_dir / f".{self._file_path.name}.tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_file.replace(self._file_path)
            logger.debug("Settings saved atomically to %s", self._file_path)
        except Exception as e:
            logger.error("Failed to atomically save settings to %s: %s", self._file_path, e)
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)


# Singleton instance
_settings_instance: SettingsManager | None = None


def get_settings_manager() -> SettingsManager:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance
