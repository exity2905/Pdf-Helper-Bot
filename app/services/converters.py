from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from xml.sax.saxutils import escape
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

from pypdf import PdfReader


class ConversionError(RuntimeError):
    pass


def pdf_to_word(input_path: Path, output_path: Path) -> Path:
    pages = _extract_pdf_text_pages(input_path)
    if not pages:
        raise ConversionError(
            "В PDF не найден текстовый слой. Если это скан или фото, сначала нужен OCR."
        )

    _write_text_docx(output_path, pages)
    return output_path


def word_to_pdf(input_path: Path, output_path: Path) -> Path:
    if input_path.suffix.lower() == ".docx":
        with tempfile.TemporaryDirectory(prefix="pdf-helper-docx-") as temp_dir:
            prepared_path = Path(temp_dir) / input_path.name
            try:
                _prepare_docx_for_pdf(input_path, prepared_path)
                return _convert_with_libreoffice(
                    prepared_path,
                    output_path,
                    "pdf:writer_pdf_Export",
                    ".pdf",
                )
            except (BadZipFile, OSError, UnicodeDecodeError):
                pass

    return _convert_with_libreoffice(input_path, output_path, "pdf:writer_pdf_Export", ".pdf")


def _prepare_docx_for_pdf(input_path: Path, output_path: Path) -> None:
    with ZipFile(input_path) as source, ZipFile(output_path, "w", ZIP_DEFLATED) as target:
        for item in source.infolist():
            content = source.read(item.filename)
            if _is_word_xml_part(item.filename):
                content = _relax_table_row_heights(content)
            target.writestr(item, content)


def _is_word_xml_part(filename: str) -> bool:
    return filename.startswith("word/") and filename.endswith(".xml")


def _relax_table_row_heights(content: bytes) -> bytes:
    text = content.decode("utf-8")
    text = re.sub(r"<w:trHeight\b[^>]*/>", "", text)
    return text.encode("utf-8")


def _extract_pdf_text_pages(input_path: Path) -> list[str]:
    try:
        reader = PdfReader(str(input_path))
    except Exception as exc:
        raise ConversionError(f"Не удалось прочитать PDF: {exc}") from exc

    pages = []

    for page in reader.pages:
        try:
            text = (page.extract_text() or "").strip()
        except Exception:
            text = ""
        if text:
            pages.append(text)

    return pages


def _write_text_docx(output_path: Path, pages: list[str]) -> None:
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    paragraphs = []
    for page_index, page_text in enumerate(pages):
        if len(pages) > 1:
            paragraphs.append(_docx_paragraph(f"Страница {page_index + 1}"))

        for line in page_text.splitlines():
            line = line.strip()
            if line:
                paragraphs.append(_docx_paragraph(line))

        if page_index < len(pages) - 1:
            paragraphs.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        f"{''.join(paragraphs)}"
        '<w:sectPr>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="708" w:footer="708" w:gutter="0"/>'
        "</w:sectPr>"
        "</w:body>"
        "</w:document>"
    )

    with ZipFile(output_path, "w", ZIP_DEFLATED) as docx:
        docx.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>",
        )
        docx.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>",
        )
        docx.writestr("word/document.xml", document_xml)


def _docx_paragraph(text: str) -> str:
    return (
        "<w:p>"
        "<w:r>"
        f'<w:t xml:space="preserve">{escape(text)}</w:t>'
        "</w:r>"
        "</w:p>"
    )


def _convert_with_libreoffice(
    input_path: Path,
    output_path: Path,
    target_format: str,
    target_suffix: str,
) -> Path:
    soffice = _find_soffice()
    input_path = input_path.resolve()
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        output_path.unlink()

    produced_path = output_path.parent / f"{input_path.stem}{target_suffix}"
    if produced_path != output_path and produced_path.exists():
        produced_path.unlink()

    with tempfile.TemporaryDirectory(prefix="pdf-helper-lo-") as profile_dir:
        command = [
            soffice,
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            f"-env:UserInstallation={Path(profile_dir).as_uri()}",
            "--convert-to",
            target_format,
            "--outdir",
            str(output_path.parent),
            str(input_path),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

    if result.returncode != 0 or not produced_path.exists():
        details = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
        raise ConversionError(details or "LibreOffice conversion failed.")

    if produced_path != output_path:
        produced_path.replace(output_path)

    return output_path


def _find_soffice() -> str:
    soffice = shutil.which("soffice")
    if soffice:
        return soffice

    macos_path = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    if macos_path.exists():
        return str(macos_path)

    raise ConversionError("LibreOffice is not installed or soffice is not available.")
