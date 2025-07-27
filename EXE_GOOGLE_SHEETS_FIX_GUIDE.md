# EXE環境でのGoogle Sheets認証パス修正ガイド

## 問題の概要
EXE環境で起動時に表示される以下のメッセージ：
```
⚠️ Google Sheets認証ファイル: 未設定または存在しません
   設定値: C:\Users\tky99\.techzip\config\google_service_account.json
```

この問題は、古い設定値がキャッシュされているために発生します。

## 修正手順

### 方法1: 自動修正スクリプトを使用（推奨）

1. PowerShellを管理者権限で開く
2. 以下のコマンドを実行：
   ```powershell
   cd C:\Users\tky99\DEV\technical-fountain-series-support-tool
   .\fix_google_sheets_path_final.ps1
   ```
3. スクリプトが自動的に正しいパスに修正します
4. TECHZIP1.5.exeを再起動

### 方法2: 手動修正

1. 以下のファイルをメモ帳で開く：
   ```
   C:\Users\tky99\.techzip\config\settings.json
   ```

2. `google_sheet`セクションの`credentials_path`を確認：
   ```json
   "google_sheet": {
     "sheet_id": "...",
     "credentials_path": "ここを修正"
   }
   ```

3. 以下のいずれかの形式に修正：
   - 相対パス形式（推奨）: `"config\\techbook-analytics-aa03914c6639.json"`
   - または: `"config/techbook-analytics-aa03914c6639.json"`

4. ファイルを保存

5. 認証ファイルが存在することを確認：
   ```
   C:\Users\tky99\.techzip\config\techbook-analytics-aa03914c6639.json
   ```

6. TECHZIP1.5.exeを再起動

## 確認方法

修正後、アプリケーションを起動して以下を確認：

1. 起動時ログに以下のような表示があること：
   ```
   ✓ Google Sheets認証ファイル: C:\Users\tky99\.techzip\config\techbook-analytics-aa03914c6639.json
   ```

2. Google Sheetsからのデータ取得が正常に動作すること

## トラブルシューティング

### 認証ファイルが見つからない場合
1. 開発環境から認証ファイルをコピー：
   ```
   元: C:\Users\tky99\dev\techbookanalytics\config\techbook-analytics-aa03914c6639.json
   先: C:\Users\tky99\.techzip\config\
   ```

2. `copy_google_sheets_auth.ps1`を実行

### 設定が反映されない場合
1. アプリケーションを完全に終了（タスクマネージャーで確認）
2. 以下のフォルダ内の一時ファイルを削除：
   ```
   C:\Users\tky99\.techzip\temp\
   C:\Users\tky99\.techzip\logs\
   ```
3. アプリケーションを再起動

## 技術的背景

この問題は以下の理由で発生します：

1. **WSL環境でのビルド**: WSLでPyInstallerを使用してビルドすると、Path解決が異なる
2. **設定のキャッシュ**: Configクラスがシングルトンパターンを使用しているため、初回読み込み時の値がキャッシュされる
3. **パス形式の違い**: 絶対パスと相対パスの混在

修正版では以下の対策を実装しています：
- EXE起動時の設定リセット機能
- 相対パス形式への自動変換
- runtime_hookでの初期設定修正