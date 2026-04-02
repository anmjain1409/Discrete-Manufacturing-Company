# ✅ MOCK LLM SERVICE (NO OpenAI required)

def extract_intent(user_message: str) -> dict:
    msg = user_message.lower()

    # Fuel related
    if "fuel" in msg or "tank" in msg:
        return {
            "system": "fuel",
            "system_id": "SYS-007",
            "change_type": "capacity_increase",
            "magnitude": "20%",
            "keywords": ["fuel", "tank"]
        }

    # Generator / electrical
    elif "generator" in msg or "electrical" in msg:
        return {
            "system": "electrical",
            "system_id": "SYS-003",
            "change_type": "replacement",
            "magnitude": "10%",
            "keywords": ["generator", "power"]
        }

    # Structure related
    elif "structure" in msg or "hull" in msg:
        return {
            "system": "structure",
            "system_id": "SYS-002",
            "change_type": "modification",
            "magnitude": "5%",
            "keywords": ["structure", "hull"]
        }

    # Default (propulsion)
    else:
        return {
            "system": "propulsion",
            "system_id": "SYS-001",
            "change_type": "power_upgrade",
            "magnitude": "15%",
            "keywords": ["engine", "power"]
        }


def synthesise_report(user_query: str, impact_data: dict) -> str:
    impacts = impact_data.get("impacts", [])
    class_rules = impact_data.get("class_rules", [])
    cost = impact_data.get("cost_estimate", {})

    return f"""
Design Change Impact Assessment:

User Request:
{user_query}

Key Findings:
- Total impacted systems: {len(impacts)}
- Class rules triggered: {len(class_rules)}

Cost Estimate:
- P10: ${cost.get("total_p10_usd", 0)}
- P50: ${cost.get("total_p50_usd", 0)}
- P90: ${cost.get("total_p90_usd", 0)}

Analysis:
The proposed change has cascading impacts across multiple ship systems.
High severity dependencies should be reviewed carefully.

Conclusion:
The design change is feasible with moderate cost and manageable risk.

(Note: This is a mock AI-generated report for PoC demonstration.)
"""