# 技術の泉シリーズ制作支援ツール - ドキュメント

**バージョン**: 1.8  
**最終更新**: 2025-08-06

## 📚 ドキュメント一覧

### 🎯 重要ドキュメント

#### [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) 🔴
**既知の問題と機能制限**  
現在判明しているバグ、機能制限、回避策をまとめた重要ドキュメント。  
**必ず最初にお読みください。**

主な内容：
- NextPublishing APIサーバーエラー（Critical）
- 文字エンコーディング問題（部分解決済み）
- DI Container初期化警告（影響なし）
- 各問題の回避策と対処法

---

### 📋 仕様・構造ドキュメント

#### [TECHZIP_FILE_STRUCTURE_SPECIFICATION.md](./TECHZIP_FILE_STRUCTURE_SPECIFICATION.md)
プロジェクト全体のファイル構造を機能グループ別に整理した仕様書。10の主要グループに分類。

#### [TECHZIP_DEVELOPMENT_ROADMAP.md](./TECHZIP_DEVELOPMENT_ROADMAP.md)
開発ロードマップと今後の計画。Phase 1-3完了状況とQ3-Q4の予定。

#### [TECHZIP_REFACTORING_ROADMAP.md](./TECHZIP_REFACTORING_ROADMAP.md)
リファクタリング計画とアーキテクチャ改善の詳細。

---

### 🚀 セットアップガイド

#### [WINDOWS_SETUP_GUIDE.md](./WINDOWS_SETUP_GUIDE.md)
Windows環境でのセットアップ手順。Python環境構築からEXEビルドまで。

#### [EXE_BUILD_GUIDE_COMPLETE.md](./EXE_BUILD_GUIDE_COMPLETE.md)
Windows EXE完全ビルドガイド。PyInstallerによるビルド手順詳細。

#### [GMAIL_API_SETUP_GUIDE.md](./GMAIL_API_SETUP_GUIDE.md)
Gmail API OAuth2認証のセットアップ手順。

#### [GMAIL_OAUTH_EXE_SETUP.md](./GMAIL_OAUTH_EXE_SETUP.md)
EXE環境でのGmail OAuth設定ガイド。

#### [SLACK_APP_SETUP_GUIDE.md](./SLACK_APP_SETUP_GUIDE.md)
Slack App（Bot）のセットアップ手順。

---

### 📖 機能別マニュアル

#### [SLACK_PDF_POSTING_MANUAL.md](./SLACK_PDF_POSTING_MANUAL.md)
Slack PDF自動投稿機能の使用マニュアル。

#### [slack_pdf_post_specification.md](./slack_pdf_post_specification.md)
Slack PDF投稿機能の技術仕様書。

---

### 📁 アーカイブドキュメント

`docs/archive/` ディレクトリには、過去のバージョンや開発過程のドキュメントが保管されています：

- 各開発フェーズの完了レポート
- 旧バージョンの設計書
- 移行ガイド
- 研究・調査ドキュメント

必要に応じて参照してください。

---

## 🔍 ドキュメントの探し方

### 問題が発生した場合
1. **[KNOWN_ISSUES.md](./KNOWN_ISSUES.md)** を確認
2. 該当する問題の回避策を実施
3. 解決しない場合はサポートに連絡

### 新規セットアップの場合
1. **[WINDOWS_SETUP_GUIDE.md](./WINDOWS_SETUP_GUIDE.md)** から開始
2. 必要に応じて各種API設定ガイドを参照
3. **[EXE_BUILD_GUIDE_COMPLETE.md](./EXE_BUILD_GUIDE_COMPLETE.md)** でEXE化

### 機能を理解したい場合
1. **[TECHZIP_FILE_STRUCTURE_SPECIFICATION.md](./TECHZIP_FILE_STRUCTURE_SPECIFICATION.md)** で全体構造を把握
2. 各機能別マニュアルで詳細を確認
3. 技術仕様書で実装詳細を理解

### 開発に参加する場合
1. **[TECHZIP_DEVELOPMENT_ROADMAP.md](./TECHZIP_DEVELOPMENT_ROADMAP.md)** で現状を確認
2. **[KNOWN_ISSUES.md](./KNOWN_ISSUES.md)** で既知の問題を把握
3. **[TECHZIP_REFACTORING_ROADMAP.md](./TECHZIP_REFACTORING_ROADMAP.md)** で改善計画を確認

---

## 📊 ドキュメント管理状況

| カテゴリ | 最新化済み | アーカイブ済み | 合計 |
|----------|------------|----------------|------|
| 仕様書 | 3 | 15 | 18 |
| ガイド | 6 | 8 | 14 |
| マニュアル | 2 | 5 | 7 |
| レポート | 0 | 12 | 12 |
| **合計** | **11** | **40** | **51** |

---

## 🔄 更新履歴

- **2025-08-06**: ドキュメント整理完了、KNOWN_ISSUES.md作成
- **2025-08-06**: アーカイブ構造整備（25ファイルをarchiveへ移動）
- **2025-08-06**: 主要ドキュメント最新化（v1.8対応）

---

## 📝 ドキュメント作成ガイドライン

新規ドキュメント作成時は以下に従ってください：

1. **命名規則**: `CATEGORY_DESCRIPTION.md` （例：`SETUP_DOCKER.md`）
2. **配置場所**: 
   - 現行版 → `docs/`
   - 古いバージョン → `docs/archive/`
3. **必須項目**:
   - タイトルと更新日
   - 目的と対象読者
   - 前提条件
   - 手順または内容
   - トラブルシューティング（該当する場合）

---

## 🚨 次回作業内容

### 最優先タスク：TECHZIPバグフィックス

次回のセッションは以下のバグフィックスから開始してください：

1. **NextPublishing APIエラーの完全回避策実装**
   - 現在のエラー検出機能を改善
   - メール送信モードへの自動切り替え機能追加
   - ユーザーへの明確なガイダンス表示

2. **文字エンコーディング問題の完全解決**
   - レスポンスのContent-Type自動検出強化
   - 文字化けパターンの拡充
   - UTF-8 BOM処理の改善

3. **DI Container警告の抑制**
   - 不要な警告メッセージの削除
   - ログレベルの適切な設定

### 作業順序
1. KNOWN_ISSUES.mdの🔴 Critical Issuesから着手
2. 各問題の根本原因を調査
3. 修正実装とテスト
4. ドキュメント更新

**更新履歴**:
- 2025-08-06: 次回作業内容を追加（TECHZIPバグフィックス優先）

---

## 🆘 ヘルプ

ドキュメントに関する質問や改善提案は、GitHubのIssuesまたは開発チームのSlackチャンネルまでお寄せください。

**重要**: 技術的な問題が発生した場合は、必ず **[KNOWN_ISSUES.md](./KNOWN_ISSUES.md)** を最初に確認してください。多くの問題には既に回避策が用意されています。