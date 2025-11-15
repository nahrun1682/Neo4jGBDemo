import asyncio
import yaml
from pathlib import Path
from dotenv import load_dotenv
from neo4j_graphrag.experimental.pipeline.config.runner import PipelineRunner

load_dotenv()

async def main():
    """
    スキーマ外出し版の実行例
    ゆうと様推奨の構成✨
    """
    
    # 1. schema.yamlを読み込み
    with open("schema.yaml") as f:
        schema_data = yaml.safe_load(f)
    
    # 2. config.yamlを読み込み
    with open("config.yaml") as f:
        config_data = yaml.safe_load(f)
    
    # 3. スキーマをマージ✨
    config_data["schema"] = schema_data
    
    print(f"✅ スキーマ読み込み完了")
    print(f"   ノードタイプ: {len(schema_data.get('node_types', []))}個")
    
    # 4. パイプライン実行
    pipeline = PipelineRunner.from_config(config_data)
    result = await pipeline.run({"file_path": "document.pdf"})
    
    print(f"✅ 処理完了!")

if __name__ == "__main__":
    asyncio.run(main())
