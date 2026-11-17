# -*- mode: python ; coding: utf-8 -*-
import os
import platform
import sys
from pathlib import Path
import PySide6

spec_path = Path(SPEC).resolve() if "SPEC" in locals() else Path("packaging/pyinstaller/oqteris.spec").resolve()
PROJECT_ROOT = spec_path.parents[2] if len(spec_path.parents) > 2 and spec_path.parent.name == "pyinstaller" else spec_path.parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
PYSIDE6_DIR = Path(PySide6.__file__).resolve().parent

system = platform.system()

datas = [
    (str(SRC_DIR / "oqteris" / "ui" / "qml"), "oqteris/ui/qml"),
    (str(ASSETS_DIR), "assets"),
]

# PySide6/qml ships with PySide6-Addons; guard against environments where it is absent.
_pyside6_qml = PYSIDE6_DIR / "qml"
if _pyside6_qml.is_dir():
    datas.append((str(_pyside6_qml), "PySide6/qml"))

hiddenimports = [
    "oqteris",
    "oqteris.main",
    "oqteris.application.single_instance",
    "oqteris.config.settings",
    "oqteris.database.connection",
    "oqteris.database.models",
    "oqteris.platform.storage",
    "oqteris.pdf.signatures.service",
    "oqteris.pdf.signatures.models",
    "oqteris.ui.controllers.pdf_controller",
    "oqteris.ui.controllers.app_controller",
    "oqteris.ui.controllers.ribbon_controller",
    "oqteris.ui.controllers.annotation_controller",
    "oqteris.ui.controllers.signature_controller",
    "oqteris.ui.controllers.organize_controller",
    "oqteris.repositories.bookmarks_repo",
    "oqteris.repositories.recent_files_repo",
    "pyhanko",
    "pyhanko.pdf_utils.incremental_writer",
    "pyhanko.sign.validation",
    "pyhanko.sign.fields",
    "pyhanko.sign.signers",
    "pyhanko_certvalidator",
    "cryptography",
    "asn1crypto",
    "asn1crypto.pem",
    "asn1crypto.x509",
    "fitz",
    "pymupdf",
    "sqlalchemy",
    "sqlalchemy.dialects.sqlite",
    "sqlite3",
    "PIL",
]

excludes = [
    "tkinter",
    "unittest",
    "pytest",
    "IPython",
    "matplotlib",
    "scipy",
    "pandas",
    "PySide6.Qt3DCore",
    "PySide6.Qt3DRender",
    "PySide6.Qt3DAnimation",
    "PySide6.QtSensors",
    "PySide6.QtSerialPort",
    "PySide6.QtBluetooth",
    "PySide6.QtNfc",
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineQuick",
    "PySide6.QtQuick3D",
]

a = Analysis(
    [str(PROJECT_ROOT / "run_app.py")],
    pathex=[str(SRC_DIR), str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

icon_file = None
if system == "Windows":
    ico = ASSETS_DIR / "icons" / "app" / "oqteris-logo.ico"
    if ico.exists():
        icon_file = str(ico)
elif system == "Darwin":
    icns = ASSETS_DIR / "icons" / "app" / "oqteris-logo.icns"
    if icns.exists():
        icon_file = str(icns)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Oqteris",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Oqteris",
)

if system == "Darwin":
    app = BUNDLE(
        coll,
        name="Oqteris.app",
        icon=icon_file,
        bundle_identifier="app.vercel.originsd.oqteris",
        info_plist={
            "CFBundleDisplayName": "Oqteris",
            "CFBundleName": "Oqteris",
            "CFBundleIdentifier": "app.vercel.originsd.oqteris",
            "CFBundleVersion": "1.0.0",
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": "True",
            "LSMinimumSystemVersion": "12.0",
        },
    )
