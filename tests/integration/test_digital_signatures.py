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
    assert sig_ctrl.statusSummary == "Valid (Untrusted Root CA)"

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
    assert sig_ctrl.statusSummary == "Digitally Signed & Trusted"
    sigs_after = sig_ctrl.documentSignatures
    assert sigs_after[0]["trustStatus"] == "trusted"
    assert sig_ctrl.signaturesRevision > 1

    page_sigs = sig_ctrl.getSignaturesForPage(0)
    assert len(page_sigs) == 1
    assert page_sigs[0]["trustStatus"] == "trusted"
    assert page_sigs[0]["sigIndex"] == 0

    # 5. Untrust the certificate
    untrust_ok = sig_ctrl.untrustSignatureCertificate(0)
    assert untrust_ok is True
    assert sig_ctrl.allValidAndTrusted is False
    assert sig_ctrl.documentSignatures[0]["trustStatus"] == "untrusted"

    # Cleanup
    pdf_ctrl.closeDocument()
    assert pdf_ctrl.hasDocument is False


def test_encrypted_pdf_signature_inspection(
    sample_pdf_normal: Path,
    test_p12_certificate: tuple[Path, str],
    temp_dir: Path,
    test_db,
):
    """Test that digital signatures in encrypted/password-protected PDFs are detected with password."""
    import pymupdf

    p12_path, passphrase = test_p12_certificate
    signed_pdf = temp_dir / "signed_before_encrypt.pdf"
    encrypted_signed_pdf = temp_dir / "encrypted_signed.pdf"

    cert_repo = CertificatesRepository(db_manager=test_db)
    service = SignatureService(cert_repo=cert_repo)

    # 1. Sign
    service.sign_pdf(
        input_path=sample_pdf_normal,
        output_path=signed_pdf,
        pkcs12_path=p12_path,
        passphrase=passphrase,
        field_name="Sig_Encrypted",
        reason="Encrypted test",
        page_index=0,
    )

    # 2. Encrypt
    doc = pymupdf.open(str(signed_pdf))
    doc.save(
        str(encrypted_signed_pdf),
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        user_pw="secret123",
        owner_pw="owner123",
    )
    doc.close()

    # 3. Without password -> returns empty list (graceful failure)
    sigs_nopw = service.inspect_and_validate_signatures(encrypted_signed_pdf)
    assert len(sigs_nopw) == 0

    # 4. With password -> successfully decrypts and detects signature
    sigs_pw = service.inspect_and_validate_signatures(encrypted_signed_pdf, password="secret123")
    assert len(sigs_pw) == 1
    assert sigs_pw[0].field_name == "Sig_Encrypted"
    assert sigs_pw[0].certificate is not None
    assert sigs_pw[0].certificate.common_name == "Test Signer"


def test_legacy_rsa_sha1_signature_detection_and_validation(test_db):
    """Test detection and cryptographic validation of legacy Adobe adbe.x509.rsa_sha1 digital signature."""
    fixture_pdf = Path(__file__).parent.parent / "fixtures" / "sample_rsa_sha1_signed.pdf"
    assert fixture_pdf.exists()

    cert_repo = CertificatesRepository(db_manager=test_db)
    service = SignatureService(cert_repo=cert_repo)

    # 1. Inspect and validate
    sigs = service.inspect_and_validate_signatures(fixture_pdf)
    assert len(sigs) == 1

    sig = sigs[0]
    assert sig.field_name == "Alice-1-1081652293"
    assert sig.signer_name == "Alice"
    assert sig.reason == "This is the trial version, please buy to activate."
    assert sig.location == "Sign Location / city"
    assert sig.contact_info == "some contact info..."
    assert sig.subfilter == "adbe.x509.rsa_sha1"
    assert sig.page_number == 0
    assert sig.is_intact is True
    assert sig.is_cryptographically_valid is True
    assert sig.doc_modified_since_signing is False
    assert sig.trust_status == SignatureTrustStatus.EXPIRED

    assert sig.certificate is not None
    assert sig.certificate.common_name == "Alice"
    assert sig.certificate.organization == "Tecxoft"
    assert sig.certificate.issuer == "Alice"
    assert sig.certificate.is_self_signed is True
    assert sig.certificate.is_expired is True
    assert sig.certificate.is_trusted is False
    assert sig.certificate.raw_pem.startswith("-----BEGIN CERTIFICATE-----")


