from flask import jsonify, Request

from root_agent import onboard_supplier
from negotiate_rfq import negotiate_rfq_handler
from simulate_inbound_email import simulate_inbound_email


# --------------------------------------------------
# Onboard Supplier
# --------------------------------------------------
def onboard_supplier_http(request: Request):
    if request.method != "POST":
        return jsonify({"error": "Only POST allowed"}), 405

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    result = onboard_supplier(payload)
    return jsonify(result), 200


# --------------------------------------------------
# Negotiate RFQ
# --------------------------------------------------
def negotiate_rfq_http(request: Request):
    if request.method != "POST":
        return jsonify({"error": "Only POST allowed"}), 405

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    result = negotiate_rfq_handler(payload)
    return jsonify(result), 200


# --------------------------------------------------
# Simulate Inbound Email (POC Webhook)
# --------------------------------------------------
def simulate_inbound_email_http(request: Request):
    return simulate_inbound_email(request)

