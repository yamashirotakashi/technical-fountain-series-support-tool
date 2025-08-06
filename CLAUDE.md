# 技術の泉シリーズ制作支援ツール (TECHZIP) v1.8

## 🚨 次回セッション最優先タスク

**必ず最初に確認**: [docs/README.md](./docs/README.md)

次回セッションは、docs/README.mdに記載されている内容から開始すること。
特に以下を確認：
1. 既知の問題リスト（[docs/KNOWN_ISSUES.md](./docs/KNOWN_ISSUES.md)）
2. 次回作業内容の指示
3. 優先度の高いバグフィックス

**重要**: 今後のタスク更新や問題報告は、docs/README.mdに記載すること。

## 📋 プロジェクト概要
**現行バージョン**: 1.8 (Windows EXE Build Complete)  
**技術スタック**: Python 3.13+ | PyQt6 | Dependency Injection | 統一設定管理  
**エントリーポイント**: `main.py` (唯一の現行エントリーポイント)  
**実行形態**: スタンドアロンWindows EXE (`TECHZIP.1.8.exe`)

## 🏗️ モダンアーキテクチャ (Phase 3-2完了)

### DIコンテナシステム
```python
# core/di_container.py - ServiceContainer実装
- register_singleton(): 単一インスタンス管理
- register_transient(): 都度新規インスタンス
- register_scoped(): スコープ付きライフタイム
- @inject デコレーター: 宣言的依存注入
```

### 統一設定管理
```python
# core/configuration_provider.py - ConfigurationProvider
- 全サービス設定の一元管理
- 環境変数との自動統合
- デフォルト値の適切な管理
- DIコンテナとの完全統合
```

### Qt6完全移行 (PyQt5から完全移行済み)
- PyQt6ベースのモダンGUIフレームワーク
- レスポンシブデザインとシグナル/スロット最新化
- main_window.py, settings_dialog.py等、全GUI層をQt6で統一

## 🚀 実行環境

### 開発環境
```bash
# WSL/Linux
cd /mnt/c/Users/tky99/dev/technical-fountain-series-support-tool
source venv/bin/activate
python main.py

# Windows PowerShell
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool
.\run_windows.ps1
```

### 本番環境 (Windows EXE v1.8)
```bash
# スタンドアロン実行
.\dist\TECHZIP.1.8\TECHZIP.1.8.exe

# グローバルホットキー
Ctrl+Shift+I  # アプリケーション起動
```

## 🔧 主要実装機能 (v1.8)

### コアワークフロー
- **Nコード処理**: 複数形式入力対応（カンマ、タブ、改行区切り）
- **Google Sheets連携**: OAuth2認証によるAPIアクセス
- **Re:VIEW ZIP変換**: 自動変換・監視システム
- **Gmail監視**: OAuth2によるリアルタイム通知検出
- **Word処理**: 1行目削除・整形処理（DI統合対応）
- **NextPublishing連携**: 文字化け(mojibake)対策実装済み

### 技術的特徴
- **DIコンテナ**: Service Locatorアンチパターン除去済み
- **設定統合**: ConfigurationProviderによる一元管理
- **認証統合**: Gmail/Google Sheets OAuth2完全対応
- **エラーハンドリング**: 各層での適切な例外処理
- **ログ管理**: utils/logger.pyによる統一ログ出力

## 📁 プロジェクト構造

```
technical-fountain-series-support-tool/
├── main.py                    # 唯一の現行エントリーポイント
├── core/                      # コアビジネスロジック層
│   ├── di_container.py        # DIコンテナ実装
│   ├── configuration_provider.py # 統一設定管理
│   ├── workflow_processor.py  # メインワークフロー制御
│   ├── word_processor.py      # Word処理（DI統合済み）
│   └── gmail_monitor.py       # Gmail OAuth監視
├── gui/                       # PyQt6 GUI層
│   ├── main_window.py         # メインウィンドウ
│   └── settings_dialog.py     # 設定ダイアログ
├── services/                  # 外部サービス連携層
│   └── nextpublishing_service.py # NextPublishing（mojibake対応）
├── app/modules/               # スタンドアロンアプリ
│   └── CodeBlockOverFlowDisposal/ # PDF溢れ検出システム
├── dist/TECHZIP.1.8/         # Windows EXE配布物
│   └── TECHZIP.1.8.exe       # 実行ファイル
└── archive/                   # Legacy Code Archive
    ├── legacy_entry_points/   # 旧main*.pyファイル群
    ├── legacy_gui/           # 旧GUI実装
    └── documentation/        # 復旧手順書
```

## 🔄 Legacy Code アーカイブ状況

### アーカイブ済みファイル
- **旧エントリーポイント**: main_gui.py, main_clean.py, main_no_google.py, main_qt6.py
- **旧GUI実装**: main_window_qt6.py, main_window_refactored.py等
- **移行ツール**: migrate_to_qt6_properly.ps1, convert_to_qt6.ps1等

### 現行システム
- **エントリーポイント**: `main.py`のみ
- **GUI実装**: PyQt6統一実装
- **アーキテクチャ**: DIコンテナ + 統一設定管理

## 🛡️ 品質保証

### 実装済み修正
- ✅ WordProcessor DI統合問題の根本解決
- ✅ NextPublishing文字化け完全対策
- ✅ Gmail OAuth2認証の安定化
- ✅ Service Locatorアンチパターンの完全除去

### 監視中の課題
- Gmail到着通知の最大20分遅延（Gmail API制限）
- 大容量ZIPアップロード時のタイムアウト

## 📈 次期開発計画 (Phase 4)

### 拡張機能
1. **Slack統合強化**: PDF自動投稿、進捗通知
2. **機械学習統合**: CodeBlockOverFlowDisposal ML版
3. **クラウド対応**: AWS Lambda デプロイメント

### 技術改善
- DIパフォーマンス最適化（目標: <1ms per resolution）
- メモリ管理の最適化
- 循環依存の自動検出強化

## 🔍 開発ガイドライン

### コーディング規約
- 新サービスは必ずDIコンテナに登録
- 設定アクセスはConfigurationProvider経由のみ
- ログ出力はutils/logger.py使用必須
- @injectデコレーターによる宣言的依存注入

### テスト方針
- ユニットテスト: サービス個別検証
- 統合テスト: DI統合の健全性確認
- E2Eテスト: ワークフロー全体動作確認

---

**重要**: legacy codeは全てarchive/配下に移動済み。現行開発では`main.py`のみを使用してください。  
**復旧**: 必要時は`archive/documentation/RECOVERY_INSTRUCTIONS.md`を参照