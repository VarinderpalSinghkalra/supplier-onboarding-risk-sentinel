from google.adk.agents import LlmAgent

compliance_agent = LlmAgent(
    name="ComplianceAgent",
    model="gemini-2.5-flash",
    instruction="Check compliance including tax form correctness."
)

