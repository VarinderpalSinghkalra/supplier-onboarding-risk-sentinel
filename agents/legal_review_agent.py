from google.adk.agents import LlmAgent

# ⚠️ Sanctions policy (can later be moved to Firestore)
SANCTIONED_COUNTRIES = {"IR", "KP", "SY", "CU", "RU"}

legal_review_agent = LlmAgent(
    name="LegalReviewAgent",
    model="gemini-2.5-flash",
    instruction="""
You are a Legal Review Agent in a supplier onboarding system.

You will receive JSON input in the following format:
{
  "country": "US | IR | KP | ...",
  "risk_reason": "string"
}

COMPLIANCE RULES (STRICT):

1. If the country is sanctioned (IR, KP, SY, CU, RU):
   - DO NOT perform any legal review
   - status = "NOT_APPLICABLE"
   - review = "No legal review conducted because the supplier is from a sanctioned country"

2. If the country is NOT sanctioned:
   - Perform a standard legal review
   - If no legal issues are found:
       status = "COMPLETED"
       review = "No legal issues identified"

IMPORTANT RULES:
- Do NOT invent legal risks
- Do NOT change status values
- Do NOT include explanations outside the review field

Return ONLY valid JSON in this exact format:
{
  "status": "NOT_APPLICABLE | COMPLETED",
  "review": "string"
}
"""
)
