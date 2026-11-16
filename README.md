# Oqteris

<p align="center">
  <img src="assets/icons/app/oqteris-logo.png" alt="Oqteris Logo" width="128" height="128">
</p>

<p align="center">
  <b>Complete Cross-Platform Desktop PDF Reader and Editor</b><br>
  Engineered with Python 3.13+ and Qt Quick / QML
</p>

<p align="center">
  <a href="https://github.com/subhadip6869/Oqteris-Desktop/actions/workflows/build-and-release.yml"><img src="https://img.shields.io/github/actions/workflow/status/subhadip6869/Oqteris-Desktop/build-and-release.yml?branch=main&label=Build%20%26%20Release" alt="Build Status"></a>
  <a href="https://github.com/subhadip6869/Oqteris-Desktop/releases"><img src="https://img.shields.io/github/v/release/subhadip6869/Oqteris-Desktop?label=Release" alt="Latest Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache-2.0"></a>
  <a href="https://originsd.vercel.app"><img src="https://img.shields.io/badge/Organization-OriginSD-0078D4.svg" alt="Organization: OriginSD"></a>
</p>

---

## Overview

**Oqteris** is a dedicated, high-performance desktop PDF reader, editor, annotator, and security suite built for Windows, macOS, and Linux. It pairs a ribbon-based interface implemented in Qt Quick / QML with Python 3.13+ document processing services.

Oqteris provides a reliable reading experience, direct PDF manipulation, AcroForm filling, cryptographic digital signature verification via pyHanko, searchable PDF generation via OCR, and safe transactional persistence.

## Key Capabilities

- **Ribbon Desktop Interface**: Custom Qt Quick ribbon featuring *Home*, *View*, *Edit*, *Comment*, *Organize*, *Convert*, *Fill & Sign*, *Protect*, and *Help* command groups with light and dark themes.
- **High-Performance Document Engine**: Powered by PyMuPDF with asynchronous page rasterization and a bounded LRU memory tile cache.
- **PDF Manipulation**: Direct text insertion, text replacement with clean background redaction, image insertion, and hyperlink authoring with an undo/redo command stack.
- **Comprehensive Markup & Annotation**: Text highlighting, underlining, strikethrough, sticky comment notes, freehand ink drawings, geometric shapes (rectangles, circles, lines, arrows), and document stamps.
- **Page Organization**: Reorder, rotate, delete, extract, split, and merge PDF pages with single-click actions.
- **Cryptographic Digital Signatures**: pyHanko-powered signature inspection, byte-range integrity verification, certificate chain validation, trust store evaluation, and PKCS#12 digital signing.
- **Form Workflows**: Interactive AcroForms detection, field inspection, form filling, field resetting, and form flattening.
- **OCR Engine**: Tesseract OCR and OpenCV image preprocessing (deskewing, contrast enhancement) for generating searchable PDFs from scanned documents.
- **Optimization & Compression**: Stream compression, image downsampling, and metadata cleaning via pikepdf.
- **Local Application Persistence**: SQLite database managed with SQLAlchemy and platform-aware storage adhering to Windows `%LOCALAPPDATA%`, macOS `Application Support`, and Linux XDG standards.
- **Single-Instance IPC**: Native local socket coordinator for handling command-line arguments and file associations.

## Technology Stack

| Technology | Responsibility |
|---|---|
| **Python 3.13+** | Core application logic and asynchronous services |
| **PySide6** | Python bindings for Qt 6 |
| **Qt Quick / QML** | Ribbon user interface and GPU-accelerated workspace |
| **PyMuPDF** | Primary PDF rendering, text extraction, search, and page interaction |
| **pikepdf** | Structural manipulation, stream optimization, and merging/splitting |
| **pyHanko** | Cryptographic digital signatures, certificate validation, and PKCS#12 signing |
| **OCRmyPDF / Tesseract** | OCR text recognition and searchable PDF creation |
| **OpenCV** | Image preprocessing, deskewing, and contrast binarization |
| **SQLite + SQLAlchemy** | Persistent relational database for recent files, bookmarks, and trust stores |
| **Nuitka** | Standalone compilation and native binary deployment |

## Quick Start

### Prerequisites

- Python 3.13 or newer
- Git
- Tesseract OCR (optional, for scanned PDF recognition)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/subhadip6869/Oqteris-Desktop.git
   cd Oqteris-Desktop
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv .venv

   # Windows
   .\.venv\Scripts\activate

   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Run the Application**:
   ```bash
   python -m oqteris
   ```

5. **Run the Automated Test Suite**:
   ```bash
   pytest -v
   ```

## Documentation

Comprehensive project documentation is available in the [`docs/`](docs/) directory:

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Feature Breakdown](docs/FEATURES.md)
- [Building & Compilation](docs/BUILD.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Platform Integration & Default Viewer](docs/PLATFORM_INTEGRATION.md)
- [Data Storage & Persistence Layout](docs/DATA_STORAGE.md)
- [Digital Signatures & Security Trust Model](docs/DIGITAL_SIGNATURES.md)
- [OCR Capabilities & Setup](docs/OCR.md)
- [CI/CD & Release Process](docs/RELEASE_PROCESS.md)
- [Third-Party Dependency Licenses](docs/DEPENDENCY_LICENSES.md)
- [Project Roadmap](docs/ROADMAP.md)

## Organization & Maintainer

- **Developer**: Subhadip Dutta ([@subhadip6869](https://github.com/subhadip6869))
- **Organization**: OriginSD ([originsd.vercel.app](https://originsd.vercel.app))
- **Repository**: [https://github.com/subhadip6869/Oqteris-Desktop](https://github.com/subhadip6869/Oqteris-Desktop)
- **Application ID**: `app.vercel.originsd.oqteris`

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
