from pathlib import Path

from pypdf import PdfReader, PdfWriter


def compress_pdf(input_path: Path, output_path: Path) -> Path:
    reader = PdfReader(str(input_path))
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as output_file:
        writer.write(output_file)

    return output_path


def split_pdf(input_path: Path, output_dir: Path) -> list[Path]:
    reader = PdfReader(str(input_path))
    output_dir.mkdir(parents=True, exist_ok=True)
    pages: list[Path] = []

    for index, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        page_path = output_dir / f"page_{index:03}.pdf"
        with page_path.open("wb") as output_file:
            writer.write(output_file)
        pages.append(page_path)

    return pages


def extract_pdf_text(input_path: Path) -> str:
    reader = PdfReader(str(input_path))
    chunks = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            chunks.append(f"--- Page {index} ---\n{text}")

    return "\n\n".join(chunks)
