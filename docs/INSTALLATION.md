# Installing Oqteris

## Standalone Release Downloads

Pre-built binaries for supported operating systems are available on the [GitHub Releases](https://github.com/subhadip6869/Oqteris-Desktop/releases) page:

| Operating System | Package Type | Filename |
|---|---|---|
| **Windows (x64)** | Setup Installer | `Oqteris-X.X.X-Windows-x64-Setup.exe` |
| **macOS (Apple Silicon)** | DMG Disk Image | `Oqteris-X.X.X-macOS-arm64.dmg` |
| **Linux (Debian / Ubuntu)** | Debian Package | `Oqteris-X.X.X-Linux-x64.deb` |
| **Linux (Fedora / RHEL)** | RPM Package | `Oqteris-X.X.X-Linux-x64.rpm` |

---

## Installing from Source

If you prefer running Oqteris directly from source:

### 1. Prerequisites
- Python 3.13 or newer
- Git
- Tesseract OCR (Optional, for OCR recognition)

### 2. Steps
```bash
git clone https://github.com/subhadip6869/Oqteris-Desktop.git
cd Oqteris-Desktop

python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .

# Launch Oqteris
python -m oqteris
```
