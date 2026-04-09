import re

def extract_intent(user_message: str) -> dict:
    msg = user_message.lower()

    #Extract percentage (dynamic)
    match = re.search(r"(\d+)\s*%", msg)
    magnitude = match.group(1) + "%" if match else "10%"

    #Fuel related
    if "fuel" in msg or "tank" in msg:
        return {
            "system": "fuel",
            "system_id": "SYS-007",
            "change_type": "capacity_increase",
            "magnitude": magnitude,
            "keywords": ["fuel", "tank"]
        }

    #Electrical / Generator
    elif "generator" in msg or "electrical" in msg:
        return {
            "system": "electrical",
            "system_id": "SYS-003",
            "change_type": "replacement",
            "magnitude": magnitude,
            "keywords": ["generator", "power"]
        }

    #Structure
    elif "structure" in msg or "hull" in msg:
        return {
            "system": "structure",
            "system_id": "SYS-002",
            "change_type": "modification",
            "magnitude": magnitude,
            "keywords": ["structure", "hull"]
        }

    #Weapons
    elif "weapon" in msg:
        return {
            "system": "weapons",
            "system_id": "SYS-006",
            "change_type": "addition",
            "magnitude": magnitude,
            "keywords": ["weapon", "mount"]
        }

    #Default (Propulsion)
    else:
        return {
            "system": "propulsion",
            "system_id": "SYS-001",
            "change_type": "power_upgrade",
            "magnitude": magnitude,
            "keywords": ["engine", "power"]
        }

def synthesise_report(user_query: str, impact_data: dict) -> str:
    impacts = impact_data.get("impacts", [])
    class_rules = impact_data.get("class_rules", [])
    historical = impact_data.get("historical", [])
    cost = impact_data.get("cost_estimate", {})

    #Cost formatting
    def format_currency(value):
        return f"${value:,.0f}" if isinstance(value, (int, float)) else "$0"

    return f"""
Design Change Impact Assessment:

User Request:
{user_query}

----------------------------------------
Key Findings:
- Total impacted systems: {len(impacts)}
- Class rules triggered: {len(class_rules)}
- Historical analogues found: {len(historical)}

----------------------------------------
Cost Estimate (USD):
- P10 (Optimistic): {format_currency(cost.get("total_p10_usd", 0))}
- P50 (Most Likely): {format_currency(cost.get("total_p50_usd", 0))}
- P90 (Pessimistic): {format_currency(cost.get("total_p90_usd", 0))}

----------------------------------------
Analysis:
The proposed change has cascading impacts across multiple ship systems.
Critical dependencies across propulsion, structure, and electrical systems
should be carefully reviewed before implementation.

----------------------------------------
Conclusion:
The design change is feasible with moderate cost and manageable risk.
Further validation using detailed engineering analysis is recommended.

----------------------------------------
(Note: This is a mock AI-generated report for PoC demonstration.)
"""