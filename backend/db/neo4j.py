from neo4j import GraphDatabase
from backend.core.config import settings
from backend.core.logging import logger

class Neo4jClient:
    def __init__(self):
        self.driver = None

    def connect(self):
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info("Connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise e

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")

    def check_connection(self):
        if not self.driver:
            self.connect()
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS number")
                record = result.single()
                return record["number"] == 1
        except Exception as e:
            logger.error(f"Neo4j connectivity check failed: {e}")
            return False

neo4j_client = Neo4jClient()
