# UV vs Poetry 最新比較（2024年版）

## 重要な発見：UVは既にフル機能のプロジェクト管理ツール

### UV の現在の機能（公式ドキュメントより）

✅ **プロジェクト管理**
- `uv init` でプロジェクト初期化
- `pyproject.toml` の完全サポート
- `.python-version` で Python バージョン管理

✅ **ロックファイル**
- `uv.lock` ファイルをサポート（TOML形式）
- クロスプラットフォーム対応
- 人間が読める形式

✅ **依存関係管理**
- `uv add/remove` で依存関係を管理
- バージョン制約のサポート
- Git リポジトリからの直接インストール

✅ **ビルド機能**
- `uv build` でパッケージビルド
- `.whl` と `.tar.gz` の生成

✅ **その他**
- ワークスペースのサポート
- グローバルキャッシュで効率的
- pip 互換インターフェース

## このプロジェクトでの推奨

### 🎯 **UV を推奨する理由**

1. **速度**: 10-100倍高速
2. **機能**: Poetry とほぼ同等の機能を既に実装
3. **シンプルさ**: pip に近い使用感
4. **将来性**: Astral 社（Ruff 開発元）による活発な開発

### UV での移行手順

```bash
# 1. 現在の Poetry プロジェクトから UV へ移行
cd discord-arxiv-bot

# 2. UV をインストール（まだの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Poetry の依存関係を UV 形式に変換
uv pip compile pyproject.toml -o requirements.txt

# 4. UV プロジェクトとして初期化
uv venv
uv pip sync requirements.txt

# 5. 今後は UV コマンドを使用
uv add fastapi  # 依存関係追加
uv lock         # ロックファイル更新
uv sync         # 依存関係同期
uv run python src/webhook_server.py  # 実行
```

## 機能比較表（2024年版）

| 機能 | UV | Poetry |
|------|-----|--------|
| **速度** | ⚡ 超高速 (Rust製) | 🐌 遅い (Python製) |
| **ロックファイル** | ✅ uv.lock | ✅ poetry.lock |
| **pyproject.toml** | ✅ 対応 | ✅ 対応 |
| **依存関係追加** | ✅ uv add | ✅ poetry add |
| **ビルド** | ✅ uv build | ✅ poetry build |
| **公開** | ❓ 未確認 | ✅ poetry publish |
| **仮想環境** | ✅ 自動管理 | ✅ 自動管理 |
| **Python バージョン管理** | ✅ .python-version | ✅ pyproject.toml |
| **ワークスペース** | ✅ 対応 | ❌ 非対応 |
| **キャッシュ効率** | ✅ グローバルキャッシュ | 🔺 プロジェクト単位 |

## 結論

**このプロジェクトには UV を推奨します**

理由：
1. Discord Bot は頻繁にデプロイ・更新される → UV の速度が有利
2. パッケージ公開の予定なし → Poetry の publish 機能不要
3. 依存関係は比較的シンプル → UV で十分管理可能
4. CI/CD の高速化 → デプロイ時間の短縮

## 実装提案

```toml
# pyproject.toml を UV 用に最適化
[project]
name = "arxiv-discord-bot"
version = "0.1.0"
description = "Discord bot for searching and sharing arXiv research papers"
requires-python = ">=3.10"
dependencies = [
    "discord-py>=2.3.2",
    "arxiv>=2.0.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "pynacl>=1.5.0",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0", 
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 移行コマンド

```bash
# Poetry を完全に UV に置き換え
uv init --name arxiv-discord-bot
uv add discord-py arxiv fastapi uvicorn pynacl httpx
uv add --dev pytest pytest-asyncio pytest-cov ruff
uv lock
```