"""In-memory redrawing of layered PDF signature appearances (n0..n4 Acro6 / iText layers).

Reproduces what Adobe Acrobat / Reader and Foxit do for layered signature appearances:
The file on disk stores only one static state (often a yellow question mark in n1 and
'Signature Not Verified' in n4). At display time, the viewer rewrites n1, n3, and n4
in memory based on cryptographic verification and certificate trust.
The file on disk is never touched, so the cryptographic signature remains intact.
"""

from __future__ import annotations

import logging
import re
from enum import Enum
from typing import Any, Optional

import pymupdf

from oqteris.pdf.signatures.models import SignatureInfo, SignatureTrustStatus

logger = logging.getLogger(__name__)

BLANK = "q Q\n"

# Standard Helvetica character widths (1000 units per em)
HELVETICA_WIDTHS: dict[str, int] = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667, "'": 191,
    "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333, ".": 278, "/": 278,
    "0": 556, "1": 556, "2": 556, "3": 556, "4": 556, "5": 556, "6": 556, "7": 556,
    "8": 556, "9": 556, ":": 278, ";": 278, "<": 584, "=": 584, ">": 584, "?": 556,
    "@": 1015, "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 500, "K": 667, "L": 556, "M": 833, "N": 722, "O": 778,
    "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944,
    "X": 667, "Y": 667, "Z": 611, "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556,
    "`": 333, "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556,
    "h": 556, "i": 222, "j": 222, "k": 500, "l": 222, "m": 833, "n": 556, "o": 556,
    "p": 556, "q": 556, "r": 333, "s": 500, "t": 278, "u": 556, "v": 500, "w": 722,
    "x": 500, "y": 500, "z": 500, "{": 334, "|": 260, "}": 334, "~": 584
}


class State(str, Enum):
    VALID = "VALID"
    UNKNOWN = "UNKNOWN"
    INVALID = "INVALID"


def _f(v: float) -> str:
    return f"{v:.3f}"


def _string_width_helvetica(text: str) -> float:
    return sum(HELVETICA_WIDTHS.get(c, 550) for c in text)


def _polyline(sb: list[str], pts: list[list[float]], ox: float, oy: float, s: float, color: str) -> None:
    sb.append(color + "\n")
    for i, (px, py) in enumerate(pts):
        sb.append(f"{_f(ox + px * s)} {_f(oy + py * s)}")
        sb.append(" m\n" if i == 0 else " l\n")
    sb.append("S\n")


def _box(doc: pymupdf.Document, xref: int) -> list[float]:
    """[x, y, width, height] of the layer's bounding box."""
    _, bbox_str = doc.xref_get_key(xref, "BBox")
    nums = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", bbox_str)]
    if len(nums) == 4 and nums[2] > nums[0] and nums[3] > nums[1]:
        return [nums[0], nums[1], nums[2] - nums[0], nums[3] - nums[1]]
    return [0.0, 0.0, 100.0, 100.0]


def _tick(b: list[float]) -> str:
    """Green tick with dark drop shadow, matching Acrobat's 'Signature valid' mark."""
    s = min(b[2], b[3])
    ox = b[0] + (b[2] - s) / 2.0
    oy = b[1] + (b[3] - s) / 2.0
    d = 0.035 * s
    pts = [[0.12, 0.50], [0.36, 0.20], [0.90, 0.88]]
    sb = [f"q 1 J 1 j {_f(0.16 * s)} w\n"]
    _polyline(sb, pts, ox + d, oy - d, s, "0 0 0 RG")  # shadow
    _polyline(sb, pts, ox, oy, s, "0.04 0.67 0.27 RG")  # green
    sb.append("Q\n")
    return "".join(sb)


