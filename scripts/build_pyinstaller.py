"""Build script for packaging Oqteris into a standalone distribution using PyInstaller."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
DIST_DIR = PROJECT_ROOT / "dist"
SPEC_FILE = PROJECT_ROOT / "packaging" / "pyinstaller" / "oqteris.spec"


def run_pyinstaller_build() -> int:
    """Run PyInstaller with the project spec file and stage outputs for packaging."""
    system = platform.system()
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    if not SPEC_FILE.exists():
        print(f"ERROR: Spec file not found at {SPEC_FILE}", file=sys.stderr)
        return 1

    work_dir = PROJECT_ROOT / "build" / "pyinstaller"
    work_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(work_dir),
        str(SPEC_FILE),
    ]

    print(f"Executing PyInstaller build command:\n{' '.join(cmd)}\n")

    env = os.environ.copy()
    current_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + current_pp if current_pp else "")

    ret = subprocess.call(cmd, env=env)
    if ret != 0:
        print(f"ERROR: PyInstaller failed with exit code {ret}", file=sys.stderr)
        return ret

    # Staging for installers:
    # Inno Setup (Windows) and RPM/DEB (Linux) expect files in dist/Oqteris.dist
    oqteris_dir = DIST_DIR / "Oqteris"
    oqteris_dist = DIST_DIR / "Oqteris.dist"

    if system in ("Windows", "Linux"):
        if oqteris_dir.exists():
            print(f"Staging {oqteris_dir} -> {oqteris_dist} for installers...")
            shutil.copytree(oqteris_dir, oqteris_dist, dirs_exist_ok=True)

        # Verify executable exists
        expected_exe = oqteris_dist / ("Oqteris.exe" if system == "Windows" else "Oqteris")
        if expected_exe.exists():
            print(f"Executable successfully generated at: {expected_exe}")
        else:
            print(f"WARNING: Expected executable not found at {expected_exe}", file=sys.stderr)
    elif system == "Darwin":
        expected_app = DIST_DIR / "Oqteris.app"
        if expected_app.exists():
            print(f"macOS Application Bundle successfully generated at: {expected_app}")
        else:
            print(f"WARNING: Expected macOS bundle not found at {expected_app}", file=sys.stderr)

    print("==> PyInstaller build completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(run_pyinstaller_build())
