from google.cloud import storage
from uuid import uuid4
from datetime import datetime

client = storage.Client()
BUCKET_NAME = "supplier-onboarding-risk-sentinel"

def store_quotation_email(
    supplier_id: str,
    rfq_id: str,
    raw_email: str,
    metadata: dict | None = None
) -> str:
    """
    Stores raw quotation email in GCS.
    This is the SYSTEM OF RECORD.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{timestamp}_{uuid4()}.eml"

    path = f"quotations/{rfq_id}/{supplier_id}/{filename}"

    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(path)

    if metadata:
        blob.metadata = metadata

    blob.upload_from_string(raw_email, content_type="message/rfc822")

    return f"gs://{BUCKET_NAME}/{path}"
