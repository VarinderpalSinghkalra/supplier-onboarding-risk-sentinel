from agents.negotiation_agent import negotiate_rfq
from tools.email_tool import send_email
from tools.firestore_tool import get_supplier_by_id

ADMIN_EMAIL = "varinderpalsinghcareer@gmail.com"


def negotiate_rfq_handler(payload: dict) -> dict:
    """
    Main RFQ negotiation handler.
    - Executes negotiation agent
    - Enriches supplier data
    - Sends deterministic email if requested
    """

    try:
        # -----------------------------------
        # INPUT VALIDATION
        # -----------------------------------
        if not payload:
            return {"status": "ERROR", "message": "Request body missing"}

        rfq_id = payload.get("rfq_id")
        send_email_flag = payload.get("send_email", False)

        if not rfq_id:
            return {"status": "ERROR", "message": "rfq_id is required"}

        print(f"📌 RFQ ID: {rfq_id}")
        print(f"📌 send_email flag: {send_email_flag}")

        # -----------------------------------
        # RUN NEGOTIATION
        # -----------------------------------
        negotiation_result = negotiate_rfq({"rfq_id": rfq_id})
        status = negotiation_result.get("status")

        print(f"✅ Negotiation status: {status}")

        email_sent = False

        if status != "NEGOTIATION_READY":
            return {
                "rfq_id": rfq_id,
                "status": status,
                "negotiation_result": negotiation_result,
                "email_sent": email_sent
            }

        approval_payload = negotiation_result.get("approval_payload")

        if not approval_payload:
            return {
                "rfq_id": rfq_id,
                "status": "ERROR",
                "message": "approval_payload missing",
                "email_sent": email_sent
            }

        # -----------------------------------
        # ENRICH FROM FIRESTORE
        # -----------------------------------
        enriched_alternatives = []

        for alt in approval_payload.get("alternatives", []):
            supplier_id = alt.get("supplier_id")
            supplier_data = get_supplier_by_id(supplier_id)

            enriched_alternatives.append({
                "rfq_id": rfq_id,
                "supplier_id": supplier_id,
                "supplier_name": (
                    supplier_data.get("name")
                    if supplier_data and supplier_data.get("name")
                    else alt.get("supplier_name") or "Unknown Supplier"
                ),
                "unit_price": alt.get("unit_price"),
                "delivery_days": alt.get("delivery_days"),
                "risk_score": (
                    supplier_data.get("risk_score")
                    if supplier_data else alt.get("risk_score")
                ),
                "weighted_score": alt.get("weighted_score") or alt.get("score")
            })

        approval_payload["alternatives"] = enriched_alternatives

        # -----------------------------------
        # DETERMINISTIC EMAIL (UI Triggered)
        # -----------------------------------
        if status == "NEGOTIATION_READY" and send_email_flag:

            subject = f"RFQ {rfq_id} – Vendor Recommendation Ready"

            recommended_vendor = approval_payload.get("recommended_vendor", "N/A")
            rationale = approval_payload.get("rationale", "No rationale provided")

            body = f"RFQ ID: {rfq_id}\n\n"
            body += f"Recommended Vendor:\n{recommended_vendor}\n\n"
            body += f"Rationale:\n{rationale}\n\n"
            body += "Supplier Comparison:\n\n"

            for alt in enriched_alternatives:
                body += f"Supplier Name: {alt.get('supplier_name')}\n"
                body += f"Unit Price: {alt.get('unit_price')}\n"
                body += f"Delivery Days: {alt.get('delivery_days')}\n"
                body += f"Risk Score: {alt.get('risk_score')}\n"
                body += f"Weighted Score: {alt.get('weighted_score')}\n"
                body += "-" * 40 + "\n"

            body += (
                "\n⚠️ This is an AI-generated recommendation. "
                "Final approval is required from Procurement."
            )

            try:
                print("📧 Sending email to admin...")
                send_email(
                    recipients=[ADMIN_EMAIL],
                    subject=subject,
                    body=body
                )
                email_sent = True
                print("✅ Email sent successfully")
            except Exception as e:
                print("❌ Email send failed:", str(e))
                email_sent = False
        else:
            print("ℹ️ Email not triggered")

        # -----------------------------------
        # FINAL RESPONSE
        # -----------------------------------
        return {
            "rfq_id": rfq_id,
            "status": status,
            "negotiation_result": negotiation_result,
            "email_sent": email_sent
        }

    except Exception as e:
        print(f"❌ Error in negotiate_rfq_handler: {str(e)}")
        return {
            "status": "ERROR",
            "message": str(e),
            "email_sent": False
        }
