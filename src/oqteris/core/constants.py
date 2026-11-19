"""Application constants and metadata for Oqteris."""

from __future__ import annotations

import sys
from pathlib import Path

# Application Metadata
APP_NAME: str = "Oqteris"
APP_DISPLAY_NAME: str = "Oqteris PDF Editor"
APP_DESCRIPTION: str = "Complete Cross-Platform PDF Reader and Editor"
APP_VERSION: str = "1.2.0"
APP_IDENTIFIER: str = "app.vercel.originsd.oqteris"

# Organization & Developer
ORGANIZATION_NAME: str = "OriginSD"
ORGANIZATION_DOMAIN: str = "originsd.vercel.app"
ORGANIZATION_URL: str = "https://originsd.vercel.app"
DEVELOPER_NAME: str = "Subhadip Dutta"
DEVELOPER_GITHUB_USERNAME: str = "subhadip6869"
REPOSITORY_NAME: str = "Oqteris-Desktop"
REPOSITORY_URL: str = "https://github.com/subhadip6869/Oqteris-Desktop"
ISSUES_URL: str = "https://github.com/subhadip6869/Oqteris-Desktop/issues"
RELEASES_API_URL: str = "https://api.github.com/repos/subhadip6869/Oqteris-Desktop/releases/latest"

# File extensions & MIME types
PDF_EXTENSION: str = ".pdf"
PDF_MIME_TYPE: str = "application/pdf"
SUPPORTED_IMAGE_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")

# Default UI & Viewer settings
DEFAULT_WINDOW_WIDTH: int = 1280
DEFAULT_WINDOW_HEIGHT: int = 820
MIN_WINDOW_WIDTH: int = 800
MIN_WINDOW_HEIGHT: int = 600

# Zoom Limits & Steps
MIN_ZOOM_LEVEL: float = 0.1
MAX_ZOOM_LEVEL: float = 10.0
DEFAULT_ZOOM_LEVEL: float = 1.0
ZOOM_STEP: float = 0.15

# Rendering Cache Limits
DEFAULT_MAX_PAGE_CACHE_ITEMS: int = 30
DEFAULT_MAX_PAGE_CACHE_MB: int = 256

# Memory & PDF Limits
MAX_PDF_FILE_SIZE_BYTES: int = 1024 * 1024 * 1024  # 1 GB safe threshold
MAX_PAGES_BATCH_RENDER: int = 20

# IPC Socket Name
IPC_PORT_FILE_NAME: str = "oqteris.ipc"


def get_assets_dir() -> Path:
    """Resolve the assets directory across development, frozen bundles, and installed environments."""
    # 1. PyInstaller bundle directory (_MEIPASS)
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        cand = Path(sys._MEIPASS) / "assets"
        if cand.is_dir():
            return cand
        cand_internal = Path(sys._MEIPASS) / "_internal" / "assets"
        if cand_internal.is_dir():
            return cand_internal

    # 2. Alongside executable or in _internal directory
    exe_dir = Path(sys.executable).parent
    candidates = [
        exe_dir / "assets",
        exe_dir / "_internal" / "assets",
        # macOS App Bundle (Contents/Resources/assets or Contents/MacOS/assets)
        exe_dir.parent / "Resources" / "assets",
        exe_dir.parent / "Resources",
        # Linux standard locations (/opt/oqteris/assets, /usr/share/oqteris/assets)
        Path("/opt/oqteris/assets"),
        Path("/usr/share/oqteris/assets"),
    ]
    for cand in candidates:
        if cand.is_dir() and (cand / "icons").is_dir():
            return cand

    # 3. Development source tree (search up parent directories)
    for p in Path(__file__).resolve().parents:
        cand = p / "assets"
        if cand.is_dir() and (cand / "icons").is_dir():
            return cand

    # Fallback to local assets relative to repo root
    return Path(__file__).resolve().parents[3] / "assets"
