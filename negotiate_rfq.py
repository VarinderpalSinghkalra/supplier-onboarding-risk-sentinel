import os
from agents.negotiation_agent import negotiate_rfq
from tools.email_tool import send_email


ADMIN_EMAIL = "varinderpalsinghcareer@gmail.com"


def negotiate_rfq_handler(payload: dict) -> dict:
    if not payload:
        return {"status": "ERROR", "message": "Request body is missing"}

    rfq_id = payload.get("rfq_id")
    send_email_flag = payload.get("send_email", False)

    if not rfq_id:
        return {"status": "ERROR", "message": "rfq_id is required"}

    print("📌 RFQ ID:", rfq_id)
    print("📌 send_email flag:", send_email_flag)

    negotiation_result = negotiate_rfq({"rfq_id": rfq_id})
    status = negotiation_result.get("status")

    print("✅ Negotiation status:", status)

    email_sent = False

    if status == "NEGOTIATION_READY" and send_email_flag is True:

        approval_payload = negotiation_result.get("approval_payload")

        if not approval_payload:
            print("⚠️ approval_payload missing")
            return {
                "rfq_id": rfq_id,
                "status": status,
                "negotiation_result": negotiation_result,
                "email_sent": False
            }

        # ------------------------------
        # Build Email Deterministically
        # ------------------------------
        subject = f"RFQ {rfq_id} – Vendor Recommendation Ready"

        body = f"RFQ ID: {rfq_id}\n\n"
        body += f"Recommended Vendor:\n{approval_payload['recommended_vendor']}\n\n"
        body += f"Rationale:\n{approval_payload['rationale']}\n\n"
        body += "Supplier Comparison:\n\n"

        for alt in approval_payload["alternatives"]:
            body += f"Supplier Name: {alt['supplier_name']}\n"
            body += f"Unit Price: {alt['unit_price']}\n"
            body += f"Delivery Days: {alt['delivery_days']}\n"
            body += f"Risk Score: {alt['risk_score']}\n"
            body += f"Weighted Score: {alt['score']}\n"
            body += "-" * 40 + "\n"

        body += "\n⚠️ This is an AI-generated recommendation. Final approval is required from Procurement."

        try:
            send_email(
                recipients=[ADMIN_EMAIL],
                subject=subject,
                body=body
            )
            email_sent = True
        except Exception as e:
            print("❌ Email send failed:", str(e))
            email_sent = False

    else:
        print("ℹ️ RFQ email skipped")

    return {
        "rfq_id": rfq_id,
        "status": status,
        "negotiation_result": negotiation_result,
        "email_sent": email_sent
    }

