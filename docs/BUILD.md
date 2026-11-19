# Building and Compiling Oqteris

This guide details how to build and package Oqteris into standalone native binaries for Windows, macOS, and Linux.

## Requirements

- Python 3.13 or newer
- PyInstaller (`pip install pyinstaller`)

## Standalone Packaging with PyInstaller

Oqteris includes an automated build script: [`scripts/build_pyinstaller.py`](../scripts/build_pyinstaller.py).

```bash
# Activate virtual environment
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate # Linux/macOS

# Run the build script
python scripts/build_pyinstaller.py
```

The script configures PyInstaller using the project spec file [`packaging/pyinstaller/oqteris.spec`](../packaging/pyinstaller/oqteris.spec) with:

- `--onedir` standalone bundle
- PySide6 and QML plugins collection
- Data directories for QML files and assets
- Platform-appropriate icons and GUI flags

Packaged artifacts will be located under `dist/Oqteris.dist/` (Windows/Linux) or `dist/Oqteris.app/` (macOS).

---

## Windows Packaging

### Inno Setup Installer

To produce a single-file executable installer (`Oqteris-X.X.X-Windows-x64-Setup.exe`):

1. Package the standalone distribution via `python scripts/build_pyinstaller.py` or `powershell ./scripts/build_windows.ps1`.
2. Install [Inno Setup 6](https://jrsoftware.org/isdl.php).
3. Compile the setup script:
   ```cmd
   iscc packaging\windows\setup.iss
   ```
4. The installer executable will be generated under `dist\`.

The installer automatically:

- Registers the application under Windows Programs.
- Configures `.pdf` file associations.
- Assigns the dedicated PDF document icon (`oqteris-document.ico`).
- Registers Oqteris with Windows *Default Apps*.

---

## Linux Packaging

### Debian Package (.deb)

```bash
dpkg-buildpackage -us -uc -b
```

### RPM Package (.rpm)

```bash
rpmbuild -ba packaging/linux/rpm/oqteris.spec
```

### Arch Linux Package (.pkg.tar.zst)

```bash
cd packaging/linux/arch
makepkg -si
```

---

## macOS Packaging

Nuitka produces an application bundle `dist/Oqteris.app`.

To package into a distributable DMG:

```bash
hdiutil create -volname "Oqteris" -srcfolder dist/Oqteris.app -ov -format UDZO dist/Oqteris-X.X.X-macOS.dmg
```
