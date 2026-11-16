"""Integration tests for PDF optimization, merging, splitting, and conversions."""

from pathlib import Path
from PIL import Image
import fitz
from oqteris.pdf.optimisation.service import OptimizationService


def test_merge_and_split_pdfs(sample_pdf_normal: Path, temp_dir: Path):
    # 1. Merge
    merged_path = temp_dir / "merged.pdf"
    OptimizationService.merge_pdfs([sample_pdf_normal, sample_pdf_normal], merged_path)
    assert merged_path.exists()

    doc_m = fitz.open(str(merged_path))
    assert len(doc_m) == 4  # 2 + 2
    doc_m.close()

    # 2. Split
    split_dir = temp_dir / "split_output"
    parts = OptimizationService.split_pdf(merged_path, split_dir, pages_per_file=2)
    assert len(parts) == 2


def test_extract_pages(sample_pdf_normal: Path, temp_dir: Path):
    extracted_path = temp_dir / "extracted_p1.pdf"
    OptimizationService.extract_pages(sample_pdf_normal, extracted_path, [0])
    assert extracted_path.exists()

    doc_e = fitz.open(str(extracted_path))
    assert len(doc_e) == 1
    doc_e.close()


def test_images_to_pdf_and_export(temp_dir: Path):
    # Create test image
    img_path = temp_dir / "test_img.png"
    img = Image.new("RGB", (200, 200), color="blue")
    img.save(img_path)

    # Images to PDF
    pdf_from_img = temp_dir / "from_images.pdf"
    OptimizationService.images_to_pdf([img_path], pdf_from_img)
    assert pdf_from_img.exists()

    doc = fitz.open(str(pdf_from_img))
    assert len(doc) == 1

    # Export pages as images
    export_dir = temp_dir / "exported_imgs"
    exported = OptimizationService.export_pages_as_images(doc, export_dir, image_format="png", dpi=150)
    assert len(exported) == 1
    assert exported[0].exists()

    doc.close()


def test_compress_pdf(sample_pdf_normal: Path, temp_dir: Path):
    compressed_path = temp_dir / "compressed.pdf"
    res = OptimizationService.compress_pdf(sample_pdf_normal, compressed_path)
    assert compressed_path.exists()
    assert "originalSize" in res
    assert "compressedSize" in res
