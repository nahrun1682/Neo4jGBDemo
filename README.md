# GraphRAG Starter — Neo4j Graph Builder + Python (+ Langfuse optional)

「まず動く」を目標にした GraphRAG のスターターキットです。
このリポジトリは、PDF などのドキュメントから Neo4j Graph Builder を用いてKnowledge Graph を抽出し、Neo4j に書き込みつつ検索用に JSON も保存する最小構成を提供します。

## リポジトリ構成

```
Neo4jGBDemo/
├─ .env                          # 環境変数（接続情報）※.gitignore で無視
├─ .env.example                  # 環境変数テンプレート
├─ .gitignore
├─ .python-version               # Python 3.11
├─ pyproject.toml                # uv 依存関係管理
├─ uv.lock                       # uv ロックファイル
├─ README.md
├─ Neo4jGBGUI.md                 # Graph Builder GUI 手順
├─ src/
│  ├─ config/                    # 設定関連（現在空）
│  └─ scripts/
│     ├─ extractor/              # 抽出スクリプト
│     │  ├─ kg_extract_toJson.py     # PDF → JSON 抽出
│     │  └─ kg_extract_toNeo4j.py    # PDF → Neo4j 直接書込み
│     └─ writer/                 # 書込みスクリプト
│        └─ writer_JsonToNeo4j.py    # JSON → Neo4j インポート
├─ artifacts/                    # 抽出結果 JSON の置き場
│  ├─ kg_graph_オグリキャップ.json
│  └─ kg_graph_オースミシャダイ.json
├─ data/                         # 入力 PDF の置き場
│  ├─ オグリキャップ.pdf
│  └─ オースミシャダイ.pdf
├─ images/                       # ドキュメント用画像
│  └─ image.png
├─ notebooks/                    # Jupyter ノートブック
│  └─ gb-demo.ipynb              # デモ用ノートブック
└─ infra/                        # インフラ関連
   ├─ langfuse/                  # Langfuse 設定（フォルダのみ追跡）
   └─ neo4j/                     # Neo4j Docker 設定
      └─ docker-compose.yml      # ローカル Neo4j 起動用
```

## 前提

- Python 3.11（uv で管理）
- uv（Python パッケージマネージャ）
- Neo4j Aura Free（クラウド / TLS）
- Docker / Docker Compose（ローカルで Neo4j や Langfuse を使う場合）

## セットアップ

1. uv のインストール（まだの場合）

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Python 環境の準備と依存関係をインストール

```bash
uv sync
cp .env.example .env
```

2. `.env` を編集して接続情報を設定します。
ローカル Neo4j を使う場合は `NEO4J_URI=bolt://neo4j:7687` に切り替えてください。

## Quick Start



```bash
cd infra/neo4j
docker compose up
```

`.env` を `bolt://neo4j:7687` に切り替えてから:

```bash
# ローカル Neo4j への抽出
uv run python -m src/scripts/extractor/kg_extract_toNeo4j.py
```

（任意）Langfuse を使う場合:

```bash

```

## スクリプト

このリポジトリには3つの主要なスクリプトがあります：

### 📄 JSON 抽出: `kg_extract_toJson.py`

PDF から Knowledge Graph を抽出し、JSON ファイルに保存します。

```bash
uv run python -m src.scripts.extractor.kg_extract_toJson
```

- **入力**: `data/オースミシャダイ.pdf`
- **出力**: `artifacts/kg_graph.json`
- **特徴**: Neo4j には書き込まず、JSON ファイルのみ生成

### 🔗 Neo4j 直接書込み: `kg_extract_toNeo4j.py`

PDF から Knowledge Graph を抽出し、Neo4j データベースに直接書き込みます。

```bash
uv run python -m src.scripts.extractor.kg_extract_toNeo4j
```

- **入力**: `data/オースミシャダイ.pdf`
- **出力**: Neo4j データベース
- **前提**: `.env` でNeo4j接続情報が設定済み

### 📊 JSON → Neo4j インポート: `writer_JsonToNeo4j.py`

既存の JSON ファイルを Neo4j データベースにインポートします。

```bash
uv run python -m src.scripts.writer.writer_JsonToNeo4j
```

- **入力**: `artifacts/kg_graph_オグリキャップ.json`
- **出力**: Neo4j データベース
- **前提**: Neo4j に APOC プラグインが必要

### 💡 使い分け

- **JSON で確認したい** → `kg_extract_toJson.py`
- **直接 Neo4j に保存** → `kg_extract_toNeo4j.py`  
- **JSON から Neo4j に移行** → `writer_JsonToNeo4j.py`
