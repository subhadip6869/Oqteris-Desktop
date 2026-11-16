"""Build script for compiling Oqteris into a standalone executable using Nuitka."""

import os
import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
MAIN_SCRIPT = SRC_DIR / "oqteris" / "__main__.py"


def run_nuitka_build() -> int:
    system = platform.system()
    output_dir = PROJECT_ROOT / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--enable-plugin=pyside6",
        "--include-package=oqteris",
        f"--include-data-dir={SRC_DIR / 'oqteris' / 'ui' / 'qml'}=oqteris/ui/qml",
        f"--include-data-dir={ASSETS_DIR}=assets",
        "--follow-imports",
        f"--output-dir={output_dir}",
        "--output-filename=Oqteris",
        "--company-name=OriginSD",
        "--product-name=Oqteris",
        "--product-version=1.0.0",
        "--file-version=1.0.0",
        "--file-description=Complete Cross-Platform PDF Reader and Editor",
        "--copyright=Copyright 2026 OriginSD / Subhadip Dutta",
    ]

    # Platform specific icon and GUI flags
    if system == "Windows":
        cmd.extend([
            "--windows-console-mode=disable",
            f"--windows-icon-from-ico={ASSETS_DIR / 'icons' / 'app' / 'oqteris-logo.ico'}",
        ])
    elif system == "Darwin":
        cmd.extend([
            "--macos-create-app-bundle",
            f"--macos-app-icon={ASSETS_DIR / 'icons' / 'app' / 'oqteris-logo.png'}",
            "--macos-app-name=Oqteris",
        ])
    elif system == "Linux":
        cmd.extend([
            f"--linux-icon={ASSETS_DIR / 'icons' / 'app' / 'oqteris-logo.png'}",
        ])

    cmd.append(str(MAIN_SCRIPT))

    print(f"Executing Nuitka build command:\n{' '.join(cmd)}\n")
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(run_nuitka_build())
