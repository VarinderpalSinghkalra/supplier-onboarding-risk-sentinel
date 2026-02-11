import json

def parse_agent_response(response):
    """
    Normalizes ADK agent responses into Python dicts.
    """

    # Case 1: Already a dict
    if isinstance(response, dict):
        return response

    # Case 2: String JSON
    if isinstance(response, str):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"Agent returned non-JSON string: {response}")

    # Case 3: ADK AgentResponse-like object
    if hasattr(response, "content"):
        try:
            return json.loads(response.content)
        except Exception:
            raise ValueError(f"Unable to parse agent response: {response}")

    raise ValueError(f"Unsupported agent response type: {type(response)}")

