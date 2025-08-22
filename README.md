GraphRAG Starter — Neo4j + Python (+ Langfuse optional)

「まず動く」に全振りした GraphRAG スターターです。
Week1 は GUI（Neo4j Graph Builder / Aura）で一気通貫を体験しつつ、Python で抽出 → Neo4j へ書込み + JSON 保存 を最小構成で回します。

目的：質問に答える＋根拠（どのチャンク/ノードを使ったか）を見せる。

TL;DR
pip install -r requirements.txt
cp .env.example .env

# 疎通 & 索引（Aura でも Local でも共通）
python -m src.scripts.test_connection
python -m src.scripts.create_indexes

# 抽出（PDF→KG）：Neo4j 書込み + JSON 保存（artifacts/）
python -m src.scripts.kg_extract sample.pdf


GUI でチャットする場合は Graph Builder の /chat-only を開き、同じ Neo4j に接続します。

Features

抽出（KG 化）：neo4j-graphrag の SimpleKGPipeline

二刀流出力：Neo4j 書込み＋JSON 保存（監査/再現用）

検索土台：Full-Text Index＋Vector Index

GUI 連携：Graph Builder（ホスト/自己ホスト）から 同じ DB に接続して Q&A

.env 管理：Aura / Local を 環境変数で切替

（任意）Docker/Compose：Neo4j / Langfuse を profiles で起動

Repository Layout
repo/
├─ src/
│  ├─ scripts/
│  │  ├─ test_connection.py      # Aura/Local 疎通（RETURN 1）
│  │  ├─ create_indexes.py       # Full-Text / Vector Index 作成
│  │  └─ kg_extract.py           # SimpleKGPipeline：Neo4j 書込み + JSON 保存
│  └─ config/
│     └─ settings.py             # .env 読み込み
├─ artifacts/                    # 抽出結果 JSON の置き場
├─ infra/
│  ├─ compose.yml                # Neo4j / Langfuse（profiles で出し分け）
│  └─ import/                    # （任意）APOC import 用
├─ .env.example
├─ requirements.txt
└─ README.md

Prerequisites

Python 3.10+

推奨：Neo4j Aura Free（クラウド / TLS）

任意：Docker / Docker Compose（ローカル Neo4j や Langfuse を使う場合）

Setup
1) インストール & 環境変数
pip install -r requirements.txt
cp .env.example .env


.env（例：Aura を使う場合）

NEO4J_URI=neo4j+s://<hash>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=********

OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-large

# （任意）Langfuse / Postgres
PG_USER=langfuse
PG_PASSWORD=langfuse
PG_DB=langfuse
NEXTAUTH_SECRET=devsecret_change_me
ENCRYPTION_KEY=devkeydevkeydevkeydevkey
COMPOSE_PROJECT_NAME=graphrag


ローカル Neo4j を使う場合は NEO4J_URI=bolt://neo4j:7687 に切替。

Quick Start
A) Aura（Docker 不要）
python -m src.scripts.test_connection        # RETURN 1
python -m src.scripts.create_indexes         # FTS / Vector 作成
python -m src.scripts.kg_extract sample.pdf  # → artifacts/extracted_kg.json


GUI チャット：Graph Builder の /chat-only を開き、.env と同じ Aura に接続。

B) Local（Docker で Neo4j 起動）
# Neo4j だけ起動（profiles: neo4j）
docker compose -f infra/compose.yml --profile neo4j up -d

# .env を bolt://neo4j:7687 に切替してから：
python -m src.scripts.test_connection
python -m src.scripts.create_indexes
python -m src.scripts.kg_extract sample.pdf


（任意）Langfuse を使う場合：

docker compose -f infra/compose.yml --profile langfuse up -d
# Web: http://localhost:3001

Scripts

src/scripts/test_connection.py：Aura / Local への接続確認（RETURN 1）

src/scripts/create_indexes.py：索引作成（Cypher 例）

CREATE FULLTEXT INDEX chunkText IF NOT EXISTS
FOR (c:Chunk) ON EACH [c.text];

CREATE VECTOR INDEX chunkEmbedding IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS { indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};


src/scripts/kg_extract.py：SimpleKGPipeline で 抽出 → Neo4j 書込み＋JSON 保存
（内部で MultiWriter：Neo4jWriter + JsonWriter を使用）

Docker（任意）

infra/compose.yml に Neo4j / Langfuse を統合しています（profiles で出し分け）。

# Neo4jのみ
docker compose -f infra/compose.yml --profile neo4j up -d

# Langfuseのみ（Web+Worker+Postgres）
docker compose -f infra/compose.yml --profile langfuse up -d

# 両方まとめて
docker compose -f infra/compose.yml --profile neo4j --profile langfuse up -d


サービス間は サービス名で接続（例：bolt://neo4j:7687）。localhost ではありません。

Data Flow（最小）

PDF / テキスト投入

Split → LLM 抽出（Entities/Relations）

Neo4j へ MERGE（Doc / Chunk / Entity / REL）

FTS / Vector Index を作成

GUI or Python で質問 → 候補チャンク＋近傍を文脈化 → 回答

根拠（chunk_id / score / excerpt）を表示

Troubleshooting

接続できない：Aura は neo4j+s://、Local は bolt://。ポート 7687 と認証、.env を確認。

Vector Index エラー：埋め込み次元（例：1536）と similarity_function を一致。

Docker 内から localhost に繋がらない：neo4j サービス名へ接続。

データが消えた：docker compose down -v はボリュームも削除します（通常は down のみ）。

Deliverables（インターン向け）

PDF→KG→FTS/Vector→回答＋根拠表示 が通る

.env で Aura / Local を切替可能

本 README の手順で 再現可能

License

MIT（予定）