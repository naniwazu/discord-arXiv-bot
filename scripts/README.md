# Discord Bot Command Management Scripts

新しいクエリ構文に対応したDiscordスラッシュコマンドを管理するためのスクリプト集です。

## 🚀 クイックスタート

### 1. 既存コマンドの確認
```bash
python scripts/list_commands.py
```
現在登録されているすべてのスラッシュコマンドを表示します。

### 2. 古いコマンドのクリーンアップ
```bash
python scripts/cleanup_all_commands.py
```
⚠️ **注意**: すべてのスラッシュコマンドを削除します（アーカイブサーチ、arxivなど）

### 3. 新しいコマンドの登録
```bash
python scripts/update_commands.py
```
新しいクエリ構文に対応した `/arxiv` コマンドを登録します。

## 📝 スクリプト詳細

### `list_commands.py`
- 現在登録されているコマンドを一覧表示
- コマンドID、説明、オプションを表示
- ボット招待リンクも生成

### `cleanup_all_commands.py` 
- **すべて**のスラッシュコマンドを削除
- 削除前に確認プロンプト
- 削除結果の詳細レポート

### `update_commands.py`
- 古い `arxiv` コマンドを削除してから新しいものを登録
- 新しいクエリ構文に対応した説明文
- 使用例とボット招待リンクを表示

### `register_help_command.py`
- `/arxiv` と `/arxiv-help` の両方を登録
- ヘルプコマンドで詳細な構文ガイドを提供

## 🔧 環境変数

すべてのスクリプトは以下の環境変数が必要です：

```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
```

## 📋 推奨手順

1. **現状確認**: `list_commands.py` で既存コマンドを確認
2. **クリーンアップ**: `cleanup_all_commands.py` で古いコマンドを全削除
3. **新規登録**: `update_commands.py` で新しいコマンドを登録
4. **動作確認**: Discordで `/arxiv` コマンドをテスト

## 🎯 新しいクエリ構文の例

登録後、以下のような高度なクエリが使用可能になります：

```
/arxiv query: quantum computing
/arxiv query: quantum | neural
/arxiv query: @hinton #cs.AI 50 ra
/arxiv query: (bert | gpt | t5) @google -survey
/arxiv query: ti:(transformer | attention) #cs.AI
```

## ⚠️ 注意事項

- `cleanup_all_commands.py` は**すべて**のコマンドを削除します
- コマンド更新後、Discordクライアントの再読み込み（Ctrl+R）が必要な場合があります
- ボットを新しいサーバーに招待する際は、生成された招待リンクを使用してください