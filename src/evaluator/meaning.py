from __future__ import annotations

import re


def contains_required_fact(answer: str, fact: dict) -> tuple[bool, dict]:
    normalized = answer.casefold().replace(",", "")
    amounts = [int(value) for value in re.findall(r"(?<!\d)(\d+)(?!\d)", normalized)]
    currency_found = bool(
        re.search(r"\binr\b|\bindian\s+rupees?\b", normalized, flags=re.IGNORECASE)
    )
    observed = {
        "amounts": amounts,
        "recognized_currency": "INR" if currency_found else None,
    }
    return fact["amount"] in amounts and currency_found, observed


def find_prohibited_claims(answer: str, claim_rules: list[dict]) -> list[str]:
    normalized = " ".join(answer.casefold().split())
    return [
        rule["name"]
        for rule in claim_rules
        if any(pattern.casefold() in normalized for pattern in rule["patterns"])
    ]
