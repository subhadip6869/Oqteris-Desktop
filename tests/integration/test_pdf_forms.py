"""Integration tests for PDF AcroForm detection, reading, updating, and resetting."""

from pathlib import Path
from oqteris.pdf.document.document import PDFDocument
from oqteris.pdf.forms.models import FormFieldType
from oqteris.pdf.forms.service import FormService


def test_acroforms_detection_and_filling(sample_pdf_form: Path, temp_dir: Path):
    doc = PDFDocument(doc_id="form_doc")
    doc.open(sample_pdf_form)

    fields = FormService.get_all_fields(doc)
    assert len(fields) >= 2

    # Verify text field
    name_field = next(f for f in fields if f.field_name == "fullName")
    assert name_field.field_type == FormFieldType.TEXT
    assert name_field.value == "John Doe"

    # Update text field value
    update_ok = FormService.set_field_value(doc, 0, "fullName", "Jane Smith")
    assert update_ok is True
    assert doc.is_modified is True

    # Save filled form and re-read
    out_form = temp_dir / "filled_form.pdf"
    doc.save(out_form)
    doc.close()

    doc_reopened = PDFDocument(doc_id="reopened_form")
    doc_reopened.open(out_form)
    reopened_fields = FormService.get_all_fields(doc_reopened)
    updated_name = next(f for f in reopened_fields if f.field_name == "fullName")
    assert updated_name.value == "Jane Smith"

    # Test reset fields
    reset_ok = FormService.reset_all_fields(doc_reopened)
    assert reset_ok is True

    doc_reopened.close()
