"""Digital signature inspection, cryptographic validation, and signing via pyHanko and cryptography."""

from __future__ import annotations

import hashlib
import io
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pymupdf as fitz  # PyMuPDF
from asn1crypto import pem, x509, cms, core
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.primitives.serialization import load_der_public_key

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


def _parse_pdf_date(date_str: str) -> str:
    """Parse PDF date format (e.g. D:20091002001131+05'00') into human-readable string."""
    if not date_str:
        return ""
    clean = str(date_str).replace("D:", "").replace("'", "")
    # Try YYYYMMDDHHmmss
    m = re.match(r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})", clean)
    if m:
        try:
            dt = datetime(
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                int(m.group(4)),
                int(m.group(5)),
                int(m.group(6)),
                tzinfo=timezone.utc,
            )
            return dt.strftime("%d-%b-%Y %H:%M:%S")
        except Exception:
            pass
    # Try YYYYMMDD
    m2 = re.match(r"^(\d{4})(\d{2})(\d{2})", clean)
    if m2:
        try:
            dt = datetime(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)), tzinfo=timezone.utc)
            return dt.strftime("%d-%b-%Y")
        except Exception:
            pass
    return clean


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
                        raw_bytes = r.certificate_pem.encode("utf-8")
                        if pem.detect(raw_bytes):
                            _, _, der_bytes = pem.unarmor(raw_bytes)
                        else:
                            der_bytes = raw_bytes
                        cert = x509.Certificate.load(der_bytes)
                        trusted_certs.append(cert)
                    except Exception as e:
                        logger.warning("Could not parse certificate %s: %s", r.common_name, e)
        except Exception as e:
            logger.error("Failed to load trusted roots: %s", e)
        return trusted_certs

    def inspect_and_validate_signatures(
        self,
        pdf_path: str | Path,
        password: str = "",
        check_revocation_online: bool = False,
    ) -> list[SignatureInfo]:
        """Inspect all embedded digital signatures in a PDF and validate their cryptographic integrity and trust."""
        path = Path(pdf_path).resolve()
        if not path.exists():
            return []

        results: list[SignatureInfo] = []

        try:
            doc_fitz = fitz.open(str(path))
            if doc_fitz.is_encrypted and password:
                doc_fitz.authenticate(password)

            with open(path, "rb") as f:
                pdf_bytes = f.read()

            # Set up validation context
            trusted_roots = self.get_trusted_roots()
            val_context = ValidationContext(
                trust_roots=trusted_roots if trusted_roots else None,
                allow_fetching=check_revocation_online,
            )

            # Check if pyHanko can load any embedded signatures
            pyhanko_emb_map: dict[str, Any] = {}
            hanko_stream = io.BytesIO(pdf_bytes)
            try:
                hanko_logger = logging.getLogger("pyhanko.sign.validation.pdf_embedded")
                prev_level = hanko_logger.level
                hanko_logger.setLevel(logging.CRITICAL)
                try:
                    reader = PdfFileReader(hanko_stream, strict=False)
                    if reader.encrypted and password:
                        reader.decrypt(password)
                    for emb in reader.embedded_signatures:
                        if emb.field_name:
                            pyhanko_emb_map[emb.field_name] = emb
                finally:
                    hanko_logger.setLevel(prev_level)
            except Exception as e:
                logger.debug("pyHanko embedded signatures sweep notice: %s", e)

            # Discover all signature candidates across all structures in the PDF
            candidates = self._collect_signature_candidates(doc_fitz, pdf_bytes, password=password)

            for cand in candidates:
                try:
                    sig_info = self._validate_candidate(
                        cand=cand,
                        doc_fitz=doc_fitz,
                        pdf_bytes=pdf_bytes,
                        val_context=val_context,
                        pyhanko_emb_map=pyhanko_emb_map,
                    )
                    if sig_info is not None:
                        results.append(sig_info)
                except Exception as e:
                    logger.error("Failed validating signature candidate %s: %s", cand.get("field_name"), e)

            doc_fitz.close()
        except Exception as e:
            logger.error("Failed inspecting signatures on %s: %s", path, e)

        return results

    def _collect_signature_candidates(
        self,
        doc_fitz: fitz.Document,
        pdf_bytes: bytes,
        password: str = "",
    ) -> list[dict[str, Any]]:
        """Collect all digital signature occurrences across widgets, AcroForm, Perms, and direct xrefs."""
        candidates_by_xref: dict[int, dict[str, Any]] = {}

        # 1. Page widgets sweep
        for page_idx, page in enumerate(doc_fitz):
            pw, ph = page.rect.width, page.rect.height
            for widget in page.widgets():
                w_field_name = widget.field_name or ""
                is_sig_field = (
                    widget.field_type == fitz.PDF_WIDGET_TYPE_SIGNATURE
                    or widget.is_signed
                    or doc_fitz.xref_get_key(widget.xref, "FT")[1] == "/Sig"
                )
                if not is_sig_field:
                    continue

                v_type, v_val = doc_fitz.xref_get_key(widget.xref, "V")
                sig_xref = None
                if v_type == "xref":
                    try:
                        sig_xref = int(v_val.split()[0])
                    except Exception:
                        sig_xref = None

                r = widget.rect
                norm_rect = [
                    float(r.x0 / pw) if pw > 0 else 0.0,
                    float(r.y0 / ph) if ph > 0 else 0.0,
                    float(r.width / pw) if pw > 0 else 0.0,
                    float(r.height / ph) if ph > 0 else 0.0,
                ]

                if sig_xref is not None and sig_xref > 0:
                    candidates_by_xref[sig_xref] = {
                        "sig_xref": sig_xref,
                        "field_name": w_field_name or f"Signature_{sig_xref}",
                        "page": page_idx,
                        "rect": [float(r.x0), float(r.y0), float(r.x1), float(r.y1)],
                        "norm_rect": norm_rect,
                        "widget_xref": widget.xref,
                    }

        # 2. AcroForm /Fields hierarchy sweep
        try:
            catalog_xref = doc_fitz.pdf_catalog()
            af_type, af_val = doc_fitz.xref_get_key(catalog_xref, "AcroForm")
            if af_type == "xref":
                af_xref = int(af_val.split()[0])
                self._scan_acroform_fields(doc_fitz, af_xref, candidates_by_xref)
            elif af_type == "dict":
                # Check directly
                f_type, f_val = doc_fitz.xref_get_key(catalog_xref, "AcroForm/Fields")
                if f_type == "xref":
                    self._scan_fields_array(doc_fitz, int(f_val.split()[0]), candidates_by_xref)
        except Exception as e:
            logger.debug("AcroForm sweep notice: %s", e)

        # 3. Document /Perms sweep (DocMDP / UR / UR3)
        try:
            perms_type, perms_val = doc_fitz.xref_get_key(doc_fitz.pdf_catalog(), "Perms")
            if perms_type == "xref":
                px = int(perms_val.split()[0])
                for perm_key in ("DocMDP", "UR", "UR3"):
                    pk_type, pk_val = doc_fitz.xref_get_key(px, perm_key)
                    if pk_type == "xref":
                        sx = int(pk_val.split()[0])
                        if sx not in candidates_by_xref:
                            candidates_by_xref[sx] = {
                                "sig_xref": sx,
                                "field_name": f"Document_{perm_key}",
                                "page": 0,
                                "rect": [0.0, 0.0, 0.0, 0.0],
                                "norm_rect": [0.0, 0.0, 0.0, 0.0],
                                "widget_xref": None,
                            }
        except Exception as e:
            logger.debug("Perms sweep notice: %s", e)

        # 4. Indirect objects sweep for /Type /Sig or /Type /DocTimeStamp
        for xref in range(1, doc_fitz.xref_length()):
            try:
                t_type, t_val = doc_fitz.xref_get_key(xref, "Type")
                if t_val in ("/Sig", "/DocTimeStamp"):
                    # Verify it has ByteRange and Contents
                    br_type, _ = doc_fitz.xref_get_key(xref, "ByteRange")
                    cnt_type, _ = doc_fitz.xref_get_key(xref, "Contents")
                    if br_type != "null" and cnt_type != "null":
                        if xref not in candidates_by_xref:
                            name_val = doc_fitz.xref_get_key(xref, "Name")[1]
                            t_name = doc_fitz.xref_get_key(xref, "T")[1]
                            fname = name_val or t_name or f"Signature_{xref}"
                            candidates_by_xref[xref] = {
                                "sig_xref": xref,
                                "field_name": fname,
                                "page": 0,
                                "rect": [0.0, 0.0, 0.0, 0.0],
                                "norm_rect": [0.0, 0.0, 0.0, 0.0],
                                "widget_xref": None,
                            }
            except Exception:
                pass

        return list(candidates_by_xref.values())

    def _scan_acroform_fields(
        self,
        doc: fitz.Document,
        af_xref: int,
        candidates_by_xref: dict[int, dict[str, Any]],
    ) -> None:
        """Scan AcroForm dictionary for signature fields."""
        f_type, f_val = doc.xref_get_key(af_xref, "Fields")
        if f_type == "xref":
            self._scan_fields_array(doc, int(f_val.split()[0]), candidates_by_xref)
        elif f_type == "array":
            # Extract refs from array string
            for m in re.finditer(r"(\d+)\s+0\s+R", f_val):
                self._check_field_node(doc, int(m.group(1)), candidates_by_xref)

    def _scan_fields_array(
        self,
        doc: fitz.Document,
        arr_xref: int,
        candidates_by_xref: dict[int, dict[str, Any]],
    ) -> None:
        """Scan field array referenced by xref."""
        obj_text = doc.xref_object(arr_xref)
        for m in re.finditer(r"(\d+)\s+0\s+R", obj_text):
            self._check_field_node(doc, int(m.group(1)), candidates_by_xref)

    def _check_field_node(
        self,
        doc: fitz.Document,
        node_xref: int,
        candidates_by_xref: dict[int, dict[str, Any]],
    ) -> None:
        """Inspect a field node (or its Kids)."""
        ft_type, ft_val = doc.xref_get_key(node_xref, "FT")
        v_type, v_val = doc.xref_get_key(node_xref, "V")
        t_type, t_val = doc.xref_get_key(node_xref, "T")

        if ft_val == "/Sig" or (v_type == "xref"):
            if v_type == "xref":
                sx = int(v_val.split()[0])
                if sx not in candidates_by_xref:
                    candidates_by_xref[sx] = {
                        "sig_xref": sx,
                        "field_name": t_val or f"Signature_{sx}",
                        "page": 0,
                        "rect": [0.0, 0.0, 0.0, 0.0],
                        "norm_rect": [0.0, 0.0, 0.0, 0.0],
                        "widget_xref": node_xref,
                    }

        # Check Kids
        kids_type, kids_val = doc.xref_get_key(node_xref, "Kids")
        if kids_type in ("array", "xref"):
            kids_text = doc.xref_object(int(kids_val.split()[0])) if kids_type == "xref" else kids_val
            for m in re.finditer(r"(\d+)\s+0\s+R", kids_text):
                self._check_field_node(doc, int(m.group(1)), candidates_by_xref)

    def _validate_candidate(
        self,
        cand: dict[str, Any],
        doc_fitz: fitz.Document,
        pdf_bytes: bytes,
        val_context: ValidationContext,
        pyhanko_emb_map: dict[str, Any],
    ) -> Optional[SignatureInfo]:
        """Validate one signature candidate using appropriate cryptographic routing."""
        sig_xref = cand["sig_xref"]
        field_name = cand.get("field_name") or f"Signature_{sig_xref}"

        obj_str = doc_fitz.xref_object(sig_xref)

        subfilter = doc_fitz.xref_get_key(sig_xref, "SubFilter")[1].strip("/")
        reason = doc_fitz.xref_get_key(sig_xref, "Reason")[1]
        location = doc_fitz.xref_get_key(sig_xref, "Location")[1]
        contact_info = doc_fitz.xref_get_key(sig_xref, "ContactInfo")[1]
        name = doc_fitz.xref_get_key(sig_xref, "Name")[1]
        m_str = doc_fitz.xref_get_key(sig_xref, "M")[1]
        signing_time = _parse_pdf_date(m_str)

        # Parse ByteRange
        br_match = re.search(r"/ByteRange\s*\[\s*([0-9\s]+)\]", obj_str)
        if not br_match:
            return None
        nums = [int(x) for x in re.findall(r"\d+", br_match.group(1))]
        if len(nums) < 4 or len(nums) % 2 != 0:
            return None

        # Build signed data from byte ranges
        signed_chunks: list[bytes] = []
        for i in range(0, len(nums), 2):
            offset, length = nums[i], nums[i + 1]
            signed_chunks.append(pdf_bytes[offset : offset + length])
        signed_data = b"".join(signed_chunks)

        # Detect document modification after signing
        last_offset = nums[-2]
        last_length = nums[-1]
        doc_modified = (last_offset + last_length) < len(pdf_bytes)

        # Extract /Contents binary bytes
        raw_contents = self._extract_contents_bytes(pdf_bytes, nums, obj_str)
        if not raw_contents:
            return None

        # Extract /Cert bytes list (if present in signature dict)
        cert_bytes_list = self._extract_cert_bytes_list(doc_fitz, sig_xref, obj_str)

        # Try pyHanko first if standard SubFilter is present and available
        if field_name in pyhanko_emb_map and subfilter in (
            "adbe.pkcs7.detached",
            "ETSI.CAdES.detached",
            "PBAD.PAdES",
            "ETSI.RFC3161",
        ):
            try:
                emb = pyhanko_emb_map[field_name]
                info = self._validate_single_signature_pyhanko(emb, val_context)
                info.field_name = field_name
                info.page_number = cand.get("page", 0)
                info.rect = cand.get("rect", [0.0, 0.0, 0.0, 0.0])
                info.norm_rect = cand.get("norm_rect", [0.0, 0.0, 0.0, 0.0])
                if not info.reason and reason:
                    info.reason = reason
                if not info.location and location:
                    info.location = location
                if not info.contact_info and contact_info:
                    info.contact_info = contact_info
                if not info.signing_time and signing_time:
                    info.signing_time = signing_time
                return info
            except Exception as e:
                logger.debug("pyHanko validation fell back to direct validation for %s: %s", field_name, e)

        # Routing by SubFilter and structure
        is_intact = False
        is_crypto_valid = False
        val_msg = ""
        signing_cert: Optional[x509.Certificate] = None

        if subfilter == "adbe.x509.rsa_sha1" or (cert_bytes_list and not subfilter.startswith("ETSI.RFC")):
            # Path A: RSA PKCS#1 v1.5 with X.509 certificate in /Cert
            is_intact, is_crypto_valid, signing_cert, val_msg = self._validate_rsa_sha1(
                raw_contents=raw_contents,
                signed_data=signed_data,
                cert_bytes_list=cert_bytes_list,
                doc_modified=doc_modified,
            )
        elif subfilter in ("adbe.pkcs7.detached", "adbe.pkcs7.sha1", "ETSI.CAdES.detached", "PBAD.PAdES") or (
            raw_contents and raw_contents[0] == 0x30
        ):
            # Path B: CMS / PKCS#7 SignedData
            is_intact, is_crypto_valid, signing_cert, val_msg, extracted_time = self._validate_cms_direct(
                raw_contents=raw_contents,
                signed_data=signed_data,
                doc_modified=doc_modified,
                subfilter=subfilter,
            )
            if extracted_time and not signing_time:
                signing_time = extracted_time
        elif subfilter in ("ETSI.RFC3161", "1.2.840.113583.1.1.8"):
            # Path C: RFC 3161 Document Timestamp
            is_intact, is_crypto_valid, signing_cert, val_msg, extracted_time = self._validate_timestamp_direct(
                raw_contents=raw_contents,
                signed_data=signed_data,
                doc_modified=doc_modified,
            )
            if extracted_time and not signing_time:
                signing_time = extracted_time
        else:
            # Path D: Fallback attempt (try CMS then RSA)
            try:
                is_intact, is_crypto_valid, signing_cert, val_msg, _ = self._validate_cms_direct(
                    raw_contents=raw_contents,
                    signed_data=signed_data,
                    doc_modified=doc_modified,
                    subfilter=subfilter,
                )
            except Exception:
                if cert_bytes_list:
                    is_intact, is_crypto_valid, signing_cert, val_msg = self._validate_rsa_sha1(
                        raw_contents=raw_contents,
                        signed_data=signed_data,
                        cert_bytes_list=cert_bytes_list,
                        doc_modified=doc_modified,
                    )

        # Build Certificate Details and Trust Status
        cert_details: Optional[CertificateDetails] = None
        trust_status = SignatureTrustStatus.UNKNOWN
        signer_name = name

        if signing_cert:
            cert_details, trust_status, final_msg = self._build_certificate_details(
                cert=signing_cert,
                is_crypto_valid=is_crypto_valid,
                doc_modified=doc_modified,
                is_intact=is_intact,
                base_message=val_msg,
            )
            if cert_details.common_name and not signer_name:
                signer_name = cert_details.common_name
            if final_msg:
                val_msg = final_msg
        else:
            if not is_crypto_valid:
                trust_status = SignatureTrustStatus.INVALID
                val_msg = val_msg or "Signature validation failed: certificate could not be resolved."
            else:
                trust_status = SignatureTrustStatus.UNKNOWN

        return SignatureInfo(
            field_name=field_name,
            signer_name=signer_name or "Unknown Signer",
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
            validation_message=val_msg,
            page_number=cand.get("page", 0),
            rect=cand.get("rect", [0.0, 0.0, 0.0, 0.0]),
            norm_rect=cand.get("norm_rect", [0.0, 0.0, 0.0, 0.0]),
        )

    def _validate_rsa_sha1(
        self,
        raw_contents: bytes,
        signed_data: bytes,
        cert_bytes_list: list[bytes],
        doc_modified: bool,
    ) -> tuple[bool, bool, Optional[x509.Certificate], str]:
        """Validate an Adobe PPKMS / PPKLite / adbe.x509.rsa_sha1 digital signature."""
        if not cert_bytes_list:
            return False, False, None, "No certificate found in signature /Cert entry."

        try:
            cert = x509.Certificate.load(cert_bytes_list[0])
            pub_key = load_der_public_key(cert.public_key.dump())
        except Exception as e:
            return False, False, None, f"Failed parsing signer certificate: {e}"

        # Extract RSA signature bytes (typically last key_size // 8 bytes)
        key_size_bytes = pub_key.key_size // 8
        sig_bytes = raw_contents[-key_size_bytes:] if len(raw_contents) >= key_size_bytes else raw_contents

        is_intact = False
        val_msg = ""

        # Try SHA-1 (standard for adbe.x509.rsa_sha1), with SHA-256 fallback
        for hash_algo in (hashes.SHA1(), hashes.SHA256(), hashes.SHA384(), hashes.SHA512(), hashes.MD5()):
            try:
                pub_key.verify(sig_bytes, signed_data, padding.PKCS1v15(), hash_algo)
                is_intact = True
                break
            except Exception:
                continue

        if not is_intact:
            val_msg = "Signature cryptographic integrity verification failed."
            return False, False, cert, val_msg

        if doc_modified:
            val_msg = "Document has been modified after signing."
            return True, False, cert, val_msg

        val_msg = "Signature is cryptographically intact and document is unmodified."
        return True, True, cert, val_msg

    def _validate_cms_direct(
        self,
        raw_contents: bytes,
        signed_data: bytes,
        doc_modified: bool,
        subfilter: str = "",
    ) -> tuple[bool, bool, Optional[x509.Certificate], str, str]:
        """Direct cryptographic validation of CMS / PKCS#7 SignedData structures."""
        try:
            content_info = cms.ContentInfo.load(raw_contents)
            sd = content_info["content"]
            certs = [c.chosen.untag() for c in sd["certificates"] if c.name == "certificate"]
            signer_info = sd["signer_infos"][0]
        except Exception as e:
            return False, False, None, f"Failed parsing CMS SignedData structure: {e}", ""

        # Locate signer certificate
        sid = signer_info["sid"]
        signing_cert: Optional[x509.Certificate] = None
        if sid.name == "issuer_and_serial_number":
            iss = sid.chosen["issuer"]
            sn = sid.chosen["serial_number"].native
            for c in certs:
                if c.issuer == iss and c.serial_number == sn:
                    signing_cert = c
                    break
        elif sid.name == "subject_key_identifier":
            ski = sid.chosen.native
            for c in certs:
                if c.key_identifier == ski:
                    signing_cert = c
                    break
        if not signing_cert and certs:
            signing_cert = certs[0]

        if not signing_cert:
            return False, False, None, "No matching certificate found in CMS signed data.", ""

        try:
            pub_key = load_der_public_key(signing_cert.public_key.dump())
        except Exception as e:
            return False, False, signing_cert, f"Could not load public key from certificate: {e}", ""

        algo_name = signer_info["digest_algorithm"]["algorithm"].native.lower()
        hash_map: dict[str, Any] = {
            "sha1": hashes.SHA1(),
            "sha256": hashes.SHA256(),
            "sha384": hashes.SHA384(),
            "sha512": hashes.SHA512(),
            "md5": hashes.MD5(),
        }
        hash_algo = hash_map.get(algo_name, hashes.SHA256())

        extracted_time = ""
        is_intact = False

        signed_attrs = signer_info["signed_attrs"]
        if signed_attrs is not core.VOID:
            # Extract expected message digest and signing time
            expected_digest = None
            for attr in signed_attrs:
                t = attr["type"].native
                if t == "message_digest":
                    expected_digest = attr["values"][0].native
                elif t == "signing_time":
                    st_val = attr["values"][0].native
                    if isinstance(st_val, datetime):
                        extracted_time = st_val.strftime("%d-%b-%Y %H:%M:%S")

            # Compute actual digest over byte range
            h = hashlib.new(algo_name if algo_name in hashlib.algorithms_available else "sha256")
            h.update(signed_data)
            actual_digest = h.digest()

            if expected_digest is not None and actual_digest != expected_digest:
                return False, False, signing_cert, "Message digest mismatch: document content altered.", extracted_time

            # Verify signature over signed attributes SET OF
            data_to_verify = signed_attrs.untag().dump()
            sig_bytes = signer_info["signature"].native

            try:
                if isinstance(pub_key, rsa.RSAPublicKey):
                    pub_key.verify(sig_bytes, data_to_verify, padding.PKCS1v15(), hash_algo)
                elif isinstance(pub_key, ec.EllipticCurvePublicKey):
                    pub_key.verify(sig_bytes, data_to_verify, ec.ECDSA(hash_algo))
                else:
                    pub_key.verify(sig_bytes, data_to_verify, padding.PKCS1v15(), hash_algo)
                is_intact = True
            except Exception:
                # Try RSA-PSS
                try:
                    if isinstance(pub_key, rsa.RSAPublicKey):
                        pub_key.verify(
                            sig_bytes,
                            data_to_verify,
                            padding.PSS(mgf=padding.MGF1(hash_algo), salt_length=padding.PSS.MAX_LENGTH),
                            hash_algo,
                        )
                        is_intact = True
                except Exception:
                    is_intact = False
        else:
            # Simple detached signature without signed attributes
            sig_bytes = signer_info["signature"].native
            try:
                if isinstance(pub_key, rsa.RSAPublicKey):
                    pub_key.verify(sig_bytes, signed_data, padding.PKCS1v15(), hash_algo)
                else:
                    pub_key.verify(sig_bytes, signed_data, padding.PKCS1v15(), hash_algo)
                is_intact = True
            except Exception:
                is_intact = False

        if not is_intact:
            return False, False, signing_cert, "CMS signature cryptographic verification failed.", extracted_time

        if doc_modified:
            return True, False, signing_cert, "Document has been modified after signing.", extracted_time

        return True, True, signing_cert, "Signature is cryptographically intact and document is unmodified.", extracted_time

    def _validate_timestamp_direct(
        self,
        raw_contents: bytes,
        signed_data: bytes,
        doc_modified: bool,
    ) -> tuple[bool, bool, Optional[x509.Certificate], str, str]:
        """Validate RFC 3161 document timestamp token."""
        try:
            content_info = cms.ContentInfo.load(raw_contents)
            sd = content_info["content"]
            certs = [c.chosen.untag() for c in sd["certificates"] if c.name == "certificate"]
            signing_cert = certs[0] if certs else None

            # Extract TSTInfo from encap_content_info
            encap = sd["encap_content_info"]
            extracted_time = ""
            if encap["content_type"].native == "tst_info":
                tst_info = cms.TSTInfo.load(encap["content"].native)
                gen_time = tst_info["gen_time"].native
                if isinstance(gen_time, datetime):
                    extracted_time = gen_time.strftime("%d-%b-%Y %H:%M:%S")

            is_intact = not doc_modified
            is_crypto_valid = is_intact
            val_msg = "Timestamp is valid." if is_crypto_valid else "Document modified after timestamp."
            return is_intact, is_crypto_valid, signing_cert, val_msg, extracted_time
        except Exception as e:
            return False, False, None, f"Failed validating timestamp token: {e}", ""

    def _build_certificate_details(
        self,
        cert: x509.Certificate,
        is_crypto_valid: bool,
        doc_modified: bool,
        is_intact: bool,
        base_message: str = "",
    ) -> tuple[CertificateDetails, SignatureTrustStatus, str]:
        """Construct CertificateDetails and evaluate trust status against repository and CAs."""
        native_subj = cert.subject.native if hasattr(cert.subject, "native") else {}
        native_iss = cert.issuer.native if hasattr(cert.issuer, "native") else {}

        subject_name = native_subj.get("common_name") or cert.subject.human_friendly
        issuer_name = native_iss.get("common_name") or cert.issuer.human_friendly
        org_name = native_subj.get("organization_name") or native_subj.get("organization") or ""

        sha256_fp = cert.sha256_fingerprint.replace(" ", "").lower()
        not_before = str(cert.not_valid_before)
        not_after = str(cert.not_valid_after)

        now = datetime.now(timezone.utc)
        is_expired = now > cert.not_valid_after.replace(tzinfo=timezone.utc)
        is_self_signed = cert.self_signed in ("yes", "maybe") or cert.subject == cert.issuer

        cert_pem = pem.armor("CERTIFICATE", cert.dump()).decode("utf-8")

        # Check local SQLite trust store
        existing_trusted = self.cert_repo.find_by_fingerprint(sha256_fp)
        is_explicitly_trusted = existing_trusted is not None and existing_trusted.is_trusted

        # Check against trusted root CAs loaded from cert_repo
        trusted_roots = self.get_trusted_roots()
        is_ca_trusted = False
        for root in trusted_roots:
            if root.sha256_fingerprint.replace(" ", "").lower() == sha256_fp:
                is_ca_trusted = True
                break
            if cert.issuer == root.subject:
                # Direct chain link
                is_ca_trusted = True
                break

        is_trusted = is_explicitly_trusted or is_ca_trusted

        if not is_crypto_valid:
            trust_status = SignatureTrustStatus.INVALID
            if not is_intact:
                val_msg = "Signature cryptographic integrity verification failed."
            elif doc_modified:
                val_msg = "Document has been modified after signing."
            else:
                val_msg = base_message or "Signature verification failed."
        elif is_trusted:
            trust_status = SignatureTrustStatus.TRUSTED
            val_msg = "Signature is valid and certificate is trusted."
        elif is_expired:
            trust_status = SignatureTrustStatus.EXPIRED
            val_msg = "Signature is cryptographically intact, but the signer's certificate has expired."
        else:
            trust_status = SignatureTrustStatus.UNTRUSTED
            val_msg = "Signature is cryptographically intact, but the signer's certificate is not trusted."

        cert_details = CertificateDetails(
            common_name=subject_name,
            organization=org_name,
            issuer=issuer_name,
            serial_number=hex(cert.serial_number),
            fingerprint_sha256=sha256_fp,
            valid_from=not_before,
            valid_to=not_after,
            is_self_signed=is_self_signed,
            is_expired=is_expired,
            is_trusted=is_trusted,
            raw_pem=cert_pem,
        )

        return cert_details, trust_status, val_msg

    def _extract_contents_bytes(
        self,
        pdf_bytes: bytes,
        nums: list[int],
        obj_str: str,
    ) -> bytes:
        """Extract binary contents bytes of signature using byte-range gap with xref fallback."""
        if len(nums) >= 4:
            gap = pdf_bytes[nums[0] + nums[1] : nums[2]].strip()
            if gap.startswith(b"<") and gap.endswith(b">"):
                hex_str = gap[1:-1].replace(b"\r", b"").replace(b"\n", b"").replace(b" ", b"")
                try:
                    return bytes.fromhex(hex_str.decode("ascii"))
                except Exception:
                    pass

        # Fallback to obj_str regex
        m = re.search(r"/Contents\s*<([0-9a-fA-F\s]+)>", obj_str)
        if m:
            hex_str_s = m.group(1).replace("\r", "").replace("\n", "").replace(" ", "")
            try:
                return bytes.fromhex(hex_str_s)
            except Exception:
                pass

        return b""

    def _extract_cert_bytes_list(
        self,
        doc: fitz.Document,
        sig_xref: int,
        obj_str: str,
    ) -> list[bytes]:
        """Extract list of DER certificates from /Cert entry."""
        certs: list[bytes] = []
        try:
            array_m = re.search(r"/Cert\s*\[([^\]]+)\]", obj_str)
            if array_m:
                for item in re.finditer(r"<([0-9a-fA-F\s]+)>", array_m.group(1)):
                    h = item.group(1).replace("\r", "").replace("\n", "").replace(" ", "")
                    certs.append(bytes.fromhex(h))
            else:
                m = re.search(r"/Cert\s*<([0-9a-fA-F\s]+)>", obj_str)
                if m:
                    h = m.group(1).replace("\r", "").replace("\n", "").replace(" ", "")
                    certs.append(bytes.fromhex(h))
                else:
                    cert_key = doc.xref_get_key(sig_xref, "Cert")
                    if cert_key[0] == "xref":
                        cx = int(cert_key[1].split()[0])
                        c_obj = doc.xref_object(cx)
                        m2 = re.search(r"<([0-9a-fA-F\s]+)>", c_obj)
                        if m2:
                            h2 = m2.group(1).replace("\r", "").replace("\n", "").replace(" ", "")
                            certs.append(bytes.fromhex(h2))
                        else:
                            st = doc.xref_stream(cx)
                            if st:
                                certs.append(st)
        except Exception as e:
            logger.debug("Failed extracting cert bytes: %s", e)
        return certs

    def _validate_single_signature_pyhanko(
        self,
        embedded_sig: Any,
        val_context: ValidationContext,
    ) -> SignatureInfo:
        """Validate standard CMS embedded signature using pyHanko."""
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

            status = validation.validate_pdf_signature(embedded_sig, val_context)

            is_intact = bool(status.intact)
            doc_modified = not bool(status.docmdp_ok) or (
                hasattr(status, "diff_result")
                and status.diff_result is not None
                and hasattr(status.diff_result, "modification_level")
                and status.diff_result.modification_level.value > 0
            )
            is_crypto_valid = is_intact and not doc_modified

            if hasattr(status, "signer_reported_dt") and status.signer_reported_dt:
                signing_time = status.signer_reported_dt.strftime("%d-%b-%Y %H:%M:%S")
            elif "/M" in sig_obj:
                signing_time = _parse_pdf_date(str(sig_obj.get("/M", "")))

            signing_cert = status.signing_cert
            if signing_cert:
                cert_details, trust_status, validation_msg = self._build_certificate_details(
                    cert=signing_cert,
                    is_crypto_valid=is_crypto_valid,
                    doc_modified=doc_modified,
                    is_intact=is_intact,
                    base_message="",
                )
                signer_name = cert_details.common_name
            else:
                validation_msg = "No embedded signing certificate found."
                trust_status = SignatureTrustStatus.INVALID

        except Exception as e:
            logger.error("Error validating embedded signature with pyHanko: %s", e)
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
