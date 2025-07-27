# Slack PDF投稿機能 運用手順書

## 📋 概要
技術の泉シリーズ制作支援ツールに統合されたSlack PDF投稿機能の操作手順書です。PDF生成完了後に、対応するSlackチャネルへ自動投稿する機能を提供します。

## 🚀 機能開始手順

### 1. 環境確認
```bash
# 1. プロジェクトディレクトリに移動
cd /mnt/c/Users/tky99/dev/technical-fountain-series-support-tool

# 2. 仮想環境を有効化
source venv/bin/activate

# 3. アプリケーションを起動
python main.py
```

### 2. Slack Bot Token設定確認
- 環境変数`SLACK_BOT_TOKEN`が設定されていることを確認
- 設定されていない場合：
  ```bash
  export SLACK_BOT_TOKEN="xoxb-your-bot-token-here"
  ```

## 💡 基本的な使用方法

### Step 1: N番号入力
1. メインウィンドウの「Nコード入力」エリアに、PDFを投稿したいN番号を入力
2. **重要**: PDF投稿機能は1つのN番号のみ受け付けます

### Step 2: PDF投稿実行
1. **「PDF投稿」ボタン（オレンジ色）** をクリック
2. システムが以下を自動実行：
   - N番号の検証
   - チャネル番号の抽出（例: N01234 → 1234）
   - Slackワークスペース内の対応チャネル検索（例: n1234-xxx）
   - PDFファイルの自動検出

### Step 3: 確認ダイアログ
1. PDFファイルとチャネルが特定されると確認ダイアログが表示
2. 以下の情報を確認：
   - 投稿先チャネル名
   - PDFファイルパス
   - 投稿メッセージ（編集可能）
3. **「投稿」** をクリックして実行

### Step 4: 投稿完了
- 成功時：「PDF投稿が完了しました」メッセージ
- 失敗時：エラーメッセージと詳細

## ⚠️ 注意事項とエラー対応

### 入力エラー
**エラー**: 「N番号を入力してください」
- **対応**: Nコード入力エリアに有効なN番号を入力

**エラー**: 「PDF投稿は1つのN番号のみ指定してください」
- **対応**: 複数のN番号ではなく、1つのN番号のみ入力

**エラー**: 「正しいN番号を入力してください（例: N01234）」
- **対応**: N + 4桁以上の数字の形式で入力

### チャネル検索エラー
**エラー**: 「対応するSlackチャネルが見つかりません」
- **原因**: チャネル名が「n数字-」パターンに一致しない
- **対応**: 
  1. Slackワークスペースでチャネル名を確認
  2. 「n1234-book-title」のような命名規則に従っているか確認
  3. Botがチャネルに招待されているか確認

### PDFファイル検索エラー
**エラー**: 「PDFファイルが見つかりません」
- **原因**: 指定されたディレクトリにPDFファイルが存在しない
- **対応**:
  1. 出力ディレクトリを確認（通常は`G:\.shortcut-targets-by-id\...`）
  2. 該当するN番号のフォルダが存在するか確認
  3. PDFファイルが生成されているか確認

### Slack API エラー
**エラー**: 「Slack APIエラー: invalid_auth」
- **原因**: Bot Tokenが無効または未設定
- **対応**: 正しいBot Tokenを設定

**エラー**: 「Slack APIエラー: channel_not_found」
- **原因**: チャネルが存在しないか、Botが招待されていない
- **対応**: 
  1. チャネルの存在を確認
  2. Botをチャネルに招待：`/invite @TechZip PDF投稿Bot`

**エラー**: 「Slack APIエラー: file_uploads_disabled」
- **原因**: ワークスペースでファイルアップロードが無効
- **対応**: ワークスペース管理者に設定確認を依頼

## 🔧 設定とトラブルシューティング

### 設定ファイル確認
- **config/settings.json**: 出力ディレクトリの設定
- **.env**: Slack Bot Token設定

### ログの確認
```bash
# 詳細なログ出力を有効化
export TECHZIP_LOG_LEVEL=DEBUG
python main.py
```

### テスト投稿
- **推奨**: 最初に`n9999-bottest`チャネルでテスト実行
- テスト用N番号: `N09999`

## 📁 関連ファイル

### 主要実装ファイル
- `src/slack_pdf_poster.py` - PDF投稿のメインロジック
- `gui/pdf_post_dialog.py` - 確認ダイアログ
- `gui/components/input_panel.py` - UI統合
- `gui/main_window.py` - メインウィンドウ統合

### テストファイル
- `tests/test_slack_pdf_poster.py` - 単体テスト
- `test_integration_simple.py` - 統合テスト

## 🆘 緊急時対応

### 機能無効化
何らかの問題で機能を一時的に無効化する場合：
```python
# gui/components/input_panel.py の237行目付近
def on_pdf_post_clicked(self):
    """PDF投稿ボタンがクリックされた時の処理"""
    self.show_error("PDF投稿機能は一時的に無効化されています。")
    return  # この行を追加して機能を無効化
```

### Bot Token の緊急変更
```bash
# 新しいBot Tokenを設定
export SLACK_BOT_TOKEN="xoxb-new-token-here"

# アプリケーションを再起動
python main.py
```

## 📞 サポート

### 技術的な問題
- 実装者：Claude Code Development Kit
- ログファイル：`logs/` ディレクトリ（自動生成）

### Slack関連の問題
- ワークスペース管理者に連絡
- Bot設定の確認：https://api.slack.com/apps

---

**最終更新**: 2025-01-27
**バージョン**: 1.0.0
**対応プラットフォーム**: Windows WSL, Linux