"""Build script for compiling Oqteris into a standalone executable using Nuitka."""

import os
import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
MAIN_SCRIPT = PROJECT_ROOT / "run_app.py"


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
        "--lto=no",
        "--nofollow-import-to=pytest,unittest,setuptools,pip,IPython,tkinter",
        "--enable-plugin=pyside6",
        "--include-qt-plugins=sensible,qml",
        "--include-package=oqteris",
        f"--include-data-dir={SRC_DIR / 'oqteris' / 'ui' / 'qml'}=oqteris/ui/qml",
        f"--include-data-dir={ASSETS_DIR}=assets",
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
        icns_path = ASSETS_DIR / "icons" / "app" / "oqteris-logo.icns"
        icon_arg = icns_path if icns_path.exists() else (ASSETS_DIR / "icons" / "app" / "oqteris-logo.png")
        cmd.extend([
            "--macos-create-app-bundle",
            f"--macos-app-icon={icon_arg}",
            "--macos-app-name=Oqteris",
        ])
    elif system == "Linux":
        cmd.extend([
            f"--linux-icon={ASSETS_DIR / 'icons' / 'app' / 'oqteris-logo.png'}",
        ])

    cmd.append(str(MAIN_SCRIPT))

    print(f"Executing Nuitka build command:\n{' '.join(cmd)}\n")

    # Set PYTHONPATH to include src so Nuitka can always locate oqteris package
    env = os.environ.copy()
    current_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + current_pp if current_pp else "")

    ret = subprocess.call(cmd, env=env)
    if ret != 0:
        return ret

    # Normalize directory name to dist/Oqteris.dist
    candidate_dists = [
        output_dir / "run_app.dist",
        output_dir / "__main__.dist",
    ]
    target_dist = output_dir / "Oqteris.dist"

    for cand in candidate_dists:
        if cand.exists() and not target_dist.exists():
            print(f"Renaming {cand} to {target_dist}")
            cand.rename(target_dist)
            break

    # Ensure executable name inside Oqteris.dist is Oqteris.exe / Oqteris
    if target_dist.exists():
        if system == "Windows":
            for name in ["run_app.exe", "__main__.exe"]:
                old_exe = target_dist / name
                oqteris_exe = target_dist / "Oqteris.exe"
                if old_exe.exists() and not oqteris_exe.exists():
                    old_exe.rename(oqteris_exe)
        else:
            for name in ["run_app.bin", "__main__.bin", "run_app", "__main__"]:
                old_bin = target_dist / name
                oqteris_bin = target_dist / "Oqteris"
                if old_bin.exists() and not oqteris_bin.exists():
                    old_bin.rename(oqteris_bin)

    return 0


if __name__ == "__main__":
    sys.exit(run_nuitka_build())
