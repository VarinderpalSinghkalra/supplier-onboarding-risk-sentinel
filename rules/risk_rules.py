def classify_risk(score: int) -> str:
    if score < 40:
        return "LOW"
    if score <= 70:
        return "MEDIUM"
    return "HIGH"

