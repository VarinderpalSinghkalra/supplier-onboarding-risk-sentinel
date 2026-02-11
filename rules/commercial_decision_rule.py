def commercial_rule(ai_suggestion: dict) -> str:
    """
    Rule-based interpretation of AI suggestion
    """
    if not ai_suggestion:
        return "MANUAL_REVIEW"

    action = ai_suggestion.get("suggested_action")

    if action == "NEGOTIATE":
        return "MANUAL_REVIEW"

    if action == "ACCEPT":
        return "PASS"

    return "MANUAL_REVIEW"
