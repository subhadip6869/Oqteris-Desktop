"""PDF optimization, compression, splitting, merging, and image conversion using pikepdf and PyMuPDF."""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional

from PIL import Image
import pikepdf
import pymupdf

from oqteris.core.exceptions import OptimizationError, PDFError

logger = logging.getLogger(__name__)


class OptimizationService:
    """Provides document optimization, page reorganization, and format conversions."""

    @staticmethod
    def compress_pdf(
        source_path: str | Path,
        target_path: str | Path,
        compress_images: bool = True,
        image_quality: int = 75,
        remove_metadata: bool = False,
    ) -> dict[str, Any]:
        """Compress PDF streams, clean unused objects, and optionally recompress embedded images."""
        src = Path(source_path).resolve()
        dst = Path(target_path).resolve()
        if not src.exists():
            raise OptimizationError(f"Source file not found: {src}")

        original_size = src.stat().st_size
        dst.parent.mkdir(parents=True, exist_ok=True)

        try:
            with pikepdf.open(src) as pdf:
                if remove_metadata:
                    if "/Metadata" in pdf.Root:
                        del pdf.Root["/Metadata"]
                    if "/PieceInfo" in pdf.Root:
                        del pdf.Root["/PieceInfo"]

                if compress_images:
                    for page in pdf.pages:
                        if "/Resources" in page and "/XObject" in page["/Resources"]:
                            xobjs = page["/Resources"]["/XObject"]
                            for name, obj in list(xobjs.items()):
                                if obj.get("/Subtype") == "/Image":
                                    try:
                                        # Attempt image recompression if uncompressed or lossy
                                        pim = pikepdf.PdfImage(obj)
                                        pil_img = pim.as_pil_image()
                                        if pil_img.mode in ("RGB", "L"):
                                            buf = io.BytesIO()
                                            pil_img.save(buf, format="JPEG", quality=image_quality, optimize=True)
                                            buf.seek(0)
                                            new_img = pikepdf.PdfImage.from_pil(
                                                pdf,
                                                Image.open(buf),
                                            )
                                            xobjs[name] = new_img.as_pdf_object()
                                    except Exception:
                                        pass

                # Save with maximum linear compression and garbage collection
                pdf.save(
                    dst,
                    compress_streams=True,
                    object_stream_mode=pikepdf.ObjectStreamMode.generate,
                    recompress_flate=True,
                )

            new_size = dst.stat().st_size
            saved_bytes = max(0, original_size - new_size)
            ratio = round((1.0 - (new_size / original_size)) * 100, 1) if original_size > 0 else 0.0

            return {
                "originalSize": original_size,
                "compressedSize": new_size,
                "savedBytes": saved_bytes,
                "compressionRatio": ratio,
            }
        except Exception as e:
            logger.error("Failed to compress PDF %s: %s", src, e)
            if dst.exists():
                dst.unlink(missing_ok=True)
            raise OptimizationError(f"Optimization failed: {e}")

    @staticmethod
    def merge_pdfs(input_paths: list[str | Path], output_path: str | Path) -> Path:
        """Merge multiple PDF documents into a single document."""
        out = Path(output_path).resolve()
        if len(input_paths) < 2:
            raise PDFError("At least two PDF files are required to merge.")

        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            merged = pikepdf.new()
            for p in input_paths:
                file_path = Path(p).resolve()
                if not file_path.exists():
                    raise PDFError(f"File not found: {file_path}")
                with pikepdf.open(file_path) as src_pdf:
                    merged.pages.extend(src_pdf.pages)

            merged.save(out)
            merged.close()
            logger.info("Merged %d PDFs into %s", len(input_paths), out)
            return out
        except Exception as e:
            logger.error("Failed merging PDFs: %s", e)
            if out.exists():
                out.unlink(missing_ok=True)
            raise PDFError(f"Merge operation failed: {e}")

    @staticmethod
    def split_pdf(source_path: str | Path, output_dir: str | Path, pages_per_file: int = 1) -> list[Path]:
        """Split a PDF into multiple documents with N pages per file."""
        src = Path(source_path).resolve()
        out_dir = Path(output_dir).resolve()
        if not src.exists():
            raise PDFError(f"Source file not found: {src}")

        out_dir.mkdir(parents=True, exist_ok=True)
        output_files: list[Path] = []

        try:
            with pikepdf.open(src) as pdf:
                total_pages = len(pdf.pages)
                stem = src.stem

                file_counter = 1
                for i in range(0, total_pages, pages_per_file):
                    chunk_pdf = pikepdf.new()
                    chunk_pages = pdf.pages[i : i + pages_per_file]
                    chunk_pdf.pages.extend(chunk_pages)

                    out_name = f"{stem}_part{file_counter}.pdf"
                    chunk_path = out_dir / out_name
                    chunk_pdf.save(chunk_path)
                    chunk_pdf.close()
                    output_files.append(chunk_path)
                    file_counter += 1

            return output_files
        except Exception as e:
            logger.error("Failed splitting PDF: %s", e)
            raise PDFError(f"Split operation failed: {e}")

    @staticmethod
    def extract_pages(source_path: str | Path, output_path: str | Path, page_indices: list[int]) -> Path:
        """Extract a specific subset of pages into a new PDF document."""
        src = Path(source_path).resolve()
        dst = Path(output_path).resolve()
        if not src.exists():
            raise PDFError(f"Source file not found: {src}")

        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            with pikepdf.open(src) as pdf:
                extracted = pikepdf.new()
                for p_idx in page_indices:
                    if 0 <= p_idx < len(pdf.pages):
                        extracted.pages.append(pdf.pages[p_idx])

                extracted.save(dst)
                extracted.close()
            return dst
        except Exception as e:
            logger.error("Failed extracting pages: %s", e)
            if dst.exists():
                dst.unlink(missing_ok=True)
            raise PDFError(f"Page extraction failed: {e}")

    @staticmethod
    def images_to_pdf(image_paths: list[str | Path], output_path: str | Path) -> Path:
        """Convert a sequence of images into a single PDF document."""
        out = Path(output_path).resolve()
        if not image_paths:
            raise PDFError("No image files provided.")

        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            doc = pymupdf.open()
            for img_path in image_paths:
                p = Path(img_path).resolve()
                if not p.exists():
                    continue

                img_doc = pymupdf.open(str(p))
                pdf_bytes = img_doc.convert_to_pdf()
                img_doc.close()

                img_pdf = pymupdf.open("pdf", pdf_bytes)
                doc.insert_pdf(img_pdf)
                img_pdf.close()

            doc.save(str(out), deflate=True)
            doc.close()
            return out
        except Exception as e:
            logger.error("Failed converting images to PDF: %s", e)
            if out.exists():
                out.unlink(missing_ok=True)
            raise PDFError(f"Image conversion failed: {e}")

    @staticmethod
    def export_pages_as_images(
        document: Any,
        output_dir: str | Path,
        image_format: str = "png",
        dpi: int = 200,
        page_range: list[int] | None = None,
    ) -> list[Path]:
        """Export pages of an open PDF document as standalone image files."""
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        exported: list[Path] = []

        raw_doc = document.raw_doc if hasattr(document, "raw_doc") else document
        if not raw_doc:
            return exported

        total_pages = len(raw_doc)
        pages = page_range if page_range is not None else list(range(total_pages))

        stem = Path(document.file_path).stem if hasattr(document, "file_path") and document.file_path else "page"

        for p_idx in pages:
            if 0 <= p_idx < total_pages:
                page = raw_doc[p_idx]
                pix = page.get_pixmap(dpi=dpi)
                out_file = out_dir / f"{stem}_page_{p_idx + 1}.{image_format.lower()}"
                pix.save(str(out_file))
                exported.append(out_file)

        return exported
