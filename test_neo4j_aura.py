from neo4j import GraphDatabase

URI = "neo4j+s://1ceb1fae.databases.neo4j.io:7687"
USER = "neo4j"
PASSWORD = "xw4uJ3DP62AMygCxvB1hRnx2fYXYgKQOUqL0GsehTew"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

try:
    driver.verify_connectivity()
    print("🎉 Kết nối Neo4j Aura thành công!")
except Exception as e:
    print("❌ Lỗi kết nối:", e)
