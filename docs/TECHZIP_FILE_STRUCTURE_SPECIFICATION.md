# 技術の泉シリーズ制作支援ツール - ファイル構造仕様書
最終更新: 2025-08-06

## 📁 プロジェクト全体構成

本プロジェクトは機能別に明確に分離されたモジュール構造を採用しており、各モジュールが独立した責務を持つよう設計されています。

---

## 🎯 1. メインアプリケーション層

### エントリーポイント
- **main.py** - GUIアプリケーションのメインエントリーポイント
  - PyQt5アプリケーションの初期化
  - 例外ハンドリング設定
  - GUIウィンドウの起動
  
- **main_cli.py** - CLIバージョンのエントリーポイント
  - コマンドライン引数処理
  - バッチ処理対応
  - 非対話的実行モード

---

## 🖼️ 2. GUI層 (/gui)

### メインウィンドウ
- **gui/main_window.py** - メインウィンドウコントローラー
  - タブ管理
  - イベントハンドリング
  - 全体的なUI制御
  
- **gui/ui_main_window.py** - UIデザイン定義
  - Qt Designerからの自動生成ファイル
  - レイアウト定義
  - ウィジェット配置

### 設定画面
- **gui/settings_dialog.py** - 設定ダイアログコントローラー
  - 設定の読み込み・保存
  - バリデーション処理
  
- **gui/ui_settings_dialog.py** - 設定UIデザイン
  - API設定（Re:VIEW、NextPublishing）
  - パス設定
  - 認証情報設定

### 操作画面
- **gui/preview_dialog.py** - プレビューダイアログ
  - 処理結果の確認
  - エクスポート機能
  
- **gui/ui_preview_dialog.py** - プレビューUIデザイン

---

## 🔧 3. コア機能層 (/core)

### 設定管理
- **core/config_manager.py** - 設定管理の中核
  - 設定ファイルの読み書き
  - デフォルト値管理
  - 環境変数統合
  
- **core/configuration_provider.py** - 統一設定プロバイダー
  - DI用設定インターフェース
  - 設定値の集約管理

### 依存性注入
- **core/di_container.py** - DIコンテナ実装
  - サービス登録・解決
  - ライフタイム管理
  - パフォーマンス監視

### ワークフロー処理
- **core/workflow_processor.py** - メインワークフロー制御
  - ProcessingEngine クラス
  - 全体処理フローの管理
  - 各サービスの協調制御
  
- **core/api_processor.py** - Re:VIEW API処理
  - ZIP変換リクエスト
  - 変換状態監視
  - ダウンロード処理

### Word文書処理
- **core/word_processor.py** - Word文書操作
  - 1行目削除処理
  - Wordファイル探索
  - ZIP内Word処理

### Gmail連携
- **core/gmail_monitor.py** - Gmail監視サービス
  - メール受信監視
  - 添付ファイル処理
  - ダウンロードリンク抽出

### プリフライトチェック (/core/preflight)
- **core/preflight/word2xhtml_scraper.py** - Word2XHTML変換検証
  - HTML生成確認
  - 変換エラー検出
  - 品質チェック

---

## 🔌 4. 外部サービス層 (/services)

### NextPublishing連携
- **services/nextpublishing_service.py** - NextPublishing API連携
  - ファイルアップロード
  - 認証処理
  - エラーハンドリング
  - 文字エンコーディング対応（mojibake対策）

---

## 🏭 5. アプリケーション層 (/app)

### スタンドアロンアプリ (/app/modules)

#### CodeBlockOverFlowDisposal (/app/modules/CodeBlockOverFlowDisposal)
**PDF内コードブロック溢れ検出システム**

- **main.py** - アプリケーションエントリーポイント
- **main_window.py** - メインウィンドウコントローラー
- **pdf_processor.py** - PDF処理エンジン
  - OCR処理
  - ページ分析
  - 溢れ検出アルゴリズム
- **ocr_engine.py** - OCRエンジンラッパー
  - pdf2image統合
  - pytesseract処理
  - 日本語対応
- **overflow_detector.py** - 溢れ検出ロジック
  - パターンマッチング
  - 右端検出アルゴリズム
  - 検出結果管理
- **settings_manager.py** - 設定管理
- **result_manager.py** - 検出結果管理・エクスポート

### ミニアプリ (/app/mini_apps)

#### project_initializer (/app/mini_apps/project_initializer)
**プロジェクト初期化専用ツール**

- **PJinit.py** - プロジェクト初期化メイン
- **slack_manager.py** - Slackチャンネル作成
- **github_manager.py** - GitHubリポジトリ作成
- **template_manager.py** - テンプレート管理
- **project_config.py** - プロジェクト設定

---

## 🧪 6. テストスイート (/tests)

### ユニットテスト
- **tests/test_config_manager.py** - 設定管理テスト
- **tests/test_api_processor.py** - API処理テスト
- **tests/test_word_processor.py** - Word処理テスト
- **tests/test_gmail_monitor.py** - Gmail監視テスト
- **tests/test_workflow_processor.py** - ワークフロー全体テスト

