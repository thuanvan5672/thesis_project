from neo4j import GraphDatabase

URI = "neo4j+s://8fb3088f.databases.neo4j.io:7687"
USER = "neo4j"
PASSWORD = "7d1Gao8xzCaSwi3EpYkmoXHr1b95fYzZ-ENz5e33itw"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

try:
    driver.verify_connectivity()
    print("🎉 Kết nối Neo4j Aura thành công!")
except Exception as e:
    print("❌ Lỗi kết nối:", e)
