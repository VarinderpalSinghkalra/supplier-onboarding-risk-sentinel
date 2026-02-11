def get_required_tax_form(country: str, supplier_type: str = "COMPANY") -> str:
    if country.upper() == "US":
        return "W-9"
    if supplier_type.upper() == "INDIVIDUAL":
        return "W-8BEN"
    return "W-8BEN-E"

