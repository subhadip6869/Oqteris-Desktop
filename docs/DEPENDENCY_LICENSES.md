# Third-Party Dependencies and Licensing Compliance

This document outlines the licensing terms, obligations, and distribution requirements for all core libraries bundled or linked with Oqteris.

## Summary Matrix

| Library | Primary License | Distribution Obligations & Compliance Notes |
|---|---|---|
| **PySide6** | LGPLv3 / Commercial | Dynamic linking allowed under LGPLv3; user must be able to replace Qt shared libraries or source code must be available. Commercial Qt license optional for proprietary static builds. |
| **PyMuPDF** | AGPLv3 / Commercial | PyMuPDF is dual-licensed under AGPLv3 and commercial license. Distributing compiled standalone bundles containing PyMuPDF triggers AGPLv3 copyleft terms unless a commercial Artifex license is acquired. Source code of Oqteris is made available under compatible open terms. |
| **pikepdf** | MPL-2.0 / QPDF Apache-2.0 | Permissive copyleft on file-by-file basis; compatible with proprietary and open distributions provided MPL-modified source files are disclosed. |
| **pyHanko** | MIT License | Permissive; requires inclusion of copyright notice and license text in distributions. |
| **cryptography** | Apache-2.0 / BSD-3-Clause | Permissive; requires standard attribution notices. |
| **SQLAlchemy** | MIT License | Permissive; requires copyright attribution. |
| **alembic** | MIT License | Permissive; requires copyright attribution. |
| **opencv-python-headless** | Apache-2.0 | Permissive; includes OpenCV patent and copyright notices. |
| **pytesseract** | Apache-2.0 | Permissive wrapper around external Tesseract binary. |
| **Tesseract OCR** | Apache-2.0 | Permissive external executable; distributed separately or with notice. |
| **OCRmyPDF** | MPL-2.0 | Permissive file-level copyleft; compliant with standalone invocation. |
| **Pillow** | MIT-CMU License | Permissive; requires attribution notices. |

## Important Compliance Notice for Commercial Distributors

When distributing standalone compiled packages of Oqteris:
1. **PyMuPDF AGPLv3 Notice**: If Oqteris is distributed in closed-source proprietary environments without source availability, a commercial license from Artifex Software is strictly required. For open distributions, the complete source code of Oqteris and modifications must remain available under AGPLv3/Apache-2.0 compatible terms.
2. **PySide6 LGPLv3 Notice**: Shared library dynamic linking or object relinking mechanisms must be preserved to fulfill LGPLv3 requirements.
3. Third-party licenses and notices are distributed in compiled installers under the `licenses/` or `resources/` directory.
