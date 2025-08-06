# 既知の問題と機能制限

**最終更新**: 2025-08-06  
**バージョン**: 1.8  
**対象**: 技術の泉シリーズ制作支援ツール

## 🔴 Critical Issues（重大な問題）

### 1. NextPublishing API サーバーエラー
**状態**: 🔴 **未解決** - サーバー側の問題により機能停止中  
**影響範囲**: API経由のファイルアップロード機能全般  
**発生条件**: NextPublishing APIへのファイルアップロード試行時  

#### 症状
- HTTPステータス200が返るが、実際にはPHP設定エラーが含まれている
- レスポンス例:
  ```
  <br />
  <b>Warning</b>: PHP Startup: Unable to load dynamic library 'mcrypt.so'
  ```
- アップロード自体は成功する場合もあるが、エラー表示により正常な動作が妨げられる

#### 回避策
1. **メール送信モードを使用**（推奨）
   - APIアップロードの代わりにメールで原稿を送信
   - Gmail OAuth2認証を設定してメール送信機能を使用

2. **手動アップロード**
   - ファイルを手動でNextPublishingにアップロード
   - ツールで変換処理のみを実行

#### 関連ファイル
- `services/nextpublishing_service.py` - エラー検出機能実装済み
- `test_enhanced_error_handling.py` - エラーハンドリングテスト

---

## 🟡 Major Issues（主要な問題）

### 2. 文字エンコーディング問題（Mojibake）
**状態**: 🟡 **部分的に解決**  
**影響範囲**: NextPublishing APIレスポンスの日本語表示  
**発生条件**: APIレスポンスがISO-8859-1として誤認識される場合  

#### 症状
- 「アップロード完了」が「ã¢ããã­ã¼ããå®äºãã¾ãã」と表示される
- BOM付きUTF-8レスポンスの処理エラー

#### 対策済み内容
- UTF-8強制デコード実装（`nextpublishing_service.py` L289-295）
- BOM除去処理実装（L309-317）
- 複数の文字化けパターン検出（L335-345）

#### 残存問題
- サーバー側のContent-Type設定が不適切な場合の完全な対応
- 一部の特殊文字での文字化け

---

### 3. DI Container 初期化警告
**状態**: 🟡 **動作に影響なし**  
**影響範囲**: アプリケーション起動時のログ  
**発生条件**: legacy codeから移植した部分でDIコンテナ未対応の場合  

#### 症状
```python
DI Container初期化エラー: No module named 'xxx'
```

#### 実際の影響
- **なし** - フォールバック処理により正常動作
- 警告メッセージがログに記録されるのみ

#### 関連ファイル
- `main.py` L36-44 - DI初期化エラーハンドリング
- `core/di_container.py` - DIコンテナ実装

---

## 🟢 Minor Issues（軽微な問題）

### 4. EXE環境での設定ファイル読み込み
**状態**: 🟢 **回避策実装済み**  
**影響範囲**: Windows EXE版での設定管理  
**発生条件**: PyInstallerでビルドしたEXE実行時  

#### 症状
- 設定ファイルパスの解決エラー
- `_MEIPASS`ディレクトリ関連の警告

#### 実装済み対策
- `utils/path_resolver.py` - EXE環境検出と適切なパス解決
- `utils/env_manager.py` - 環境変数の適切な管理
- `main.py` L20-22 - EXE環境での設定リセット

---

### 5. Legacy GUI Components の非互換性
**状態**: 🟢 **アーカイブ済み**  
**影響範囲**: 旧バージョンのGUIコンポーネント  
**発生条件**: legacy main_*.pyファイル使用時  

#### 対処
- すべてのlegacyコンポーネントを`archive/`にアーカイブ
- 現行システム（`main.py`）は完全にQt6対応
- 必要時は`archive/documentation/RECOVERY_INSTRUCTIONS.md`参照

---

## ⚠️ 制限事項

### 6. 機能制限

#### API アップロード機能
- **制限**: NextPublishing APIの不安定性により信頼性が低い
- **推奨**: メール送信モードの使用

#### ファイルサイズ制限
- **制限**: 大容量ファイル（100MB以上）のアップロード時にタイムアウト
- **対策**: タイムアウト値を600秒に延長済み（`nextpublishing_service.py`）

#### 同時処理制限
- **制限**: 複数ファイルの並列アップロード非対応
- **仕様**: 順次処理のみサポート

---

## 📊 問題の優先度と対応状況

| 優先度 | 問題 | 状態 | 対応予定 |
|--------|------|------|----------|
| 🔴 Critical | NextPublishing APIエラー | サーバー側問題 | NextPublishing側の対応待ち |
| 🟡 High | 文字エンコーディング | 部分対応済み | v1.9で完全対応予定 |
| 🟡 Medium | DI Container警告 | 影響なし | v2.0で完全移行予定 |
| 🟢 Low | EXE設定読み込み | 対策済み | 解決済み |
| 🟢 Low | Legacy互換性 | アーカイブ済み | 対応不要 |

---

## 🔧 トラブルシューティング

### NextPublishing APIエラーが発生した場合

1. **エラーメッセージを確認**
   ```
   logs/TechnicalFountainTool_YYYYMMDD_HHMMSS.log
   ```

2. **メール送信モードに切り替え**
   - 設定 > 処理モード > 「メール送信」を選択
   - Gmail認証を設定

3. **サポートへの報告**
   - NextPublishing技術サポートに以下を報告：
     - PHP mcrypt.so エラー
     - サーバー設定の確認依頼

### 文字化けが発生した場合

1. **ログファイルで実際のレスポンスを確認**
2. **BOM付きUTF-8の可能性を確認**
3. **必要に応じて手動でファイルを確認**

### DI Container警告を消したい場合

1. **動作に影響はないため無視して問題なし**
2. **ログレベルをINFO以上に設定して警告を非表示化**
   ```python
   # utils/logger.py で設定
   logging.getLogger().setLevel(logging.INFO)
   ```

---

## 📝 今後の改善予定

### Version 1.9（予定）
- [ ] 文字エンコーディング問題の完全解決
- [ ] エラーメッセージの日本語化
- [ ] APIタイムアウトの動的調整

### Version 2.0（予定）
- [ ] DI Container完全移行
- [ ] 並列アップロード対応
- [ ] NextPublishing API v2対応（APIが更新された場合）

---

## 📞 サポート情報

### 問題報告先
- **開発チーム**: [内部Slackチャンネル]
- **NextPublishing技術サポート**: [NextPublishing問い合わせフォーム]

### ログファイル収集
問題報告時は以下を添付：
1. `logs/TechnicalFountainTool_*.log`
2. エラー発生時のスクリーンショット
3. 使用していた設定内容

### 緊急時の対処
1. `archive/documentation/RECOVERY_INSTRUCTIONS.md` を参照
2. Legacy版での一時的な運用も可能（非推奨）

---

**注意**: このドキュメントは定期的に更新されます。最新の問題状況はGitHubのIssuesも参照してください。