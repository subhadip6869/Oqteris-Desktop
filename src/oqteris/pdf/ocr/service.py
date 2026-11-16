"""OCR service for scanned PDF detection, text recognition, and searchable PDF generation."""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Callable, Optional

import cv2
import numpy as np
import pymupdf
import pytesseract

from oqteris.config.settings import get_settings_manager
from oqteris.core.exceptions import OCRError
from oqteris.pdf.ocr.preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)


class OCRService:
    """Orchestrates Tesseract detection, image preprocessing, and searchable PDF creation."""

    def __init__(self) -> None:
        self._settings = get_settings_manager()
        self.resolve_tesseract_binary()

    def resolve_tesseract_binary(self) -> Optional[Path]:
        """Locate Tesseract executable in settings, PATH, or standard installation directories."""
        custom_path = self._settings.get("ocr_tesseract_path")
        if custom_path and Path(custom_path).is_file():
            pytesseract.pytesseract.tesseract_cmd = str(custom_path)
            return Path(custom_path)

        which_tess = shutil.which("tesseract")
        if which_tess:
            pytesseract.pytesseract.tesseract_cmd = which_tess
            return Path(which_tess)

        # Standard Windows locations
        candidates = [
            Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
            Path("/usr/bin/tesseract"),
            Path("/usr/local/bin/tesseract"),
            Path("/opt/homebrew/bin/tesseract"),
        ]

        for cand in candidates:
            if cand.is_file():
                pytesseract.pytesseract.tesseract_cmd = str(cand)
                return cand

        return None

    def is_tesseract_available(self) -> bool:
        """Check if Tesseract binary is executable."""
        try:
            ver = pytesseract.get_tesseract_version()
            return bool(ver)
        except Exception:
            return False

    def get_available_languages(self) -> list[str]:
        """List installed Tesseract OCR language models (e.g. ['eng', 'ben', 'deu'])."""
        if not self.is_tesseract_available():
            return []
        try:
            return pytesseract.get_languages()
        except Exception as e:
            logger.warning("Could not list tesseract languages: %s", e)
            return ["eng"]

    def ocr_pdf(
        self,
        source_path: str | Path,
        target_path: str | Path,
        languages: list[str] | None = None,
        page_range: list[int] | None = None,
        deskew: bool = True,
        binarize: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> Path:
        """Process a scanned PDF and produce a new searchable PDF document."""
        if not self.is_tesseract_available():
            raise OCRError(
                "Tesseract OCR is not installed or not found. "
                "Please install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki (Windows) "
                "or your system package manager (apt/brew/pacman) and configure its path in Settings."
            )

        src = Path(source_path).resolve()
        dst = Path(target_path).resolve()
        if not src.exists():
            raise OCRError(f"Source PDF file not found: {src}")

        langs_str = "+".join(languages) if languages else "eng"

        try:
            doc = pymupdf.open(str(src))
            total_pages = len(doc)
            pages_to_process = page_range if page_range is not None else list(range(total_pages))
            pages_to_process = [p for p in pages_to_process if 0 <= p < total_pages]

            output_doc = pymupdf.open()

            for step_idx, p_idx in enumerate(pages_to_process):
                if is_cancelled and is_cancelled():
                    output_doc.close()
                    doc.close()
                    raise OCRError("OCR operation was cancelled by user.")

                if progress_callback:
                    progress_callback(step_idx + 1, len(pages_to_process), f"Processing page {p_idx + 1}...")

                page = doc[p_idx]
                # High-res pixmap (300 DPI for optimal OCR recognition)
                pix = page.get_pixmap(dpi=300)
                img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))

                # Optional OpenCV image preprocessing
                processed = img_data
                if deskew:
                    processed = ImagePreprocessor.deskew(processed)
                if binarize:
                    processed = ImagePreprocessor.binarize(processed)

                # Generate single-page searchable PDF with OCR overlay
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                    processed,
                    extension="pdf",
                    lang=langs_str,
                )

                single_page_doc = pymupdf.open("pdf", pdf_bytes)
                output_doc.insert_pdf(single_page_doc)
                single_page_doc.close()

            # Save generated searchable PDF
            dst.parent.mkdir(parents=True, exist_ok=True)
            output_doc.save(str(dst), deflate=True, garbage=3)
            output_doc.close()
            doc.close()

            logger.info("Searchable PDF created successfully at %s", dst)
            return dst
        except OCRError:
            raise
        except Exception as e:
            logger.error("OCR operation failed on %s: %s", src, e)
            if dst.exists():
                dst.unlink(missing_ok=True)
            raise OCRError(f"OCR processing failed: {e}")
