from pathlib import Path
from datetime import datetime

def ingest(transaction_path: str, card_id: str) -> dict:
    raw = Path(transaction_path).read_text().strip()
    amount, country, hour, is_online, category, card_country = raw.split(",")

    amount_f = float(amount)
    hour_i = int(hour)
    country_s = country.strip()
    card_country_s = card_country.strip()

    features = {
        "amount": amount_f,
        "country": country_s,
        "hour": hour_i,
        "is_online": is_online.strip().lower() == "true",
        "merchant_category": category.strip(),
        "high_amount": amount_f > 500,
        "odd_hour": hour_i < 6 or hour_i >= 22,
        "country_mismatch": country_s != card_country_s,
    }

    return {
        "source_id": card_id,
        "timestamp": datetime.now().isoformat(),
        "features": features,
        "metadata": {
            "channel": "ecommerce",
            "card_country": card_country_s,
        },
    }