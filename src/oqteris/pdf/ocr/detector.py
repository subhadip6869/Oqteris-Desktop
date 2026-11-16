"""Scanned PDF detection and OpenCV image preprocessing for OCR."""

from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np

from oqteris.pdf.document.document import PDFDocument

logger = logging.getLogger(__name__)


class ScannedPDFDetector:
    """Detects whether a PDF or individual page is primarily a scanned image."""

    @staticmethod
    def is_page_scanned(document: PDFDocument, page_index: int, min_text_chars: int = 50) -> bool:
        """Determines if a page lacks selectable text and contains large raster images."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            text = page.get_text("text").strip()
            if len(text) >= min_text_chars:
                return False

            # Check if there are embedded images covering a significant area
            images = page.get_images()
            return len(images) > 0
        except Exception as e:
            logger.error("Error inspecting page %d for scan status: %s", page_index, e)
            return False

    @staticmethod
    def is_document_scanned(document: PDFDocument, sample_pages: int = 5) -> bool:
        """Heuristically checks if the document is scanned by sampling pages."""
        if not document.is_open or document.page_count == 0:
            return False

        pages_to_check = min(sample_pages, document.page_count)
        scanned_count = sum(
            1 for p in range(pages_to_check)
            if ScannedPDFDetector.is_page_scanned(document, p)
        )
        return (scanned_count / pages_to_check) >= 0.6


class ImagePreprocessor:
    """OpenCV image preprocessing utilities for OCR accuracy enhancement."""

    @staticmethod
    def deskew(image: np.ndarray) -> np.ndarray:
        """Detect and correct rotation skew using OpenCV minAreaRect."""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Invert and threshold
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            coords = np.column_stack(np.where(thresh > 0))
            if coords.shape[0] < 50:
                return image

            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            if abs(angle) < 0.5:
                return image

            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
            )
            return rotated
        except Exception as e:
            logger.warning("Deskew failed, returning original image: %s", e)
            return image

    @staticmethod
    def binarize(image: np.ndarray) -> np.ndarray:
        """Convert image to clean high-contrast black-and-white for OCR."""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Denoise and adaptive threshold
            denoised = cv2.medianBlur(gray, 3)
            return cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        except Exception as e:
            logger.warning("Binarization failed: %s", e)
            return image
