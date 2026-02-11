from rules.sanctions_rule import is_sanctioned_country

def allow_commercial_decision(context: dict) -> bool:
    """
    Commercial decision is allowed ONLY if country is NOT sanctioned
    """
    country = context.get("country")
    return not is_sanctioned_country(country)