def _cross(b: list[float]) -> str:
    """Red cross with dark drop shadow, matching Acrobat's 'Signature invalid' mark."""
    s = min(b[2], b[3])
    ox = b[0] + (b[2] - s) / 2.0
    oy = b[1] + (b[3] - s) / 2.0
    d = 0.035 * s
    a = [[0.16, 0.16], [0.84, 0.84]]
    c = [[0.16, 0.84], [0.84, 0.16]]
    sb = [f"q 1 J 1 j {_f(0.15 * s)} w\n"]
    _polyline(sb, a, ox + d, oy - d, s, "0 0 0 RG")
    _polyline(sb, c, ox + d, oy - d, s, "0 0 0 RG")
    _polyline(sb, a, ox, oy, s, "0.86 0.10 0.10 RG")
    _polyline(sb, c, ox, oy, s, "0.86 0.10 0.10 RG")
    sb.append("Q\n")
    return "".join(sb)


def _question_mark(doc: pymupdf.Document, n1_xref: int, b: list[float]) -> str:
    """Big yellow question mark (validity unknown) with Helvetica-Bold."""
    s = min(b[2], b[3])
    try:
        doc.xref_set_key(n1_xref, "Resources/Font/F_Bold", "<</Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold>>")
    except Exception:
        pass
    size = s * 1.15
    w = 0.611 * size
    h = 0.73 * size
    x = b[0] + (b[2] - w) / 2.0
    y = b[1] + (b[3] - h) / 2.0
    d = 0.03 * s
    return (
        "q\n"
        f"BT /F_Bold {_f(size)} Tf 0 g {_f(x + d)} {_f(y - d)} Td (?) Tj ET\n"
        f"BT /F_Bold {_f(size)} Tf 1 0.80 0 rg {_f(x)} {_f(y)} Td (?) Tj ET\n"
        "Q\n"
    )


def _caption(doc: pymupdf.Document, n4_xref: int, b4: list[float], b2: Optional[list[float]], text: str) -> str:
    """Caption in the top section of the signature field (e.g. 'Signature valid')."""
    try:
        doc.xref_set_key(n4_xref, "Resources/Font/F_Helv", "<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>")
    except Exception:
        pass
    zone_h = b4[3]
    if b2 is not None and b4[3] >= 0.75 * b2[3]:
        zone_h = b4[3] * 0.3
    zone_y = b4[1] + b4[3] - zone_h
    size = zone_h * 0.62
    text_w = _string_width_helvetica(text) / 1000.0 * size
    max_w = b4[2] - 8
    if text_w > max_w and text_w > 0:
        size *= max_w / text_w
    x = b4[0] + 4
    y = zone_y + (zone_h - size * 0.72) / 2.0
    return f"q\nBT /F_Helv {_f(size)} Tf 0 g {_f(x)} {_f(y)} Td ({text}) Tj ET\nQ\n"


def _write(doc: pymupdf.Document, xref: int, content: str) -> None:
    """Replace content stream of a form layer in memory."""
    doc.update_stream(xref, content.encode("latin1"), compress=False)


def _extract_dict(text: str, start_key: str) -> str:
    """Extract nested dictionary text < ... > starting at start_key."""
    idx = text.find(start_key)
    if idx == -1:
        return ""
    start_bracket = text.find("<<", idx)
    if start_bracket == -1:
        return ""
    depth = 0
    i = start_bracket
    while i < len(text) - 1:
        if text[i : i + 2] == "<<":
            depth += 1
            i += 2
        elif text[i : i + 2] == ">>":
            depth -= 1
            i += 2
            if depth == 0:
                return text[start_bracket:i]
        else:
            i += 1
    return text[start_bracket:]


