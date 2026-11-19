#!/usr/bin/env bash
# macOS Installer Build Script for Oqteris
# Runs PyInstaller packaging and packages Apple Disk Image (.dmg)

set -euo pipefail

echo "==> Packaging Oqteris macOS Application Bundle with PyInstaller..."
python scripts/build_pyinstaller.py

if [ ! -d "dist/Oqteris.app" ]; then
    echo "ERROR: Expected app bundle dist/Oqteris.app was not created!" >&2
    exit 1
fi

echo "==> Preparing DMG staging area..."
STAGING_DIR="dist/dmg_staging"
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"
cp -R dist/Oqteris.app "$STAGING_DIR/"
ln -s /Applications "$STAGING_DIR/Applications"

DMG_OUTPUT="dist/Oqteris-1.2.0-macOS-arm64.dmg"
rm -f "$DMG_OUTPUT"

echo "==> Creating macOS DMG installer with hdiutil..."
hdiutil create -volname "Oqteris" -srcfolder "$STAGING_DIR" -ov -format UDZO "$DMG_OUTPUT"
rm -rf "$STAGING_DIR"

if [ ! -f "$DMG_OUTPUT" ]; then
    echo "ERROR: Expected DMG installer not found at $DMG_OUTPUT" >&2
    exit 1
fi

echo "==> macOS DMG installer created successfully: $DMG_OUTPUT"
