import os
import asyncio
import json
from pathlib import Path

from neo4j import GraphDatabase
from neo4j.exceptions import ClientError
from dotenv import load_dotenv

from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.embeddings import OpenAIEmbeddings


async def main(pdf_path: Path) -> None:
    load_dotenv()  # .env から環境変数を読み込み

    # --- ENV ---
    NEO4J_URI = os.environ["NEO4J_URI"]              # bolt://localhost:7687 or neo4j+s://... (Aura)
    NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

    # --- Clients ---
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    llm = OpenAILLM(
        model_name="gpt-5-mini",
        api_key=OPENAI_API_KEY,
    )
    
    embedder = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small"
    )

    # --- Pipeline (PDF入力) ---
    kg_builder = SimpleKGPipeline(
        llm=llm,              # エンティティ/リレーション抽出
        driver=driver,        # 結果をNeo4jへ書き込み
        embedder=embedder,    # チャンク埋め込み（ベクトル）
        from_pdf=True,        # ★ PDF を直接パース
        # schema=...          # 必要なら抽出スキーマを dict で渡せます
        # neo4j_database="neo4j",  # AuraでDB名を指定したい場合
    )

    try:
        try:
            result = await kg_builder.run_async(file_path=str(pdf_path))
        except ClientError as e:
            # 代表的な APOC 未導入エラーを検出して分かりやすいメッセージを出す
            msg = str(e)
            if 'apoc.create.addLabels' in msg or 'apoc.create.addLabels()' in msg:
                print("ERROR: Neo4j reported missing APOC procedure 'apoc.create.addLabels'.")
                print("- 対処1: ローカル Neo4j を使っている場合、APOC プラグインを有効にしてください。")
                print("  例: Neo4j Desktop / Docker の plugins に apoc を追加し、neo4j.conf に apoc.allowed.* 設定を追加")
                print("- 対処2: Aura を使っている場合は一部 APOC が制限されるため、別の（ローカル）DB を使うか、ライブラリ側の写経/設定変更を検討してください。")
            # re-raise so caller / CI sees the original traceback if needed
            raise

        # 返り値があれば保存（監査/再現用）
        Path("artifacts").mkdir(parents=True, exist_ok=True)
        serializable = None
        # try common conversion methods for pipeline result
        if hasattr(result, "dict"):
            try:
                serializable = result.dict()
            except Exception:
                serializable = None
        if serializable is None and hasattr(result, "to_dict"):
            try:
                serializable = result.to_dict()
            except Exception:
                serializable = None
        if serializable is None and hasattr(result, "json"):
            try:
                serializable = json.loads(result.json())
            except Exception:
                serializable = None
        if serializable is None:
            # 最終フォールバック: 再帰的にオブジェクトを文字列化して保存
            try:
                def fallback(o):
                    try:
                        return o.__dict__
                    except Exception:
                        return repr(o)

                serializable = json.loads(json.dumps(result, default=lambda o: fallback(o)))
            except Exception:
                serializable = {"repr": repr(result)}

        with open("artifacts/kg_result.json", "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
        print("✅ KG build finished. Graph written to Neo4j. JSON saved to artifacts/kg_result.json")
    finally:
        # 後始末
        try:
            await llm.async_client.close()
        except Exception:
            pass
        driver.close()


if __name__ == "__main__":
    pdf_path = Path("data/オグリキャップ.pdf")
    asyncio.run(main(pdf_path))
