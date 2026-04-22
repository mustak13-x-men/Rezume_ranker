import pdfplumber
import docx


def extract_text_from_pdf(path: str) -> str:
    """Extract all text from a PDF file using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


def extract_text_from_docx(path: str) -> str:
    """Extract text from a DOCX using python-docx."""
    text = ""
    try:
        doc = docx.Document(path)
        paragraphs = [p.text for p in doc.paragraphs]
        text = "\n".join(paragraphs)
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text
