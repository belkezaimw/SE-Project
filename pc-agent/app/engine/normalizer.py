import re

def normalize_price(price_str):
    match = re.findall(r"\d+[\.,]?\d*", price_str)
    return float(match[0].replace(",", "")) if match else None
