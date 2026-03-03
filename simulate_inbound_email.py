import re
from negotiate_rfq import negotiate_rfq_handler
from tools.gcs_tool import upload_quotation
from tools.bq_tool import insert_quotation_into_bq


# ----------------------------------
# 🔥 RISK SCORING ENGINE
# ----------------------------------
def calculate_risk_score(unit_price: float, delivery_days: int) -> int:
    risk = 0

    if unit_price > 150000:
        risk += 30

    if unit_price < 80000:
        risk += 25

    if delivery_days > 30:
        risk += 40
    elif delivery_days > 15:
        risk += 20

    return risk


# ----------------------------------
# 🚀 MAIN CLOUD FUNCTION
# ----------------------------------
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

    if request.method != "POST":
        return (
            {"status": "ERROR", "message": "Only POST allowed"},
            405,
            {"Access-Control-Allow-Origin": "*"},
        )

    try:
        subject = ""
        body = ""
        sender = ""

        # ----------------------------------
        # 🔥 CASE 1 — SENDGRID INBOUND
        # ----------------------------------
        if request.form:
            print("📩 SendGrid Inbound Triggered")

            subject = str(request.form.get("subject", "")).strip()
            body = str(request.form.get("text", "")).strip()
            sender = str(request.form.get("from", "")).strip()

        # ----------------------------------
        # 🔥 CASE 2 — JSON (UI / Postman)
        # ----------------------------------
        elif request.is_json:
            print("📩 JSON UI Triggered")

            data = request.get_json(silent=True) or {}
            subject = str(data.get("subject", "")).strip()
            body = str(data.get("body", "")).strip()
            sender = "UI"

        else:
            return (
                {"status": "ERROR", "message": "Unsupported content type"},
                400,
                {"Access-Control-Allow-Origin": "*"},
            )

        print("📩 Subject:", subject)
        print("📩 Body:", body)

        # ----------------------------------
        # 🔍 Extract RFQ ID
        # ----------------------------------
        rfq_match = re.search(r"(RFQ-[A-Za-z0-9-]+)", subject)

        if not rfq_match:
            return (
                {"status": "ERROR", "message": "RFQ ID not found in subject"},
                400,
                {"Access-Control-Allow-Origin": "*"},
            )

        rfq_id = rfq_match.group(1).strip()
        print("📌 RFQ ID:", rfq_id)

        # ----------------------------------
        # 🔍 Extract Quotation Fields
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
        # 🔥 Calculate Risk Score
        # ----------------------------------
        risk_score = calculate_risk_score(unit_price, delivery_days)
        print("📊 Risk Score:", risk_score)

        # ----------------------------------
        # 🔥 Store in GCS
        # ----------------------------------
        quotation_data = {
            "rfq_id": rfq_id,
            "supplier_name": supplier_name,
            "unit_price": unit_price,
            "delivery_days": delivery_days,
            "risk_score": risk_score,
            "sender": sender
        }

        gcs_path = upload_quotation(
            rfq_id=rfq_id,
            supplier_name=supplier_name,
            quotation_data=quotation_data
        )

        print("✅ Stored in GCS:", gcs_path)

        # ----------------------------------
        # 🔥 Insert into BigQuery
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

        print("✅ Inserted into BigQuery:", supplier_id)

        # ----------------------------------
        # 🔥 Trigger Negotiation + Email
        # ----------------------------------
        negotiation_result = negotiate_rfq_handler({
            "rfq_id": rfq_id,
            "send_email": True
        })

        print("✅ Negotiation Result:", negotiation_result)

        # ----------------------------------
        # ✅ SUCCESS RESPONSE
        # ----------------------------------
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
        print("❌ Error:", str(e))
        return (
            {"status": "ERROR", "message": str(e)},
            500,
            {"Access-Control-Allow-Origin": "*"},
        )
