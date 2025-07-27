# TechZip Slack統合機能 Phase 1 仕様書

最終更新: 2025-01-27

## 概要

技術の泉シリーズ制作支援ツール（TechZip）にSlack投稿機能を統合し、PDF生成から配布までのワークフローを自動化する。

## 機能要件

### FR001: Slack Bot作成と設定
- Slack Appを新規作成
- Bot Userを設定
- 必要なOAuth Scopesを設定
  - files:write（PDF投稿）
  - chat:write（メッセージ投稿）
  - groups:read（プライベートチャネル読取）
  - groups:write（Phase 2用・事前設定）
  - incoming-webhook（Phase 2用・事前設定）

### FR002: Bot一括チャネル登録
- 管理者権限での一括招待スクリプト作成
- 全ての技術の泉プロジェクトチャネルへBotを参加させる
- エラーハンドリング（既に参加済みの場合など）

### FR003: PDF自動投稿機能
- PDF生成完了後の自動Slack投稿
- チャネル名の自動判定（リポジトリ名 = チャネル名）
- 定型文テンプレートによるメッセージ生成
- 投稿成功/失敗の通知

### FR004: GUI統合
- メインウィンドウに「Slack投稿設定」セクション追加
- 「完了後Slackに投稿」チェックボックス
- 投稿メッセージのプレビュー機能
- Bot Token設定画面（初回のみ）

### FR005: 設定管理
- Bot Tokenの暗号化保存
- デフォルトメッセージテンプレート設定
- 自動投稿のON/OFF設定

## 非機能要件

### NFR001: セキュリティ
- Bot Tokenは暗号化して保存
- 環境変数での設定も可能

### NFR002: パフォーマンス
- Slack API Rate Limitを考慮（50+ requests/minute）
- ファイルサイズ制限: 1GB

### NFR003: エラーハンドリング
- チャネル不在時の対応
- Bot未参加時の対応
- ネットワークエラー時のリトライ

## 技術仕様

### 使用ライブラリ
- slack-sdk（Python用Slack SDK）
- cryptography（トークン暗号化用）

### API設計
```python
class SlackIntegration:
    def __init__(self, bot_token: str):
        """Slack統合の初期化"""
        
    def post_pdf_to_channel(
        self,
        pdf_path: str,
        repo_name: str,
        message_template: str
    ) -> dict:
        """PDFをSlackチャネルに投稿"""
        
    def get_channel_id_by_name(self, channel_name: str) -> str:
        """チャネル名からチャネルIDを取得"""
        
    def test_connection(self) -> bool:
        """Slack接続テスト"""
```

### GUI拡張仕様
- QGroupBox: "Slack投稿設定"
  - QCheckBox: "PDF生成後にSlackに自動投稿"
  - QPushButton: "Bot設定..."
  - QTextEdit: "投稿メッセージプレビュー"

### 設定ファイル構造
```json
{
  "slack": {
    "enabled": false,
    "bot_token": "encrypted_token_here",
    "default_message_template": "📚 {book_title} のPDFが更新されました\n\n作成日時: {timestamp}\nリポジトリ: {repo_name}",
    "auto_post": true,
    "last_channel_cache": {}
  }
}
```

## 実装計画

### Phase 1.0: 事前準備（Week 1）
1. Slack App作成
2. Bot設定とトークン取得
3. 一括チャネル登録スクリプト作成・実行

### Phase 1.1: コア機能実装（Week 2）
1. SlackIntegrationクラス実装
2. チャネル名→ID変換機能
3. PDF投稿機能
4. エラーハンドリング

### Phase 1.2: GUI統合（Week 3）
1. GUI部品追加
2. 設定画面実装
3. プレビュー機能実装

### Phase 1.3: テストとリリース（Week 4）
1. 単体テスト実装
2. 統合テスト
3. 本番環境での検証
4. ドキュメント作成

## 成功基準

- PDF生成→Slack投稿の作業時間: 5分 → 0分（自動化）
- エラー率: 1%未満
- ユーザー満足度: 90%以上

## リスクと対策

### リスク1: Slack API変更
- 対策: SDK定期更新、エラー監視

### リスク2: トークン漏洩
- 対策: 暗号化保存、環境変数推奨

### リスク3: Rate Limit超過
- 対策: リトライロジック、投稿間隔制御