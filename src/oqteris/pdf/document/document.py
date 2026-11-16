"""Thread-safe PDF document wrapper using PyMuPDF."""

from __future__ import annotations

import logging
import os
import shutil
import threading
from pathlib import Path
from typing import Any, Optional

import pymupdf

from oqteris.core.exceptions import (
    PDFCorruptedError,
    PDFEncryptedError,
    PDFError,
    PDFPermissionError,
)
from oqteris.pdf.document.models import (
    DocumentMetadata,
    ExtractedImageInfo,
    OutlineItem,
    PageGeometry,
    SearchMatch,
)

logger = logging.getLogger(__name__)


class PDFDocument:
    """Encapsulates a single open PDF document and coordinates low-level PyMuPDF operations."""

    def __init__(self, doc_id: str) -> None:
        self.doc_id = doc_id
        self._doc: Optional[pymupdf.Document] = None
        self._file_path: Optional[Path] = None
        self._password: str = ""
        self._lock = threading.RLock()
        self._is_modified: bool = False
        self._is_encrypted: bool = False

    @property
    def is_open(self) -> bool:
        with self._lock:
            return self._doc is not None and not self._doc.is_closed

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @is_modified.setter
    def is_modified(self, val: bool) -> None:
        self._is_modified = val

    @property
    def file_path(self) -> Optional[Path]:
        return self._file_path

    @property
    def page_count(self) -> int:
        with self._lock:
            if not self.is_open or self._doc is None:
                return 0
            return len(self._doc)

    def open(self, file_path: str | Path, password: str = "") -> DocumentMetadata:
        """Open a PDF file from disk, decrypting if a password is provided."""
        path = Path(file_path).resolve()
        if not path.exists():
            raise PDFError(f"File not found: {path}")

        with self._lock:
            try:
                self._doc = pymupdf.open(str(path))
            except Exception as e:
                logger.error("Failed to open PDF %s: %s", path, e)
                raise PDFCorruptedError(f"Could not open PDF file: {e}")

            self._is_encrypted = self._doc.is_encrypted
            if self._doc.is_encrypted:
                if not password:
                    raise PDFEncryptedError("Document is encrypted and requires a password.")
                success = self._doc.authenticate(password)
                if not success:
                    raise PDFEncryptedError("Incorrect password.")
                self._password = password

            self._file_path = path
            self._is_modified = False
            return self.get_metadata()

    def close(self) -> None:
        """Close the open PDF document and release native file handles."""
        with self._lock:
            if self._doc and not self._doc.is_closed:
                try:
                    self._doc.close()
                except Exception as e:
                    logger.warning("Error while closing PDF %s: %s", self._file_path, e)
            self._doc = None
            self._file_path = None
            self._is_modified = False

    def get_metadata(self) -> DocumentMetadata:
        """Extract document metadata and permission flags."""
        with self._lock:
            if not self.is_open or self._doc is None:
                return DocumentMetadata()

            meta = self._doc.metadata or {}
            size = self._file_path.stat().st_size if self._file_path and self._file_path.exists() else 0

            # Permissions
            permissions = self._doc.permissions
            can_print = bool(permissions & pymupdf.PDF_PERM_PRINT)
            can_modify = bool(permissions & pymupdf.PDF_PERM_MODIFY)
            can_copy = bool(permissions & pymupdf.PDF_PERM_COPY)
            can_annotate = bool(permissions & pymupdf.PDF_PERM_ANNOTATE)

            # Check if digitally signed
            is_signed = False
            try:
                for page in self._doc:
                    for annot in page.annots():
                        if annot.type[0] == pymupdf.PDF_ANNOT_WIDGET:
                            # Signature widget inspection
                            pass
                # Check for sig fields in PDF catalog
                if self._doc.is_pdf:
                    for i in range(len(self._doc)):
                        page = self._doc[i]
                        for field in page.widgets():
                            if field.field_type == pymupdf.PDF_WIDGET_TYPE_SIGNATURE:
                                is_signed = True
                                break
            except Exception:
                pass

            return DocumentMetadata(
                title=meta.get("title", ""),
                author=meta.get("author", ""),
                subject=meta.get("subject", ""),
                keywords=meta.get("keywords", ""),
                creator=meta.get("creator", ""),
                producer=meta.get("producer", ""),
                creation_date=meta.get("creationDate", ""),
                modification_date=meta.get("modDate", ""),
                format_version=f"PDF-{self._doc.pdf_version()}" if hasattr(self._doc, "pdf_version") else "PDF-1.7",
                page_count=len(self._doc),
                is_encrypted=self._is_encrypted,
                is_signed=is_signed,
                can_print=can_print,
                can_modify=can_modify,
                can_copy=can_copy,
                can_annotate=can_annotate,
                file_size_bytes=size,
                file_path=str(self._file_path) if self._file_path else "",
            )

    def get_page_geometry(self, page_index: int) -> PageGeometry:
        """Return the dimensions and rotation of the specified page."""
        with self._lock:
            if not self.is_open or self._doc is None or not (0 <= page_index < len(self._doc)):
                return PageGeometry(page_index, 612.0, 792.0, 0)

            page = self._doc[page_index]
            rect = page.rect
            return PageGeometry(
                page_index=page_index,
                width=float(rect.width),
                height=float(rect.height),
                rotation=int(page.rotation),
            )

    def get_table_of_contents(self) -> list[OutlineItem]:
        """Parse table of contents outline tree."""
        with self._lock:
            if not self.is_open or self._doc is None:
                return []

            raw_toc = self._doc.get_toc(simple=False)
            if not raw_toc:
                return []

            root_items: list[OutlineItem] = []
            stack: list[tuple[int, OutlineItem]] = []

            for item in raw_toc:
                level, title, page = item[0], item[1], max(0, item[2] - 1)
                outline_node = OutlineItem(title=title, page_index=page, level=level)

                while stack and stack[-1][0] >= level:
                    stack.pop()

                if not stack:
                    root_items.append(outline_node)
                else:
                    stack[-1][1].children.append(outline_node)

                stack.append((level, outline_node))

            return root_items

    def search_text(self, query: str, case_sensitive: bool = False) -> list[SearchMatch]:
        """Search across all pages for text occurrences."""
        results: list[SearchMatch] = []
        if not query.strip():
            return results

        with self._lock:
            if not self.is_open or self._doc is None:
                return results

            flags = pymupdf.TEXT_DEHYPHENATE
            if not case_sensitive:
                flags |= 0  # Default case folding in pymupdf search_for

            for page_idx in range(len(self._doc)):
                page = self._doc[page_idx]
                hit_rects = page.search_for(query, flags=flags)
                if hit_rects:
                    rect_list = [[float(r.x0), float(r.y0), float(r.x1), float(r.y1)] for r in hit_rects]
                    results.append(SearchMatch(page_index=page_idx, rects=rect_list, snippet=query))

        return results

    def extract_text_page(self, page_index: int) -> str:
        """Extract plain text from a page."""
        with self._lock:
            if not self.is_open or self._doc is None or not (0 <= page_index < len(self._doc)):
                return ""
            page = self._doc[page_index]
            return page.get_text("text")

    def extract_words_page(self, page_index: int) -> list[dict[str, Any]]:
        """Extract word bounding boxes for text selection and search highlighting."""
        with self._lock:
            if not self.is_open or self._doc is None or not (0 <= page_index < len(self._doc)):
                return []
            page = self._doc[page_index]
            words = page.get_text("words")  # returns list of (x0, y0, x1, y1, word, block_no, line_no, word_no)
            return [
                {
                    "x0": float(w[0]),
                    "y0": float(w[1]),
                    "x1": float(w[2]),
                    "y1": float(w[3]),
                    "text": str(w[4]),
                }
                for w in words
            ]

    def extract_images_page(self, page_index: int) -> list[ExtractedImageInfo]:
        """Return metadata for all embedded images in a page."""
        images_info: list[ExtractedImageInfo] = []
        with self._lock:
            if not self.is_open or self._doc is None or not (0 <= page_index < len(self._doc)):
                return images_info
            page = self._doc[page_index]
            raw_images = page.get_images(full=True)
            for idx, img in enumerate(raw_images):
                xref = img[0]
                base_img = self._doc.extract_image(xref)
                if base_img:
                    images_info.append(
                        ExtractedImageInfo(
                            image_index=idx,
                            page_index=page_index,
                            width=base_img["width"],
                            height=base_img["height"],
                            format=base_img["ext"],
                            size_bytes=len(base_img["image"]),
                            xref=xref,
                        )
                    )
        return images_info

    def extract_image_bytes(self, xref: int) -> tuple[bytes, str]:
        """Extract raw image bytes and file extension by xref."""
        with self._lock:
            if not self.is_open or self._doc is None:
                return b"", ""
            img_data = self._doc.extract_image(xref)
            if img_data:
                return img_data["image"], img_data["ext"]
            return b"", ""

    def rotate_page(self, page_index: int, degrees: int = 90) -> int:
        """Rotate page by degrees clockwise (relative)."""
        with self._lock:
            if not self.is_open or self._doc is None or not (0 <= page_index < len(self._doc)):
                return 0
            page = self._doc[page_index]
            new_rot = (page.rotation + degrees) % 360
            page.set_rotation(new_rot)
            self._is_modified = True
            return new_rot

    def delete_page(self, page_index: int) -> int:
        """Delete a single page from the document."""
        with self._lock:
            if not self.is_open or self._doc is None or not (0 <= page_index < len(self._doc)):
                raise PDFError(f"Invalid page index {page_index}")
            if len(self._doc) <= 1:
                raise PDFError("Cannot delete the only page in the document.")
            self._doc.delete_page(page_index)
            self._is_modified = True
            return len(self._doc)

    def move_page(self, from_index: int, to_index: int) -> None:
        """Move a page from from_index to to_index."""
        with self._lock:
            if not self.is_open or self._doc is None:
                return
            n = len(self._doc)
            if not (0 <= from_index < n and 0 <= to_index < n):
                return
            self._doc.move_page(from_index, to_index)
            self._is_modified = True

    def save(self, target_path: str | Path | None = None, incremental: bool = False, deflate: bool = True) -> Path:
        """Save document with transactional write protection."""
        with self._lock:
            if not self.is_open or self._doc is None:
                raise PDFError("No document is open to save.")

            save_path = Path(target_path).resolve() if target_path else self._file_path
            if not save_path:
                raise PDFError("Save path not specified.")

            # If saving in-place and incremental is possible without corruption
            if target_path is None or str(target_path) == str(self._file_path):
                if incremental and self._doc.can_save_incrementally():
                    try:
                        self._doc.save(str(save_path), incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
                        self._is_modified = False
                        return save_path
                    except Exception as e:
                        logger.warning("Incremental save failed, falling back to atomic full save: %s", e)

            # Transactional full save via temporary file
            temp_path = save_path.parent / f".{save_path.name}.tmp"
            try:
                self._doc.save(
                    str(temp_path),
                    deflate=deflate,
                    garbage=3,
                    clean=True,
                    encryption=pymupdf.PDF_ENCRYPT_KEEP,
                )

                # If saving to same path, we need to close or reopen to safely swap file on Windows
                is_same_file = (self._file_path and save_path.resolve() == self._file_path.resolve())

                if is_same_file:
                    self._doc.close()
                    temp_path.replace(save_path)
                    self._doc = pymupdf.open(str(save_path))
                    if self._password:
                        self._doc.authenticate(self._password)
                else:
                    temp_path.replace(save_path)

                self._file_path = save_path
                self._is_modified = False
                logger.info("PDF saved successfully to %s", save_path)
                return save_path
            except Exception as e:
                if temp_path.exists():
                    temp_path.unlink(missing_ok=True)
                logger.error("Failed to save PDF to %s: %s", save_path, e)
                raise PDFError(f"Failed to save document: {e}")

    @property
    def raw_doc(self) -> Optional[pymupdf.Document]:
        """Provides access to raw PyMuPDF document for specialized rendering or editing."""
        return self._doc
