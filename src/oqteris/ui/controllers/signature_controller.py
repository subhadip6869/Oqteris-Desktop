"""Controller managing digital signature inspection, verification, and signing in QML."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QObject, Property, Signal, Slot

from oqteris.pdf.document.manager import get_document_manager
from oqteris.pdf.signatures.models import SignatureInfo
from oqteris.pdf.signatures.service import SignatureService
from oqteris.repositories.bookmarks_repo import CertificatesRepository
from oqteris.ui.controllers.pdf_controller import PDFController

logger = logging.getLogger(__name__)


class SignatureController(QObject):
    """Exposes digital signature validation results and signing actions to QML."""

    signaturesChanged = Signal()
    certificatesChanged = Signal()
    signingStatusChanged = Signal(str, bool)  # message, is_success

    def __init__(self, pdf_controller: PDFController, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._pdf_controller = pdf_controller
        self._doc_manager = get_document_manager()
        self._cert_repo = CertificatesRepository()
        self._sig_service = SignatureService(cert_repo=self._cert_repo)

        self._cached_signatures: list[SignatureInfo] = []

    @Property("QVariantList", notify=signaturesChanged)
    def documentSignatures(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self._cached_signatures]

    @Property(int, notify=signaturesChanged)
    def signatureCount(self) -> int:
        return len(self._cached_signatures)

    @Property("QVariantList", notify=certificatesChanged)
    def trustedCertificates(self) -> list[dict[str, Any]]:
        certs = self._cert_repo.get_all()
        return [
            {
                "id": c.id,
                "commonName": c.common_name,
                "organization": c.organization or "",
                "issuer": c.issuer,
                "fingerprint": c.fingerprint_sha256,
                "validFrom": c.valid_from.strftime("%Y-%m-%d"),
                "validTo": c.valid_to.strftime("%Y-%m-%d"),
                "isTrusted": c.is_trusted,
                "isRootCA": c.is_root_ca,
            }
            for c in certs
        ]

    @Slot()
    def inspectSignatures(self) -> None:
        doc = self._doc_manager.active_document
        if not doc or not doc.file_path:
            self._cached_signatures = []
            self.signaturesChanged.emit()
            return

        self._cached_signatures = self._sig_service.inspect_and_validate_signatures(doc.file_path)
        self.signaturesChanged.emit()

    @Slot(str, str, str, str, str, int, "QVariantList", result=bool)
    def signDocument(
        self,
        output_path: str,
        pkcs12_path: str,
        passphrase: str,
        reason: str,
        location: str,
        page_index: int,
        rect: list[Any],
    ) -> bool:
        doc = self._doc_manager.active_document
        if not doc or not doc.file_path:
            self.signingStatusChanged.emit("No active document open to sign.", False)
            return False

        box = (50.0, 50.0, 250.0, 120.0)
        if len(rect) >= 4:
            box = (float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]))

        try:
            success = self._sig_service.sign_pdf(
                input_path=doc.file_path,
                output_path=output_path,
                pkcs12_path=pkcs12_path,
                passphrase=passphrase,
                reason=reason,
                location=location,
                page_index=page_index,
                box=box,
            )
            if success:
                self.signingStatusChanged.emit(f"Document signed successfully and saved to {output_path}", True)
                # Open signed PDF
                self._pdf_controller.openDocument(output_path)
                return True
        except Exception as e:
            logger.error("Digital signing failed: %s", e)
            self.signingStatusChanged.emit(f"Signing failed: {e}", False)

        return False

    @Slot(int, bool)
    def setCertificateTrust(self, cert_id: int, is_trusted: bool) -> None:
        self._cert_repo.set_trust(cert_id, is_trusted)
        self.certificatesChanged.emit()
        self.inspectSignatures()  # Re-evaluate signatures against updated trust store

    @Slot(int)
    def removeCertificate(self, cert_id: int) -> None:
        self._cert_repo.remove(cert_id)
        self.certificatesChanged.emit()
        self.inspectSignatures()
