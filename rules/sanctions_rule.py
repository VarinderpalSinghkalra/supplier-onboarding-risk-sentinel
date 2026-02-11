def is_sanctioned_country(country: str) -> bool:
    """
    HARD STOP RULE
    """
    if not country:
        return True  # unknown treated as unsafe

    sanctioned_countries = {
        "Iran",
        "North Korea",
        "Syria",
        "Cuba",
        "Russia"
    }

    return country.strip() in sanctioned_countries
