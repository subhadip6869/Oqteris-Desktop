"""Data models for PDF document metadata, page geometry, search results, and outlines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentMetadata:
    """PDF document metadata and security attributes."""

    title: str = ""
    author: str = ""
    subject: str = ""
    keywords: str = ""
    creator: str = ""
    producer: str = ""
    creation_date: str = ""
    modification_date: str = ""
    format_version: str = "PDF-1.7"
    page_count: int = 0
    is_encrypted: bool = False
    is_signed: bool = False
    can_print: bool = True
    can_modify: bool = True
    can_copy: bool = True
    can_annotate: bool = True
    file_size_bytes: int = 0
    file_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title or "Untitled",
            "author": self.author,
            "subject": self.subject,
            "keywords": self.keywords,
            "creator": self.creator,
            "producer": self.producer,
            "creationDate": self.creation_date,
            "modificationDate": self.modification_date,
            "formatVersion": self.format_version,
            "pageCount": self.page_count,
            "isEncrypted": self.is_encrypted,
            "isSigned": self.is_signed,
            "canPrint": self.can_print,
            "canModify": self.can_modify,
            "canCopy": self.can_copy,
            "canAnnotate": self.can_annotate,
            "fileSizeBytes": self.file_size_bytes,
            "filePath": self.file_path,
        }


@dataclass
class PageGeometry:
    """Page dimensions and orientation."""

    page_index: int
    width: float
    height: float
    rotation: int = 0  # 0, 90, 180, 270

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height > 0 else 1.0


@dataclass
class OutlineItem:
    """PDF bookmark / Table of Contents entry."""

    title: str
    page_index: int
    level: int = 1
    dest: dict[str, Any] = field(default_factory=dict)
    children: list[OutlineItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "pageIndex": self.page_index,
            "level": self.level,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class SearchMatch:
    """Search match instance on a specific page with normalized bounding boxes."""

    page_index: int
    rects: list[list[float]]  # list of [x0, y0, x1, y1]
    snippet: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "pageIndex": self.page_index,
            "rects": self.rects,
            "snippet": self.snippet,
        }


@dataclass
class ExtractedImageInfo:
    """Information about an embedded image inside a PDF page."""

    image_index: int
    page_index: int
    width: int
    height: int
    format: str
    size_bytes: int
    xref: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "imageIndex": self.image_index,
            "pageIndex": self.page_index,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "sizeBytes": self.size_bytes,
            "xref": self.xref,
        }
