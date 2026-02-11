from google.cloud import firestore

db = firestore.Client()

# -----------------------------
# SUPPLIER MASTER (MDM)
# -----------------------------

def create_supplier_master(supplier_id: str, data: dict):
    """
    Idempotent write for supplier master (safe on retries).
    """
    db.collection("supplier_master") \
      .document(supplier_id) \
      .set(data, merge=True)


def find_supplier_by_match_key(match_key: str):
    docs = (
        db.collection("supplier_master")
        .where("match_key", "==", match_key)
        .limit(1)
        .stream()
    )
    for doc in docs:
        return doc.to_dict()
    return None


# -----------------------------
# SUPPLIERS (LIFECYCLE)
# -----------------------------

def create_supplier(supplier_id: str, data: dict):
    """
    Idempotent supplier lifecycle creation.
    """
    db.collection("suppliers") \
      .document(supplier_id) \
      .set(data, merge=True)


def update_supplier(supplier_id: str, data: dict):
    """
    Safe update (never crashes if doc exists / not exists).
    """
    db.collection("suppliers") \
      .document(supplier_id) \
      .set(data, merge=True)


# -----------------------------
# APPROVED DOCUMENT METADATA
# -----------------------------

def add_approved_document(
    supplier_id: str,
    document_type: str,
    gcs_uri: str
):
    db.collection("suppliers") \
      .document(supplier_id) \
      .set(
        {
            "approved_documents": {
                document_type: gcs_uri
            }
        },
        merge=True
      )

