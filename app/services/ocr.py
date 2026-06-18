from pathlib import Path


def image_to_text(image_path: Path, lang: str = "rus+eng") -> str:
    try:
        import pytesseract
    except ImportError as exc:
        raise RuntimeError("Install pytesseract and system tesseract to enable OCR.") from exc

    return pytesseract.image_to_string(str(image_path), lang=lang)
