from flask import jsonify, Request

from root_agent import onboard_supplier
from negotiate_rfq import negotiate_rfq_handler


def onboard_supplier_http(request: Request):
    if request.method != "POST":
        return jsonify({"error": "Only POST method allowed"}), 405

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid or empty JSON payload"}), 400

    result = onboard_supplier(payload)
    return jsonify(result), 200


def negotiate_rfq_http(request: Request):
    if request.method != "POST":
        return jsonify({"error": "Only POST method allowed"}), 405

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Invalid or empty JSON payload"}), 400

    result = negotiate_rfq_handler(payload)
    return jsonify(result), 200
