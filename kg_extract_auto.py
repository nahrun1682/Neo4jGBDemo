import asyncio
from dotenv import load_dotenv
from tqdm.asyncio import tqdm
from pydantic.v1.utils import deep_update
from neo4j_graphrag.experimental.pipeline.config.runner import PipelineRunner
from neo4j_graphrag.experimental.pipeline.notification import EventType

load_dotenv()

async def main():
    # ① Runnerを作る
    runner = PipelineRunner.from_config_file("src/scripts/config/kg_config_auto.yml")
    pipeline = runner.pipeline  # ← ここで Pipeline を取り出す

    user_input = {"file_path": "data/オグリキャップ.pdf"}
    if runner.config:
        stream_params = deep_update(runner.run_params, runner.config.get_run_params(user_input))
    else:
        stream_params = deep_update(runner.run_params, user_input)

    step_names = [
        "PDFLoader", "TextSplitter", "ChunkEmbedder", "SchemaBuilder",
        "EntityRelationExtractor", "GraphPruning", "KGWriter", "EntityResolver",
    ]

    with tqdm(total=len(step_names), desc="Knowledge Graph構築") as pbar:
        # ② pipeline.stream を使う（引数は data= で渡す）
        async for event in pipeline.stream(data=stream_params):
            if event.event_type == EventType.TASK_STARTED:
                pbar.set_description(f"🔄 {event.task_name}")
            elif event.event_type == EventType.TASK_FINISHED:
                pbar.update(1)
                pbar.set_description(f"✅ {event.task_name}")
            elif event.event_type == EventType.PIPELINE_FAILED:
                print("\n❌ Pipeline failed:", event.message)
                break

    print("✅ 自動スキーマで処理完了!")

if __name__ == "__main__":
    asyncio.run(main())
