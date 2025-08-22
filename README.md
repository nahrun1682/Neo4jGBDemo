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
# GraphRAG Starter — Neo4j + Python (+ Langfuse optional)

「まず動く」を目標にした GraphRAG のスターターキットです。
このリポジトリは、PDF などのドキュメントから Knowledge Graph を抽出し、Neo4j に書き込みつつ検索用に JSON も保存する最小構成を提供します。

## TL;DR

```bash
pip install -r requirements.txt
cp .env.example .env

# 疎通 & 索引（Aura / Local 共通）
python -m src.scripts.test_connection
python -m src.scripts.create_indexes

# 抽出（PDF → KG）：Neo4j 書込み + JSON 保存（artifacts/）
python -m src.scripts.kg_extract sample.pdf
```

GUI でチャットする場合は、Graph Builder の `/chat-only` を開き、同じ Neo4j に接続してください。

## 特徴

- 抽出（KG 化）：`neo4j-graphrag` の SimpleKGPipeline を利用
- 二刀流出力：Neo4j 書き込みと JSON 保存（監査・再現用）
- 検索基盤：Full-Text Index と Vector Index を併用
- GUI 連携：Graph Builder（ホスト/自己ホスト）から同じ DB に接続して Q&A
- `.env` で Aura / Local を切り替え可能
- （任意）Docker Compose で Neo4j / Langfuse を起動可能

## リポジトリ構成

```
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
│  ├─ compose.yml                # Neo4j / Langfuse（profiles で切替）
│  └─ import/                    # （任意）APOC import 用
├─ .env.example
├─ requirements.txt
└─ README.md
```

## 前提

- Python 3.10+
- 推奨：Neo4j Aura Free（クラウド / TLS）
- 任意：Docker / Docker Compose（ローカルで Neo4j や Langfuse を使う場合）

## セットアップ

1. 依存関係をインストール

```bash
pip install -r requirements.txt
cp .env.example .env
```

2. `.env` を編集して接続情報を設定します。

例（Aura を使う場合）:

```
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
```

ローカル Neo4j を使う場合は `NEO4J_URI=bolt://neo4j:7687` に切り替えてください。

## Quick Start

### A) Aura（Docker 不要）

```bash
python -m src.scripts.test_connection        # RETURN 1
python -m src.scripts.create_indexes         # FTS / Vector 作成
python -m src.scripts.kg_extract sample.pdf  # → artifacts/extracted_kg.json
```

Graph Builder の `/chat-only` を開き、`.env` と同じ Aura に接続すれば GUI チャットが利用できます。

### B) Local（Docker で Neo4j 起動）

Neo4j のみ起動（profiles: neo4j）:

```bash
docker compose -f infra/compose.yml --profile neo4j up -d
```

`.env` を `bolt://neo4j:7687` に切り替えてから:

```bash
python -m src.scripts.test_connection
python -m src.scripts.create_indexes
python -m src.scripts.kg_extract sample.pdf
```

（任意）Langfuse を使う場合:

```bash
docker compose -f infra/compose.yml --profile langfuse up -d
# Web UI: http://localhost:3001
```

## スクリプト

- `src/scripts/test_connection.py`：Aura / Local への接続確認（RETURN 1）
- `src/scripts/create_indexes.py`：索引作成（Cypher 例）

例 — Fulltext と Vector Index:

```cypher
CREATE FULLTEXT INDEX chunkText IF NOT EXISTS
FOR (c:Chunk) ON EACH [c.text];

CREATE VECTOR INDEX chunkEmbedding IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS { indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};
```

- `src/scripts/kg_extract.py`：SimpleKGPipeline による抽出 → Neo4j 書込み + JSON 保存
  - 内部で `MultiWriter`（`Neo4jWriter` + `JsonWriter`）を使用します。

## Docker（任意）

`infra/compose.yml` に Neo4j / Langfuse のサービス定義があります。profiles で出し分け可能です。

```bash
# Neo4j のみ
docker compose -f infra/compose.yml --profile neo4j up -d

# Langfuse のみ（Web + Worker + Postgres）
docker compose -f infra/compose.yml --profile langfuse up -d

# 両方まとめて
docker compose -f infra/compose.yml --profile neo4j --profile langfuse up -d
```

コンテナ間はサービス名で接続します（例：`bolt://neo4j:7687`）。`localhost` ではありません。

## データフロー（最小構成）

1. PDF / テキストを投入
2. Split → LLM による抽出（Entities / Relations）
3. Neo4j に MERGE（Doc / Chunk / Entity / REL）
4. FTS / Vector Index を作成
5. GUI または Python で質問 → 候補チャンク＋近傍を文脈化 → 回答
6. 根拠（`chunk_id` / `score` / `excerpt`）を表示

## トラブルシューティング

- 接続できない：Aura は `neo4j+s://`、Local は `bolt://`。ポート 7687 と認証、`.env` を確認してください。
- Vector Index エラー：埋め込み次元（例：1536）と `similarity_function` を一致させる。
- Docker 内から `localhost` に繋がらない：コンテナ間はサービス名で接続する（例：`bolt://neo4j:7687`）。
- データが消えた：`docker compose down -v` はボリュームも削除します（通常は `down` のみを使う）。

## Deliverables（インターン向け）

- PDF → KG → FTS/Vector → 回答＋根拠表示 が通ること
- `.env` で Aura / Local を切替可能であること
- 本 README の手順で再現可能であること

## ライセンス

MIT（予定）
