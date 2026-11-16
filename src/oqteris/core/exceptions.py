"""Central exception hierarchy for Oqteris."""

from __future__ import annotations


class OqterisError(Exception):
    """Base exception for all Oqteris application errors."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or ""


class PDFError(OqterisError):
    """Base class for PDF operations errors."""


class PDFEncryptedError(PDFError):
    """Raised when a PDF requires a password to open or decrypt."""

    def __init__(self, message: str = "This document is password protected.") -> None:
        super().__init__(message)


class PDFCorruptedError(PDFError):
    """Raised when a PDF file is malformed or damaged."""


class PDFPermissionError(PDFError):
    """Raised when an operation is prohibited by PDF permission flags."""


class SignatureError(OqterisError):
    """Base class for digital signature errors."""


class SignatureInvalidatedError(SignatureError):
    """Raised when an edit would invalidate existing cryptographic signatures."""


class CertificateError(OqterisError):
    """Raised when certificate validation, chaining, or parsing fails."""


class OCRError(OqterisError):
    """Raised when OCR processing fails or dependencies are missing."""


class StorageError(OqterisError):
    """Raised when filesystem or database persistence encounters an error."""


class OptimizationError(OqterisError):
    """Raised when PDF compression or optimization fails."""