def _find_layer_resources(doc: pymupdf.Document, xref: int, depth: int = 0) -> Optional[dict[str, int]]:
    """Look up layers (n1, n2, n3, n4) either directly in /N resources or in child forms (e.g. /FRM)."""
    try:
        res_type, res_val = doc.xref_get_key(xref, "Resources")
        if res_type == "null":
            return None
        res_text = res_val
        if res_type == "xref":
            m = re.search(r"(\d+)\s+0\s+R", res_val)
            if m:
                res_text = doc.xref_object(int(m.group(1)))

        xobj_dict = _extract_dict(res_text, "/XObject")
        if xobj_dict:
            if "/n1" in xobj_dict and "/n3" in xobj_dict:
                layers: dict[str, int] = {}
                for m in re.finditer(r"/(n\d+)\s+(\d+)\s+0\s+R", xobj_dict):
                    layers[m.group(1)] = int(m.group(2))
                return layers

            if depth < 2:
                for m in re.finditer(r"/(\w+)\s+(\d+)\s+0\s+R", xobj_dict):
                    child_xref = int(m.group(2))
                    found = _find_layer_resources(doc, child_xref, depth + 1)
                    if found is not None:
                        return found
    except Exception as e:
        logger.debug("Error inspecting layer resources for xref %d: %s", xref, e)

    return None


class SignatureValidityAppearance:
    """Applies Acrobat-style in-memory redrawing of Acro6 / iText layered appearances."""

    @staticmethod
    def state_of(trust_status: SignatureTrustStatus) -> State:
        if trust_status == SignatureTrustStatus.TRUSTED:
            return State.VALID
        if trust_status == SignatureTrustStatus.UNTRUSTED:
            return State.UNKNOWN
        return State.INVALID

    @staticmethod
    def caption_of(state: State) -> str:
        if state == State.VALID:
            return "Signature valid"
        if state == State.UNKNOWN:
            return "Validity unknown"
        return "Signature invalid"

    @classmethod
    def apply(
        cls,
        doc: pymupdf.Document,
        signatures: list[SignatureInfo],
    ) -> set[str]:
        """Redraw the validity layers of every signed widget in memory.

        Returns the set of field_names whose on-page appearance was redrawn.
        """
        handled_fields: set[str] = set()
        if doc is None or doc.is_closed or not signatures:
            return handled_fields

        # Map field names to their SignatureInfo
        sig_map = {s.field_name: s for s in signatures if s.field_name}

        try:
            for page in doc:
                for widget in page.widgets():
                    field_name = widget.field_name or ""
                    sig_info = sig_map.get(field_name)
                    if not sig_info:
                        continue

                    ap_type, ap_val = doc.xref_get_key(widget.xref, "AP")
                    if ap_type == "null":
                        continue

                    m_n = re.search(r"/N\s+(\d+)\s+0\s+R", ap_val)
                    if not m_n:
                        continue
                    root_xref = int(m_n.group(1))

                    layers = _find_layer_resources(doc, root_xref)
                    if not layers or "n1" not in layers or "n3" not in layers:
                        continue

                    state = cls.state_of(sig_info.trust_status)
                    n1_xref = layers.get("n1")
                    n2_xref = layers.get("n2")
                    n3_xref = layers.get("n3")
                    n4_xref = layers.get("n4")

                    b1 = _box(doc, n1_xref) if n1_xref else [0, 0, 100, 100]
                    b3 = _box(doc, n3_xref) if n3_xref else [0, 0, 100, 100]
                    b4 = _box(doc, n4_xref) if n4_xref else [0, 0, 100, 100]
                    b2 = _box(doc, n2_xref) if n2_xref else None

                    if state == State.VALID:
                        if n1_xref:
                            _write(doc, n1_xref, _tick(b1))
                        if n3_xref:
                            _write(doc, n3_xref, BLANK)
                    elif state == State.UNKNOWN:
                        if n1_xref:
                            _write(doc, n1_xref, _question_mark(doc, n1_xref, b1))
                        if n3_xref:
                            _write(doc, n3_xref, BLANK)
                    else:  # INVALID
                        if n1_xref:
                            _write(doc, n1_xref, BLANK)
                        if n3_xref:
                            _write(doc, n3_xref, _cross(b3))

                    if n4_xref:
                        _write(doc, n4_xref, _caption(doc, n4_xref, b4, b2, cls.caption_of(state)))

                    sig_info.is_layered = True
                    handled_fields.add(field_name)
                    logger.debug("Redrew layered signature appearance for %s to state %s", field_name, state.value)

        except Exception as e:
            logger.warning("Error applying signature validity appearances: %s", e)

        return handled_fields
