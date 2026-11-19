"""Update controller managing GitHub releases check, in-app download, progress tracking, and installation."""

from __future__ import annotations

import json
import logging
import os
import platform
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QCoreApplication, QObject, Property, Signal, Slot, QUrl
from PySide6.QtGui import QDesktopServices

from oqteris.core.constants import (
    APP_DISPLAY_NAME,
    APP_NAME,
    APP_VERSION,
    RELEASES_API_URL,
    REPOSITORY_URL,
)

logger = logging.getLogger(__name__)


def parse_version_tuple(v_str: str) -> tuple[int, ...]:
    """Parse a version string (e.g. 'v1.3.0', '1.2.5-beta') into an integer tuple for comparison."""
    clean = v_str.strip().lstrip("vV")
    main_part = clean.split("-")[0].split("+")[0]
    parts: list[int] = []
    for segment in main_part.split("."):
        try:
            parts.append(int(segment))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def is_version_newer(latest_str: str, current_str: str) -> bool:
    """Return True if latest_str is strictly newer than current_str."""
    return parse_version_tuple(latest_str) > parse_version_tuple(current_str)


def format_bytes_speed(bytes_val: float) -> str:
    """Format bytes per second into human-readable string."""
    if bytes_val < 1024:
        return f"{bytes_val:.0f} B/s"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB/s"
    else:
        return f"{bytes_val / (1024 * 1024):.1f} MB/s"


