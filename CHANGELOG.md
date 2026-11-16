# Changelog

All notable changes to Oqteris will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-16

### Added
- Complete modern Qt Quick / QML ribbon user interface with Home, View, Edit, Comment, Organize, Convert, Fill & Sign, Protect, and Help tabs.
- High-performance PDF rendering engine powered by PyMuPDF with asynchronous page rasterization and bounded LRU tile/page cache.
- Multi-document tab workspace supporting split-view, continuous scrolling, facing pages, zoom presets, fit-to-page, and rotation.
- Fast full-text document search with in-page highlight rectangles and navigation.
- PDF editing system supporting text addition, font selection, image insertion, links, and object properties.
- Annotation and markup tools: highlight, underline, strikethrough, sticky notes, freehand drawing, geometric shapes, and stamps.
- Page organization tools: page reordering, rotation, page deletion, extraction, splitting, and merging.
- PyHanko-powered digital signature inspection, certificate chain validation, trust store verification, and cryptographic signing.
- AcroForm viewing, interactive field editing, reset, and form flattening.
- OCR integration with Tesseract detection, image preprocessing (deskew, binarization), and searchable PDF generation.
- Document optimization, lossless/lossy compression, and image downsampling via pikepdf.
- SQLite + SQLAlchemy application persistence for recent files, bookmarks, workspace sessions, and settings.
- Platform-native data directory layout adhering to Windows `%LOCALAPPDATA%`, macOS `Application Support`, and Linux XDG specifications.
- Single-instance IPC coordinator supporting command-line PDF arguments, drag-and-drop, and OS file association.
- Packaging configurations for Windows (Inno Setup / NSIS / portable), macOS (.app / DMG), and Linux (.deb, .rpm, Arch Linux .pkg.tar.zst).
- Automated CI and release workflows via GitHub Actions.
