import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from pypdf import PdfReader, PdfWriter


def generate_w9_with_cover(
    original_w9_bytes: bytes,
    supplier_name: str
) -> bytes:
    # Create cover page
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    story = [
        Paragraph("<b>Supplier Tax Information</b>", styles["Title"]),
        Spacer(1, 20),
        Paragraph(f"<b>Supplier Name:</b> {supplier_name}", styles["Normal"]),
        Spacer(1, 10),
        Paragraph("This W-9 is provided for supplier verification and signature.", styles["Normal"])
    ]
    doc.build(story)

    cover_pdf = PdfReader(io.BytesIO(buffer.getvalue()))
    original_pdf = PdfReader(io.BytesIO(original_w9_bytes))

    writer = PdfWriter()
    writer.add_page(cover_pdf.pages[0])

    for page in original_pdf.pages:
        writer.add_page(page)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()

