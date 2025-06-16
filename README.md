# discord-arXiv-bot
arXiv上のプレプリントを検索・自動取得するためのbotです。

* Discord Botとして動作し、スラッシュコマンドまたはWebhook経由で利用できます。

## 操作方法
検索には `/arxiv` スラッシュコマンドを使用します。
```
/arxiv query: [検索クエリ]
```

### クエリ構文

#### 基本的な検索
* **キーワード検索**: `quantum computing` (デフォルトでタイトル検索)
* **フィールド指定**:
  * `@author` - 著者検索
  * `#category` - カテゴリ検索 (例: `#cs.AI`, `#physics`)
  * `*keyword` - 全フィールド検索
  * `$keyword` - アブストラクト検索
  * `"phrase search"` - フレーズ検索

#### 高度な検索 (OR/NOT演算子)
* **OR検索**: `quantum | neural` (quantumまたはneural)
* **NOT検索**: `quantum -classical` (quantumだが、classicalは除外)
* **複合検索**: `(bert | gpt) @hinton -@lecun` (bertまたはgptで、hintonが著者、lecunは除外)

#### グループ化と括弧
* **括弧グループ**: `(quantum | neural) computing` 
* **フィールドグループ**: `@(hinton lecun)` → 両方が著者の論文
* **arXivスタイル**: `ti:(quantum computing)` - タイトルに両方のキーワード

#### 表示オプション
* **件数**: `50` (1-1000件、デフォルト10件)
* **ソート**: 
  * `s`/`sd` - 投稿日降順 (デフォルト)
  * `sa` - 投稿日昇順
  * `r`/`rd` - 関連度降順
  * `ra` - 関連度昇順
  * `l`/`ld` - 更新日降順
  * `la` - 更新日昇順

## 使用例

### 基本的な検索
```
/arxiv query: quantum computing
/arxiv query: @hinton #cs.AI 20 ra
/arxiv query: "attention is all you need" @vaswani
```

### 高度な検索
```
/arxiv query: (bert | gpt | t5) @google 50 sa
/arxiv query: quantum -classical @(hinton lecun)
/arxiv query: (#cs.AI | #cs.LG) machine learning -survey
```

### 複雑なクエリ
```
/arxiv query: (quantum | neural) computing @hinton -(classical | traditional) 30 r
/arxiv query: ti:(transformer | attention) au:(vaswani | hinton) #cs.AI
```

## 自動取得について
チャンネル名を`auto`で始めると、トピック（チャンネル設定から書き込めます）に入力したクエリに従って、毎日日本時間朝6時に48~72時間前に投稿された論文を自動取得します。