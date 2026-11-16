# Oqteris Feature Breakdown

This document provides a comprehensive summary of all implemented features across the 8 functional phases of Oqteris.

## 1. Document Viewing & Navigation
- **Asynchronous Rendering**: High-speed page rasterization powered by PyMuPDF.
- **LRU Render Cache**: Bounded in-memory page cache limiting memory footprint (default 256 MB) with instant tile hits on revisiting pages.
- **Display Modes**:
  - *Continuous Mode*: Smooth vertical scrolling of all document pages.
  - *Single Page Mode*: Centered single page display.
- **Zoom Capabilities**:
  - Slider and incremental zoom buttons (10% to 1000%).
  - One-click presets: *100% Actual Size*, *Fit to Width*, *Fit Entire Page*.
- **Page Rotation**: 90-degree relative rotation per page or document-wide.
- **Document Outlines**: Interactive Table of Contents sidebar for direct chapter jumping.
- **Full-Text Search**: In-document text queries with bounding box match navigation and match counter.
- **Multi-Document Tabs**: Open and switch between multiple PDF documents simultaneously.

## 2. Ribbon Desktop Interface
- **Command Tabs**:
  - `Home`: Core file operations, undo/redo, pointer/hand tools, zoom controls, and rotation.
  - `View`: Continuous and single-page display modes, sidebar panel toggles, and search.
  - `Edit`: Add text, edit/redact text, insert images, add links.
  - `Comment`: Highlights, underlines, strikethrough, sticky comment notes, freehand ink drawings, geometric shapes, and document stamps.
  - `Organize`: Page deletion, extraction, rotation, PDF splitting, and merging.
  - `Convert`: Export pages as PNG images, convert images to PDF, OCR recognition, and compression.
  - `Fill & Sign`: AcroForm field interaction, form reset, visual drawing signature, and digital signing.
  - `Protect`: Digital signature validation, cryptographic signing, certificate trust inspection.
  - `Help`: About dialog, settings, theme toggle.
- **Quick-Access Toolbar**: Fast access to Open, Save, Undo, Redo, and Theme switches.
- **Status Bar**: Live page index input, total page count, zoom slider, zoom percentage, and fit buttons.

## 3. PDF Editing & Annotations
- **Text Insertion**: Insert custom text at arbitrary coordinates with custom font size, color, and font face.
- **Direct Text Editing**: Replace existing text within bounding boxes utilizing background redaction followed by text re-insertion.
- **Image Insertion**: Embed external images (PNG, JPEG) onto pages preserving aspect ratios.
- **Hyperlinks**: Author URI links and internal Goto-Page links.
- **Markup Annotations**:
  - Yellow / custom color text highlights.
  - Underline and strikethrough markup.
  - Sticky notes with author metadata and popups.
  - Freehand ink drawings with custom stroke width.
  - Geometric shapes (rectangles, circles, lines, arrows).
  - Pre-defined and custom stamps (APPROVED, CONFIDENTIAL, DRAFT, FINAL).
- **Undo / Redo Stack**: Reversible command pattern for all document modifications.

## 4. Digital Signatures & Cryptography
- **Signature Detection**: Automatically identifies digitally signed documents upon opening.
- **Integrity Verification**: Validates byte-range hash intactness using pyHanko.
- **Modification Checks**: Detects if document alterations were made subsequent to signing.
- **Certificate Inspection**: Extracts common name, organization, issuer, validity period, serial number, and SHA-256 fingerprint.
- **Trust Evaluation**:
  - Clear separation between cryptographic validity and certificate trust.
  - Self-signed certificates are flagged as *UNTRUSTED* until explicitly added to the application trust store.
- **PKCS#12 Digital Signing**: Cryptographically signs documents with PKCS#12 (.p12/.pfx) certificates using incremental updates, preserving prior document revisions.

## 5. AcroForms Support
- **Field Detection**: Scans and parses text fields, checkboxes, radio buttons, and choice dropdowns.
- **Interactive Values**: Reads and updates form field values.
- **Form Reset**: Restores all form inputs back to default values.

## 6. OCR & Optimization
- **Scanned Document Detection**: Evaluates text density versus raster image area to identify scanned PDFs.
- **OpenCV Preprocessing**: Corrects image skew (rotation) and enhances contrast before OCR recognition.
- **Searchable PDF Generation**: Integrates with Tesseract OCR to create invisible searchable text overlays.
- **PDF Compression**: pikepdf stream compression, object deduplication, and embedded image recompression.
- **Splitting & Merging**: Reorganize documents into multi-part chunks or combine disparate files into a unified document.

## 7. Platform Integration
- **Storage Layouts**: Adheres to Windows `%LOCALAPPDATA%`, macOS `Application Support`, and Linux XDG specifications.
- **Single-Instance IPC**: Native local socket server forwards double-clicked and command-line PDF arguments to running application.
- **Default Viewer**: Operating-system file associations and default application querying.
