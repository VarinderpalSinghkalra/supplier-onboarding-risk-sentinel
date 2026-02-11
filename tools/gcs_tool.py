from google.cloud import storage


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

