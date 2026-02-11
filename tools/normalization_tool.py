import re

# ==================================================
# SUPPLIER NAME NORMALIZATION
# ==================================================

LEGAL_SUFFIXES = [
    "PVT", "PVT LTD", "PRIVATE LIMITED",
    "LTD", "LIMITED",
    "INC", "LLC", "LLP",
    "CORP", "CORPORATION",
    "GMBH"
]

def normalize_supplier_name(name: str) -> dict:
    """
    Normalizes supplier name for deduplication & matching.
    - Uppercases
    - Removes special characters
    - Removes legal suffixes
    """
    if not name:
        raise ValueError("Supplier name is required")

    cleaned = name.upper()
    cleaned = re.sub(r"[^A-Z0-9 ]", " ", cleaned)

    for suffix in LEGAL_SUFFIXES:
        cleaned = re.sub(rf"\b{suffix}\b", "", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return {
        "normalized_name": cleaned,
        "match_key": cleaned.replace(" ", "_")
    }


# ==================================================
# COUNTRY NORMALIZATION (ISO-3166 Alpha-2)
# ==================================================

COUNTRY_MAP = {
    # United States
    "UNITED STATES": "US",
    "UNITED STATES OF AMERICA": "US",
    "USA": "US",
    "U.S.A": "US",
    "U.S.": "US",
    "US": "US",

    # India
    "INDIA": "IN",
    "BHARAT": "IN",
    "IN": "IN",

    # United Kingdom
    "UNITED KINGDOM": "GB",
    "UK": "GB",
    "GREAT BRITAIN": "GB",
    "ENGLAND": "GB",
    "GB": "GB",

    # Iran (sanctioned)
    "IRAN": "IR",
    "IRAN, ISLAMIC REPUBLIC OF": "IR",
    "IR": "IR",

    # Russia (sanctioned)
    "RUSSIA": "RU",
    "RUSSIAN FEDERATION": "RU",
    "RU": "RU",

    # China
    "CHINA": "CN",
    "PEOPLE'S REPUBLIC OF CHINA": "CN",
    "PRC": "CN",
    "CN": "CN",

    # Canada
    "CANADA": "CA",
    "CA": "CA",

    # Germany
    "GERMANY": "DE",
    "DEUTSCHLAND": "DE",
    "DE": "DE",

    # France
    "FRANCE": "FR",
    "FR": "FR",
}

def normalize_country(country: str) -> str:
    """
    Normalizes country names to ISO-3166 alpha-2 codes.
    """
    if not country:
        raise ValueError("Country is required")

    key = re.sub(r"\s+", " ", country.strip().upper())
    return COUNTRY_MAP.get(key, key)
