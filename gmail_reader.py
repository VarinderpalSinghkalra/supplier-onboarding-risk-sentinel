import base64
import requests
from googleapiclient.discovery import build

SIMULATE_URL = "https://us-central1-YOUR_PROJECT.cloudfunctions.net/simulate_inbound_email"


def process_gmail(request):

    service = build("gmail", "v1")

    results = service.users().messages().list(
        userId="me",
        q="subject:RFQ"
    ).execute()

    messages = results.get("messages", [])

    for msg in messages:

        message = service.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()

        headers = message["payload"]["headers"]

        subject = ""

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]

        body_data = message["payload"]["parts"][0]["body"]["data"]
        body = base64.urlsafe_b64decode(body_data).decode()

        requests.post(
            SIMULATE_URL,
            json={
                "subject": subject,
                "body": body
            }
        )

    return {"status": "emails processed"}