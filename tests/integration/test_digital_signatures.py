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


def test_signature_trust_and_revalidation_workflow(
    sample_pdf_normal: Path,
    test_p12_certificate: tuple[Path, str],
    temp_dir: Path,
    test_db,
    qapp,
):
    """Test full workflow: signed document opened, inspected, trusted into SQLite, and re-validated."""
    from oqteris.ui.controllers.pdf_controller import PDFController
    from oqteris.ui.controllers.signature_controller import SignatureController

    p12_path, passphrase = test_p12_certificate
    signed_pdf = temp_dir / "verified_doc.pdf"

    cert_repo = CertificatesRepository(db_manager=test_db)
    service = SignatureService(cert_repo=cert_repo)
    service.sign_pdf(
        input_path=sample_pdf_normal,
        output_path=signed_pdf,
        pkcs12_path=p12_path,
        passphrase=passphrase,
        field_name="Sig_eDistrict",
        reason="D-Sign",
        location="E-Dist 2.0",
        page_index=0,
        box=(100, 100, 300, 200),
    )

    pdf_ctrl = PDFController()
    sig_ctrl = SignatureController(pdf_controller=pdf_ctrl)
    # Inject test cert repo
    sig_ctrl._cert_repo = cert_repo
    sig_ctrl._sig_service = service

    # 1. Open document in PDFController
    pdf_ctrl.openDocument(str(signed_pdf))
    sig_ctrl.inspectSignatures()

    assert sig_ctrl.hasSignatures is True
    assert sig_ctrl.signatureCount == 1
    assert sig_ctrl.allValidAndTrusted is False
    assert "Signature Not Verified" in sig_ctrl.statusSummary

    sigs = sig_ctrl.documentSignatures
    assert len(sigs) == 1
    assert sigs[0]["signerName"] == "Test Signer"
    assert sigs[0]["trustStatus"] == "untrusted"
    assert sigs[0]["pageNumber"] == 0

    # 2. Get certificate details
    details = sig_ctrl.getCertificateDetails(0)
    assert details["commonName"] == "Test Signer"
    assert details["isTrusted"] is False
    assert details["rawPem"] != ""

    # 3. Trust the signature certificate
    trusted_ok = sig_ctrl.trustSignatureCertificate(0)
    assert trusted_ok is True

    # 4. Re-verify: now trusted and valid!
    assert sig_ctrl.allValidAndTrusted is True
    assert "Signed and all signatures are valid" in sig_ctrl.statusSummary
    sigs_after = sig_ctrl.documentSignatures
    assert sigs_after[0]["trustStatus"] == "trusted"

    # 5. Untrust the certificate
    untrust_ok = sig_ctrl.untrustSignatureCertificate(0)
    assert untrust_ok is True
    assert sig_ctrl.allValidAndTrusted is False
    assert sig_ctrl.documentSignatures[0]["trustStatus"] == "untrusted"

    # Cleanup
    pdf_ctrl.closeDocument()
    assert pdf_ctrl.hasDocument is False

