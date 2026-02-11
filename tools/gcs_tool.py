import json
import time
from google.cloud import storage


# -----------------------------------------
# CONTRACT DOCUMENT UPLOAD (Existing)
# -----------------------------------------
def upload_approved_document(
    supplier_id: str,
    document_type: str,
    filename: str,
    file_bytes: bytes,
    content_type: str = "application/pdf",
    content_disposition: str = None
) -> str:

    client = storage.Client()
    bucket = client.bucket("contracts-demo-277069041958")

    destination_path = f"{supplier_id}/{document_type}/{filename}"
    blob = bucket.blob(destination_path)

    blob.upload_from_string(file_bytes, content_type=content_type)

    if content_disposition:
        blob.content_disposition = content_disposition
        blob.patch()

    return f"gs://{bucket.name}/{destination_path}"


# -----------------------------------------
# 🔥 QUOTATION UPLOAD (New Logic)
# -----------------------------------------
def upload_quotation(
    rfq_id: str,
    supplier_name: str,
    quotation_data: dict
) -> str:
    """
    Stores supplier quotation JSON in:
    supplier-onboarding-risk-sentinel bucket
    """

    client = storage.Client()
    bucket = client.bucket("supplier-onboarding-risk-sentinel")

    timestamp = int(time.time())

    # Clean supplier name for safe file naming
    safe_supplier = supplier_name.replace(" ", "_").upper()

    destination_path = (
        f"quotations/{rfq_id}/"
        f"{safe_supplier}_{timestamp}.json"
    )

    blob = bucket.blob(destination_path)

    blob.upload_from_string(
        json.dumps(quotation_data, indent=2),
        content_type="application/json"
    )

    return f"gs://{bucket.name}/{destination_path}"
