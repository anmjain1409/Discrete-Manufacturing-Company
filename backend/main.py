import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.neo4j_service import (
    get_cascade_impacts, get_class_rules_for_systems,
    get_similar_historical_changes
)
from services.llm_service import extract_intent, synthesise_report
from services.cost_model import estimate_cost
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

app = FastAPI(title="DCIA PoC API")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(req: ChatRequest):
    # Step 1: Extract intent
    intent = extract_intent(req.message)

    # Step 2: Graph traversal — get cascading impacts
    impacts = get_cascade_impacts(intent.get("system_id", "SYS-001"), max_hops=3)

    # Step 3: Class rules for all affected systems
    affected_ids = [i["id"] for i in impacts] + [intent.get("system_id", "SYS-001")]
    class_rules = get_class_rules_for_systems(list(set(affected_ids)))

    # Step 4: Historical analogues
    historical = get_similar_historical_changes(intent.get("keywords", []))

    # Step 5: Cost estimate
    magnitude = float(intent.get("magnitude", "10").replace("%", "").strip() or 10)
    cost = estimate_cost(intent.get("system", "propulsion"), magnitude, impacts)

    # Step 6: LLM synthesis
    all_data = {
        "impacts": impacts,
        "class_rules": class_rules,
        "historical": historical,
        "cost_estimate": cost
    }
    report = synthesise_report(req.message, all_data)

    return {
        "intent": intent,
        "impacts": impacts,
        "class_rules": class_rules,
        "historical": historical,
        "cost_estimate": cost,
        "report": report
    }

@app.get("/api/health")
async def health():
    return {"status": "ok"}