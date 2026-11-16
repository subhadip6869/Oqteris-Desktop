"""OpenCV image preprocessing utilities for OCR enhancement."""

from __future__ import annotations

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Image enhancement algorithms: deskewing and adaptive binarization."""

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
        """Convert image to high-contrast binary format."""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            denoised = cv2.medianBlur(gray, 3)
            return cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        except Exception as e:
            logger.warning("Binarization failed: %s", e)
            return image
