import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


SENDER_EMAIL = "varinderpalsinghcareer@gmail.com"


def send_email(recipients, subject, body):
    """
    Enterprise-grade email sender.

    GUARANTEES:
    - Single runtime authority (Cloud Functions only)
    - No silent fallbacks
    - No implicit defaults
    - Fails loudly on misuse
    """

    # --------------------------------------------------
    # 🔒 Runtime lock (SAFE + CORRECT)
    # --------------------------------------------------
    runtime = os.getenv("EMAIL_RUNTIME")

    if runtime is None:
        raise RuntimeError(
            "send_email blocked: EMAIL_RUNTIME is not set. "
            "Expected EMAIL_RUNTIME=CLOUD_FUNCTIONS."
        )

    if runtime != "CLOUD_FUNCTIONS":
        raise RuntimeError(
            f"send_email blocked: invalid runtime '{runtime}'. "
            "Only CLOUD_FUNCTIONS may send emails."
        )

    # --------------------------------------------------
    # 🔒 Hard validation (CRITICAL)
    # --------------------------------------------------
    if not subject or not isinstance(subject, str):
        raise RuntimeError(
            "send_email blocked: subject is missing or invalid"
        )

    if not body or not isinstance(body, str):
        raise RuntimeError(
            "send_email blocked: body is missing or invalid"
        )

    if not isinstance(recipients, list) or not recipients:
        raise RuntimeError(
            "send_email blocked: recipients must be a non-empty list"
        )

    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        raise RuntimeError(
            "send_email blocked: SENDGRID_API_KEY is NOT set"
        )

    # --------------------------------------------------
    # 🔒 Force internal delivery only (INTENTIONAL)
    # --------------------------------------------------
    forced_recipients = ["varinderpalsinghcareer@gmail.com"]

    # --------------------------------------------------
    # 📧 Build message (plain text + HTML)
    # --------------------------------------------------
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=forced_recipients,
        subject=subject,
        plain_text_content=body,
        html_content=f"""
<html>
  <body>
    <pre style="font-family:Arial, sans-serif; font-size:14px;">
{body}
    </pre>
  </body>
</html>
"""
    )

    # --------------------------------------------------
    # 🚀 Send via SendGrid
    # --------------------------------------------------
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        print("✅ Email sent successfully")
        print("📬 Forced To:", forced_recipients)
        print("📨 Subject:", subject)
        print("📡 SendGrid Status:", response.status_code)

        return True

    except Exception as e:
        print("❌ SendGrid error:", str(e))
        raise
