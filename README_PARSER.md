# Query Parser Implementation Summary

## Overview
新しいクエリパーサーを実装しました。Phase 1の基本機能が完成し、以下の新構文をサポートしています：

## 実装済み機能 (Phase 1)

### 基本検索
- `quantum` → `ti:quantum` （タイトル検索がデフォルト）
- `quantum computing` → `ti:quantum AND ti:computing`

### プレフィックス検索
- `@hinton` → `au:hinton` （著者）
- `#cs.AI` → `cat:cs.AI` （カテゴリ）
- `*quantum` → `all:quantum` （全フィールド）
- `$neural` → `abs:neural` （アブストラクト）

### カテゴリ機能
- **ショートカット**: `#cs` → `cat:cs.*`
- **大文字小文字修正**: `#cs.ai` → `cat:cs.AI`

### その他の機能
- **件数指定**: `quantum 50` （1-1000の範囲）
- **ソート指定**: 
  - `sd`/`s` - 投稿日降順（デフォルト）
  - `rd`/`r` - 関連度降順
  - `ld`/`l` - 更新日降順
  - `sa`, `ra`, `la` - 昇順版
- **フレーズ検索**: `"quantum computing"` → `ti:"quantum computing"`

### クエリ変換の可視化
webhook_server.pyに組み込まれ、実行されたクエリが表示されます：
```
→ Query: `ti:quantum AND au:hinton` (20 results, Relevance Descending)
```

## ファイル構成
```
src/
├── query_parser/
│   ├── __init__.py       # モジュールエクスポート
│   ├── parser.py         # メインパーサー
│   ├── tokenizer.py      # トークン化処理
│   ├── transformer.py    # クエリ変換
│   ├── validator.py      # 検証処理
│   ├── constants.py      # 定数定義
│   └── types.py          # 型定義
└── tools.py              # 後方互換性維持

tests/
└── test_query_parser/
    └── test_parser.py    # パーサーのテスト
```

## 後方互換性
- tools.pyは新しいパーサーを使用し、エラー時は従来の実装にフォールバック
- 既存のクエリ形式も引き続き動作

## 今後の実装予定

### Phase 2: 演算子サポート
- OR検索: `quantum | neural`
- NOT検索: `quantum -classical`
- 昇順ソート: `sa`, `ra`, `la`

### Phase 3: 高度な機能
- 括弧によるグループ化: `(quantum | neural) @hinton`
- 複雑な入れ子構造のサポート

## テスト方法
```bash
# 簡易テスト
python3 test_parser_simple.py

# poetryがある環境では
poetry run pytest tests/test_query_parser/
```