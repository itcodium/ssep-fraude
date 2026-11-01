def classify(event: dict) -> dict:
    f = event["features"]
    risk_score = 0
    risk_factors = []

    if f["high_amount"]:
        risk_score += 2
        risk_factors.append("high_amount")
    if f["odd_hour"]:
        risk_score += 2
        risk_factors.append("odd_hour")
    if f["is_online"] and f["merchant_category"] == "electronics":
        risk_score += 1
        risk_factors.append("online_electronics")
    if f["country_mismatch"]:
        risk_score += 3
        risk_factors.append("country_mismatch")

    if risk_score >= 8 and f["amount"] > 1000:
        label, confidence = "fraude_confirmado", 0.87
    elif risk_score >= 5:
        label, confidence = "sospechosa", 0.68
    else:
        label, confidence = "normal", 0.94

    return {
        "label": label,
        "confidence": confidence,
        "uncertainty": 1.0 - confidence,
        "model_version": "imr-fraude-v0.1",
        "source_id": event["source_id"],
        "risk_factors": risk_factors,
    }