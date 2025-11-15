import asyncio
import json
from typing import Any
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
from neo4j_graphrag.experimental.components.types import (
    Neo4jGraph,
    Neo4jNode,
    Neo4jRelationship
)
from neo4j_graphrag.experimental.components.kg_writer import KGWriterModel

load_dotenv()

class Neo4jGraphExporter:
    """
    Neo4jからグラフをエクスポートして
    KGWriter互換のNeo4jGraph形式で出力✨
    
    根拠: KGWriter/KGWriterModelと同じデータ構造を使用
    URL: https://neo4j.com/docs/neo4j-graphrag-python/current/api-documentation.html#kgwriter
    """
    
    def __init__(self, driver, neo4j_database: str = "neo4j"):
        self.driver = driver
        self.neo4j_database = neo4j_database
    
    async def export_graph(self) -> tuple[Neo4jGraph, KGWriterModel]:
        """
        Neo4jからNeo4jGraph形式でエクスポート
        
        Returns:
            Neo4jGraph: ノードとリレーションシップのリスト
            KGWriterModel: 実行結果のメタデータ
        """
        try:
            # ① ノード取得
            nodes = await self._fetch_nodes()
            
            # ② リレーションシップ取得
            relationships = await self._fetch_relationships()
            
            # ③ Neo4jGraph形式で構築✨
            graph = Neo4jGraph(
                nodes=nodes,
                relationships=relationships
            )
            
            # ④ KGWriterModel形式でメタデータ返却
            result = KGWriterModel(
                status="SUCCESS",
                metadata={
                    "node_count": len(nodes),
                    "relationship_count": len(relationships)
                }
            )
            
            return graph, result
        
        except Exception as e:
            # エラー時もKGWriterModel形式で返却
            result = KGWriterModel(
                status="FAILURE",
                metadata={"error": str(e)}
            )
            return Neo4jGraph(nodes=[], relationships=[]), result
    
    async def _fetch_nodes(self) -> list[Neo4jNode]:
        """全ノードを Neo4jNode 形式で取得"""
        with self.driver.session(database=self.neo4j_database) as session:
            result = session.run("""
                MATCH (n)
                RETURN elementId(n) as element_id, 
                       labels(n) as labels, 
                       properties(n) as properties
            """)
            
            nodes = []
            for record in result:
                node = Neo4jNode(
                    id=str(record["element_id"]),
                    label=record["labels"][0] if record["labels"] else "Unknown",
                    properties=record["properties"] or {}
                )
                nodes.append(node)
            
            return nodes
    
    async def _fetch_relationships(self) -> list[Neo4jRelationship]:
        """全リレーションシップを Neo4jRelationship 形式で取得"""
        with self.driver.session(database=self.neo4j_database) as session:
            result = session.run("""
                MATCH (s)-[r]->(t)
                RETURN type(r) as type,
                       elementId(s) as start_node_id,
                       elementId(t) as end_node_id,
                       properties(r) as properties
            """)
            
            relationships = []
            for record in result:
                rel = Neo4jRelationship(
                    type=record["type"],
                    start_node_id=str(record["start_node_id"]),
                    end_node_id=str(record["end_node_id"]),
                    properties=record["properties"] or {}
                )
                relationships.append(rel)
            
            return relationships

async def main():
    """
    Neo4jからエクスポートしてJSON保存
    KGWriter互換形式✨
    """
    # ① Driver作成
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(
            os.getenv("NEO4J_USER", "neo4j"),
            os.getenv("NEO4J_PASSWORD", "password")
        )
    )
    
    # ② エクスポート実行
    exporter = Neo4jGraphExporter(driver=driver)
    graph, result = await exporter.export_graph()
    
    # ③ 結果表示
    if result.status == "SUCCESS":
        print(f"✅ Export {result.status}")
        print(f"   ノード数: {result.metadata['node_count']}")
        print(f"   リレーションシップ数: {result.metadata['relationship_count']}")
        
        # ④ JSON保存 (KGWriter互換形式✨)
        output = {
            "graph": graph.model_dump(),  # Neo4jGraph形式
            "result": result.model_dump()  # KGWriterModel形式
        }
        
        with open("artifacts/neo4j_export.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print("✅ artifacts/neo4j_export.json に保存しました!")
    else:
        print(f"❌ Export {result.status}")
        print(f"   エラー: {result.metadata.get('error')}")
    
    driver.close()

if __name__ == "__main__":
    asyncio.run(main())