### 統合テスト
- **tests/test_di_integration.py** - DI統合テスト
- **tests/test_nextpublishing_integration.py** - NextPublishing連携テスト

### 検証スクリプト
- **test_proper_di_fix.py** - DI修正検証
- **test_unified_config.py** - 統一設定検証

---

## 🛠️ 7. ユーティリティ層 (/utils)

### ロギング
- **utils/logger.py** - ロギングユーティリティ
  - 統一ログフォーマット
  - ログレベル管理
  - ファイル出力設定

### 共通処理
- **utils/file_utils.py** - ファイル操作ユーティリティ
- **utils/encoding_utils.py** - 文字エンコーディング処理
- **utils/path_utils.py** - パス操作ユーティリティ

---

## 📜 8. スクリプト層 (/scripts)

### 自動化スクリプト
- **scripts/batch_processor.py** - バッチ処理スクリプト
- **scripts/cleanup.py** - クリーンアップ処理
- **scripts/backup_manager.py** - バックアップ管理

### 品質管理
- **scripts/quality_analyzer.py** - コード品質分析
- **scripts/code_health_checker.py** - コード健全性チェック

### MCP関連
- **scripts/comprehensive_mcp_backup.py** - MCP設定バックアップ
- **scripts/comprehensive_mcp_backup_automation.py** - 自動バックアップ

---

## 🚀 9. ビルド・配布層 (/dist)

### ビルドスクリプト
- **dist/build_techzip18_folder.ps1** - v1.8ビルドスクリプト
  - PyInstaller設定
  - 依存関係解決
  - EXE生成

### 配布物
- **dist/TECHZIP.1.8/** - 実行可能ファイル配布フォルダ
  - TECHZIP.1.8.exe - 実行ファイル
  - README.txt - 使用説明書
  - config/ - 設定ファイル

---

## 🔒 10. 環境設定層

### 起動スクリプト
- **run_windows.ps1** - Windows用起動スクリプト
- **run_wsl.sh** - WSL用起動スクリプト
- **hotkey_quick_launch.ps1** - ホットキー設定

### 環境設定
- **.env** - 環境変数設定（Gmail認証等）
- **config/settings.json** - アプリケーション設定
- **requirements.txt** - Python依存関係

---

## 📊 機能グループごとの責務

### 1. **ワークフロー制御グループ**
主要ファイル: workflow_processor.py, api_processor.py
- Nコード処理フローの全体管理
- 各処理ステップの協調制御
- エラーハンドリングとリトライ

### 2. **外部API連携グループ**
主要ファイル: nextpublishing_service.py, gmail_monitor.py
- 外部サービスとの通信管理
- 認証・セッション管理
- レスポンス処理

### 3. **文書処理グループ**
主要ファイル: word_processor.py, pdf_processor.py
- ドキュメント形式の変換
- コンテンツの編集・整形
- メタデータ処理

### 4. **設定・DI管理グループ**
主要ファイル: config_manager.py, di_container.py, configuration_provider.py
- アプリケーション設定の一元管理
- 依存関係の注入と解決
- 環境別設定の切り替え

### 5. **UI/UXグループ**
主要ファイル: main_window.py, settings_dialog.py
- ユーザーインターフェース管理
- イベント処理
- ユーザー入力の検証

### 6. **品質保証グループ**
主要ファイル: word2xhtml_scraper.py, overflow_detector.py
- 変換品質の検証
- エラー検出とレポート
- 品質メトリクスの収集

---

## 🔄 データフロー

```
[ユーザー入力] 
    ↓
[GUI層] → [ワークフロー制御層]
    ↓           ↓
[設定管理]  [外部API連携]
    ↓           ↓
[文書処理] ← [Gmail監視]
    ↓
[品質チェック]
    ↓
[出力・配置]
```

---

## 🎯 今後の拡張ポイント

### 機能追加時の指針
1. **新機能は適切な層に配置**
   - UI要素 → /gui
   - ビジネスロジック → /core
   - 外部連携 → /services
   
2. **DIコンテナへの登録**
   - 新サービスはdi_container.pyのconfigure_services()に追加
   
3. **設定の統合**
   - 新設定項目はconfig_manager.pyのデフォルト値に追加
   - configuration_provider.pyで統一アクセス提供

4. **テストの追加**
   - ユニットテストは/testsに配置
   - 統合テストで全体動作確認

---

## 📝 メンテナンス指針

### コード変更時の注意点
1. **DI統合の維持**
   - @injectデコレーターの使用を推奨
   - Service Locatorパターンは避ける

2. **設定管理の一元化**
   - ConfigurationProvider経由でアクセス
   - 直接ファイル読み込みは避ける

3. **エラーハンドリング**
   - 各層で適切な例外処理
   - ユーザーへの分かりやすいエラーメッセージ

4. **ログ出力**
   - utils/logger.py使用を統一
   - 適切なログレベルの選択

---

この仕様書は、プロジェクトの機能拡張や保守作業時の参照ガイドとして活用してください。
各ファイルの詳細な実装については、該当ファイルのdocstringとコメントを参照してください。