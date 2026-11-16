# Platform Integration and Default PDF Viewer

Oqteris integrates natively with the desktop environment across Windows, Linux, and macOS.

## Default PDF Viewer Registration

### Windows
1. **ProgID Registration**: Registers `Oqteris.PDF` under `HKCU\Software\Classes\Oqteris.PDF`.
2. **Document Icon**: Maps `assets/icons/document/oqteris-document.ico` to the `DefaultIcon` registry key.
3. **Open Command**: Associates `"Oqteris.exe" "%1"` under `shell\open\command`.
4. **Registered Applications**: Declares capability under `Software\RegisteredApplications` so Windows *Default Apps Settings* recognizes Oqteris as a PDF reader.

### Linux
1. **Desktop Entry**: Installs `app.vercel.originsd.oqteris.desktop` to `/usr/share/applications/` or `~/.local/share/applications/`.
2. **MIME Association**: Registers `application/pdf` via `xdg-mime default app.vercel.originsd.oqteris.desktop application/pdf`.
3. **Application & Document Icons**: Installs PNG icons into the standard `hicolor` icon theme directory.

### macOS
1. **Info.plist**: Declares `CFBundleDocumentTypes` with extension `pdf` and role `Editor`.
2. **Document Icon**: Embeds `oqteris-document.icns`.

---

## Single-Instance Coordination & IPC

To prevent multiple overlapping windows and resource contention, Oqteris enforces single-instance execution:
- **Mechanism**: PySide6 `QLocalServer` and `QLocalSocket`.
- **Socket Identifier**: `app.vercel.originsd.oqteris_<username>_ipc`.
- **Behavior**:
  - If an existing instance is active, subsequent invocations forward command-line file paths via the local socket and immediately exit.
  - The primary instance receives the incoming path list, brings its main window to the foreground, and opens the requested PDF documents in workspace tabs.
