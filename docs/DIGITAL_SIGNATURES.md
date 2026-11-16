# Digital Signatures and Certificate Security

Oqteris integrates [pyHanko](https://github.com/MatthiasValvekens/pyHanko) for digital signature validation and signing.

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
