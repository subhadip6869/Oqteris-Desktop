# Building and Compiling Oqteris

This guide details how to build and package Oqteris into standalone native binaries for Windows, macOS, and Linux.

## Requirements

- Python 3.13 or newer
- C/C++ compiler toolchain (Visual Studio Build Tools on Windows, Xcode CLI on macOS, GCC/Clang on Linux)
- Nuitka (`pip install nuitka`)

## Standalone Compilation with Nuitka

Oqteris includes an automated build script: [`scripts/build_nuitka.py`](../scripts/build_nuitka.py).

```bash
# Activate virtual environment
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate # Linux/macOS

# Run the build script
python scripts/build_nuitka.py
```

The script configures Nuitka with:

- `--standalone`
- `--enable-plugin=pyside6`
- `--include-package=oqteris`
- Data directories for QML files and icons
- Platform-appropriate icons and GUI flags (`--windows-console-mode=disable`, `--macos-create-app-bundle`)

Compiled artifacts will be located under `dist/Oqteris.dist/` (Windows/Linux) or `dist/Oqteris.app/` (macOS).

---

## Windows Packaging

### Inno Setup Installer

To produce a single-file executable installer (`Oqteris-1.0.0-Windows-x64-Setup.exe`):

1. Compile the standalone distribution via `python scripts/build_nuitka.py`.
2. Install [Inno Setup 6](https://jrsoftware.org/isdl.php).
3. Compile the setup script:
   ```cmd
   iscc packaging\windows\setup.iss
   ```
4. The installer executable will be generated under `dist\installer\`.

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
hdiutil create -volname "Oqteris" -srcfolder dist/Oqteris.app -ov -format UDZO dist/Oqteris-1.0.0-macOS.dmg
```
