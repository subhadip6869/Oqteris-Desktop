"""Document session manager coordinating multiple open PDF documents."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Optional

from oqteris.core.exceptions import PDFError
from oqteris.pdf.document.document import PDFDocument
from oqteris.pdf.document.models import DocumentMetadata

logger = logging.getLogger(__name__)


class DocumentManager:
    """Coordinates lifecycle of multiple open PDF documents in the workspace."""

    def __init__(self) -> None:
        self._documents: dict[str, PDFDocument] = {}
        self._active_doc_id: Optional[str] = None

    @property
    def active_doc_id(self) -> Optional[str]:
        return self._active_doc_id

    @active_doc_id.setter
    def active_doc_id(self, doc_id: Optional[str]) -> None:
        if doc_id is None or doc_id in self._documents:
            self._active_doc_id = doc_id

    @property
    def active_document(self) -> Optional[PDFDocument]:
        if self._active_doc_id:
            return self._documents.get(self._active_doc_id)
        return None

    def get_document(self, doc_id: str) -> Optional[PDFDocument]:
        return self._documents.get(doc_id)

    def open_document(self, file_path: str | Path, password: str = "") -> tuple[PDFDocument, DocumentMetadata]:
        """Open a PDF and register it with a unique session ID."""
        path = Path(file_path).resolve()

        # Check if already open
        for doc_id, doc in self._documents.items():
            if doc.file_path and doc.file_path.resolve() == path:
                self._active_doc_id = doc_id
                return doc, doc.get_metadata()

        doc_id = str(uuid.uuid4())[:8]
        doc = PDFDocument(doc_id=doc_id)
        metadata = doc.open(path, password=password)

        self._documents[doc_id] = doc
        self._active_doc_id = doc_id
        return doc, metadata

    def close_document(self, doc_id: str) -> bool:
        """Close an open document and remove it from the manager."""
        if doc_id in self._documents:
            doc = self._documents.pop(doc_id)
            doc.close()

            if self._active_doc_id == doc_id:
                # Switch active doc to next available or None
                self._active_doc_id = next(iter(self._documents.keys())) if self._documents else None
            return True
        return False

    def close_all(self) -> None:
        """Close all open documents."""
        for doc in list(self._documents.values()):
            doc.close()
        self._documents.clear()
        self._active_doc_id = None

    def list_open_documents(self) -> list[dict[str, Any]]:
        """List open documents summary."""
        items = []
        for doc_id, doc in self._documents.items():
            items.append({
                "docId": doc_id,
                "filePath": str(doc.file_path) if doc.file_path else "",
                "fileName": doc.file_path.name if doc.file_path else "Untitled",
                "pageCount": doc.page_count,
                "isModified": doc.is_modified,
                "isActive": (doc_id == self._active_doc_id),
            })
        return items


# Singleton instance
_doc_manager_instance: DocumentManager | None = None


def get_document_manager() -> DocumentManager:
    global _doc_manager_instance
    if _doc_manager_instance is None:
        _doc_manager_instance = DocumentManager()
    return _doc_manager_instance
