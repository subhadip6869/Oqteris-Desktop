"""Digital signature inspection, cryptographic validation, and signing via pyHanko."""

from __future__ import annotations

import hashlib
import io
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from asn1crypto import x509
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign import fields, signers, validation
from pyhanko.sign.fields import SigFieldSpec
from pyhanko.sign.signers import PdfSignatureMetadata, SimpleSigner, sign_pdf
from pyhanko_certvalidator import ValidationContext

from oqteris.core.exceptions import CertificateError, SignatureError
from oqteris.pdf.signatures.models import (
    CertificateDetails,
    SignatureInfo,
    SignatureTrustStatus,
)
from oqteris.repositories.bookmarks_repo import CertificatesRepository

logger = logging.getLogger(__name__)


class SignatureService:
    """Manages digital signature validation, trust evaluation, and PKCS#12 signing."""

    def __init__(self, cert_repo: Optional[CertificatesRepository] = None) -> None:
        self.cert_repo = cert_repo or CertificatesRepository()

    def get_trusted_roots(self) -> list[x509.Certificate]:
        """Load trusted CA certificates from the SQLite repository."""
        trusted_certs: list[x509.Certificate] = []
        try:
            db_records = self.cert_repo.get_all()
            for r in db_records:
                if r.is_trusted and r.certificate_pem:
                    try:
                        cert = x509.Certificate.load(r.certificate_pem.encode("utf-8"))
                        trusted_certs.append(cert)
                    except Exception as e:
                        logger.warning("Could not parse certificate %s: %s", r.common_name, e)
        except Exception as e:
            logger.error("Failed to load trusted roots: %s", e)
        return trusted_certs

    def inspect_and_validate_signatures(
        self,
        pdf_path: str | Path,
        check_revocation_online: bool = False,
    ) -> list[SignatureInfo]:
        """Inspect all embedded digital signatures in a PDF and validate their cryptographic integrity and trust."""
        path = Path(pdf_path).resolve()
        if not path.exists():
            return []

        results: list[SignatureInfo] = []

        try:
            with open(path, "rb") as f:
                reader = PdfFileReader(f, strict=False)
                embedded_sigs = reader.embedded_signatures

                if not embedded_sigs:
                    return []

                trusted_roots = self.get_trusted_roots()
                val_context = ValidationContext(
                    trust_roots=trusted_roots if trusted_roots else None,
                    allow_fetching=check_revocation_online,
                )

                for embedded_sig in embedded_sigs:
                    field_name = embedded_sig.field_name or "Signature"
                    sig_info = self._validate_single_signature(embedded_sig, val_context)
                    sig_info.field_name = field_name
                    results.append(sig_info)

        except Exception as e:
            logger.error("Failed inspecting signatures on %s: %s", path, e)

        return results

    def _validate_single_signature(
        self,
        embedded_sig: Any,
        val_context: ValidationContext,
    ) -> SignatureInfo:
        """Validate one embedded signature."""
        signer_name = ""
        signing_time = ""
        reason = ""
        location = ""
        contact_info = ""
        subfilter = ""
        is_intact = False
        is_crypto_valid = False
        doc_modified = False
        trust_status = SignatureTrustStatus.UNKNOWN
        cert_details: Optional[CertificateDetails] = None
        validation_msg = ""

        try:
            sig_obj = embedded_sig.sig_object
            subfilter = str(sig_obj.get("/SubFilter", ""))
            reason = str(sig_obj.get("/Reason", ""))
            location = str(sig_obj.get("/Location", ""))
            contact_info = str(sig_obj.get("/ContactInfo", ""))

            # Cryptographic validation
            status = validation.validate_pdf_signature(embedded_sig, val_context)

            is_intact = status.intact
            is_crypto_valid = status.valid
            doc_modified = not bool(status.docmdp_ok)

            # Certificate extraction
            signing_cert = status.signing_cert
            if signing_cert:
                native_subj = signing_cert.subject.native if hasattr(signing_cert.subject, "native") else {}
                native_iss = signing_cert.issuer.native if hasattr(signing_cert.issuer, "native") else {}
                subject_name = native_subj.get("common_name", signing_cert.subject.human_friendly)
                issuer_name = native_iss.get("common_name", signing_cert.issuer.human_friendly)
                signer_name = subject_name
                is_self_signed = signing_cert.self_signed == "yes"

                sha256_fp = signing_cert.sha256_fingerprint.replace(" ", "").lower()
                not_before = str(signing_cert.not_valid_before)
                not_after = str(signing_cert.not_valid_after)

                now = datetime.now(timezone.utc)
                is_expired = now > signing_cert.not_valid_after.replace(tzinfo=timezone.utc)

                # Trust status logic
                is_trusted = False
                if is_crypto_valid:
                    if status.trusted:
                        trust_status = SignatureTrustStatus.TRUSTED
                        is_trusted = True
                        validation_msg = "Signature is valid and certificate chain is trusted."
                    else:
                        trust_status = SignatureTrustStatus.UNTRUSTED
                        validation_msg = "Signature is cryptographically intact, but the certificate is not trusted."
                else:
                    trust_status = SignatureTrustStatus.INVALID
                    validation_msg = "Signature cryptographic integrity verification failed."

                if is_expired:
                    trust_status = SignatureTrustStatus.EXPIRED
                    validation_msg += " (Certificate has expired)"

                if doc_modified:
                    validation_msg += " (Document has been modified after signing)"

                cert_details = CertificateDetails(
                    common_name=subject_name,
                    issuer=issuer_name,
                    serial_number=hex(signing_cert.serial_number),
                    fingerprint_sha256=sha256_fp,
                    valid_from=not_before,
                    valid_to=not_after,
                    is_self_signed=is_self_signed,
                    is_expired=is_expired,
                    is_trusted=is_trusted,
                )
            else:
                validation_msg = "No embedded signing certificate found."

        except Exception as e:
            logger.error("Error validating embedded signature: %s", e)
            validation_msg = f"Validation error: {e}"
            trust_status = SignatureTrustStatus.INVALID

        return SignatureInfo(
            field_name="",
            signer_name=signer_name,
            signing_time=signing_time,
            reason=reason,
            location=location,
            contact_info=contact_info,
            subfilter=subfilter,
            is_intact=is_intact,
            is_cryptographically_valid=is_crypto_valid,
            doc_modified_since_signing=doc_modified,
            trust_status=trust_status,
            certificate=cert_details,
            validation_message=validation_msg,
        )

    def sign_pdf(
        self,
        input_path: str | Path,
        output_path: str | Path,
        pkcs12_path: str | Path,
        passphrase: str,
        field_name: str = "Signature1",
        reason: str = "Document approval",
        location: str = "",
        page_index: int = 0,
        box: tuple[float, float, float, float] = (50, 50, 250, 120),
    ) -> bool:
        """Sign a PDF document with PKCS#12 (.p12/.pfx) digital certificate using incremental update."""
        in_p = Path(input_path).resolve()
        out_p = Path(output_path).resolve()
        p12_p = Path(pkcs12_path).resolve()

        if not in_p.exists():
            raise SignatureError(f"Input PDF does not exist: {in_p}")
        if not p12_p.exists():
            raise SignatureError(f"PKCS#12 certificate file does not exist: {p12_p}")

        try:
            signer = SimpleSigner.load_pkcs12(
                pfx_file=str(p12_p),
                passphrase=passphrase.encode("utf-8") if passphrase else None,
            )
        except Exception as e:
            logger.error("Failed to load PKCS#12 credentials: %s", e)
            raise CertificateError(f"Failed to load certificate: {e}")

        meta = PdfSignatureMetadata(
            field_name=field_name,
            reason=reason,
            location=location,
        )

        sig_field_spec = SigFieldSpec(
            sig_field_name=field_name,
            on_page=page_index,
            box=box,
        )

        try:
            with open(in_p, "rb") as inf, open(out_p, "wb") as outf:
                writer = IncrementalPdfFileWriter(inf)
                sign_pdf(
                    pdf_out=writer,
                    signature_meta=meta,
                    signer=signer,
                    new_field_spec=sig_field_spec,
                    output=outf,
                )
            logger.info("PDF signed successfully: %s", out_p)
            return True
        except Exception as e:
            logger.error("Failed signing PDF: %s", e)
            if out_p.exists():
                out_p.unlink(missing_ok=True)
            raise SignatureError(f"Signing failed: {e}")
