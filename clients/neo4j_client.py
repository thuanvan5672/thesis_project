from typing import Any, Dict, List
from neo4j import GraphDatabase
from clients.config import Config


class Neo4jClient:
    def __init__(self) -> None:
        if not (Config.NEO4J_URI and Config.NEO4J_USER and Config.NEO4J_PASSWORD):
            raise ValueError("Thiếu cấu hình Neo4j (NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD).")

        # Kết nối Neo4j Aura (URI dạng neo4j+s://....databases.neo4j.io)
        self.driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD),
        )

    def close(self) -> None:
        self.driver.close()

    def run_query(self, cypher: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        params = params or {}
        with self.driver.session() as session:
            result = session.run(cypher, params)
            # Chuyển record -> dict
            return [record.data() for record in result]


neo4j_client = Neo4jClient()
