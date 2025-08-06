# PROJECT_CONTEXT.md
最終更新: 2025-08-06

## 1. プロジェクト概要
**プロジェクト名**: 技術の泉シリーズ制作支援ツール (コードネーム: `techzip`)
**現行バージョン**: 1.8 (Windows EXE Build Complete)
**アーキテクチャ**: Dependency Injection + 統一設定管理システム

## 2. 技術スタック（2025年8月現在）
- **言語**: Python 3.13+
- **GUIフレームワーク**: PyQt6 (2025年7月にPyQt5から完全移行)
- **アーキテクチャパターン**: ヘキサゴナルアーキテクチャ + DIコンテナ
- **主要ライブラリ**:
  - `PyQt6`: モダンGUIフレームワーク
  - `dependency-injector`: DIコンテナ管理
  - `ConfigurationProvider`: 統一設定システム
  - `google-api-python-client`: Google Sheets/Gmail OAuth連携
  - `python-docx`: Word文書処理
  - `GitPython`: Gitリポジトリ操作
  - `requests`: HTTP通信
  - `beautifulsoup4`: HTMLパース

## 3. モダンアーキテクチャ (Phase 3-2完了)
```
┌─────────────────────────────────────────────┐
│       プレゼンテーション層 (PyQt6)          │
├─────────────────────────────────────────────┤
│         DIコンテナ & サービス層              │
│  - ServiceContainer                         │
│  - @inject デコレータ                       │
├─────────────────────────────────────────────┤
│      統一設定プロバイダー層                  │
│  - ConfigurationProvider                    │
│  - ConfigManager                            │
├─────────────────────────────────────────────┤
│        コアサービス層                        │
│  - Gmail OAuth認証                          │
│  - NextPublishingサービス                   │
│  - Word2XHTMLスクレイパー                   │
└─────────────────────────────────────────────┘
```

## 4. 実行環境
- **ターゲット環境**: Windows (ネイティブEXE v1.8)
- **エントリーポイント**:
  - `main.py`: Qt6ベースアプリケーション
  - `run_windows.ps1`: PowerShellランチャー
  - Windows EXE: `TECHZIP.1.8.exe`
- **グローバルホットキー**: `Ctrl+Shift+I` (AutoHotkey統合)

## 5. 主要機能 (v1.8)
### コア機能
- **統一設定管理**: ConfigurationProviderによる一元管理
- **Gmail OAuth認証**: 完全なOAuth2ワークフロー実装
- **NextPublishingサービス**: 文字化け(mojibake)修正対応
- **DIコンテナ**: 適切な依存性注入アーキテクチャ
- **Qt6 GUI**: モダンでレスポンシブなインターフェース

### ワークフロー自動化
1. **Nコード入力処理**: 複数形式対応（カンマ、タブ、スペース、改行区切り）
2. **Googleシート連携**: APIによる自動検索・データ取得
3. **リポジトリ管理**: GitHub/ローカルリポジトリの自動検出
4. **ZIP変換処理**: Re:VIEW形式からの自動変換
5. **メール監視**: Gmail APIによる完了通知自動検出
6. **Word処理**: 1行目削除と整形処理
7. **ファイル配置**: 指定フォルダへの自動配置

## 6. 最新実装状況 (2025年8月)
### 完了したフェーズ
- ✅ **Phase 1**: 認証リファクタリング完了
- ✅ **Phase 2**: 設定統合完了
- ✅ **Phase 3-2**: DI統合完了
- ✅ **Qt6移行**: 完全移行完了
- ✅ **Windows EXE v1.8**: ビルド・配布準備完了

### 実装済み修正
- ✅ WordProcessor DI統合問題の根本解決
- ✅ NextPublishing文字化け対策実装
- ✅ Gmail OAuth2完全対応
- ✅ 設定管理の一元化（ConfigurationProvider）
- ✅ Service Locatorアンチパターンの除去

## 7. ディレクトリ構造
```
technical-fountain-series-support-tool/
├── core/               # コアビジネスロジック
│   ├── di_container.py          # DIコンテナ実装
│   ├── configuration_provider.py # 統一設定プロバイダー
│   ├── config_manager.py        # 設定管理
│   ├── workflow_processor.py    # ワークフロー制御
│   ├── api_processor.py         # Re:VIEW API処理
│   ├── word_processor.py        # Word文書処理
│   └── gmail_monitor.py         # Gmail監視
├── gui/                # PyQt6 GUI層
│   ├── main_window.py           # メインウィンドウ
│   └── settings_dialog.py       # 設定ダイアログ
├── services/           # 外部サービス連携
│   └── nextpublishing_service.py # NextPublishing連携
├── app/                # スタンドアロンアプリ
│   └── modules/                  # モジュール群
├── utils/              # ユーティリティ
│   └── logger.py                # ロギング
├── docs/               # ドキュメント
│   ├── TECHZIP_FILE_STRUCTURE_SPECIFICATION.md
│   └── archive/                 # アーカイブ済み文書
└── dist/               # 配布物
    └── TECHZIP.1.8/             # EXE配布フォルダ
```

## 8. 開発環境セットアップ
### 必要条件
- Python 3.13+
- Windows 10/11
- Google Cloud Platform アカウント（Sheets API用）
- Gmail アカウント（OAuth認証用）

### インストール
```bash
# 仮想環境作成
python -m venv venv

# 依存関係インストール
pip install -r requirements.txt

# 実行
python main.py
```

## 9. トラブルシューティング
### よくある問題と解決策
1. **DI関連エラー**: `configure_services()`の呼び出し確認
2. **設定読み込みエラー**: ConfigurationProviderの初期化確認
3. **Qt6関連エラー**: PyQt6パッケージの完全性確認
4. **Gmail認証エラー**: OAuth2設定とトークンの有効性確認

## 10. 今後の開発計画
### Phase 4（計画中）
- Slack統合の完全実装
- 機械学習ベースの品質チェック機能
- バッチ処理の最適化
- クラウドデプロイメント対応

## 11. 参考資料
- [ファイル構造仕様書](docs/TECHZIP_FILE_STRUCTURE_SPECIFICATION.md)
- [開発ロードマップ](docs/TECHZIP_DEVELOPMENT_ROADMAP.md)
- [リファクタリングロードマップ](docs/TECHZIP_REFACTORING_ROADMAP.md)