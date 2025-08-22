# run_pipeline_save_json.py
import os, asyncio
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
import json
from pydantic import validate_call
from neo4j_graphrag.experimental.components.kg_writer import KGWriter, KGWriterModel
from neo4j_graphrag.experimental.components.types import Neo4jGraph

class JsonWriter(KGWriter):
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name

    @validate_call
    async def run(self, graph: Neo4jGraph) -> KGWriterModel:
        # PydanticモデルをそのままJSON化
        with open(self.file_name, "w", encoding="utf-8") as f:
            json.dump(graph.model_dump(), f, ensure_ascii=False, indent=2)
        return KGWriterModel(status="SUCCESS")
    

async def main(pdf_path: Path):
    load_dotenv()
    NEO4J_URI = os.environ["NEO4J_URI"]     # bolt://localhost:7687 or neo4j+s://... (Aura)
    NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    
    llm = OpenAILLM(
        model_name="gpt-5-nano",
        api_key=OPENAI_API_KEY,
    )
    
    embedder = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small"
    )

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    kg = SimpleKGPipeline(
        llm=llm,
        driver=driver,
        embedder=embedder,
        from_pdf=True,
    )

    await kg.run_async(file_path=str(pdf_path))
    driver.close()
    print("✅ saved nodes & relationships to Neo4j")

if __name__ == "__main__":
    asyncio.run(main(Path("data/オースミシャダイ.pdf")))
