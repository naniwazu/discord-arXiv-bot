# Query Parser リファクタリング計画

## 現在のコードの問題点

1. **単一責任原則の違反**
   - parse関数が全ての処理を担当（トークン化、検証、変換）
   - 123行の巨大な関数

2. **拡張性の欠如**
   - 新しい演算子（OR, NOT）の追加が困難
   - 括弧によるグループ化が実装不可能な構造

3. **エラーハンドリング不足**
   - エラー時はNoneを返すのみ
   - ユーザーへのフィードバックなし

4. **ハードコードされた値**
   - JST（-9時間）がハードコード
   - 将来のタイムゾーン対応が困難

5. **テスタビリティの低さ**
   - 巨大関数のため単体テストが困難
   - 内部ロジックの検証が不可能

## リファクタリング設計

### 1. クラス構造

```python
# query_parser.py
class QueryParser:
    """メインのパーサークラス"""
    def __init__(self, timezone_offset: int = -9):
        self.tokenizer = Tokenizer()
        self.transformer = QueryTransformer(timezone_offset)
        self.validator = QueryValidator()
    
    def parse(self, query: str) -> ParseResult:
        # トークン化 → 検証 → 変換
        pass

# tokenizer.py
class Token:
    """トークンを表現するデータクラス"""
    type: TokenType  # KEYWORD, AUTHOR, CATEGORY, etc.
    value: str
    position: int

class Tokenizer:
    """クエリをトークンに分解"""
    def tokenize(self, query: str) -> List[Token]:
        pass

# transformer.py
class QueryTransformer:
    """トークンをarXivクエリに変換"""
    def transform(self, tokens: List[Token]) -> arxiv.Search:
        pass

# validator.py
class QueryValidator:
    """トークンの検証"""
    def validate(self, tokens: List[Token]) -> ValidationResult:
        pass

# result.py
@dataclass
class ParseResult:
    """パース結果を格納"""
    success: bool
    search: Optional[arxiv.Search]
    error: Optional[str]
    debug_info: Optional[Dict[str, Any]]  # クエリ変換の可視化用
```

### 2. 定数の外部化

```python
# constants.py
CATEGORY_SHORTCUTS = {
    "cs": "cs.*",
    "physics": "physics.*",
    "math": "math.*",
    "stat": "stat.*",
}

CATEGORY_CORRECTIONS = {
    "cs.ai": "cs.AI",
    "cs.lg": "cs.LG",
    # ...
}

SORT_MAPPINGS = {
    "sd": (arxiv.SortCriterion.SubmittedDate, arxiv.SortOrder.Descending),
    "sa": (arxiv.SortCriterion.SubmittedDate, arxiv.SortOrder.Ascending),
    # ...
}
```

### 3. 実装の段階

#### Phase 1: 基本的なリファクタリング
1. 現在の機能を保ちながらクラス構造に分解
2. 単体テストの追加
3. エラーハンドリングの改善

#### Phase 2: 新構文の実装
1. プレフィックス（@, #, *, $）のサポート
2. デフォルトのタイトル検索
3. カテゴリショートカット
4. 新しいソート記法

#### Phase 3: 高度な機能
1. OR/NOT演算子
2. フレーズ検索
3. 括弧によるグループ化

## ディレクトリ構造

```
src/
├── query_parser/
│   ├── __init__.py
│   ├── parser.py         # メインパーサー
│   ├── tokenizer.py      # トークン化
│   ├── transformer.py    # クエリ変換
│   ├── validator.py      # 検証
│   ├── constants.py      # 定数定義
│   └── types.py          # 型定義
├── tools.py              # 後方互換性のため残す
└── tests/
    └── test_query_parser/
        ├── test_tokenizer.py
        ├── test_transformer.py
        └── test_parser.py
```

## 移行計画

1. 新しいquery_parserモジュールを作成
2. 既存のtools.pyから新モジュールを呼び出す（後方互換性）
3. 段階的に新機能を追加
4. 最終的にtools.pyを廃止

## テスト戦略

```python
# 基本的なテストケース
def test_simple_keyword():
    result = parser.parse("quantum")
    assert result.search.query == "ti:quantum"

def test_author_prefix():
    result = parser.parse("@hinton")
    assert result.search.query == "au:hinton"

def test_category_shortcut():
    result = parser.parse("#cs")
    assert result.search.query == "cat:cs.*"

def test_complex_query():
    result = parser.parse("quantum @hinton #cs.AI 20 rd")
    assert result.search.query == "ti:quantum AND au:hinton AND cat:cs.AI"
    assert result.search.max_results == 20
```