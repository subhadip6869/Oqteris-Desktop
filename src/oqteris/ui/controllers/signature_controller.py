"""Controller managing digital signature inspection, verification, and signing in QML."""

from __future__ import annotations

import logging
import platform
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse

from asn1crypto import pem, x509
from PySide6.QtCore import QObject, Property, Signal, Slot

from oqteris.pdf.document.manager import get_document_manager
from oqteris.pdf.signatures.models import SignatureInfo, SignatureTrustStatus
from oqteris.pdf.signatures.service import SignatureService
from oqteris.repositories.bookmarks_repo import CertificatesRepository
from oqteris.ui.controllers.pdf_controller import PDFController

logger = logging.getLogger(__name__)


def _clean_path(path_or_url: str) -> str:
    """Strip file:// protocol and normalize path across Windows and POSIX."""
    if path_or_url.startswith("file:"):
        parsed = urlparse(path_or_url)
        path = unquote(parsed.path)
        if platform.system() == "Windows" and path.startswith("/") and len(path) > 2 and path[2] == ":":
            path = path[1:]
        return path
    return path_or_url


class SignatureController(QObject):
    """Exposes digital signature validation results, trust store management, and signing actions to QML."""

    signaturesChanged = Signal()
    certificatesChanged = Signal()
    signingStatusChanged = Signal(str, bool)  # message, is_success
    statusMessageRequested = Signal(str, str)  # title, message

    def __init__(self, pdf_controller: PDFController, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._pdf_controller = pdf_controller
        self._doc_manager = get_document_manager()
        self._cert_repo = CertificatesRepository()
        self._sig_service = SignatureService(cert_repo=self._cert_repo)

        self._cached_signatures: list[SignatureInfo] = []
        self._signatures_revision: int = 0

        # Automatically inspect signatures when documents are opened or changed
        self._pdf_controller.documentChanged.connect(self._on_document_changed)

    def _on_document_changed(self) -> None:
        """Triggered automatically when a document is opened, switched, or closed."""
        self.inspectSignatures()

    # --- QML Properties ---

    @Property(int, notify=signaturesChanged)
    def signaturesRevision(self) -> int:
        return self._signatures_revision

    @Property("QVariantList", notify=signaturesChanged)
    def documentSignatures(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self._cached_signatures]

    @Property(int, notify=signaturesChanged)
    def signatureCount(self) -> int:
        return len(self._cached_signatures)

    @Property(bool, notify=signaturesChanged)
    def hasSignatures(self) -> bool:
        return len(self._cached_signatures) > 0

    @Property(bool, notify=signaturesChanged)
    def allValidAndTrusted(self) -> bool:
        if not self._cached_signatures:
            return False
        return all(
            s.trust_status == SignatureTrustStatus.TRUSTED
            and s.is_intact
            and s.is_cryptographically_valid
            and not s.doc_modified_since_signing
            for s in self._cached_signatures
        )

    @Property(str, notify=signaturesChanged)
    def statusSummary(self) -> str:
        if not self._cached_signatures:
            return ""

        count = len(self._cached_signatures)
        all_trusted = all(s.trust_status == SignatureTrustStatus.TRUSTED for s in self._cached_signatures)
        any_invalid = any(
            s.trust_status == SignatureTrustStatus.INVALID or not s.is_cryptographically_valid or s.doc_modified_since_signing
            for s in self._cached_signatures
        )
        any_expired = any(s.trust_status == SignatureTrustStatus.EXPIRED for s in self._cached_signatures)

        if any_invalid:
            return "At least one signature has problems: Signature is invalid or document was modified after signing."
        if any_expired:
            return "At least one signature has problems: Certificate has expired."
        if all_trusted:
            if count == 1:
                return "Signed and all signatures are valid."
            return f"Signed and all {count} signatures are valid."

        return "At least one signature has problems: Signature Not Verified (Signer's certificate is not trusted)."

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

    # --- Actions & Slots ---

    @Slot()
    def inspectSignatures(self) -> None:
        """Inspect and cryptographically validate all digital signatures in the active document."""
        doc = self._doc_manager.active_document
        if not doc or not doc.file_path or not doc.is_open:
            self._cached_signatures = []
            self._signatures_revision += 1
            self.signaturesChanged.emit()
            return

        try:
            self._cached_signatures = self._sig_service.inspect_and_validate_signatures(doc.file_path)
        except Exception as e:
            logger.error("Error inspecting signatures: %s", e)
            self._cached_signatures = []

        self._signatures_revision += 1
        self.signaturesChanged.emit()

    @Slot(int, result=bool)
    def trustSignatureCertificate(self, sig_index: int) -> bool:
        """Add the signing certificate of the specified signature into the local trust store as trusted."""
        if not (0 <= sig_index < len(self._cached_signatures)):
            return False

        sig = self._cached_signatures[sig_index]
        if not sig.certificate or not sig.certificate.raw_pem:
            logger.warning("No certificate data to trust for signature %d", sig_index)
            return False

        cert = sig.certificate
        try:
            vf = datetime.fromisoformat(cert.valid_from) if cert.valid_from else datetime.now(timezone.utc)
        except Exception:
            vf = datetime.now(timezone.utc)

        try:
            vt = datetime.fromisoformat(cert.valid_to) if cert.valid_to else (datetime.now(timezone.utc) + timedelta(days=365))
        except Exception:
            vt = datetime.now(timezone.utc) + timedelta(days=365)

        try:
            self._cert_repo.add_certificate(
                fingerprint_sha256=cert.fingerprint_sha256,
                common_name=cert.common_name,
                issuer=cert.issuer,
                valid_from=vf,
                valid_to=vt,
                certificate_pem=cert.raw_pem,
                organization=cert.organization,
                is_trusted=True,
                is_root_ca=True,
            )
            logger.info("Added certificate '%s' to trusted roots", cert.common_name)
            self.certificatesChanged.emit()
            self.inspectSignatures()
            self._pdf_controller.invalidateRender()
            self.statusMessageRequested.emit("Certificate Trusted", f"Added '{cert.common_name}' to trusted certificates. Signature validated successfully.")
            return True
        except Exception as e:
            logger.error("Failed trusting certificate: %s", e)
            return False

    @Slot(int, result=bool)
    def untrustSignatureCertificate(self, sig_index: int) -> bool:
        """Remove trust from the signing certificate of the specified signature."""
        if not (0 <= sig_index < len(self._cached_signatures)):
            return False

        sig = self._cached_signatures[sig_index]
        if not sig.certificate:
            return False

        db_cert = self._cert_repo.find_by_fingerprint(sig.certificate.fingerprint_sha256)
        if db_cert:
            self._cert_repo.set_trust(db_cert.id, False)
            self.certificatesChanged.emit()
            self.inspectSignatures()
            self._pdf_controller.invalidateRender()
            self.statusMessageRequested.emit("Trust Removed", f"Removed trust for certificate '{sig.certificate.common_name}'.")
            return True
        return False

    @Slot(int, result="QVariantMap")
    def getCertificateDetails(self, sig_index: int) -> dict[str, Any]:
        """Return rich certificate and validation parameters for inspection dialogs."""
        if not (0 <= sig_index < len(self._cached_signatures)):
            return {}

        sig = self._cached_signatures[sig_index]
        result: dict[str, Any] = {
            "fieldName": sig.field_name,
            "signerName": sig.signer_name,
            "signingTime": sig.signing_time,
            "reason": sig.reason,
            "location": sig.location,
            "contactInfo": sig.contact_info,
            "isIntact": sig.is_intact,
            "isValid": sig.is_cryptographically_valid,
            "docModified": sig.doc_modified_since_signing,
            "trustStatus": sig.trust_status.value,
            "validationMessage": sig.validation_message,
            "pageNumber": sig.page_number,
        }

        if sig.certificate:
            cert = sig.certificate
            result.update({
                "commonName": cert.common_name,
                "organization": cert.organization,
                "issuer": cert.issuer,
                "serialNumber": cert.serial_number,
                "fingerprintSha256": cert.fingerprint_sha256,
                "validFrom": cert.valid_from,
                "validTo": cert.valid_to,
                "isSelfSigned": cert.is_self_signed,
                "isExpired": cert.is_expired,
                "isTrusted": cert.is_trusted,
                "rawPem": cert.raw_pem,
            })
        return result

    @Slot(int, result="QVariantList")
    def getSignaturesForPage(self, page_index: int) -> list[dict[str, Any]]:
        """Return signatures placed on the specified zero-indexed page."""
        res: list[dict[str, Any]] = []
        for i, s in enumerate(self._cached_signatures):
            if s.page_number == page_index and s.norm_rect and len(s.norm_rect) == 4:
                d = s.to_dict()
                d["sigIndex"] = i
                res.append(d)
        return res

    @Slot(int, str, result=bool)
    def exportCertificate(self, sig_index: int, target_path: str) -> bool:
        """Export the public X.509 certificate to a file on disk."""
        if not (0 <= sig_index < len(self._cached_signatures)):
            return False

        sig = self._cached_signatures[sig_index]
        if not sig.certificate or not sig.certificate.raw_pem:
            return False

        clean_p = Path(_clean_path(target_path))
        try:
            clean_p.parent.mkdir(parents=True, exist_ok=True)
            clean_p.write_text(sig.certificate.raw_pem, encoding="utf-8")
            self.statusMessageRequested.emit("Certificate Exported", f"Saved certificate to {clean_p.name}")
            return True
        except Exception as e:
            logger.error("Failed exporting certificate: %s", e)
            return False

    @Slot(str, result=bool)
    def importCertificateFile(self, file_path: str) -> bool:
        """Import an external X.509 certificate file (.cer, .crt, .pem) into trusted certificates."""
        p = Path(_clean_path(file_path))
        if not p.is_file():
            return False

        try:
            raw_bytes = p.read_bytes()
            if pem.detect(raw_bytes):
                _, _, der_bytes = pem.unarmor(raw_bytes)
                pem_str = raw_bytes.decode("utf-8", errors="replace")
            else:
                der_bytes = raw_bytes
                pem_str = pem.armor("CERTIFICATE", der_bytes).decode("utf-8")

            cert = x509.Certificate.load(der_bytes)
            native_subj = cert.subject.native if hasattr(cert.subject, "native") else {}
            native_iss = cert.issuer.native if hasattr(cert.issuer, "native") else {}

            common_name = native_subj.get("common_name", cert.subject.human_friendly)
            issuer = native_iss.get("common_name", cert.issuer.human_friendly)
            org = native_subj.get("organization_name") or native_subj.get("organization") or ""
            fp = cert.sha256_fingerprint.replace(" ", "").lower()

            self._cert_repo.add_certificate(
                fingerprint_sha256=fp,
                common_name=common_name,
                issuer=issuer,
                valid_from=cert.not_valid_before,
                valid_to=cert.not_valid_after,
                certificate_pem=pem_str,
                organization=org,
                is_trusted=True,
                is_root_ca=True,
            )
            self.certificatesChanged.emit()
            self.inspectSignatures()
            self.statusMessageRequested.emit("Certificate Imported", f"Imported '{common_name}' into trusted certificates.")
            return True
        except Exception as e:
            logger.error("Failed importing certificate from %s: %s", p, e)
            return False

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

        out_clean = _clean_path(output_path)
        p12_clean = _clean_path(pkcs12_path)

        box = (50.0, 50.0, 250.0, 120.0)
        if len(rect) >= 4:
            box = (float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]))

        try:
            success = self._sig_service.sign_pdf(
                input_path=doc.file_path,
                output_path=out_clean,
                pkcs12_path=p12_clean,
                passphrase=passphrase,
                reason=reason,
                location=location,
                page_index=page_index,
                box=box,
            )
            if success:
                self.signingStatusChanged.emit(f"Document signed successfully and saved to {out_clean}", True)
                self._pdf_controller.openDocument(out_clean)
                return True
        except Exception as e:
            logger.error("Digital signing failed: %s", e)
            self.signingStatusChanged.emit(f"Signing failed: {e}", False)

        return False

    @Slot(int, bool)
    def setCertificateTrust(self, cert_id: int, is_trusted: bool) -> None:
        self._cert_repo.set_trust(cert_id, is_trusted)
        self.certificatesChanged.emit()
        self.inspectSignatures()

    @Slot(int)
    def removeCertificate(self, cert_id: int) -> None:
        self._cert_repo.remove(cert_id)
        self.certificatesChanged.emit()
        self.inspectSignatures()
