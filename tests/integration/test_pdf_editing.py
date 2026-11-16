"""Integration tests for text insertion, text editing, and undo/redo operations."""

from pathlib import Path
from oqteris.pdf.document.document import PDFDocument
from oqteris.pdf.editing.text_editor import TextEditorService
from oqteris.pdf.editing.undo_redo import Command, UndoRedoStack


def test_insert_text_and_verify(sample_pdf_normal: Path, temp_dir: Path):
    doc = PDFDocument(doc_id="edit_doc")
    doc.open(sample_pdf_normal)

    success = TextEditorService.insert_text(
        doc,
        page_index=0,
        point=(50, 300),
        text="New Text Inserted via Oqteris",
        font_size=14,
    )
    assert success is True
    assert doc.is_modified is True

    # Save to temp path and verify text is present
    out_pdf = temp_dir / "edited_text.pdf"
    doc.save(out_pdf)
    doc.close()

    # Reopen and check text
    doc_reopened = PDFDocument(doc_id="reopened")
    doc_reopened.open(out_pdf)
    text = doc_reopened.extract_text_page(0)
    assert "New Text Inserted via Oqteris" in text
    doc_reopened.close()


def test_undo_redo_stack():
    stack = UndoRedoStack(max_history=10)

    state = {"count": 0}

    class IncrementCommand(Command):
        def execute(self) -> bool:
            state["count"] += 1
            return True

        def undo(self) -> bool:
            state["count"] -= 1
            return True

        @property
        def name(self) -> str:
            return "Increment"

    cmd1 = IncrementCommand()
    stack.push_and_execute(cmd1)
    assert state["count"] == 1
    assert stack.can_undo is True

    stack.undo()
    assert state["count"] == 0
    assert stack.can_redo is True

    stack.redo()
    assert state["count"] == 1
