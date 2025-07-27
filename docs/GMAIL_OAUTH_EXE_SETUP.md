# Gmail OAuth認証 EXE環境セットアップガイド

## 問題の概要
EXE化後のアプリケーションでGmail API方式を選択すると、OAuth2.0認証ファイルが見つからないエラーが発生します。

## エラーメッセージ
```
✗ N02132 の処理に失敗: OAuth2.0認証ファイルが見つかりません: config/gmail_oauth_credentials.json
```

## 解決方法

### 方法1: Gmail OAuth認証ファイルを正しい場所に配置

1. **認証ファイルの配置場所を確認**
   ```
   C:\Users\[ユーザー名]\.techzip\config\
   ```

2. **ディレクトリが存在しない場合は作成**
   ```powershell
   mkdir C:\Users\$env:USERNAME\.techzip\config
   ```

3. **既存の認証ファイルをコピー**
   - 開発環境の認証ファイル:
     ```
     C:\Users\tky99\dev\technical-fountain-series-support-tool\config\gmail_oauth_credentials.json
     ```
   - コピー先:
     ```
     C:\Users\[ユーザー名]\.techzip\config\gmail_oauth_credentials.json
     ```

4. **トークンファイルもコピー（存在する場合）**
   ```
   C:\Users\tky99\dev\technical-fountain-series-support-tool\config\gmail_token.pickle
   → C:\Users\[ユーザー名]\.techzip\config\gmail_token.pickle
   ```

### 方法2: 新規にOAuth認証をセットアップ

OAuth認証ファイルがない場合は、以下の手順で新規作成:

1. **Google Cloud Consoleにアクセス**
   https://console.cloud.google.com/

2. **新しいプロジェクトを作成または既存のプロジェクトを選択**

3. **Gmail APIを有効化**
   - APIs & Services > Enable APIs and Services
   - 「Gmail API」を検索して有効化

4. **OAuth 2.0認証情報を作成**
   - APIs & Services > Credentials
   - 「+ CREATE CREDENTIALS」> OAuth client ID
   - Application type: Desktop app
   - Name: TechZip Gmail Monitor

5. **認証情報をダウンロード**
   - 作成した認証情報の「Download JSON」ボタンをクリック
   - ダウンロードしたファイルを `gmail_oauth_credentials.json` にリネーム
   - `C:\Users\[ユーザー名]\.techzip\config\` に配置

### 方法3: IMAPパスワード方式を使用（代替手段）

Gmail APIが使用できない場合は、IMAPパスワード方式にフォールバックします:

1. **設定ダイアログを開く**
   - ツール > 設定

2. **メール設定タブ**
   - 「メール監視を有効にする」をチェック
   - Gmailアドレスを入力
   - アプリパスワードを入力

3. **Gmailアプリパスワードの取得**
   - Googleアカウント設定 > セキュリティ
   - 2段階認証を有効化
   - アプリパスワードを生成

## トラブルシューティング

### 認証ファイルパスの確認
アプリケーションは以下の順序でファイルを探します:

1. `C:\Users\[ユーザー名]\.techzip\config\gmail_oauth_credentials.json`
2. EXE同梱の `config\gmail_oauth_credentials.json`（読み取り専用）

### ログの確認
エラーの詳細は以下のログファイルで確認できます:
```
C:\Users\[ユーザー名]\.techzip\logs\techzip_YYYYMMDD.log
```

### 権限の問題
- `.techzip`フォルダに書き込み権限があることを確認
- ウイルス対策ソフトがファイルアクセスをブロックしていないか確認

## 推奨事項

1. **初回セットアップ時**
   - 開発環境で正常に動作することを確認
   - 認証ファイルとトークンファイルを事前にコピー

2. **配布時**
   - OAuth認証ファイルは機密情報のため、EXEに同梱しない
   - セットアップ手順をドキュメント化して提供

3. **セキュリティ**
   - OAuth認証ファイルは他人と共有しない
   - 定期的にトークンを更新

## 関連ファイル
- `/core/gmail_oauth_monitor.py` - Gmail OAuth認証実装
- `/core/gmail_oauth_exe_helper.py` - EXE環境対応ヘルパー
- `/utils/path_resolver.py` - パス解決ユーティリティ