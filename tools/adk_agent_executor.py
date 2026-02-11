from config.email_config import EMAIL_CONFIG

SANCTIONED_COUNTRIES = {"IR", "KP", "SY", "CU", "RU"}


def execute_agent(agent, payload: dict) -> dict:
    """
    Deterministic agent executor (POC-safe).
    """

    agent_name = getattr(agent, "name", "").lower()

    # -----------------------------
    # Document collection
    # -----------------------------
    if "document" in agent_name:
        return {
            "W-9": {"file_bytes": b"dummy"},
            "W-8BEN-E": {"file_bytes": b"dummy"}
        }

    # -----------------------------
    # Document validation
    # -----------------------------
    if "validation" in agent_name:
        return {"valid": True}

    # -----------------------------
    # Compliance
    # -----------------------------
    if "compliance" in agent_name:
        return {"compliant": True}

    # -----------------------------
    # Risk scoring
    # -----------------------------
    if "risk" in agent_name:
        country = payload.get("country", "").upper()
        supplier = payload.get("supplier_name", "").lower()

        if country in SANCTIONED_COUNTRIES:
            return {"risk_score": 90, "risk_reason": "Sanctioned country"}

        if any(
            k in supplier
            for k in ["accenture", "deloitte", "pwc", "ey", "kpmg", "ibm", "oracle"]
        ):
            return {"risk_score": 50, "risk_reason": "High-profile global supplier"}

        if country and country != "US":
            return {"risk_score": 40, "risk_reason": "Non-US supplier"}

        return {"risk_score": 20, "risk_reason": "Low-risk supplier"}

    # -----------------------------
    # Legal review
    # -----------------------------
    if "legal" in agent_name:
        country = payload.get("country", "").upper()

        if country in SANCTIONED_COUNTRIES:
            return {
                "status": "NOT_APPLICABLE",
                "review": "No legal review conducted because supplier is from a sanctioned country"
            }

        return {
            "status": "COMPLETED",
            "review": "No legal issues identified"
        }

    # -----------------------------
    # Notification (🔥 FINAL & CORRECT 🔥)
    # -----------------------------
    if "notification" in agent_name:
        decision = payload.get("decision")
        supplier = payload.get("supplier")
        country = payload.get("country")
        is_sanctioned = payload.get("is_sanctioned", False)

        recipients = []
        subject = ""
        body = ""

        if decision == "APPROVED":
            recipients = EMAIL_CONFIG["ROLE_RECIPIENTS"]["PROCUREMENT"]
            subject = "Supplier Approved"
            body = f"Supplier {supplier} has been approved."

        elif decision == "MANUAL_REVIEW":
            recipients = (
                EMAIL_CONFIG["ROLE_RECIPIENTS"]["LEGAL"]
                + EMAIL_CONFIG["ROLE_RECIPIENTS"]["AUDIT"]
            )
            subject = "Manual Review Required – Supplier Onboarding"
            body = (
                f"Supplier {supplier} requires manual review.\n"
                f"Country: {country}"
            )

        elif decision == "REJECTED" and is_sanctioned:
            recipients = (
                EMAIL_CONFIG["ROLE_RECIPIENTS"]["LEGAL"]
                + EMAIL_CONFIG["ROLE_RECIPIENTS"]["AUDIT"]
            )
            subject = "Supplier Auto-Rejected – Sanctions Policy"
            body = (
                f"Supplier {supplier} was automatically rejected "
                f"due to sanctions on country {country}."
            )

        elif decision == "REJECTED":
            recipients = EMAIL_CONFIG["ROLE_RECIPIENTS"]["PROCUREMENT"]
            subject = "Supplier Rejected"
            body = f"Supplier {supplier} has been rejected."

        return {
            "recipients": list(set(recipients)),
            "subject": subject,
            "body": body
        }

    return {}
