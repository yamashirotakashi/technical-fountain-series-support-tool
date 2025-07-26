# Gmail API設定ガイド

## 概要
技術の泉シリーズ制作支援ツールでは、メール監視機能にGmail APIを使用できます。これにより、アプリパスワード不要で安全にメールを監視できます。

## 設定手順

### 1. Gmail APIの有効化

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成または選択
3. 「APIとサービス」→「ライブラリ」
4. 「Gmail API」を検索して有効化

### 2. OAuth 2.0認証情報の作成

1. 「APIとサービス」→「認証情報」
2. 「+ 認証情報を作成」→「OAuth クライアント ID」
3. アプリケーションの種類：「デスクトップアプリ」
4. 名前：「TechZip Gmail Monitor」
5. 作成したJSONファイルをダウンロード

### 3. 認証ファイルの配置

ダウンロードしたJSONファイルを以下の場所に保存：
```
technical-fountain-series-support-tool/
└── config/
    └── gmail_oauth_credentials.json  ← ここに配置
```

### 4. 設定ファイルの更新

`config/settings.json`を編集：
```json
{
  "email": {
    "use_gmail_api": true,  // ← trueに変更
    "gmail_credentials_path": "config/gmail_oauth_credentials.json"
  }
}
```

### 5. 初回認証

1. ツールを起動して「処理開始」
2. メール自動取得で「はい」を選択
3. ブラウザが開いて認証画面が表示される
4. Googleアカウントでログイン
5. 「このアプリを信頼しますか？」で「許可」

認証が完了すると、`config/gmail_token.pickle`が作成され、次回以降は自動的に認証されます。

## 利点

- **セキュリティ**: OAuth 2.0による安全な認証
- **簡便性**: アプリパスワード不要
- **保守性**: トークンの自動更新

## トラブルシューティング

### 認証エラーが発生する場合
1. `config/gmail_token.pickle`を削除して再認証
2. Gmail APIが有効になっているか確認
3. 認証情報ファイルのパスが正しいか確認

### メールが取得できない場合
1. Gmailの「すべてのメール」ラベルを確認
2. 検索期間の設定を確認
3. ログでエラーメッセージを確認

## 従来のIMAP方式に戻す

`config/settings.json`で`use_gmail_api`を`false`に変更すれば、従来のIMAPベースのメール監視に戻せます。