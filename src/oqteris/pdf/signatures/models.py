"""Data models for digital signatures and X.509 certificate validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SignatureTrustStatus(str, Enum):
    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"
    INVALID = "invalid"
    REVOKED = "revoked"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


@dataclass
class CertificateDetails:
    """X.509 certificate metadata and trust parameters."""

    common_name: str
    organization: str = ""
    issuer: str = ""
    serial_number: str = ""
    fingerprint_sha256: str = ""
    valid_from: str = ""
    valid_to: str = ""
    is_self_signed: bool = False
    is_expired: bool = False
    is_trusted: bool = False
    raw_pem: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "commonName": self.common_name,
            "organization": self.organization,
            "issuer": self.issuer,
            "serialNumber": self.serial_number,
            "fingerprintSha256": self.fingerprint_sha256,
            "validFrom": self.valid_from,
            "validTo": self.valid_to,
            "isSelfSigned": self.is_self_signed,
            "isExpired": self.is_expired,
            "isTrusted": self.is_trusted,
            "rawPem": self.raw_pem,
        }


@dataclass
class SignatureInfo:
    """Detailed cryptographic status and provenance of a digital signature."""

    field_name: str
    signer_name: str = ""
    signing_time: str = ""
    reason: str = ""
    location: str = ""
    contact_info: str = ""
    subfilter: str = ""
    is_intact: bool = False
    is_cryptographically_valid: bool = False
    doc_modified_since_signing: bool = False
    trust_status: SignatureTrustStatus = SignatureTrustStatus.UNKNOWN
    certificate: Optional[CertificateDetails] = None
    validation_message: str = ""
    page_number: int = 0
    rect: list[float] = field(default_factory=list)
    norm_rect: list[float] = field(default_factory=list)
    is_layered: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "fieldName": self.field_name,
            "signerName": self.signer_name or "Unknown Signer",
            "signingTime": self.signing_time,
            "reason": self.reason,
            "location": self.location,
            "contactInfo": self.contact_info,
            "subfilter": self.subfilter,
            "isIntact": self.is_intact,
            "isValid": self.is_cryptographically_valid,
            "docModified": self.doc_modified_since_signing,
            "trustStatus": self.trust_status.value,
            "certificate": self.certificate.to_dict() if self.certificate else None,
            "validationMessage": self.validation_message,
            "pageNumber": self.page_number,
            "rect": self.rect,
            "normRect": self.norm_rect,
            "isLayered": self.is_layered,
        }
