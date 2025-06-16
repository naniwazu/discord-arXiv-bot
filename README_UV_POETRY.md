# UV と Poetry の使い分けガイド

## 推奨される使い分けパターン

### パターン1: UV メイン + Poetry は CI/CD のみ（推奨）

**ローカル開発**: UV を使用
```bash
# 仮想環境作成
uv venv

# 依存関係インストール
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# または pyproject.toml から直接
uv pip install -e ".[dev]"

# テスト実行
uv run pytest tests/

# サーバー起動
uv run python src/webhook_server.py
```

**CI/CD**: Poetry を使用（pyproject.toml の設定を活用）
- GitHub Actions で poetry を使用
- より厳密な依存関係管理

### パターン2: UV で Poetry を実行

```bash
# uvx を使って poetry コマンドを実行
uvx poetry install --with dev
uvx poetry run pytest tests/

# または uv tool を使用
uv tool install poetry
uv tool run poetry install
```

### パターン3: 用途別使い分け

**UV を使う場面**:
- 素早い環境構築
- 開発中の頻繁なパッケージ追加/削除
- ローカルでのテスト実行
- プロトタイピング

**Poetry を使う場面**:
- 依存関係のロック（poetry.lock）
- パッケージのビルド/公開
- 厳密なバージョン管理が必要な場合
- チーム開発での環境統一

## 実装例

### 1. requirements.txt を生成して UV で使用

```bash
# Poetry から requirements.txt を生成
poetry export -f requirements.txt -o requirements.txt --without-hashes
poetry export -f requirements.txt -o requirements-dev.txt --without-hashes --with dev

# UV で使用
uv pip install -r requirements.txt  # 本番依存関係
uv pip install -r requirements-dev.txt  # 開発依存関係
```

### 2. Makefile を UV 対応に更新

```makefile
# UV モードの追加
install-uv:
	uv pip install -r requirements.txt -r requirements-dev.txt

test-uv:
	uv run pytest tests/ -v

run-webhook-uv:
	uv run python src/webhook_server.py

# 環境変数で切り替え
ifdef USE_UV
  PYTHON_RUN = uv run
else
  PYTHON_RUN = poetry run
endif

test:
	$(PYTHON_RUN) pytest tests/ -v
```

### 3. 開発用スクリプトを UV 対応に

```bash
#!/bin/bash
# scripts/setup_dev_uv.sh

echo "Setting up development environment with UV..."

# UV がインストールされているか確認
if ! command -v uv &> /dev/null; then
    echo "UV not found. Please install UV first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 仮想環境作成
uv venv

# requirements.txt 生成（poetry.lock から）
if command -v poetry &> /dev/null; then
    poetry export -f requirements.txt -o requirements.txt --without-hashes
    poetry export -f requirements.txt -o requirements-dev.txt --without-hashes --with dev
else
    echo "Poetry not found. Using existing requirements files..."
fi

# 依存関係インストール
uv pip install -r requirements.txt -r requirements-dev.txt

echo "Setup complete! Activate the virtual environment with:"
echo "source .venv/bin/activate"
```

## ハイブリッドアプローチ（推奨）

### pyproject.toml に UV サポートを追加

```toml
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

# Poetry の設定も残す（後方互換性）
[tool.poetry]
# ... existing poetry config ...
```

### 統一コマンド

```bash
# run.sh - 環境に応じて適切なランナーを選択
#!/bin/bash

if [ -n "$USE_UV" ] || command -v uv &> /dev/null && [ ! -n "$USE_POETRY" ]; then
    echo "Using UV..."
    uv run "$@"
elif command -v poetry &> /dev/null; then
    echo "Using Poetry..."
    poetry run "$@"
else
    echo "Using system Python..."
    python "$@"
fi
```

## GitHub Actions での併用

```yaml
- name: Setup Python with UV
  uses: actions/setup-python@v4
  with:
    python-version: ${{ matrix.python-version }}

- name: Install UV
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "$HOME/.cargo/bin" >> $GITHUB_PATH

- name: Install dependencies with UV
  run: |
    uv venv
    uv pip install -r requirements.txt -r requirements-dev.txt

- name: Run tests
  run: |
    uv run pytest tests/
```

## メリット・デメリット

### UV を使うメリット
- 高速なパッケージインストール
- シンプルなコマンド
- pip と互換性がある
- キャッシュが効率的

### Poetry を残すメリット
- 依存関係の厳密な管理
- poetry.lock による再現性
- パッケージ公開機能
- 多くのプロジェクトで採用されている

## 結論

1. **ローカル開発では UV を使用**（高速で効率的）
2. **pyproject.toml は Poetry 形式を維持**（互換性のため）
3. **requirements.txt を自動生成**（UV での利用）
4. **CI/CD では両方サポート**（柔軟性）

この方法により、UV の速度とシンプルさを活用しながら、Poetry のエコシステムとの互換性も保てます。