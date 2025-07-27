# User Token取得手順

## 1. App設定の更新

1. https://api.slack.com/apps/A097K6HTULW/general にアクセス
2. **App Credentials**セクションから**Client Secret**をコピー
3. `src/oauth_server.py`の`CLIENT_SECRET`に設定

## 2. Redirect URLの設定

1. https://api.slack.com/apps/A097K6HTULW/oauth にアクセス
2. **Redirect URLs**セクションで「Add New Redirect URL」
3. `http://localhost:8888/callback` を追加
4. 「Save URLs」をクリック

## 3. OAuth認証の実行

```bash
# OAuth認証サーバーを起動
python src/oauth_server.py

# ブラウザが自動的に開きます
# 「Slackで認証」ボタンをクリック
# 管理者権限でログイン・承認
```

## 4. 一括招待スクリプトの実行

```bash
# User Tokenが.slack_user_tokenファイルに保存されます
python src/bulk_invite_with_user_token.py
```