import sys
import os
import time

# Verify we can import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db.sqlite import SessionLocal, init_db
from backend.db.models import Project
from backend.db.neo4j import neo4j_client
from backend.db.graph_schema import Label, Relation

def test_sqlite_persistence():
    print("--- Testing SQLite Persistence ---")
    session = SessionLocal()
    try:
        # Create Project
        project_name = f"Test Project {int(time.time())}"
        new_project = Project(name=project_name, domain="Testing")
        session.add(new_project)
        session.commit()
        session.refresh(new_project)
        print(f"Created Project in SQLite: ID={new_project.id}, Name={new_project.name}")
        
        # Verify read
        p = session.query(Project).filter(Project.id == new_project.id).first()
        assert p is not None
        assert p.name == project_name
        print("SQLite Read Verification: OK")
        return new_project.id
    except Exception as e:
        print(f"SQLite Test Failed: {e}")
        return None
    finally:
        session.close()

def test_neo4j_persistence(project_id):
    if not project_id:
        print("Skipping Graph Test due to SQLite failure")
        return

    print("\n--- Testing Neo4j Persistence ---")
    try:
        # Create Concept linked to Project
        concept_name = f"TestConcept_{project_id}"
        
        query = f"""
        MERGE (p:{Label.Project} {{project_id: $pid}})
        MERGE (c:{Label.Concept} {{name: $cname}})
        MERGE (c)-[:{Relation.BELONGS_TO_PROJECT}]->(p)
        RETURN c, p
        """
        
        with neo4j_client.driver.session() as session:
            result = session.run(query, pid=project_id, cname=concept_name)
            record = result.single()
            if record:
                print(f"Created/Matched Graph Nodes: {record['c']['name']} -> Project {record['p']['project_id']}")
                print("Neo4j Write Verification: OK")
            else:
                print("Neo4j Write Verification: Failed (No record returned)")

            # Verify Constraint (Unique Name) - Optional for this simple test but good for schema check
            # We just verify we can find it back independent of creation
            check = session.run(f"MATCH (c:{Label.Concept}) WHERE c.name = $name RETURN c", name=concept_name).single()
            assert check is not None
            print("Neo4j Read Verification: OK")

    except Exception as e:
        print(f"Neo4j Test Failed: {e}")

if __name__ == "__main__":
    # Ensure tables exist
    init_db()
    
    # Ensure graph connected
    neo4j_client.connect()
    
    pid = test_sqlite_persistence()
    test_neo4j_persistence(pid)
    
    neo4j_client.close()
