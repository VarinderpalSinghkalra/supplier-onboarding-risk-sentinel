import re
from negotiate_rfq import negotiate_rfq_handler
from tools.gcs_tool import upload_quotation
from tools.bq_tool import insert_quotation_into_bq


# ----------------------------------
# 🔥 RISK SCORING ENGINE
# ----------------------------------
def calculate_risk_score(unit_price: float, delivery_days: int) -> int:
    """
    Basic procurement risk scoring logic.
    """

    risk = 0

    # High price risk
    if unit_price > 150000:
        risk += 30

    # Suspiciously low price
    if unit_price < 80000:
        risk += 25

    # Delivery delay risk
    if delivery_days > 30:
        risk += 40
    elif delivery_days > 15:
        risk += 20

    return risk


def simulate_inbound_email(request):

    # ----------------------------------
    # ✅ CORS PRE-FLIGHT SUPPORT
    # ----------------------------------
    if request.method == "OPTIONS":
        return (
            "",
            204,
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    # ----------------------------------
    # Only POST allowed
    # ----------------------------------
    if request.method != "POST":
        return (
            {"status": "ERROR", "message": "Only POST allowed"},
            405,
            {"Access-Control-Allow-Origin": "*"},
        )

    try:
        data = request.get_json(silent=True) or {}

        if not data:
            return (
                {"status": "ERROR", "message": "Missing body"},
                400,
                {"Access-Control-Allow-Origin": "*"},
            )

        subject = str(data.get("subject", "")).strip()
        body = str(data.get("body", "")).strip()

        print("📩 Incoming Subject:", subject)
        print("📩 Incoming Body:", body)

        # ----------------------------------
        # Extract RFQ ID
        # ----------------------------------
        rfq_match = re.search(r"(RFQ-[A-Za-z0-9-]+)", subject)

        if not rfq_match:
            return (
                {"status": "ERROR", "message": "RFQ ID not found in subject"},
                400,
                {"Access-Control-Allow-Origin": "*"},
            )

        rfq_id = rfq_match.group(1).strip()
        print("📌 Extracted RFQ ID:", rfq_id)

        # ----------------------------------
        # Extract quotation fields
        # ----------------------------------
        supplier_match = re.search(r"SUPPLIER:\s*(.+)", body, re.IGNORECASE)
        price_match = re.search(r"UNIT_PRICE:\s*(\d+)", body, re.IGNORECASE)
        delivery_match = re.search(r"DELIVERY_DAYS:\s*(\d+)", body, re.IGNORECASE)

        if not supplier_match or not price_match or not delivery_match:
            return (
                {"status": "ERROR", "message": "Invalid quotation format"},
                400,
                {"Access-Control-Allow-Origin": "*"},
            )

        supplier_name = supplier_match.group(1).strip()
        unit_price = float(price_match.group(1))
        delivery_days = int(delivery_match.group(1))

        print("📌 Supplier:", supplier_name)
        print("📌 Unit Price:", unit_price)
        print("📌 Delivery Days:", delivery_days)

        # ----------------------------------
        # 🔥 CALCULATE RISK SCORE
        # ----------------------------------
        risk_score = calculate_risk_score(unit_price, delivery_days)
        print("📊 Calculated Risk Score:", risk_score)

        # ----------------------------------
        # 🔥 STORE QUOTATION IN GCS
        # ----------------------------------
        quotation_data = {
            "rfq_id": rfq_id,
            "supplier_name": supplier_name,
            "unit_price": unit_price,
            "delivery_days": delivery_days,
            "risk_score": risk_score
        }

        gcs_path = upload_quotation(
            rfq_id=rfq_id,
            supplier_name=supplier_name,
            quotation_data=quotation_data
        )

        print("✅ Stored quotation in GCS:", gcs_path)

        # ----------------------------------
        # 🔥 INSERT INTO BIGQUERY
        # ----------------------------------
        supplier_id = insert_quotation_into_bq(
            rfq_id=rfq_id,
            supplier_name=supplier_name,
            unit_price=unit_price,
            delivery_days=delivery_days,
            quotation_gcs_uri=gcs_path,
            payment_terms="NET 30",
            risk_score=risk_score
        )

        print("✅ Inserted into BigQuery with supplier_id:", supplier_id)

        # ----------------------------------
        # Trigger Negotiation + Email
        # ----------------------------------
        negotiation_result = negotiate_rfq_handler({
            "rfq_id": rfq_id,
            "send_email": True
        })

        print("✅ Negotiation handler response:", negotiation_result)

        return (
            {
                "status": "QUOTE_RECEIVED",
                "rfq_id": rfq_id,
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "unit_price": unit_price,
                "delivery_days": delivery_days,
                "risk_score": risk_score,
                "stored_in_gcs": gcs_path,
                "negotiation_result": negotiation_result
            },
            200,
            {"Access-Control-Allow-Origin": "*"},
        )

    except Exception as e:
        print("❌ simulate_inbound_email error:", str(e))
        return (
            {"status": "ERROR", "message": str(e)},
            500,
            {"Access-Control-Allow-Origin": "*"},
        )
