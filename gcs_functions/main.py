import re
from datetime import datetime, timezone

from google.cloud import bigquery
from google.cloud import storage
from google.cloud import firestore

# -------------------------------
# CONFIG
# -------------------------------
BQ_DATASET = "conversational_demo"
BQ_TABLE = "supplier_quotations"

bq_client = bigquery.Client()
storage_client = storage.Client()
fs_client = firestore.Client()


# -------------------------------
# Helpers
# -------------------------------
def _extract(pattern: str, text: str, cast=str):
    """
    Extract first capture group safely.
    """
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    return cast(match.group(1))


# --------------------------------------------------
# ENTRY POINT — GCS EVENT
# --------------------------------------------------
def quotation_gcs_to_bq(event, context):
    bucket_name = event["bucket"]
    object_name = event["name"]

    # Only process quotation emails
    if not object_name.startswith("quotations/") or not object_name.endswith(".eml"):
        print("Skipping non-quotation object:", object_name)
        return

    print(f"📩 Processing quotation: gs://{bucket_name}/{object_name}")

    # --------------------------------------------------
    # Read email
    # --------------------------------------------------
    blob = storage_client.bucket(bucket_name).blob(object_name)
    email_text = blob.download_as_text()

    # --------------------------------------------------
    # Extract RFQ + supplier from path
    # quotations/{rfq_id}/{supplier_id}/file.eml
    # --------------------------------------------------
    try:
        _, rfq_id, supplier_id, _ = object_name.split("/", 3)
    except ValueError:
        raise RuntimeError(f"Invalid quotation path: {object_name}")

    # --------------------------------------------------
    # Parse email body (SAFE REGEX)
    # --------------------------------------------------
    unit_price = _extract(r"(?:PRICE|UNIT_PRICE):\s*(\d+)", email_text, float)
    delivery_days = _extract(r"DELIVERY_DAYS:\s*(\d+)", email_text, int)
    payment_terms = _extract(r"PAYMENT_TERMS:\s*(.+)", email_text)

    # --------------------------------------------------
    # 🔍 Enrich from Firestore (SOURCE OF TRUTH)
    # --------------------------------------------------
    supplier_doc = fs_client.collection("suppliers").document(supplier_id).get()

    supplier_name = None
    risk_score = None

    if supplier_doc.exists:
        supplier_data = supplier_doc.to_dict()
        supplier_name = supplier_data.get("name")
        risk_score = supplier_data.get("risk_score")

    # --------------------------------------------------
    # Build BigQuery row (MATCHES SCHEMA EXACTLY)
    # --------------------------------------------------
    row = {
        "rfq_id": rfq_id,
        "supplier_id": supplier_id,
        "supplier_name": supplier_name,
        "unit_price": unit_price,
        "delivery_days": delivery_days,
        "payment_terms": payment_terms,
        "risk_score": risk_score,
        "quotation_gcs_uri": f"gs://{bucket_name}/{object_name}",
        "created_at": datetime.now(timezone.utc).isoformat(),  # JSON-safe
    }

    print("📊 BQ row prepared:", row)

    table_id = f"{bq_client.project}.{BQ_DATASET}.{BQ_TABLE}"

    errors = bq_client.insert_rows_json(table_id, [row])
    if errors:
        raise RuntimeError(f"❌ BigQuery insert failed: {errors}")

    print("✅ Quotation successfully inserted into BigQuery")
