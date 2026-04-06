from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()
print("NEO4J_URI:", os.getenv("NEO4J_URI"))
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

def get_cascade_impacts(system_id: str, max_hops: int = 3) -> list[dict]:
    with driver.session() as session:
        result = session.run("""
            MATCH path = (s:ShipSystem {id: $id})-[:CASCADES_TO*1..3]->(affected:ShipSystem)
            WITH affected, length(path) AS hops,
                 [r IN relationships(path) | r.reason] AS reasons,
                 [r IN relationships(path) | r.severity] AS severities
            RETURN affected.id AS id,
                   affected.name AS name,
                   affected.discipline AS discipline,
                   hops,
                   reasons,
                   severities[-1] AS severity
            ORDER BY hops
        """, id=system_id)
        return [dict(r) for r in result]

def get_class_rules_for_systems(system_ids: list[str]) -> list[dict]:
    with driver.session() as session:
        result = session.run("""
            MATCH (s:ShipSystem)-[:GOVERNED_BY]->(cr:ClassRule)
            WHERE s.id IN $ids
            RETURN s.name AS system, cr.society AS society,
                   cr.clause AS clause, cr.description AS description
        """, ids=system_ids)
        return [dict(r) for r in result]

def get_similar_historical_changes(keywords: list[str]) -> list[dict]:
    with driver.session() as session:
        result = session.run("""
            MATCH (hc:DesignChange)
            WHERE any(kw IN $keywords WHERE toLower(hc.description) CONTAINS toLower(kw))
            OPTIONAL MATCH (hc)-[:GENERATED]->(cr:CostRecord)
            RETURN hc.id AS id, hc.description AS description,
                   hc.cost_actual_usd AS cost_actual_usd,
                   hc.schedule_delay_days AS delay_days,
                   hc.summary AS summary,
                   collect(cr.category + ':' + toString(cr.amount_usd)) AS cost_breakdown
            LIMIT 3
        """, keywords=keywords)
        return [dict(r) for r in result]