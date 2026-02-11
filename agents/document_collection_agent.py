from google.adk.agents import LlmAgent

document_collection_agent = LlmAgent(
    name="DocumentCollectionAgent",
    model="gemini-2.5-flash",
    instruction="""
Determine required documents.
Always include provided tax_form (W-9 or W-8).
Return JSON:
{ "required_documents": [] }
"""
)

