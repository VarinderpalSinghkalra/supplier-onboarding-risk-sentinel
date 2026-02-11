from google.cloud import bigquery
from datetime import datetime
import uuid


PROJECT_ID = "data-engineering-479617"
DATASET = "conversational_demo"
TABLE = "supplier_quotations"


def insert_quotation_into_bq(
    rfq_id: str,
    supplier_name: str,
    unit_price: float,
    delivery_days: int,
    quotation_gcs_uri: str,
    payment_terms: str = "NET 30",
    risk_score: int = 0
):
    """
    Inserts quotation row into BigQuery table
    matching exact schema.
    """

    client = bigquery.Client(project=PROJECT_ID)

    table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"

    # Generate supplier_id automatically if not available
    supplier_id = str(uuid.uuid4())

    row = {
        "rfq_id": rfq_id,
        "supplier_id": supplier_id,
        "supplier_name": supplier_name,
        "unit_price": float(unit_price),
        "delivery_days": int(delivery_days),
        "payment_terms": payment_terms,
        "risk_score": risk_score,
        "quotation_gcs_uri": quotation_gcs_uri,
        "created_at": datetime.utcnow().isoformat()
    }

    errors = client.insert_rows_json(table_id, [row])

    if errors:
        raise Exception(f"BigQuery insert error: {errors}")

    return supplier_id

