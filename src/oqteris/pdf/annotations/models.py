"""Data models and enums for PDF annotations."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class AnnotationType(str, Enum):
    HIGHLIGHT = "highlight"
    UNDERLINE = "underline"
    STRIKEOUT = "strikeout"
    NOTE = "note"
    INK = "ink"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    LINE = "line"
    ARROW = "arrow"
    STAMP = "stamp"
    TEXT = "text"
    LINK = "link"


@dataclass
class AnnotationData:
    """Represents a PDF annotation item."""

    annot_id: str
    page_index: int
    annot_type: AnnotationType
    rect: list[float]  # [x0, y0, x1, y1]
    content: str = ""
    author: str = ""
    color_rgb: list[float] = field(default_factory=lambda: [1.0, 1.0, 0.0])  # normalized 0.0 - 1.0
    fill_rgb: Optional[list[float]] = None
    opacity: float = 1.0
    stroke_width: float = 1.5
    points: list[list[list[float]]] = field(default_factory=list)  # For ink drawings
    creation_date: str = ""
    modification_date: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.annot_id,
            "pageIndex": self.page_index,
            "type": self.annot_type.value,
            "rect": self.rect,
            "content": self.content,
            "author": self.author,
            "color": self.color_rgb,
            "fill": self.fill_rgb,
            "opacity": self.opacity,
            "strokeWidth": self.stroke_width,
            "points": self.points,
            "creationDate": self.creation_date,
            "modificationDate": self.modification_date,
        }
