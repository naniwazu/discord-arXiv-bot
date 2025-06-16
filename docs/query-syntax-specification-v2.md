# arXiv Bot クエリ構文仕様書 v2

## 1. 基本設計

### 1.1 設計方針
- **簡潔性最優先**: 最小限のキーストロークで日常的な検索を実現
- **直感的な記法**: 覚えやすく推測しやすい構文
- **段階的実装**: 基本機能から順次拡張

### 1.2 基本構造
```
/arxiv [検索語] [オプション] [件数] [ソート]
/arxiv-detail [詳細クエリ]  # 複雑な検索用（新構文）
```

## 2. 検索語の記法

### 2.1 基本検索
```
quantum          → タイトル検索（デフォルト）
quantum neural   → quantum AND neural（タイトル内）
```

### 2.2 ショートハンドプレフィックス
| 記号 | 意味 | 例 |
|------|------|-----|
| @ | 著者 | @tanaka |
| # | カテゴリ | #ai |
| $ | アブストラクト | $quantum |
| * | 全フィールド | *quantum |

### 2.3 フレーズ検索
```
"quantum computing"  → 完全一致フレーズ
"large language model" @hinton → LLMとHinton氏
```

## 3. 検索演算子

### 3.1 OR検索
```
quantum | neural      → quantum OR neural
@smith | @jones      → smith氏 OR jones氏
```

### 3.2 NOT検索
```
quantum -classical   → quantum NOT classical
#ai -@smith         → AI分野でsmith氏以外
```

### 3.3 括弧によるグループ化
```
(quantum | neural) @smith     → (quantum OR neural) AND smith
llm -(bert | gpt)            → LLMだがBERTでもGPTでもない
```

## 4. カテゴリ指定

### 4.1 基本ルール
- arXivのカテゴリ名をそのまま使用（ドットを含む）
- #プレフィックスの後に正式なカテゴリ名を記述
- 大文字小文字は自動修正される

### 4.2 使用例
```
#cs.AI      → 人工知能
#cs.LG      → 機械学習（Learning）
#cs.CV      → コンピュータビジョン
#cs.CL      → 計算言語学（NLP）
#quant-ph   → 量子物理
#stat.ML    → 統計的機械学習
#math.CO    → 組合せ論
#physics.optics → 光学
```

### 4.3 カテゴリグループ（ワイルドカード対応）

arXiv APIがワイルドカードをサポートしているため、シンプルな変換で実装可能：

```python
CATEGORY_SHORTCUTS = {
    "cs": "cs.*",          # コンピュータサイエンス全体
    "physics": "physics.*", # 物理学全体
    "math": "math.*",       # 数学全体
    "stat": "stat.*",       # 統計学全体
    "econ": "econ.*",       # 経済学全体
    "q-bio": "q-bio.*",     # 定量生物学全体
    "q-fin": "q-fin.*",     # 定量ファイナンス全体
}
```

**使用例と変換:**
```
#cs          → cat:cs.*       （CS分野全体）
#physics     → cat:physics.*   （物理分野全体）
#math        → cat:math.*      （数学分野全体）
#cs.AI       → cat:cs.AI       （AI分野のみ）
```

## 5. ソート指定

### 5.1 ソート順の指定
| 記号 | 意味 | 順序 |
|------|------|------|
| sd | 投稿日順 | 降順（新しい順）**デフォルト** |
| sa | 投稿日順 | 昇順（古い順） |
| rd | 関連度順 | 降順（高い順） |
| ra | 関連度順 | 昇順（低い順） |
| ld | 更新日順 | 降順（新しい順） |
| la | 更新日順 | 昇順（古い順） |

```
quantum 20      → 投稿日の新しい順で20件（デフォルト）
quantum 20 rd   → 関連度の高い順で20件
llm 50 sa      → 投稿日の古い順で50件
```

### 5.2 省略形も可能
```
s  → sd（投稿日降順）
r  → rd（関連度降順）
l  → ld（更新日降順）
```

## 6. 件数指定
```
quantum 30      → 30件取得
@hinton 100     → Hinton氏の論文100件
```
- デフォルト: 10件
- 最大: 1000件

## 7. 実装の簡略化

### 7.1 大文字小文字の自動修正

#### カテゴリ名の正規化
正しいカテゴリ名のマッピングテーブルを使用：
```python
CATEGORY_MAP = {
    "cs.ai": "cs.AI",
    "cs.lg": "cs.LG", 
    "cs.cv": "cs.CV",
    "cs.cl": "cs.CL",
    "stat.ml": "stat.ML",
    # ... 他のカテゴリも同様
}

# 入力を小文字化してからマッピング
user_input = "#CS.ai"
normalized = user_input[1:].lower()  # "cs.ai"
correct_category = CATEGORY_MAP.get(normalized, normalized)  # "cs.AI"
```

#### 著者名の処理
arXiv APIは著者名の大文字小文字を区別しないため、そのまま使用可能：
```
入力: @Hinton → そのまま: au:Hinton
入力: @LeCun → そのまま: au:LeCun
入力: @hinton → そのまま: au:hinton
```
※ 全て同じ結果を返す

### 7.2 エラーメッセージ
```
"Unrecognized field: foo"
"Number of results must be between 1-1000"
"Category not found: #xyz"
```

## 8. 詳細クエリモード（/arxiv-detail）

複雑な検索のための専用モード。新構文とarXiv公式構文の両方をサポート：

### 8.1 新構文での使用
```
/arxiv-detail (quantum | neural) @hinton -@lecun (#cs.AI | #cs.LG) 100 rd
```

