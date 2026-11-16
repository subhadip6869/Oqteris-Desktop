# Oqteris Architecture Guide

## Overview

Oqteris follows a modular, decoupled desktop architecture based on SOLID principles. The application separates presentation code (Qt Quick / QML) from business services, PDF document operations, and relational database persistence.

```
+-----------------------------------------------------------------+
|                    Qt Quick / QML Interface                     |
|  (RibbonBar, NavigationPanel, Workspace, Dialogs, Theme System) |
+-----------------------------------------------------------------+
                                |
                   Qt Properties, Signals & Slots
                                |
+-----------------------------------------------------------------+
|                    QObject UI Controllers                       |
|   (AppController, PDFController, RibbonController, etc.)        |
+-----------------------------------------------------------------+
                                |
                         Service Layer
                                |
+-----------------------------------------------------------------+
|                    Domain Processing Services                   |
|  - PDFDocument / PDFRasterizer (PyMuPDF)                        |
|  - pikepdf (Optimization, Merge, Split)                         |
|  - pyHanko (Signatures, ValidationContext, PKCS#12)             |
|  - OCRService (Tesseract, OpenCV Preprocessing)                 |
+-----------------------------------------------------------------+
                                |
                        Persistence Layer
                                |
+-------------------------------+---------------------------------+
|   StorageManager (AppData/XDG)|   SQLAlchemy Engine & Repos     |
|   - settings.json (Atomic)    |   - SQLite (oqteris.db, WAL)    |
|   - temp/, cache/, logs/      |   - RecentFiles, Certs, Bookmarks|
+-------------------------------+---------------------------------+
```

## Layer Responsibilities

### 1. Presentation Layer (`src/oqteris/ui/qml/`)
- Pure declarative QML components with zero direct PDF library dependencies.
- Custom ribbon controls (`OqRibbonButton`, `OqRibbonGroup`, `OqTabButton`).
- Direct GPU-backed page rendering through `QQuickImageProvider` (`image://pdf/<doc_id>/<page>?zoom=1.5`).
- Reactive theme switcher (`Theme.qml`) supporting seamless light and dark palettes.

### 2. Controller Layer (`src/oqteris/ui/controllers/`)
- QObject classes registered to the QML root context:
  - `AppController`: Application metadata, theme toggling, default viewer status.
  - `PDFController`: Multi-tab document switching, visible page navigation, zoom presets, rotation, full-text search.
  - `RibbonController`: Active tab and tool state, undo/redo dispatching.
  - `AnnotationController`: Markup additions (highlights, sticky notes, ink drawing, shapes, stamps).
  - `SignatureController`: Digital signature verification, trust badge evaluation, PKCS#12 signing.
  - `OrganizeController`: Page deletion, extraction, rotation, PDF splitting and merging.
  - `OCRController`: OCR job execution, progress reporting, cancellation.
  - `SettingsController`: Configuration read/write bindings.

### 3. PDF Engine & Service Layer (`src/oqteris/pdf/`)
- Distinct library responsibilities:
  - **PyMuPDF (`pymupdf`)**: High-speed rasterization, word-level text extraction with bounding boxes, search, and AcroForm interactions.
  - **pikepdf**: Low-level PDF object tree manipulation, stream deflate compression, deduplication, and page extraction.
  - **pyHanko**: Strict cryptographic signature validation and incremental-update digital signing.
  - **Tesseract & OpenCV**: Image deskewing, thresholding, and OCR text overlay generation.

### 4. Storage & Persistence (`src/oqteris/platform/`, `src/oqteris/database/`)
- Platform-native directory layouts (`StorageManager`).
- Scoped SQLAlchemy sessions with Write-Ahead Logging (`PRAGMA journal_mode=WAL`).
- Atomic writes (`os.replace`) for application configuration (`settings.json`).
- Centralized rotating logging with automatic redacting of private keys and passwords.
