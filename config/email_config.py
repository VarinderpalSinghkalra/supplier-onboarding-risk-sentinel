import os

EMAIL_CONFIG = {
    # ================= SMTP =================
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": 587,

    # ================= SENDER =================
    "SENDER_EMAIL": os.getenv(
        "SENDER_EMAIL",
        "varinderpalsinghcareer@gmail.com"
    ),

    # ✅ Correct: read from ENV variable
    "SENDER_PASSWORD": os.getenv("SENDER_PASSWORD"),

    # ================= FLAGS =================
    "ENABLE_EMAILS": True,

    # ================= ROLE ROUTING =================
    "ROLE_RECIPIENTS": {
        "LEGAL": ["varinderpalsinghcareer@gmail.com"],
        "PROCUREMENT": ["varinderpalsinghcareer@gmail.com"],
        "AUDIT": ["varinderpalsinghcareer@gmail.com"]
    }
}
