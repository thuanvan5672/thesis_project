# clients/neo4j_client.py
from typing import Any, Dict, List
from neo4j import GraphDatabase
from clients.config import Config


class Neo4jClient:
    def __init__(self) -> None:
        """
        Khởi tạo kết nối tới Neo4j Aura (hoặc Neo4j Desktop nếu URI phù hợp)
        Cần 3 biến môi trường:
        - NEO4J_URI       (vd: neo4j+s://8fb3088f.databases.neo4j.io)
        - NEO4J_USER      (vd: neo4j)
        - NEO4J_PASSWORD  (mật khẩu Aura)
        """
        if not (Config.NEO4J_URI and Config.NEO4J_USER and Config.NEO4J_PASSWORD):
            raise ValueError(
                "Thiếu cấu hình Neo4j (NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD)."
            )

        self.driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD),
        )

    def close(self) -> None:
        """Đóng kết nối driver (dùng khi tắt ứng dụng)."""
        if self.driver:
            self.driver.close()

    def run_query(
        self,
        cypher: str,
        params: Dict[str, Any] | None = None
    ) -> List[Dict[str, Any]]:
        """
        Chạy một câu lệnh Cypher và trả về list[dict],
        mỗi dict là một record (theo dạng record.data()).
        """
        params = params or {}
        with self.driver.session() as session:
            result = session.run(cypher, params)
            return [record.data() for record in result]
