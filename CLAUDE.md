# グローバルルールの継承
@../CLAUDE.md

# プロジェクト名: 技術の泉シリーズ制作支援ツール
最終更新: 2025-01-08

## 🎯 プロジェクト概要
- **目的**: 技術の泉シリーズの制作プロセスを自動化・効率化
- **主要機能**: Re:VIEW形式から超原稿用紙（Word）形式への自動変換と配置
- **プロジェクトキーワード**: `[techzip]`

## 📋 ワークフロー
1. **Nコード入力** - 処理対象のNコードを指定（カンマ、タブ、スペース、改行区切り対応）
2. **Googleシート検索** - Nコードからリポジトリ名を取得
3. **リポジトリ検索** - Google Drive内のリポジトリフォルダを特定
4. **ZIP作成** - Re:VIEWフォルダをZIP化
5. **アップロード** - 変換サービスにZIPをアップロード
6. **メール監視** - 変換完了メールを自動監視
7. **ダウンロード** - 変換済みファイルを取得
8. **Word処理** - 1行目を削除して整形
9. **ファイル配置** - 指定フォルダに最終成果物を配置

## 🚀 起動方法

### WSL環境
```bash
cd /mnt/c/Users/tky99/dev/technical-fountain-series-support-tool
source venv/bin/activate
python main.py
```

### Windows PowerShell（推奨）
```powershell
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool
.\run_windows.ps1
```

### ホットキー起動（Ctrl+Shift+I）

#### PowerShell内でのホットキー
```powershell
# 永続的な設定（PowerShellプロファイルに追加）
.\setup_hotkey.ps1

# 一時的な設定（現在のセッションのみ）
.\hotkey_quick_launch.ps1

# 設定を削除する場合
.\remove_hotkey.ps1
```

#### システム全体のグローバルホットキー（推奨）
PowerShellが起動していなくても使用可能：

##### スタートアップ登録方式（narouと同じ方式）
```batch
# インストール（Windows起動時に自動有効化）
install_startup.bat

# アンインストール
uninstall_startup.bat
```

##### 手動実行方式
```batch
# AutoHotkeyを使用した一時的な設定
test_hotkey_direct.bat
```
※要AutoHotkeyインストール

## 🔧 設定ファイル

### config/settings.json
```json
{
    "google_sheet": {
        "sheet_id": "17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ",
        "credentials_path": "C:\\Users\\tky99\\dev\\techbookanalytics\\config\\techbook-analytics-aa03914c6639.json"
    },
    "paths": {
        "git_base": "G:\\マイドライブ\\[git]",
        "output_base": "G:\\.shortcut-targets-by-id\\0B6euJ_grVeOeMnJLU1IyUWgxeWM\\NP-IRD"
    }
}
```

### .env（要作成）
```
GMAIL_ADDRESS=yamashiro.takashi@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
```

## ⚠️ 前提条件

### Google Cloud設定
1. **Google Sheets API** - 有効化が必要
2. **サービスアカウント** - `techbook-analyzer-local-dev@techbook-analytics.iam.gserviceaccount.com`
3. **シート共有** - サービスアカウントにGoogleシートの閲覧権限付与が必要

### Gmail設定
- **アプリパスワード** - 2段階認証を有効にしてアプリパスワードを生成
- **IMAP有効化** - Gmail設定でIMAPを有効にする

## 🛠️ トラブルシューティング

### Google Sheets APIエラー
```
"Google Sheets API has not been used in project..."
```
→ Google Cloud ConsoleでSheets APIを有効化

```
"The caller does not have permission"
```
→ Googleシートをサービスアカウントと共有

### メール監視エラー
```
"'ascii' codec can't encode characters..."
```
→ 修正済み。日本語件名の検索に対応

## 📝 既知の問題と対応状況
- ✅ Google Sheets API認証設定
- ✅ 日本語メール件名のエンコーディング対応
- ⏳ メール到着まで最大20分待機が必要

## 🔄 開発メモ
- PyQt5使用（WSL互換性のため）
- 環境変数からの認証情報取得対応
- UTF-8エンコーディング対応済み

