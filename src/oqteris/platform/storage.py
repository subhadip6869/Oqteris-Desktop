"""Platform-aware data directory and storage manager for Oqteris.

Strictly follows platform conventions:
- Windows: %LOCALAPPDATA%\\OriginSD\\Oqteris
- macOS: ~/Library/Application Support/OriginSD/Oqteris (and ~/Library/Caches, ~/Library/Logs)
- Linux: XDG Base Directory Specification (XDG_CONFIG_HOME, XDG_DATA_HOME, XDG_CACHE_HOME, XDG_STATE_HOME)
"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path

from oqteris.core.constants import APP_NAME, ORGANIZATION_NAME

logger = logging.getLogger(__name__)


class StorageManager:
    """Centralized storage management for application directories, databases, and temporary files."""

    def __init__(self, app_name: str = APP_NAME, org_name: str = ORGANIZATION_NAME) -> None:
        self._app_name = app_name
        self._org_name = org_name
        self._system = platform.system()

        self._init_paths()
        self.ensure_directories()

    def _init_paths(self) -> None:
        home = Path.home()

        if self._system == "Windows":
            # Windows: %LOCALAPPDATA%\OriginSD\Oqteris
            local_appdata = os.environ.get("LOCALAPPDATA")
            if local_appdata:
                base_dir = Path(local_appdata) / self._org_name / self._app_name
            else:
                base_dir = home / "AppData" / "Local" / self._org_name / self._app_name

            self._data_dir = base_dir
            self._config_dir = base_dir
            self._cache_dir = base_dir / "cache"
            self._logs_dir = base_dir / "logs"
            self._temp_dir = base_dir / "temp"
            self._recovery_dir = base_dir / "recovery"
            self._backups_dir = base_dir / "backups"
            self._ipc_dir = base_dir / "ipc_requests"

        elif self._system == "Darwin":
            # macOS: ~/Library/Application Support/OriginSD/Oqteris
            app_support = home / "Library" / "Application Support" / self._org_name / self._app_name
            self._data_dir = app_support
            self._config_dir = app_support
            self._cache_dir = home / "Library" / "Caches" / self._org_name / self._app_name
            self._logs_dir = home / "Library" / "Logs" / self._org_name / self._app_name
            self._temp_dir = app_support / "temp"
            self._recovery_dir = app_support / "recovery"
            self._backups_dir = app_support / "backups"
            self._ipc_dir = app_support / "ipc_requests"

        else:
            # Linux / BSD: XDG Specifications
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            xdg_data = os.environ.get("XDG_DATA_HOME")
            xdg_cache = os.environ.get("XDG_CACHE_HOME")
            xdg_state = os.environ.get("XDG_STATE_HOME")

            config_base = Path(xdg_config) if xdg_config else home / ".config"
            data_base = Path(xdg_data) if xdg_data else home / ".local" / "share"
            cache_base = Path(xdg_cache) if xdg_cache else home / ".cache"
            state_base = Path(xdg_state) if xdg_state else home / ".local" / "state"

            app_folder = self._app_name.lower()
            self._config_dir = config_base / app_folder
            self._data_dir = data_base / app_folder
            self._cache_dir = cache_base / app_folder
            self._logs_dir = state_base / app_folder / "logs"
            self._temp_dir = cache_base / app_folder / "temp"
            self._recovery_dir = data_base / app_folder / "recovery"
            self._backups_dir = data_base / app_folder / "backups"
            self._ipc_dir = state_base / app_folder / "ipc_requests"

    def ensure_directories(self) -> None:
        """Create all necessary directories if they do not exist, setting safe permissions."""
        dirs = [
            self._config_dir,
            self._data_dir,
            self._cache_dir,
            self._logs_dir,
            self._temp_dir,
            self._recovery_dir,
            self._backups_dir,
            self._ipc_dir,
        ]
        for d in dirs:
            try:
                d.mkdir(parents=True, exist_ok=True)
                # Restrict permissions on Unix systems to owner only (700)
                if self._system != "Windows":
                    try:
                        d.chmod(0o700)
                    except OSError:
                        pass
            except Exception as e:
                logger.error(f"Failed to create storage directory {d}: {e}")

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def cache_dir(self) -> Path:
        return self._cache_dir

    @property
    def logs_dir(self) -> Path:
        return self._logs_dir

    @property
    def temp_dir(self) -> Path:
        return self._temp_dir

    @property
    def recovery_dir(self) -> Path:
        return self._recovery_dir

    @property
    def backups_dir(self) -> Path:
        return self._backups_dir

    @property
    def ipc_dir(self) -> Path:
        return self._ipc_dir

    @property
    def settings_file(self) -> Path:
        return self._config_dir / "settings.json"

    @property
    def database_file(self) -> Path:
        return self._data_dir / "oqteris.db"

    @property
    def truststore_file(self) -> Path:
        return self._data_dir / "truststore.p12"

    def get_temporary_file(self, prefix: str = "oq_", suffix: str = ".tmp") -> Path:
        """Create and return a safe temporary file path in the application temp directory."""
        fd, path = tempfile.mkstemp(dir=self._temp_dir, prefix=prefix, suffix=suffix)
        os.close(fd)
        return Path(path)

    def clean_temp_directory(self) -> None:
        """Safely clean up temporary files from previous sessions."""
        if not self._temp_dir.exists():
            return
        for item in self._temp_dir.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink(missing_ok=True)
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Could not remove temp item {item}: {e}")

    def clean_cache_directory(self) -> None:
        """Safely clean up cached render artifacts."""
        if not self._cache_dir.exists():
            return
        for item in self._cache_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink(missing_ok=True)
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Could not remove cache item {item}: {e}")


# Singleton instance
_storage_instance: StorageManager | None = None


def get_storage_manager() -> StorageManager:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageManager()
    return _storage_instance
