import os
import json
from pathlib import Path
from typing import Iterable, List, Any, Dict
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 小分け(大きいJSONだとエラーになる場合があるらしい)
def chunked(it: Iterable[Any], size: int) -> Iterable[List[Any]]:
    buf = []
    for x in it:
        buf.append(x)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

def main(json_path: str = "artifacts/kg_graph.json") -> None:
    load_dotenv()
    uri  = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    pw   = os.environ["NEO4J_PASSWORD"]

    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    nodes: List[Dict] = data.get("nodes", [])
    rels:  List[Dict] = data.get("relationships", [])

    driver = GraphDatabase.driver(uri, auth=(user, pw))

    # 1) ノード投入：apoc.merge.node でラベル＋idでMERGE、props/embeddingをSET
    node_query = """
    UNWIND $rows AS row
    CALL apoc.merge.node([row.label], {id: row.id}) YIELD node
    SET node += coalesce(row.properties, {})
    FOREACH (_ IN CASE WHEN row.embedding_properties IS NULL OR row.embedding_properties.embedding IS NULL THEN [] ELSE [1] END |
    SET node.embedding = row.embedding_properties.embedding
    )
    RETURN count(*) AS upserts
    """

    # 2) リレーション投入：apoc.create.relationship を使う（start/end ノードをMATCHしてから作成）
    rel_query = """
    UNWIND $rows AS row
    MATCH (s {id: row.start_node_id})
    MATCH (t {id: row.end_node_id})
    WITH s, t, row
    CALL apoc.create.relationship(s, row.type, coalesce(row.properties, {}), t) YIELD rel
    SET rel += coalesce(row.properties, {})
    FOREACH (_ IN CASE WHEN row.embedding_properties IS NULL OR row.embedding_properties.embedding IS NULL THEN [] ELSE [1] END |
    SET rel.embedding = row.embedding_properties.embedding
    )
    RETURN count(*) AS upserts
    """

    with driver.session() as s:
        total_nodes = 0
        for batch in chunked(nodes, 1000):
            res = s.run(node_query, rows=batch).single()
            total_nodes += res["upserts"]
        print(f"Nodes upserted: {total_nodes}")

        total_rels = 0
        for batch in chunked(rels, 1000):
            res = s.run(rel_query, rows=batch).single()
            total_rels += res["upserts"]
        print(f"Relationships upserted: {total_rels}")

    driver.close()
    print("✅ Writing finished.")

if __name__ == "__main__":
    json_path = "artifacts/kg_graph_オグリキャップ.json"
    main(json_path=json_path)