### 8.2 arXiv公式構文での使用
```
/arxiv-detail (ti:quantum OR ti:neural) AND au:hinton NOT au:lecun AND (cat:cs.AI OR cat:cs.LG)
```

このモードの利点：
- 文字数制限を気にせず複雑なクエリを記述可能
- 新構文・公式構文どちらでも使用可能
- 公式ドキュメントのクエリをそのまま使える

## 9. 時刻処理（JST対応）

### 9.1 現在の仕様
- scheduler.pyの自動検索では、日付を72-48時間前として処理
- 時刻の入力・表示は暗黙的にJSTを想定

### 9.2 Phase 1の実装
- JSTをデフォルトとして使用
- 時刻関連の処理は全てJST基準

### 9.3 海外展開時の推奨仕様

**階層的タイムゾーン設定**
```
1. サーバーレベル設定（管理者が設定）
   /arxiv-config timezone America/New_York
   
2. チャンネルレベル設定（モデレーターが設定）
   /arxiv-config channel-timezone Europe/London
   
3. ユーザーレベル設定（個人設定）
   /arxiv-config my-timezone Asia/Tokyo
```

**優先順位**: ユーザー設定 > チャンネル設定 > サーバー設定 > デフォルト(UTC)

**スマートデフォルト**
- 新規サーバー: Discordサーバーのリージョンから推測
- 北米East → America/New_York
- ヨーロッパ → Europe/London  
- アジア → Asia/Tokyo

**自動検索（scheduler）の時刻表示**
```
# 各タイムゾーンで表示
Papers from Dec 25 09:00 - Dec 26 09:00 (EST)
Papers from Dec 25 14:00 - Dec 26 14:00 (UTC)
Papers from Dec 25 23:00 - Dec 26 23:00 (JST)
```

**相対時刻のサポート**
- "today", "yesterday", "this week" → 設定されたタイムゾーンで解釈
- "3 days ago", "last 24 hours" → タイムゾーン非依存

**arXiv公開スケジュールの考慮**
- arXivは米国東部時間で運営（締切: 14:00 EST）
- 各タイムゾーンでの締切時刻を表示
- 例: "Next deadline: 04:00 JST (in 5 hours)"

## 10. 使用例

### 10.1 日常的な使用
```
# シンプルな検索
llm                     # LLMのタイトル検索
transformer 30          # Transformer論文30件

# 著者とカテゴリ
@hinton                 # Hinton氏の全論文
#cs.AI transformer      # AI分野のTransformer論文
@lecun #cs.LG 50       # LeCun氏の機械学習論文50件

# 演算子の使用
bert | gpt             # BERTまたはGPT
neural -cnn            # ニューラルだがCNNではない
*quantum #physics.*    # 物理分野の量子関連（全フィールド）
```

### 10.2 やや高度な使用
```
(bert | gpt | t5) @google #cs.CL 100
# Google著者のNLP分野でBERT/GPT/T5関連を新しい順で100件（デフォルト）

"vision transformer" -@dosovitskiy #cs.CV 
# ViTに関するがDosovitskiy氏以外のCV論文
```

## 11. 実装優先順位

### Phase 1: 基本検索機能（一括実装）
```
# これらは同じパーサーロジックで実装可能
- タイトル検索（デフォルト）
- プレフィックス検索（@著者、#カテゴリ、*全フィールド、$アブストラクト）
- カテゴリショートカット（#cs → cat:cs.*）
- カテゴリ名の大文字小文字修正
- 件数指定（1-1000）
- 基本ソート（sd, rd, ld + 省略形 s/r/l）
```

### Phase 2: クエリ演算子
```
# トークナイザーの拡張が必要
- フレーズ検索（""）
- OR検索（|）
- NOT検索（-）
- ソート昇順（sa, ra, la）
```

### Phase 3: 高度な機能
```
# パーサーの再帰処理が必要
- 括弧によるグループ化
- 複雑な入れ子構造のサポート
```

## 12. クエリ変換の可視化

### 12.1 変換結果の表示
ユーザーが入力したクエリがどのようにarXiv APIクエリに変換されたかを表示する：

```
User input: quantum @hinton #cs.AI 20 rd
Query: ti:quantum AND au:hinton AND cat:cs.AI
Results: 20, Sort: Relevance (Descending)
```

### 12.2 表示例
```
# Simple search
Input: llm 30
→ Query: ti:llm (30 results, submitted date desc)

# Category group search
Input: quantum #cs 20
→ Query: ti:quantum AND cat:cs.* (20 results, submitted date desc)

# Complex search
Input: (bert | gpt) @google -@bengio #cs.CL 50 rd
→ Query: (ti:bert OR ti:gpt) AND au:google NOT au:bengio AND cat:cs.CL
  (50 results, relevance desc)

# Error case
Input: quantum foo:bar
→ Error: Unrecognized field 'foo'
```

### 12.3 実装方法
- Discordの返信メッセージに変換結果を含める
- エラー時は具体的な問題箇所を指摘
- デバッグモードで詳細な変換過程を表示可能

## 13. パーサー実装のポイント

### 13.1 トークン化の優先順位
1. 引用符で囲まれたフレーズ
2. プレフィックス付きトークン（@, #, $, *）
3. 演算子（|, -）
4. 数値（件数）
5. ソート指定（sd, rd, ld, sa, ra, la）
6. 通常の単語

### 13.2 簡単な実装アプローチ
```python
# 正規表現でトークンを抽出
# プレフィックスごとに処理
# 最後にAND結合してクエリ生成
```