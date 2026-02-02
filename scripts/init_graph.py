from neo4j import GraphDatabase
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.core.config import settings
from backend.db.graph_schema import Label

def init_graph():
    uri = settings.NEO4J_URI
    auth = (settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    
    print(f"Connecting to Neo4j at {uri}...")
    try:
        driver = GraphDatabase.driver(uri, auth=auth)
    except Exception as e:
        print(f"Failed to create driver: {e}")
        return

    commands = [
        # Concept Constraints
        f"CREATE CONSTRAINT concept_name_unique IF NOT EXISTS FOR (c:{Label.Concept}) REQUIRE c.name IS UNIQUE",
        
        # Project Constraints
        f"CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:{Label.Project}) REQUIRE p.project_id IS UNIQUE",
        
        # Indexes
        f"CREATE INDEX idea_title_idx IF NOT EXISTS FOR (i:{Label.Idea}) ON (i.title)",
        f"CREATE INDEX paper_title_idx IF NOT EXISTS FOR (p:{Label.Paper}) ON (p.title)",
    ]

    try:
        with driver.session() as session:
            for cmd in commands:
                print(f"Executing: {cmd}")
                session.run(cmd)
        print("Graph schema initialized successfully.")
    except Exception as e:
        print(f"Error initializing graph: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    init_graph()
