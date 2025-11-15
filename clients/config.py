# clients/config.py
import os

class Config:
    # MongoDB Atlas
    MONGO_URI = os.getenv("MONGO_URI", "")

    # Neo4j Aura
    NEO4J_URI = os.getenv("NEO4J_URI", "")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
