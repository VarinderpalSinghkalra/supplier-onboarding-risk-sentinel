from google.cloud import bigquery

# -------------------------------
# CONFIG
# -------------------------------
BQ_DATASET = "support_agent"
BQ_TABLE = "supplier_quotations"

PRICE_WEIGHT = 0.4
DELIVERY_WEIGHT = 0.3
RISK_WEIGHT = 0.3

bq_client = bigquery.Client()


# -------------------------------
# SUPPLIER-LEVEL ADVISORY
# -------------------------------
def commercial_suggestion(payload: dict) -> dict:
    return {
        "suggested_action": "NEGOTIATE",
        "reason": "Quotation received; awaiting RFQ-level comparison"
    }


# -------------------------------
# RFQ-LEVEL NEGOTIATION
# -------------------------------
def negotiate_rfq(payload: dict) -> dict:
    try:
        rfq_id = payload.get("rfq_id")

        if not rfq_id:
            return {
                "status": "ERROR",
                "message": "rfq_id missing"
            }

        print(f"🔎 Running negotiation for RFQ: {rfq_id}")

        query = f"""
            SELECT
                supplier_id,
                supplier_name,
                unit_price,
                delivery_days,
                IFNULL(risk_score, 50) AS risk_score
            FROM `{bq_client.project}.{BQ_DATASET}.{BQ_TABLE}`
            WHERE rfq_id = @rfq_id
        """

        job = bq_client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("rfq_id", "STRING", rfq_id)
                ]
            ),
        )

        rows = list(job)

        print(f"📊 Quotes fetched: {len(rows)}")

        if len(rows) < 2:
            return {
                "status": "INSUFFICIENT_QUOTES",
                "quotes_received": len(rows),
                "message": "At least two quotations required"
            }

        scored = []

        for r in rows:
            try:
                unit_price = float(r.unit_price or 0)
                delivery_days = float(r.delivery_days or 0)
                risk_score = float(r.risk_score or 50)

                score = (
                    (unit_price * PRICE_WEIGHT) +
                    (delivery_days * DELIVERY_WEIGHT) +
                    (risk_score * RISK_WEIGHT)
                )

                scored.append({
                    "supplier_id": r.supplier_id,
                    "supplier_name": r.supplier_name,
                    "unit_price": unit_price,
                    "delivery_days": delivery_days,
                    "risk_score": risk_score,
                    "score": round(score, 2)
                })

            except Exception as row_error:
                print("⚠️ Row scoring error:", str(row_error))

        if not scored:
            return {
                "status": "NEGOTIATION_ENGINE_ERROR",
                "message": "No valid quotations available for scoring"
            }

        best = sorted(scored, key=lambda x: x["score"])[0]

        print(f"🏆 Recommended supplier: {best['supplier_name']}")

        return {
            "status": "NEGOTIATION_READY",
            "recommended_supplier": best["supplier_id"],
            "recommended_supplier_name": best["supplier_name"],
            "approval_payload": {
                "recommended_vendor": best["supplier_name"],
                "rationale": "Best weighted score across price, delivery, and risk",
                "alternatives": [
                    s for s in scored
                    if s["supplier_id"] != best["supplier_id"]
                ]
            }
        }

    except Exception as e:
        print("🔥 Negotiation engine crashed:", str(e))
        return {
            "status": "NEGOTIATION_ENGINE_ERROR",
            "message": str(e)
        }
