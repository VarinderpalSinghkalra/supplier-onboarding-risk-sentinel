from google.adk.agents import LlmAgent

document_validation_agent = LlmAgent(
    name="DocumentValidationAgent",
    model="gemini-2.5-flash",
    instruction="Validate documents and return JSON."
)

