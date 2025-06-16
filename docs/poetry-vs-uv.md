# Poetry vs UV 比較ガイド

## 概要

### Poetry
- **開発元**: Poetry Foundation
- **リリース**: 2018年
- **言語**: Python製
- **目的**: Pythonプロジェクトの依存関係管理とパッケージング

### UV
- **開発元**: Astral (Ruffの開発元)
- **リリース**: 2024年
- **言語**: Rust製
- **目的**: 高速なPythonパッケージインストーラー・リゾルバー

## 主な違い

### 1. パフォーマンス

**UV**
- ⚡ **10-100倍高速**
- Rust製で並列処理に優れる
- 効率的なキャッシング
```bash
# 例: numpy, pandas, scipy のインストール
uv pip install numpy pandas scipy  # ~2秒
```

**Poetry**
- 🐌 相対的に遅い
- Python製でGILの制約あり
```bash
# 同じパッケージのインストール
poetry add numpy pandas scipy  # ~30秒
```

### 2. 機能範囲

**Poetry**
```
✅ 依存関係管理（poetry.lock）
✅ 仮想環境管理
✅ パッケージビルド
✅ PyPIへの公開
✅ バージョン管理
✅ スクリプト定義
✅ グループ化された依存関係
```

**UV**
```
✅ 高速なパッケージインストール
✅ 仮想環境管理
✅ pip互換性
✅ requirements.txt対応
❌ ロックファイル（開発中）
❌ パッケージビルド
❌ PyPIへの公開
```

### 3. 設定ファイル

**Poetry**
```toml
# pyproject.toml
[tool.poetry]
name = "my-project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.10"
requests = "^2.31.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
```

**UV**
```txt
# requirements.txt または pyproject.toml
requests>=2.31.0
pytest>=7.4.0
```

### 4. コマンド比較

| タスク | Poetry | UV |
|--------|--------|-----|
| 仮想環境作成 | `poetry install` | `uv venv` |
| パッケージ追加 | `poetry add requests` | `uv pip install requests` |
| 開発依存追加 | `poetry add --group dev pytest` | `uv pip install pytest` |
| スクリプト実行 | `poetry run python main.py` | `uv run python main.py` |
| 依存関係更新 | `poetry update` | `uv pip install --upgrade` |
| ロックファイル | `poetry.lock` | なし（将来実装予定） |

### 5. ワークフロー比較

**Poetry ワークフロー**
```bash
# プロジェクト初期化
poetry new my-project
cd my-project

# 依存関係追加
poetry add fastapi uvicorn
poetry add --group dev pytest black

# インストール
poetry install

# 実行
poetry run python main.py
poetry run pytest
```

**UV ワークフロー**
```bash
# プロジェクト初期化
mkdir my-project && cd my-project
uv venv

# 依存関係追加
uv pip install fastapi uvicorn
uv pip install pytest black

# 実行
uv run python main.py
uv run pytest
```

## 使い分けの指針

### Poetry を選ぶべき場合
- 📦 **パッケージを公開する予定**
- 🔒 **厳密な依存関係管理が必要**（poetry.lock）
- 👥 **チーム開発で環境を完全に統一したい**
- 📋 **複雑な依存関係グループ管理**
- 🔧 **成熟したツールチェーンが必要**

### UV を選ぶべき場合
- ⚡ **インストール速度が重要**
- 🚀 **CI/CDの時間を短縮したい**
- 🛠️ **シンプルなプロジェクト**
- 💻 **ローカル開発の効率重視**
- 🔄 **pip からの移行を簡単にしたい**

## 実際の速度比較

```bash
# テストプロジェクトでの比較（一般的なWebアプリの依存関係）

# Poetry
time poetry install
# real    0m45.123s

# UV
time uv pip install -r requirements.txt
# real    0m3.456s
```

## 移行パス

### Poetry → UV
```bash
# requirements.txt を生成
poetry export -f requirements.txt -o requirements.txt

# UV で使用
uv venv
uv pip install -r requirements.txt
```

### UV → Poetry
```bash
# 現在の環境をエクスポート
uv pip freeze > requirements.txt

# Poetry プロジェクトを初期化
poetry init
poetry add $(cat requirements.txt)
```

## 将来の展望

### UV のロードマップ
- 🔒 ロックファイルのサポート（開発中）
- 📦 プロジェクト管理機能
- 🔧 より多くのpoetry機能の実装

### Poetry の対応
- ⚡ パフォーマンス改善の取り組み
- 🦀 Rust製の依存関係リゾルバーの検討

## まとめ

**現時点での推奨**:
1. **本番プロジェクト**: Poetry（安定性と機能）
2. **ローカル開発**: UV（速度）
3. **ハイブリッド**: Poetry でロック、UV でインストール

```bash
# ハイブリッドアプローチの例
poetry lock  # 依存関係の解決とロック
poetry export -f requirements.txt -o requirements.txt
uv pip install -r requirements.txt  # 高速インストール
```

両ツールは補完関係にあり、プロジェクトの要件に応じて使い分けることが重要です。