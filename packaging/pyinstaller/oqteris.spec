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
# Only bundle QML modules actually used by Oqteris (QtQuick, Controls, Dialogs, Layouts, etc.)
# Avoid copying huge unused QML modules (QtWebEngine, Qt3D, QtQuick3D, QtCharts, etc.)
_pyside6_qml = PYSIDE6_DIR / "qml"
if _pyside6_qml.is_dir():
    qml_needed = {"QtCore", "QtQml", "QtQuick", "Qt"}
    for item in _pyside6_qml.iterdir():
        if item.is_dir() and item.name in qml_needed:
            datas.append((str(item), f"PySide6/qml/{item.name}"))

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
    "mypy",
    "PySide6.Qt3DCore",
    "PySide6.Qt3DRender",
    "PySide6.Qt3DAnimation",
    "PySide6.Qt3DInput",
    "PySide6.Qt3DLogic",
    "PySide6.Qt3DExtras",
    "PySide6.QtSensors",
    "PySide6.QtSerialPort",
    "PySide6.QtBluetooth",
    "PySide6.QtNfc",
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineQuick",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtQuick3D",
    "PySide6.QtQuick3DRuntimeRender",
    "PySide6.QtQuick3DPhysics",
    "PySide6.QtCharts",
    "PySide6.QtGraphs",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    "PySide6.QtPositioning",
    "PySide6.QtRemoteObjects",
    "PySide6.QtScxml",
    "PySide6.QtSpatialAudio",
    "PySide6.QtTest",
    "PySide6.QtDataVisualization",
    "PySide6.QtPdf",
    "PySide6.QtPdfWidgets",
    "PySide6.QtPdfQuick",
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
    optimize=2,
)

# Strip unwanted heavy native binaries (e.g. WebEngine ~195MB, FFmpeg video DLL ~30MB, 3D ~25MB)
EXCLUDED_BINARY_PATTERNS = {
    # WebEngine / Chromium
    "qt6webengine",
    "qtwebengine",
    # 3D and Quick3D
    "qt63d",
    "qt6quick3d",
    # Unused Qt multimedia / peripherals / charts
    "qt6charts",
    "qt6graphs",
    "qt6sensors",
    "qt6serialport",
    "qt6bluetooth",
    "qt6nfc",
    "qt6pdf",
    "qt6spatialaudio",
    "qt6multimedia",
    "qt6positioning",
    "qt6remoteobjects",
    "qt6scxml",
    "qt6test",
    "qt6datavisualization",
    "qt6virtualkeyboard",
    # OpenCV video codec DLL (unneeded for PDF documents)
    "opencv_videoio_ffmpeg",
}

def _keep_binary(entry):
    dest = str(entry[0]).lower()
    src = str(entry[1]).lower() if len(entry) > 1 else ""
    return not any(pat in dest or pat in src for pat in EXCLUDED_BINARY_PATTERNS)

a.binaries = [b for b in a.binaries if _keep_binary(b)]

# Strip unwanted bundled data (e.g. PyMuPDF ONNX models ~49MB, C++ dev SDK ~6.5MB, Qt translations ~8.5MB)
EXCLUDED_DATA_PATTERNS = [
    "resources/onnx",
    "resources\\onnx",
    "mupdf-devel",
    "pyside6/translations",
    "pyside6\\translations",
    "pyside6/qml/qtwebengine",
    "pyside6\\qml\\qtwebengine",
    "pyside6/qml/qt3d",
    "pyside6\\qml\\qt3d",
    "pyside6/qml/qtquick3d",
    "pyside6\\qml\\qtquick3d",
    "pyside6/qml/qtcharts",
    "pyside6\\qml\\qtcharts",
    "pyside6/qml/qtgraphs",
    "pyside6\\qml\\qtgraphs",
    "pyside6/qml/qtmultimedia",
    "pyside6\\qml\\qtmultimedia",
    "pyside6/qml/qtsensors",
    "pyside6\\qml\\qtsensors",
    "pyside6/qml/qtpositioning",
    "pyside6\\qml\\qtpositioning",
]

def _keep_data(entry):
    dest = str(entry[0]).lower().replace("/", "\\")
    src = (str(entry[1]).lower().replace("/", "\\")) if len(entry) > 1 else ""
    # Exclude data folders (ONNX models, translations, etc.)
    if any(pat.replace("/", "\\") in dest or pat.replace("/", "\\") in src for pat in EXCLUDED_DATA_PATTERNS):
        return False
    # Also exclude any unwanted binary/plugin that PyInstaller collected into datas
    if any(pat in dest or pat in src for pat in EXCLUDED_BINARY_PATTERNS):
        return False
    return True

a.datas = [d for d in a.datas if _keep_data(d)]

pyz = PYZ(a.pure)

icon_file = None
version_file = None
if system == "Windows":
    ico = ASSETS_DIR / "icons" / "app" / "oqteris-logo.ico"
    if ico.exists():
        icon_file = str(ico)
    ver_path = PROJECT_ROOT / "packaging" / "windows" / "version_info.txt"
    if ver_path.exists():
        version_file = str(ver_path)
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
    version=version_file,
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
            "CFBundleVersion": "1.2.1",
            "CFBundleShortVersionString": "1.2.1",
            "CFBundlePackageType": "APPL",
            "NSHighResolutionCapable": "True",
            "LSMinimumSystemVersion": "12.0",
            "CFBundleDocumentTypes": [
                {
                    "CFBundleTypeName": "PDF Document",
                    "CFBundleTypeRole": "Editor",
                    "LSHandlerRank": "Owner",
                    "CFBundleTypeIconFile": "oqteris-document.icns",
                    "CFBundleTypeExtensions": ["pdf"],
                    "CFBundleTypeMIMETypes": ["application/pdf"],
                    "LSItemContentTypes": ["com.adobe.pdf"],
                }
            ],
        },
    )
