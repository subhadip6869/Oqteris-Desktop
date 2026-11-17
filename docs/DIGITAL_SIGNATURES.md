# Digital Signatures and Certificate Security

Oqteris integrates a hybrid digital signature engine combining pyHanko, PyMuPDF, and low-level cryptography/asn1crypto for universal signature detection and cryptographic verification across modern and legacy PDF signature formats.

## Supported Digital Signature Formats

1. **Modern CMS / PKCS#7 Detached & PAdES**:
   - SubFilters: `/adbe.pkcs7.detached`, `/ETSI.CAdES.detached` (PAdES B-B, B-T, B-LT, B-LTA), `/PBAD.PAdES`.
2. **Legacy Adobe RSA Signatures (PPKMS / PPKLite)**:
   - SubFilter: `/adbe.x509.rsa_sha1`.
   - Contents contain DER-encoded PKCS#1 RSA signature; certificates reside in `/Cert`.
   - Cryptographically verified over the PDF ByteRange with SHA-1 / SHA-256 and public key extracted from `/Cert`.
3. **Legacy PKCS#7 SHA-1 Signatures**:
   - SubFilter: `/adbe.pkcs7.sha1`.
   - Directly parsed and cryptographically verified against the document digest.
4. **Document Timestamps**:
   - SubFilters: `/ETSI.RFC3161`, `/1.2.840.113583.1.1.8`, `/DocTimeStamp`.
   - Validates RFC 3161 TimeStampToken against byte-range digest.
5. **Universal Signature Discovery Channels**:
   - **Page Annotation Widgets**: All widget annotations (`/Subtype /Widget`) with `/FT /Sig` or `widget.is_signed`.
   - **AcroForm Fields**: Recursive traversal of the `/Catalog /AcroForm /Fields` hierarchy.
   - **Document Permissions**: Checks `/Catalog /Perms` (`/DocMDP`, `/UR`, `/UR3`).
   - **Indirect Object Sweeping**: Scans all PDF xrefs for objects of `/Type /Sig` or `/Type /DocTimeStamp` with `/ByteRange` and `/Contents`.

## Core Security Philosophy

1. **Cryptographic Integrity != Certificate Trust**:
   - A mathematically valid signature proves only that the document content matches the hash computed at signing time.
   - A valid cryptographic signature whose certificate is self-signed or issued by an untrusted authority is explicitly reported as **UNTRUSTED** (yellow indicator), never green.
2. **Incremental Updates**:
   - Digitally signed documents cannot undergo standard full saves without breaking their cryptographic byte-range hashes.
   - All subsequent signatures or approved form updates are written using incremental update mode (`IncrementalPdfFileWriter`), preserving prior revisions and certificate validity.
3. **Multi-Stage Validation Matrix**:
   - **Byte-Range Intactness**: Ensures signed bytes were not modified.
   - **Certificate Validity Period**: Checks whether the certificate was within its valid lifetime at the time of signing.
   - **Certificate Chain Validation**: Validates the path back to a trusted root CA.
   - **Revocation Checking**: Checks OCSP / CRL endpoints when enabled.
   - **Document Modification (DocMDP)**: Detects whether modifications occurred after signing.

---

## Digital Signing Workflow

Oqteris supports digital signing using PKCS#12 (`.p12` / `.pfx`) credentials:
- Prompts for certificate file and optional password/PIN.
- Allows specifying signing reason, location, and visual signature appearance.
- Appends the cryptographic signature dictionary in an incremental PDF revision.
