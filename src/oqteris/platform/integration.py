"""Platform integration for OS file associations and default PDF viewer registration."""

from __future__ import annotations

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

from oqteris.core.constants import (
    APP_DISPLAY_NAME,
    APP_IDENTIFIER,
    APP_NAME,
    PDF_EXTENSION,
    PDF_MIME_TYPE,
)

logger = logging.getLogger(__name__)


class PlatformIntegration:
    """Manages operating system file associations and default application queries."""

    def __init__(self) -> None:
        self._system = platform.system()

    def is_default_viewer(self) -> bool:
        """Check if Oqteris is registered as the default handler for application/pdf."""
        try:
            if self._system == "Windows":
                return self._is_default_windows()
            elif self._system == "Linux":
                return self._is_default_linux()
            elif self._system == "Darwin":
                return self._is_default_macos()
        except Exception as e:
            logger.warning("Could not check default PDF viewer: %s", e)
        return False

    def request_set_default(self) -> bool:
        """Register file associations and prompt the user / system to set Oqteris as default."""
        try:
            if self._system == "Windows":
                return self._set_default_windows()
            elif self._system == "Linux":
                return self._set_default_linux()
            elif self._system == "Darwin":
                return self._set_default_macos()
        except Exception as e:
            logger.error("Failed to request setting default viewer: %s", e)
        return False

    def _is_default_windows(self) -> bool:
        """Check Windows Registry for UserChoice association."""
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.pdf\UserChoice"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                prog_id, _ = winreg.QueryValueEx(key, "ProgId")
                return "Oqteris" in prog_id
        except Exception:
            return False

    def _set_default_windows(self) -> bool:
        """Register ProgID in Windows Registry and trigger Windows Settings Default Apps."""
        try:
            import winreg

            exe_path = sys.executable
            # Register Oqteris.PDF ProgID under HKCU\Software\Classes
            prog_id = "Oqteris.PDF"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}") as key:
                winreg.SetValueEx(key, None, 0, winreg.REG_SZ, "PDF Document")

            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell\open\command") as key:
                winreg.SetValueEx(key, None, 0, winreg.REG_SZ, f'"{exe_path}" "%1"')

            # Register capabilities
            cap_key = rf"Software\OriginSD\Oqteris\Capabilities\FileAssociations"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, cap_key) as key:
                winreg.SetValueEx(key, ".pdf", 0, winreg.REG_SZ, prog_id)

            # Register with RegisteredApplications
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\RegisteredApplications") as key:
                winreg.SetValueEx(key, "Oqteris", 0, winreg.REG_SZ, r"Software\OriginSD\Oqteris\Capabilities")

            # Launch Windows Default Apps Settings dialog for user to confirm
            os.system("start ms-settings:defaultapps")
            return True
        except Exception as e:
            logger.error("Windows default registration failed: %s", e)
            return False

    def _is_default_linux(self) -> bool:
        """Query xdg-mime query default application/pdf."""
        try:
            out = subprocess.check_output(
                ["xdg-mime", "query", "default", PDF_MIME_TYPE],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
            return "oqteris" in out.lower()
        except Exception:
            return False

    def _set_default_linux(self) -> bool:
        """Set xdg-mime default app.vercel.originsd.oqteris.desktop application/pdf."""
        desktop_file = f"{APP_IDENTIFIER}.desktop"
        try:
            ret = subprocess.call(
                ["xdg-mime", "default", desktop_file, PDF_MIME_TYPE],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return ret == 0
        except Exception as e:
            logger.error("Linux xdg-mime default failed: %s", e)
            return False

    def _is_default_macos(self) -> bool:
        return False

    def _set_default_macos(self) -> bool:
        return False


_platform_instance: PlatformIntegration | None = None


def get_platform_integration() -> PlatformIntegration:
    global _platform_instance
    if _platform_instance is None:
        _platform_instance = PlatformIntegration()
    return _platform_instance
