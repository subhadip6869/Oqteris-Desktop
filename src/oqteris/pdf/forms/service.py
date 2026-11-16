"""PDF Form management service supporting AcroForms inspection, filling, and resetting."""

from __future__ import annotations

import logging
from typing import Any, Optional

import pymupdf

from oqteris.core.exceptions import PDFError
from oqteris.pdf.document.document import PDFDocument
from oqteris.pdf.forms.models import FormFieldInfo, FormFieldType

logger = logging.getLogger(__name__)


class FormService:
    """Provides AcroForm field detection, reading, updating, and resetting."""

    @staticmethod
    def get_fields_for_page(document: PDFDocument, page_index: int) -> list[FormFieldInfo]:
        """Detect all form fields on a specific page."""
        fields: list[FormFieldInfo] = []
        if not document.is_open or not (0 <= page_index < document.page_count):
            return fields

        raw_doc = document.raw_doc
        if raw_doc is None:
            return fields

        try:
            page = raw_doc[page_index]
            for widget in page.widgets():
                ftype = FormService._map_field_type(widget.field_type)
                rect = [float(widget.rect.x0), float(widget.rect.y0), float(widget.rect.x1), float(widget.rect.y1)]

                options = []
                if hasattr(widget, "choice_values") and widget.choice_values:
                    options = [str(opt) for opt in widget.choice_values]

                fields.append(
                    FormFieldInfo(
                        field_name=widget.field_name or f"Field_{widget.xref}",
                        field_type=ftype,
                        page_index=page_index,
                        rect=rect,
                        value=widget.field_value,
                        default_value=getattr(widget, "default_value", None),
                        options=options,
                        is_read_only=bool(widget.field_flags & pymupdf.PDF_FIELD_IS_READ_ONLY),
                        is_required=bool(widget.field_flags & pymupdf.PDF_FIELD_IS_REQUIRED),
                        tooltip=widget.field_label or "",
                    )
                )
        except Exception as e:
            logger.error("Error reading form fields on page %d: %s", page_index, e)

        return fields

    @staticmethod
    def get_all_fields(document: PDFDocument) -> list[FormFieldInfo]:
        """Scan all pages and return all detected form fields."""
        all_fields: list[FormFieldInfo] = []
        for p in range(document.page_count):
            all_fields.extend(FormService.get_fields_for_page(document, p))
        return all_fields

    @staticmethod
    def set_field_value(
        document: PDFDocument,
        page_index: int,
        field_name: str,
        value: Any,
    ) -> bool:
        """Update the value of an AcroForm field."""
        if not document.is_open or not (0 <= page_index < document.page_count):
            return False

        try:
            page = document.raw_doc[page_index]
            for widget in page.widgets():
                if widget.field_name == field_name:
                    if widget.field_flags & pymupdf.PDF_FIELD_IS_READ_ONLY:
                        logger.warning("Field '%s' is read-only.", field_name)
                        return False

                    widget.field_value = str(value)
                    widget.update()
                    document.is_modified = True
                    return True
        except Exception as e:
            logger.error("Failed to set form field value for '%s': %s", field_name, e)

        return False

    @staticmethod
    def reset_all_fields(document: PDFDocument) -> bool:
        """Reset all form fields in the document to their default values or empty state."""
        if not document.is_open:
            return False

        try:
            for page in document.raw_doc:
                for widget in page.widgets():
                    def_val = getattr(widget, "default_value", "") or ""
                    widget.field_value = def_val
                    widget.update()
            document.is_modified = True
            return True
        except Exception as e:
            logger.error("Failed to reset form fields: %s", e)
            return False

    @staticmethod
    def _map_field_type(raw_type: int) -> FormFieldType:
        mapping = {
            pymupdf.PDF_WIDGET_TYPE_TEXT: FormFieldType.TEXT,
            pymupdf.PDF_WIDGET_TYPE_CHECKBOX: FormFieldType.CHECKBOX,
            pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON: FormFieldType.RADIO,
            pymupdf.PDF_WIDGET_TYPE_LISTBOX: FormFieldType.CHOICE,
            pymupdf.PDF_WIDGET_TYPE_COMBOBOX: FormFieldType.CHOICE,
            pymupdf.PDF_WIDGET_TYPE_SIGNATURE: FormFieldType.SIGNATURE,
            pymupdf.PDF_WIDGET_TYPE_BUTTON: FormFieldType.BUTTON,
        }
        return mapping.get(raw_type, FormFieldType.UNKNOWN)
