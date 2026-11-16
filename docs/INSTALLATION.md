# Installing Oqteris

## Standalone Release Downloads

Pre-built binaries for supported operating systems are available on the [GitHub Releases](https://github.com/subhadip6869/Oqteris-Desktop/releases) page:

| Operating System | Package Type | Filename |
|---|---|---|
| **Windows (x64)** | Setup Installer | `Oqteris-1.0.0-Windows-x64-Setup.exe` |
| **Windows (x64)** | Portable ZIP | `Oqteris-1.0.0-Windows-x64.zip` |
| **macOS (Apple Silicon)** | DMG Disk Image | `Oqteris-1.0.0-macOS-arm64.dmg` |
| **macOS (Intel)** | DMG Disk Image | `Oqteris-1.0.0-macOS-x64.dmg` |
| **Linux (Debian / Ubuntu)** | Debian Package | `Oqteris-1.0.0-Linux-x64.deb` |
| **Linux (Fedora / RHEL)** | RPM Package | `Oqteris-1.0.0-Linux-x64.rpm` |
| **Arch Linux** | Arch Package | `Oqteris-1.0.0-Arch-x86_64.pkg.tar.zst` |

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
