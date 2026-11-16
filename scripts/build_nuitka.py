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
        "--assume-yes-for-downloads",
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
    ret = subprocess.call(cmd)
    if ret != 0:
        return ret

    # Normalize directory name to dist/Oqteris.dist if Nuitka created __main__.dist
    main_dist = output_dir / "__main__.dist"
    oqteris_dist = output_dir / "Oqteris.dist"
    if main_dist.exists() and not oqteris_dist.exists():
        print(f"Renaming {main_dist} to {oqteris_dist}")
        main_dist.rename(oqteris_dist)

    # Ensure executable name inside Oqteris.dist is Oqteris.exe / Oqteris
    if oqteris_dist.exists():
        if system == "Windows":
            main_exe = oqteris_dist / "__main__.exe"
            oqteris_exe = oqteris_dist / "Oqteris.exe"
            if main_exe.exists() and not oqteris_exe.exists():
                main_exe.rename(oqteris_exe)
        else:
            main_bin = oqteris_dist / "__main__.bin"
            oqteris_bin = oqteris_dist / "Oqteris"
            if main_bin.exists() and not oqteris_bin.exists():
                main_bin.rename(oqteris_bin)

    return 0


if __name__ == "__main__":
    sys.exit(run_nuitka_build())
