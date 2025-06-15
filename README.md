# discord-arXiv-bot
arXiv上のプレプリントを検索・自動取得するためのbotです。

* Discord Botとして動作し、スラッシュコマンドまたはWebhook経由で利用できます。

## 操作方法
検索には `/arxiv` スラッシュコマンドを使用します。
```
/arxiv query: [検索クエリ]
```

クエリで指定できる内容は以下（順不同）です。
* 検索ワード  「(タグ):(検索ワード)」の形式で入力してください。
  * タグの種類は[こちら](https://info.arxiv.org/help/api/user-manual.html#:~:text=This%20returns%20nine%20results.%20The%20following%20table%20lists%20the%20field%20prefixes%20for%20all%20the%20fields%20that%20can%20be%20searched) を参照ください。
  * 検索ワードはカンマ区切りで、スペースを含めず入力してください。
  * 複数のタグを併用して検索することも可能です。現在はAND検索のみに対応しています。
  * `cat`等は完全一致検索なので、適宜ワイルドカード`*`を用いて検索してください。（例：`cat:cond-mat*`）
* 表示件数
  * 1～1000までを入力でき、それ以外の入力は無視されます。
  * デフォルトは10件です。
* 表示順
  * アルファベット1文字で、` r:relevance, s: submitted date, l:last updated date`に対応します。
  * デフォルトは`s`です。
* 期間
  * `(since|until):(YYYYDDMM|YYYYDDMMhhmm|YYYYDDMMhhmmss)`の形式で指定してください。JSTで`since`以降/`until`以前の論文を検索します。両方指定しても、片方のみでも問題ありません。

## 使用例
```
/arxiv query: ti:attention,is,all,you,need
/arxiv query: cat:cs.CL 20 r
/arxiv query: au:Hinton since:20240101
```

## 自動取得について
チャンネル名を`auto`で始めると、トピック（チャンネル設定から書き込めます）に入力したクエリに従って、毎日日本時間朝6時に48~72時間前に投稿された論文を自動取得します。