from backend.db.neo4j import neo4j_client
from backend.db.graph_schema import Label, Relation
from backend.core.logging import logger

class GraphService:
    def _get_driver(self):
        """Fix #9: Always return a live driver, re-assigning if needed after connect()."""
        if not neo4j_client.driver:
            neo4j_client.connect()
        return neo4j_client.driver

    def get_global_subgraph(self, center_node=None, depth=2, limit=50):
        # Fetches nodes/edges that are NOT project-specific
        driver = self._get_driver()

        if center_node:
            # Fix #8: Use a non-path query that returns individual n,r,m records
            # so results are parsed consistently. Variable-length paths return
            # list-of-rels which were previously silently dropped via `pass`.
            query = f"""
            MATCH (c:{Label.Concept} {{name: $name}})-[r]-(n)
            WHERE NOT EXISTS {{ MATCH (n)-[:{Relation.BELONGS_TO_PROJECT}]->({Label.Project}) }}
            RETURN c, r, n LIMIT $limit
            """
        else:
            query = """
            MATCH (n)-[r]->(m)
            WHERE NOT EXISTS {
                MATCH (n)-[:BELONGS_TO_PROJECT]->(:Project)
            }
            AND NOT EXISTS {
                 MATCH (m)-[:BELONGS_TO_PROJECT]->(:Project)
            }
            RETURN n, r, m LIMIT $limit
            """

        formatted_result = {"nodes": [], "edges": []}

        try:
            with driver.session() as session:
                result = session.run(query, name=center_node, limit=limit)

                nodes_seen = set()

                for record in result:
                    # Fix #8: Unified record parsing — no more silent `pass` for path results.
                    # Center node is under key "c" when center_node is set, otherwise "n".
                    n = record.get("c") or record.get("n")
                    m = record.get("n") if record.get("c") else record.get("m")
                    r = record.get("r")

                    if n and n.element_id not in nodes_seen:
                        formatted_result["nodes"].append(self._serialize_node(n))
                        nodes_seen.add(n.element_id)
                    if m and m.element_id not in nodes_seen:
                        formatted_result["nodes"].append(self._serialize_node(m))
                        nodes_seen.add(m.element_id)
                    if r:
                        # Handle both single relationship and list (variable path)
                        if isinstance(r, list):
                            for rel in r:
                                formatted_result["edges"].append(self._serialize_edge(rel))
                        else:
                            formatted_result["edges"].append(self._serialize_edge(r))

            return formatted_result
        except Exception as e:
            logger.error(f"Graph subgraph fetch failed: {e}")
            return {"nodes": [], "edges": []}

    def get_concept_details(self, name):
        driver = self._get_driver()  # Fix #9

        with driver.session() as session:
            # 1. Fetch Concept Properties
            c_res = session.run(f"MATCH (c:{Label.Concept} {{name: $name}}) RETURN c", name=name).single()
            if not c_res:
                return None

            concept = self._serialize_node(c_res["c"])

            # 2. Assumptions
            a_res = session.run(f"MATCH (c:{Label.Concept} {{name: $name}})-[:{Relation.ASSUMES}]->(a) RETURN a", name=name)
            concept["assumptions"] = [self._serialize_node(r["a"]) for r in a_res]

            # 3. Limitations
            l_res = session.run(f"MATCH (c:{Label.Concept} {{name: $name}})-[:{Relation.FAILS_WHEN}]->(l) RETURN l", name=name)
            concept["limitations"] = [self._serialize_node(r["l"]) for r in l_res]

            # 4. Contradictions
            conflict_res = session.run(f"MATCH (c:{Label.Concept} {{name: $name}})-[:{Relation.CONFLICTS_WITH}]-(o) RETURN o", name=name)
            concept["contradictions"] = [self._serialize_node(r["o"]) for r in conflict_res]

            return concept

    def _serialize_node(self, node):
        return {
            "id": node.element_id,
            "labels": list(node.labels),
            "properties": dict(node)
        }

    def _serialize_edge(self, rel):
        return {
            "id": rel.element_id,
            "type": rel.type,
            "start_node": rel.start_node.element_id,
            "end_node": rel.end_node.element_id,
            "properties": dict(rel)
        }

    def get_project_subgraph(self, project_id):
        # Fetches only nodes related to project
        driver = self._get_driver()  # Fix #9

        query = f"""
        MATCH (n)-[r]-(m)
        WHERE EXISTS {{ MATCH (n)-[:{Relation.BELONGS_TO_PROJECT}]->(:{Label.Project} {{project_id: $pid}}) }}
        AND EXISTS {{ MATCH (m)-[:{Relation.BELONGS_TO_PROJECT}]->(:{Label.Project} {{project_id: $pid}}) }}
        RETURN n, r, m LIMIT 100
        """

        formatted_result = {"nodes": [], "edges": []}
        try:
            with driver.session() as session:
                result = session.run(query, pid=project_id)
                nodes_seen = set()

                for record in result:
                     n = record.get("n")
                     m = record.get("m")
                     r = record.get("r")

                     if n and n.element_id not in nodes_seen:
                         formatted_result["nodes"].append(self._serialize_node(n))
                         nodes_seen.add(n.element_id)
                     if m and m.element_id not in nodes_seen:
                         formatted_result["nodes"].append(self._serialize_node(m))
                         nodes_seen.add(m.element_id)
                     if r:
                         formatted_result["edges"].append(self._serialize_edge(r))
            return formatted_result
        except Exception as e:
            logger.error(f"Project graph fetch failed: {e}")
            return {"nodes": [], "edges": []}

    def get_all_concepts(self):
        # Used for vector search initialization
        driver = self._get_driver()  # Fix #9

        query = f"MATCH (c:{Label.Concept}) RETURN c"
        results = []
        with driver.session() as session:
            res = session.run(query)
            for r in res:
                results.append(dict(r["c"])) # Return properties dict
        return results

graph_service = GraphService()