def format_bytes_size(bytes_val: int) -> str:
    """Format total bytes into human-readable size string."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"


class UpdateController(QObject):
    """Coordinates checking for updates from GitHub, streaming downloads with progress, and installing."""

    statusChanged = Signal(str)
    updateInfoChanged = Signal()
    downloadProgressChanged = Signal(float, int, int, str)  # progress, downloaded, total, speed
    errorOccurred = Signal(str, str)  # title, message

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._status: str = "idle"  # idle, checking, available, up_to_date, downloading, ready_to_install, error
        self._current_version: str = APP_VERSION
        self._latest_version: str = ""
        self._release_title: str = ""
        self._release_notes: str = ""
        self._release_date: str = ""
        self._release_url: str = REPOSITORY_URL
        self._asset_name: str = ""
        self._asset_url: str = ""
        self._asset_size: int = 0
        self._download_progress: float = 0.0
        self._downloaded_bytes: int = 0
        self._total_bytes: int = 0
        self._download_speed: str = ""
        self._downloaded_file_path: Optional[Path] = None
        self._error_message: str = ""
        self._cancel_requested: bool = False

    # --- Properties ---

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Property(str, constant=True)
    def currentVersion(self) -> str:
        return self._current_version

    @Property(str, notify=updateInfoChanged)
    def latestVersion(self) -> str:
        return self._latest_version

    @Property(str, notify=updateInfoChanged)
    def releaseTitle(self) -> str:
        return self._release_title

    @Property(str, notify=updateInfoChanged)
    def releaseNotes(self) -> str:
        return self._release_notes

    @Property(str, notify=updateInfoChanged)
    def releaseDate(self) -> str:
        return self._release_date

    @Property(str, notify=updateInfoChanged)
    def releaseUrl(self) -> str:
        return self._release_url

    @Property(str, notify=updateInfoChanged)
    def assetName(self) -> str:
        return self._asset_name

    @Property(int, notify=updateInfoChanged)
    def assetSize(self) -> int:
        return self._asset_size

    @Property(str, notify=updateInfoChanged)
    def assetSizeFormatted(self) -> str:
        return format_bytes_size(self._asset_size) if self._asset_size > 0 else ""

    @Property(float, notify=downloadProgressChanged)
    def downloadProgress(self) -> float:
        return self._download_progress

    @Property(int, notify=downloadProgressChanged)
    def downloadedBytes(self) -> int:
        return self._downloaded_bytes

    @Property(int, notify=downloadProgressChanged)
    def totalBytes(self) -> int:
        return self._total_bytes

    @Property(str, notify=downloadProgressChanged)
    def downloadSpeed(self) -> str:
        return self._download_speed

    @Property(str, notify=statusChanged)
    def downloadedFilePath(self) -> str:
        return str(self._downloaded_file_path) if self._downloaded_file_path else ""

    @Property(str, notify=errorOccurred)
    def errorMessage(self) -> str:
        return self._error_message

    # --- Slots ---

    @Slot()
    def checkForUpdates(self) -> None:
        """Check GitHub for the latest release in a background thread."""
        if self._status in ("checking", "downloading"):
            return

        self._set_status("checking")
        self._error_message = ""
        thread = threading.Thread(target=self._check_worker, daemon=True, name="update-checker")
        thread.start()

    def _set_status(self, new_status: str) -> None:
        if self._status != new_status:
            self._status = new_status
            self.statusChanged.emit(self._status)

    def _check_worker(self) -> None:
        try:
            req = urllib.request.Request(
                RELEASES_API_URL,
                headers={
                    "User-Agent": f"{APP_NAME}/{APP_VERSION}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))

            tag_name = data.get("tag_name", "").strip()
            self._latest_version = tag_name.lstrip("vV")
            self._release_title = data.get("name", "") or tag_name
            self._release_notes = data.get("body", "") or "No release notes provided."
            raw_date = data.get("published_at", "")
            if raw_date and "T" in raw_date:
                self._release_date = raw_date.split("T")[0]
            else:
                self._release_date = raw_date
            self._release_url = data.get("html_url", REPOSITORY_URL)

            # Discover asset appropriate for OS
            assets = data.get("assets", [])
            chosen_asset: Optional[dict[str, Any]] = None

            # Prioritize matching Windows asset (.exe / .msi)
            for a in assets:
                name = a.get("name", "").lower()
                if name.endswith(".exe") or name.endswith(".msi"):
                    chosen_asset = a
                    break

            if not chosen_asset:
                for a in assets:
                    name = a.get("name", "").lower()
                    if name.endswith(".zip"):
                        chosen_asset = a
                        break

            if chosen_asset:
                self._asset_name = chosen_asset.get("name", "")
                self._asset_url = chosen_asset.get("browser_download_url", "")
                self._asset_size = chosen_asset.get("size", 0)
            else:
                self._asset_name = f"{APP_NAME}-{tag_name}.zip"
                self._asset_url = data.get("zipball_url", "") or self._release_url
                self._asset_size = 0

            self.updateInfoChanged.emit()

            if is_version_newer(self._latest_version, self._current_version):
                logger.info("New version available: %s (current: %s)", self._latest_version, self._current_version)
                self._set_status("available")
            else:
                logger.info("Application is up-to-date (version: %s)", self._current_version)
                self._set_status("up_to_date")

        except urllib.error.HTTPError as e:
            if e.code == 404:
                # No release published yet
                logger.info("No releases found on GitHub repository. Up to date.")
                self._set_status("up_to_date")
            elif e.code == 403:
                msg = "GitHub API rate limit exceeded. Please try again later or view releases online."
                self._error_message = msg
                self._set_status("error")
                self.errorOccurred.emit("Rate Limit", msg)
            else:
                msg = f"HTTP Error {e.code}: {e.reason}"
                self._error_message = msg
                self._set_status("error")
                self.errorOccurred.emit("Check Failed", msg)
        except Exception as e:
            logger.warning("Failed to check for updates: %s", e)
            msg = f"Unable to connect to GitHub update service ({e})."
            self._error_message = msg
            self._set_status("error")
            self.errorOccurred.emit("Check Failed", msg)

    @Slot()
    def startDownload(self) -> None:
        """Begin in-app streaming download of the selected asset."""
        if not self._asset_url or self._status == "downloading":
            return

        self._cancel_requested = False
        self._download_progress = 0.0
        self._downloaded_bytes = 0
        self._download_speed = "Connecting..."
        self._set_status("downloading")
        self.downloadProgressChanged.emit(0.0, 0, self._asset_size, self._download_speed)

        thread = threading.Thread(target=self._download_worker, daemon=True, name="update-downloader")
        thread.start()

    def _download_worker(self) -> None:
        # Create temp download directory
        temp_dir = Path(tempfile.gettempdir()) / "Oqteris_Updates"
        try:
            temp_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        safe_filename = self._asset_name or f"oqteris-v{self._latest_version}-update.exe"
        dest_file = temp_dir / safe_filename

        try:
            req = urllib.request.Request(
                self._asset_url,
                headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                content_len = resp.headers.get("Content-Length")
                total = int(content_len) if content_len and content_len.isdigit() else self._asset_size
                self._total_bytes = total

                downloaded = 0
                chunk_size = 65536  # 64 KB
                last_time = time.time()
                last_bytes = 0
                speed_str = "Calculating..."

                with open(dest_file, "wb") as out_f:
                    while True:
                        if self._cancel_requested:
                            logger.info("Update download cancelled by user.")
                            break

                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break

                        out_f.write(chunk)
                        downloaded += len(chunk)
                        self._downloaded_bytes = downloaded

                        now = time.time()
                        dt = now - last_time
                        if dt >= 0.25:  # Update progress stats 4 times a second
                            speed_bps = (downloaded - last_bytes) / dt
                            speed_str = format_bytes_speed(speed_bps)
                            last_time = now
                            last_bytes = downloaded

                            progress = (downloaded / total) if total > 0 else 0.0
                            self._download_progress = min(1.0, max(0.0, progress))
                            self._download_speed = speed_str
                            self.downloadProgressChanged.emit(
                                self._download_progress,
                                downloaded,
                                total,
                                speed_str,
                            )

            if self._cancel_requested:
                if dest_file.exists():
                    try:
                        dest_file.unlink()
                    except Exception:
                        pass
                self._set_status("available")
                return

            # Download finished successfully
            self._download_progress = 1.0
            self._downloaded_bytes = downloaded
            self._download_speed = "Complete"
            self._downloaded_file_path = dest_file
            self.downloadProgressChanged.emit(1.0, downloaded, total, "Complete")

            logger.info("Update downloaded successfully: %s", dest_file)
            self._set_status("ready_to_install")

        except Exception as e:
            logger.error("Download failed: %s", e)
            if dest_file.exists():
                try:
                    dest_file.unlink()
                except Exception:
                    pass
            self._error_message = f"Download error: {e}"
            self._set_status("error")
            self.errorOccurred.emit("Download Failed", str(e))

    @Slot()
    def cancelDownload(self) -> None:
        """Cancel the ongoing download."""
        if self._status == "downloading":
            self._cancel_requested = True
            self._download_speed = "Cancelling..."
            self.downloadProgressChanged.emit(self._download_progress, self._downloaded_bytes, self._total_bytes, "Cancelled")

    @Slot()
    def installUpdate(self) -> bool:
        """Launch the downloaded installer or package and cleanly close Oqteris."""
        if not self._downloaded_file_path or not self._downloaded_file_path.exists():
            self._error_message = "Installer file not found on disk."
            self.errorOccurred.emit("Install Error", self._error_message)
            return False

        file_str = str(self._downloaded_file_path)
        ext = self._downloaded_file_path.suffix.lower()

        try:
            logger.info("Executing installer: %s", file_str)
            if platform.system() == "Windows":
                if ext in (".exe", ".msi"):
                    # Launch detached installer process
                    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                    subprocess.Popen([file_str], shell=True, creationflags=flags)
                    # Terminate current app cleanly so the installer can replace application files
                    QCoreApplication.quit()
                    return True
                elif ext == ".zip":
                    # Open file folder in explorer
                    os.startfile(str(self._downloaded_file_path.parent))
                    return True
                else:
                    os.startfile(file_str)
                    return True
            else:
                subprocess.Popen(["xdg-open", file_str])
                return True
        except Exception as e:
            logger.error("Failed to run installer %s: %s", file_str, e)
            self.errorOccurred.emit("Launch Error", f"Unable to run installer: {e}")
            return False

    @Slot()
    def openReleasePage(self) -> None:
        """Open the GitHub release page in the system default web browser."""
        url = self._release_url or REPOSITORY_URL
        QDesktopServices.openUrl(QUrl(url))

    @Slot()
    def resetState(self) -> None:
        """Reset status to idle."""
        if self._status != "downloading":
            self._set_status("idle")
            self._error_message = ""
