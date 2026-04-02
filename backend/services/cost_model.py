# Simplified parametric model for PoC
# In production: replace with ML model trained on MDL historical data

DISCIPLINE_COST_FACTORS = {
    "propulsion":  {"base_usd": 2500000, "per_percent_usd": 85000},
    "structure":   {"base_usd": 180000,  "per_percent_usd": 12000},
    "electrical":  {"base_usd": 95000,   "per_percent_usd": 8000},
    "weapons":     {"base_usd": 450000,  "per_percent_usd": 35000},
    "outfitting":  {"base_usd": 65000,   "per_percent_usd": 4500},
    "shafting":    {"base_usd": 120000,  "per_percent_usd": 9000},
    "fuel":        {"base_usd": 55000,   "per_percent_usd": 3500},
}

SEVERITY_MULTIPLIERS = {"HIGH": 1.0, "MEDIUM": 0.4, "LOW": 0.15}

def estimate_cost(primary_discipline: str, magnitude_pct: float,
                  affected_systems: list[dict]) -> dict:
    primary = DISCIPLINE_COST_FACTORS.get(primary_discipline, {"base_usd": 200000, "per_percent_usd": 10000})
    base = primary["base_usd"] + (magnitude_pct * primary["per_percent_usd"])

    cascade_cost = sum(
        DISCIPLINE_COST_FACTORS.get(s["discipline"], {"base_usd": 50000})["base_usd"]
        * SEVERITY_MULTIPLIERS.get(s.get("severity", "LOW"), 0.15)
        for s in affected_systems
    )

    total_p50 = base + cascade_cost
    return {
        "primary_system_usd": round(base),
        "cascade_systems_usd": round(cascade_cost),
        "total_p10_usd": round(total_p50 * 0.75),
        "total_p50_usd": round(total_p50),
        "total_p90_usd": round(total_p50 * 1.35),
        "confidence": "MEDIUM",
        "note": "PoC parametric model — replace with MDL historical data regression in production"
    }