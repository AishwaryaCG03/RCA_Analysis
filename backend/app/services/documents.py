import fitz  # PyMuPDF


class DocumentExtractionError(ValueError):
    pass


def extract_pdf_text(data: bytes) -> str:
    try:
        document = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise DocumentExtractionError("The uploaded file is not a readable PDF.") from exc
    try:
        text = "\n".join(page.get_text("text") for page in document)
    finally:
        document.close()
    cleaned = text.strip()
    if not cleaned:
        raise DocumentExtractionError(
            "No readable text was found. This may be a scanned PDF; please supply OCR text or paste the report."
        )
    return cleaned
