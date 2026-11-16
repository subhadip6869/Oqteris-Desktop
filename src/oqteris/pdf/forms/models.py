"""Data models for AcroForm fields in PDF documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class FormFieldType(str, Enum):
    TEXT = "text"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    CHOICE = "choice"  # ComboBox / ListBox
    SIGNATURE = "signature"
    BUTTON = "button"
    UNKNOWN = "unknown"


@dataclass
class FormFieldInfo:
    """Detailed metadata and current value of a PDF form field."""

    field_name: str
    field_type: FormFieldType
    page_index: int
    rect: list[float]  # [x0, y0, x1, y1]
    value: Any = None
    default_value: Any = None
    options: list[str] = field(default_factory=list)  # For Choice/Combo fields
    is_read_only: bool = False
    is_required: bool = False
    tooltip: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.field_name,
            "type": self.field_type.value,
            "pageIndex": self.page_index,
            "rect": self.rect,
            "value": str(self.value) if self.value is not None else "",
            "defaultValue": str(self.default_value) if self.default_value is not None else "",
            "options": self.options,
            "isReadOnly": self.is_read_only,
            "isRequired": self.is_required,
            "tooltip": self.tooltip,
        }
