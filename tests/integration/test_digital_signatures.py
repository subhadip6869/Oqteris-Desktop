"""Integration tests for pyHanko digital signing, verification, and certificate trust."""

from pathlib import Path
from oqteris.pdf.signatures.models import SignatureTrustStatus
from oqteris.pdf.signatures.service import SignatureService
from oqteris.repositories.bookmarks_repo import CertificatesRepository


def test_digital_signing_and_validation(sample_pdf_normal: Path, test_p12_certificate: tuple[Path, str], temp_dir: Path, test_db):
    p12_path, passphrase = test_p12_certificate
    signed_pdf_path = temp_dir / "document_signed.pdf"

    cert_repo = CertificatesRepository(db_manager=test_db)
    service = SignatureService(cert_repo=cert_repo)

    # 1. Sign document
    sign_ok = service.sign_pdf(
        input_path=sample_pdf_normal,
        output_path=signed_pdf_path,
        pkcs12_path=p12_path,
        passphrase=passphrase,
        field_name="Sig_Test",
        reason="Approved by OriginSD",
        location="Headquarters",
        page_index=0,
    )
    assert sign_ok is True
    assert signed_pdf_path.exists()

    # 2. Inspect and validate signatures
    sigs = service.inspect_and_validate_signatures(signed_pdf_path)
    assert len(sigs) == 1

    sig = sigs[0]
    assert sig.field_name == "Sig_Test"
    assert sig.reason == "Approved by OriginSD"
    assert sig.location == "Headquarters"
    assert sig.is_intact is True
    assert sig.is_cryptographically_valid is True
    assert sig.certificate is not None
    assert sig.certificate.common_name == "Test Signer"
    # Initially untrusted because self-signed certificate is not yet in trust store
    assert sig.trust_status == SignatureTrustStatus.UNTRUSTED
