from google.adk.agents import LlmAgent

risk_scoring_agent = LlmAgent(
    name="RiskScoringAgent",
    model="gemini-2.5-flash",
    instruction="""
Return risk score (0–100).
Missing/invalid tax form increases risk.
Return JSON: { "risk_score": number }
"""
)

