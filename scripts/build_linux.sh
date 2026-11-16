#!/usr/bin/env bash
# Linux Installer Build Script for Oqteris
# Builds both Debian (.deb) and Fedora/RHEL (.rpm) packages

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "==> Packaging Oqteris standalone executable with PyInstaller..."
python scripts/build_pyinstaller.py

if [ ! -d "dist/Oqteris.dist" ]; then
    echo "ERROR: Expected dist/Oqteris.dist directory was not created!" >&2
    exit 1
fi

# -------------------------------------------------------------
# 1. Build Debian Package (.deb)
# -------------------------------------------------------------
echo "==> Building Debian (.deb) package..."
DEB_DIR="dist/deb-pkg"
rm -rf "$DEB_DIR"
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/opt/oqteris"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/256x256/apps"

# Copy standalone binaries to /opt/oqteris
cp -r dist/Oqteris.dist/* "$DEB_DIR/opt/oqteris/"
chmod +x "$DEB_DIR/opt/oqteris/Oqteris"*

# Launcher script in /usr/bin/oqteris
cat << 'EOF' > "$DEB_DIR/usr/bin/oqteris"
#!/bin/sh
exec /opt/oqteris/Oqteris "$@"
EOF
chmod +x "$DEB_DIR/usr/bin/oqteris"

# Desktop entry and icon
cp packaging/linux/app.vercel.originsd.oqteris.desktop "$DEB_DIR/usr/share/applications/"
cp assets/icons/app/oqteris-logo.png "$DEB_DIR/usr/share/icons/hicolor/256x256/apps/app.vercel.originsd.oqteris.png"

# Control file
cat << 'EOF' > "$DEB_DIR/DEBIAN/control"
Package: oqteris
Version: 1.0.0
Section: office
Priority: optional
Architecture: amd64
Maintainer: Subhadip Dutta <subhadip6869@users.noreply.github.com>
Homepage: https://originsd.vercel.app
Description: Complete Cross-Platform PDF Reader and Editor
 Oqteris is a dedicated desktop PDF reader, editor, annotator, and security
 suite built with Python and Qt Quick/QML. Features high-performance rendering,
 digital signatures validation, OCR recognition, and document optimization.
EOF

DEB_OUTPUT="dist/Oqteris-1.0.0-Linux-x64.deb"
dpkg-deb --build "$DEB_DIR" "$DEB_OUTPUT"
rm -rf "$DEB_DIR"

if [ ! -f "$DEB_OUTPUT" ]; then
    echo "ERROR: Expected Debian package not found at $DEB_OUTPUT" >&2
    exit 1
fi
echo "==> Debian package created successfully: $DEB_OUTPUT"

# -------------------------------------------------------------
# 2. Build Fedora/RHEL RPM Package (.rpm)
# -------------------------------------------------------------
echo "==> Building Fedora/RHEL (.rpm) package..."
RPM_TOP="$PROJECT_ROOT/rpmbuild"
rm -rf "$RPM_TOP"
mkdir -p "$RPM_TOP"/{BUILD,RPMS,SOURCES,SPECS,SRPMS,BUILDROOT}

rpmbuild -bb \
    --define "_topdir $RPM_TOP" \
    --define "_sourcedir $PROJECT_ROOT" \
    packaging/linux/rpm/oqteris.spec

RPM_FILE=$(find "$RPM_TOP/RPMS" -type f -name "*.rpm" | head -n 1)
if [ -z "$RPM_FILE" ] || [ ! -f "$RPM_FILE" ]; then
    echo "ERROR: rpmbuild failed to produce an RPM package!" >&2
    exit 1
fi

RPM_OUTPUT="dist/Oqteris-1.0.0-Linux-x64.rpm"
cp "$RPM_FILE" "$RPM_OUTPUT"
rm -rf "$RPM_TOP"

echo "==> RPM package created successfully: $RPM_OUTPUT"