def test_legacy_signature_trust_and_controller_workflow(test_db, qapp):
    """Test UI controller workflow on legacy adbe.x509.rsa_sha1 signature including trust and untrust."""
    from oqteris.ui.controllers.pdf_controller import PDFController
    from oqteris.ui.controllers.signature_controller import SignatureController

    fixture_pdf = Path(__file__).parent.parent / "fixtures" / "sample_rsa_sha1_signed.pdf"
    assert fixture_pdf.exists()

    cert_repo = CertificatesRepository(db_manager=test_db)
    service = SignatureService(cert_repo=cert_repo)

    pdf_ctrl = PDFController()
    sig_ctrl = SignatureController(pdf_controller=pdf_ctrl, cert_repo=cert_repo)
    sig_ctrl._sig_service = service

    pdf_ctrl.openDocument(str(fixture_pdf))
    sig_ctrl.inspectSignatures()

    assert sig_ctrl.hasSignatures is True
    assert sig_ctrl.signatureCount == 1
    assert sig_ctrl.hasUntrusted is True
    assert sig_ctrl.statusSummary == "Valid (Certificate Expired)"

    sigs = sig_ctrl.documentSignatures
    assert len(sigs) == 1
    assert sigs[0]["signerName"] == "Alice"
    assert sigs[0]["trustStatus"] == "expired"

    # Trust the certificate
    trusted_ok = sig_ctrl.trustSignatureCertificate(0)
    assert trusted_ok is True

    # Re-verify: now trusted!
    assert sig_ctrl.allValidAndTrusted is True
    assert sig_ctrl.statusSummary == "Digitally Signed & Trusted"
    assert sig_ctrl.documentSignatures[0]["trustStatus"] == "trusted"

    # Untrust the certificate
    untrust_ok = sig_ctrl.untrustSignatureCertificate(0)
    assert untrust_ok is True
    assert sig_ctrl.allValidAndTrusted is False
    assert sig_ctrl.documentSignatures[0]["trustStatus"] == "expired"

    pdf_ctrl.closeDocument()


def test_legacy_signature_tamper_detection(temp_dir: Path, test_db):
    """Test that tampering byte ranges or appending unauthorized data marks signature invalid."""
    fixture_pdf = Path(__file__).parent.parent / "fixtures" / "sample_rsa_sha1_signed.pdf"
    orig_bytes = fixture_pdf.read_bytes()

    cert_repo = CertificatesRepository(db_manager=test_db)
    service = SignatureService(cert_repo=cert_repo)

    # 1. Tamper signed data: flip byte 50
    tampered_bytes = bytearray(orig_bytes)
    tampered_bytes[50] ^= 0xFF
    tampered_pdf = temp_dir / "tampered_legacy.pdf"
    tampered_pdf.write_bytes(tampered_bytes)

    sigs_tampered = service.inspect_and_validate_signatures(tampered_pdf)
    assert len(sigs_tampered) == 1
    assert sigs_tampered[0].is_intact is False
    assert sigs_tampered[0].is_cryptographically_valid is False
    assert sigs_tampered[0].trust_status == SignatureTrustStatus.INVALID

    # 2. Append unauthorized revision after signature
    appended_bytes = orig_bytes + b"\n% unauthorized trailing content\n"
    appended_pdf = temp_dir / "appended_legacy.pdf"
    appended_pdf.write_bytes(appended_bytes)

    sigs_appended = service.inspect_and_validate_signatures(appended_pdf)
    assert len(sigs_appended) == 1
    assert sigs_appended[0].is_intact is True
    assert sigs_appended[0].doc_modified_since_signing is True
    assert sigs_appended[0].is_cryptographically_valid is False
    assert sigs_appended[0].trust_status == SignatureTrustStatus.INVALID



