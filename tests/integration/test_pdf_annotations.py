"""Integration tests for PDF annotations: highlights, notes, drawings, shapes, and stamps."""

from pathlib import Path
from oqteris.pdf.annotations.manager import AnnotationService
from oqteris.pdf.annotations.models import AnnotationType
from oqteris.pdf.document.document import PDFDocument


def test_add_and_delete_annotations(sample_pdf_normal: Path):
    doc = PDFDocument(doc_id="annot_doc")
    doc.open(sample_pdf_normal)

    # 1. Add Highlight
    h_ok = AnnotationService.add_highlight(doc, 0, [[50, 100, 200, 120]])
    assert h_ok is True

    # 2. Add Sticky Note
    n_ok = AnnotationService.add_sticky_note(doc, 0, (100, 200), "Review this section", "Reviewer")
    assert n_ok is True

    # 3. Add Freehand Ink
    ink_ok = AnnotationService.add_ink(doc, 0, [[[10, 10], [20, 20], [30, 25]]])
    assert ink_ok is True

    # 4. Add Rectangle Shape
    shape_ok = AnnotationService.add_shape(doc, 0, "rectangle", [100, 150, 300, 250])
    assert shape_ok is True

    # 5. Add Stamp
    stamp_ok = AnnotationService.add_stamp(doc, 0, [50, 50, 200, 100], "APPROVED")
    assert stamp_ok is True

    # Verify annotations list
    annots = AnnotationService.get_annotations_for_page(doc, 0)
    assert len(annots) >= 5

    # Delete first annotation
    del_ok = AnnotationService.delete_annotation(doc, 0, 0)
    assert del_ok is True

    doc.close()
