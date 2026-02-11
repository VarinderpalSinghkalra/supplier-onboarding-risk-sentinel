import io
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PyPdfError


def generate_prefilled_w9(
    template_bytes: bytes,
    supplier_name: str,
    supplier_type: str = "COMPANY"
) -> bytes:
    """
    Attempts to prefill a W-9.
    If PDF is NOT fillable, returns original PDF safely.
    """

    reader = PdfReader(io.BytesIO(template_bytes))
    writer = PdfWriter()

    # ❗ If PDF has no AcroForm, DO NOT try to edit
    if "/AcroForm" not in reader.trailer["/Root"]:
        # Return original PDF untouched
        return template_bytes

    page = reader.pages[0]
    writer.add_page(page)

    try:
        writer.update_page_form_field_values(
            page,
            {
                "f1_01": supplier_name,
                "f1_02": supplier_name
            }
        )
    except PyPdfError:
        # Safety fallback
        return template_bytes

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()

