# arXiv Bot クエリ構文仕様書

## 1. 基本原則

### 1.1 設計思想
- **簡潔性優先**: 日常的な検索は最小限のキーストロークで
- **段階的複雑性**: 基本的な使い方から高度な検索まで段階的に学習可能
- **後方互換性**: 既存のクエリ形式も引き続きサポート

### 1.2 クエリの構成要素
```
[検索語] [オプション] [件数] [ソート]
```

## 2. 検索語の記法

### 2.1 基本検索（プレフィックスなし）
```
quantum          → ti:quantum （タイトル検索がデフォルト）
quantum neural   → ti:quantum AND ti:neural
```

### 2.2 ショートハンドプレフィックス
| 記号 | 意味 | 従来形式 | 例 |
|------|------|----------|-----|
| @ | 著者 | au: | @tanaka → au:tanaka |
| # | カテゴリ | cat: | #cs.AI → cat:cs.AI |
| $ | アブストラクト | abs: | $quantum → abs:quantum |
| % | 全フィールド | all: | %quantum → all:quantum |

### 2.3 フィールド混在検索
```
quantum @smith #cs.AI → ti:quantum AND au:smith AND cat:cs.AI
```

### 2.4 引用符によるフレーズ検索
```
"quantum computing" → ti:"quantum computing"
@"John Smith"       → au:"John Smith"
```

## 3. 検索演算子

### 3.1 OR検索（パイプ記号）
```
quantum | neural        → ti:quantum OR ti:neural
@smith | @jones        → au:smith OR au:jones
quantum | @smith       → ti:quantum OR au:smith
```

### 3.2 NOT検索（マイナス記号）
```
quantum -classical     → ti:quantum NOT ti:classical
#cs.AI -@smith        → cat:cs.AI NOT au:smith
```

### 3.3 グループ化（括弧）
```
(quantum | neural) @smith     → (ti:quantum OR ti:neural) AND au:smith
quantum -(classical | analog) → ti:quantum NOT (ti:classical OR ti:analog)
```

### 3.4 複合フィールド検索
```
ti,abs:quantum → ti:quantum OR abs:quantum （カンマで複数フィールド指定）
```

## 4. 日付指定

### 4.1 相対日付ショートカット
| キーワード | 意味 | 実際の期間 |
|------------|------|------------|
| today | 今日 | 今日の00:00から現在まで |
| yesterday | 昨日 | 昨日の00:00から23:59まで |
| week | 1週間 | 7日前の00:00から現在まで |
| month | 1ヶ月 | 30日前の00:00から現在まで |
| year | 1年 | 365日前の00:00から現在まで |

```
quantum week        → 過去1週間のquantum論文
@smith month 50     → smithさんの過去1ヶ月の論文を50件
```

### 4.2 絶対日付指定（従来形式も維持）
```
since:20240101      → 2024年1月1日以降
until:20241231      → 2024年12月31日まで
20240101-20241231   → 期間指定（新形式）
```

## 5. 結果制御

### 5.1 件数指定
```
quantum 50          → 50件取得（デフォルト10件）
quantum @smith 100  → 100件取得
```

### 5.2 ソート指定
| 記号 | 意味 | 従来形式 |
|------|------|----------|
| R/r | 関連度順 | 同じ |
| S/s | 投稿日順 | 同じ |
| L/l | 更新日順 | 同じ |
| ★ | 関連度順（新） | R |
| ↓ | 投稿日順（新） | S |
| ↻ | 更新日順（新） | L |

```
quantum 20 R        → 関連度順で20件
quantum week ↓      → 過去1週間を投稿日順
```

## 6. カテゴリショートカット

### 6.1 主要カテゴリの省略形
```
#ai     → cat:cs.AI
#ml     → cat:cs.LG
#cv     → cat:cs.CV
#nlp    → cat:cs.CL
#qc     → cat:quant-ph
#hep    → cat:hep-*（高エネルギー物理全般）
#cs     → cat:cs.*（コンピュータサイエンス全般）
```

## 7. 実装の段階的アプローチ

### Phase 1: 基本機能（優先実装）
- プレフィックスなしのタイトル検索
- ショートハンドプレフィックス（@, #, $）
- 基本的な日付ショートカット（today, week）
- 従来形式との互換性維持

### Phase 2: 演算子サポート
- OR検索（|）
- NOT検索（-）
- フレーズ検索（""）

### Phase 3: 高度な機能
- 括弧によるグループ化
- カテゴリショートカット
- 絵文字ソート記号

## 8. エラーハンドリング

### 8.1 エラーメッセージの改善
```python
# 現在: None を返す
# 改善案: 具体的なエラーメッセージ
"Invalid query: Unknown field 'foo' in 'foo:bar'"
"Invalid date format: Expected YYYYMMDD, got '2024/01/01'"
"Query too complex: Maximum 10 search terms allowed"
```

### 8.2 クエリ補完提案
```
入力: "quantm"（スペルミス）
提案: "Did you mean: quantum?"

入力: "cs.ai"（大文字小文字）
自動修正: "cat:cs.AI"
```

## 9. 使用例

### 9.1 日常的な使用例
```
# シンプルな検索
llm                     # LLMに関する論文
transformer 30          # Transformerの論文30件

# 著者とカテゴリ
@hinton #ai            # Hinton氏のAI論文
neural @lecun week     # LeCun氏の今週のニューラル論文

# 期間指定
quantum today          # 今日のquantum論文
"large language" month # 過去1ヶ月のLLM論文
```

### 9.2 高度な使用例
```
# OR検索
bert | gpt | llama @ai              # 主要LLMモデル
(quantum | neural) -classical 50    # 古典的でない量子・ニューラル論文50件

# 複合検索
ti,abs:transformer @vaswani since:20240101 100 R
# Vaswani氏の2024年以降のTransformer関連論文を関連度順で100件
```

## 10. 移行計画

### 10.1 後方互換性の保証
- 既存のクエリ形式は全て動作継続
- 新旧の記法を混在可能
- 段階的な機能追加

### 10.2 ユーザー教育
- /help コマンドでクイックリファレンス表示
- よく使う例を自動提案
- エラー時に正しい構文をサジェスト

## 11. 実装上の考慮事項

### 11.1 パーサーの設計
```python
# トークナイザーで記号を識別
# 優先順位: 引用符 > 括弧 > OR > AND > NOT
# 左から右への評価
```

### 11.2 パフォーマンス
- クエリのキャッシング
- 頻出パターンの事前コンパイル
- 構文エラーの早期検出

### 11.3 将来の拡張性
- プラグイン可能な演算子システム
- カスタムショートカットの定義
- ユーザー定義の検索テンプレート