## 🚧 実装済み機能
### リモートリポジトリ対応（2025-01-19実装）
- **優先順位**: GitHubユーザー`irdtechbook`のリモートリポジトリから優先取得
- **フォールバック**: リモート取得失敗時はローカルGoogle Drive（`G:\マイドライブ\[git]`）から取得
- **実装内容**: 
  1. GitRepositoryManagerクラスによるGitHub連携
  2. ローカルキャッシュ機能（`~/.techzip/repo_cache`）
  3. GUIからのリポジトリ設定管理（ツール→リポジトリ設定）
  4. 環境変数`GITHUB_TOKEN`によるプライベートリポジトリ対応

## 🎯 次期開発計画（2025-07-30更新）

### 🎉 CodeBlockOverFlowDisposal開発ロードマップ
**Phase1完了済み（2025-07-30）**: 
- OCRベース右端はみ出し検出システム実装完了
- Windows EXE化対応完了
- PyQt6独立アプリケーション完成

### 📋 Phase2: 機械学習機能の充実（次期開発）
**目標**: より高精度で汎用的な溢れ検出システムの構築

**実装項目**:
1. **高度な溢れパターン学習システム**
   - ユーザー判定データからの継続学習機能
   - 複数のPDFレイアウトパターンへの対応
   - 検出精度の自動改善メカニズム

2. **機械学習ベースの検出エンジン**
   - テキスト配置パターンの学習
   - フォント・レイアウト特徴の自動抽出
   - 偽陽性・偽陰性の学習による精度向上

3. **インテリジェント判定支援**
   - 検出結果の信頼度表示
   - 学習データに基づく推奨アクション
   - ユーザー習慣の学習と提案

**推定工数**: 15-20時間

### 🔗 Phase3: TECHZIP支援アプリへの統合
**目標**: Re:VIEW→Word変換ワークフローへの自動品質チェック統合

**統合内容**:
1. **PDF後処理フックとしての統合**
   - Word変換完了後の自動溢れチェック実行
   - 変換品質レポートの自動生成
   - 問題検出時の修正推奨機能

2. **TECHZIP GUIへの統合**
   - 品質チェックタブの追加
   - 一括処理時の自動チェック機能
   - 履歴管理とトレンド分析

3. **ワークフロー最適化**
   - 設定ファイル統合（settings.json拡張）
   - バッチ処理対応
   - ログ統合とレポート機能

**推定工数**: 12-18時間

### Phase 3: Slack統合（延期）
- PDF生成完了後の自動Slack投稿機能
- 新規にSlack Bot作成（PDF投稿機能）
- 「完了後Slackに投稿」オプション追加
- 詳細: `/docs/TECHZIP_DEVELOPMENT_ROADMAP.md`

### Phase 4: TechZip Admin（延期）
- プロジェクト初期化専用の管理者ツール（別アプリ）
- Slack/GitHubリソースの一括作成
- 高権限操作の安全な実行
- 詳細: `/docs/project_initialization_automation_research.md`

## 🚨 次回セッション必須タスク（2025-01-08追加）

### 1. 【最優先】TECHZIP1.8 Windows EXE Build & Test (TECHZIP-BUILD-001)
**状況**: Build script作成完了、ディレクトリ修正済み
**実行場所**: `C:\Users\tky99\DEV\technical-fountain-series-support-tool\dist\`
**緊急度**: 🔴 Critical - 即座実行必須

**Phase 1: EXE Build実行**:
```powershell
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool\dist
.\build_techzip18_folder.ps1
```

**Phase 2: 機能検証**:
- [x] ビルドスクリプト作成（完了）
- [x] ディレクトリパス修正（完了）
- [ ] PyInstaller実行とEXE生成
- [ ] GUI起動テスト
- [ ] API設定画面動作確認（2列レイアウト）
- [ ] ConfigManager統合動作確認
- [ ] 全機能動作テスト

**Phase 3: 配布準備**:
- [ ] README.txt作成（自動）
- [ ] 動作確認レポート作成
- [ ] バージョン1.8の新機能動作確認

**実装済み内容**:
- ✅ ConfigManager class統合
- ✅ API設定画面2列レイアウト
- ✅ 全API設定項目デフォルト値適用
- ✅ パスワードマスク除去
- ✅ Python 3.13.5完全対応
- ✅ ビルドスクリプト作成・修正完了