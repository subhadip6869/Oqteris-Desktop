# Oqteris Project Roadmap

## Version 1.0.0 (Current Release)
- [x] Modern ribbon desktop interface in Qt Quick / QML.
- [x] PyMuPDF rendering engine with bounded LRU memory tile caching.
- [x] Continuous and single-page viewing modes with fit-to-width and fit-page presets.
- [x] Full-text search with bounding box highlights and match navigation.
- [x] Text insertion and direct text replacement with background redaction.
- [x] Markup tools: highlights, underlines, strikethrough, sticky notes, ink drawing, shapes, and stamps.
- [x] Page organization: page deletion, extraction, rotation, PDF splitting and merging.
- [x] pyHanko digital signature validation, certificate inspection, and PKCS#12 signing.
- [x] AcroForm inspection, field value updating, and field resetting.
- [x] Tesseract OCR and OpenCV deskew/binarization for searchable PDF creation.
- [x] pikepdf stream compression and image optimization.
- [x] SQLite relational storage for recent files, bookmarks, and trust stores.
- [x] Cross-platform native storage layouts (Windows, Linux, macOS).
- [x] Single-instance local IPC coordinator.
- [x] Automated GitHub Actions CI and multi-platform release workflows.

## Version 1.1.0 (Upcoming)
- [ ] Hardware-accelerated PDF rendering via Vulkan / Metal backends.
- [ ] Advanced redaction workflows (pattern-based automated redaction for SSN, emails, credit cards).
- [ ] PDF/A compliance validation and conversion profiles (PDF/A-1b, PDF/A-2b).
- [ ] Interactive measurement tools (perimeter, area, calibrated scale ruler).
- [ ] Online OCSP / CRL automatic certificate revocation query daemon.
- [ ] AcroForm builder (creating new interactive text boxes, checkboxes, and signature fields).
