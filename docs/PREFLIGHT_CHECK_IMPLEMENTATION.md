# Pre-flight Quality Check機能 実装計画書

最終更新: 2025-01-25

## 概要

技術の泉シリーズ制作支援ツールに「Pre-flight Quality Check」機能を追加し、Word2XHTML5サービス（http://trial.nextpublishing.jp/upload_46tate/）を活用してWordファイルのPDF変換可能性を事前検証する。

### 背景と目的

- **問題**: Nフォルダ内のWordファイルが組版実行時にPDF生成に失敗することがある
- **解決策**: Word2XHTML5サービスを逆手に取り、全ファイルを個別に変換テストすることで問題ファイルを特定
- **注意**: 本来の単一ファイル変換サービスを検証ツールとして活用する特殊な使用方法

## アーキテクチャ設計

### Strategy Patternによる将来的なAPI移行対応

```python
from abc import ABC, abstractmethod
from typing import List, Dict

class PreflightVerifier(ABC):
    @abstractmethod
    def submit_batch(self, file_paths: List[str], email: str) -> List[str]:
        """複数ファイルを送信してジョブIDリストを返す"""
        pass
    
    @abstractmethod
    def check_all_status(self, job_ids: List[str]) -> Dict[str, tuple[str, str | None]]:
        """全ジョブのステータスを確認"""
        pass

class Word2XhtmlScrapingVerifier(PreflightVerifier):
    """Seleniumによる現行実装"""
    def submit_batch(self, file_paths: List[str], email: str) -> List[str]:
        job_ids = []
        for file_path in file_paths:
            job_id = self._submit_single(file_path, email)
            job_ids.append(job_id)
            time.sleep(5)  # クールダウン
        return job_ids

class Word2XhtmlApiVerifier(PreflightVerifier):
    """将来的なAPI実装（予約）"""
    pass
```

## 実装フェーズ

### Phase 1: UI基盤（1日）
- メインウィンドウに「Pre-flight Check」ボタン追加
- 設定ボタンの隣に配置
- アイコンとツールチップの実装

### Phase 2: Seleniumインフラ（2日）
- ChromeDriver自動ダウンロード機能
- WebDriver管理クラス
- ブラウザ制御の基本実装

### Phase 3: アップロード処理（2日）
- Word2XHTML5サービスへの自動アップロード
- ファイル選択とメールアドレス入力
- 送信処理とジョブID取得
- **連続アップロード**: 全ファイルを5秒クールダウンで順次処理

### Phase 4: 結果取得（2日）
- メール監視機能の拡張
- **長時間待機**: ReVIEW変換の20倍以上の処理時間を考慮
- PDF生成成功/失敗の判定
- ダウンロード試行による検証

### Phase 5: 結果表示（1日）
- エラーファイル一覧表示
- 成功/失敗の統計情報
- CSVエクスポート機能

### Phase 6: 状態管理（1日）
- 処理中断・再開機能
- 進捗の永続化
- クラッシュリカバリ

### Phase 7: API移行準備（1日）
- Strategy Patternの完全実装
- API仕様書テンプレート作成
- 移行ガイドライン文書

## 技術仕様

### 処理フロー
1. **バッチアップロード**
   - 全Wordファイルを連続でアップロード
   - ファイル間に5秒のクールダウンを挿入
   - ジョブIDをリストで管理
   
2. **一括メール監視**
   - 全アップロード完了後にメール監視開始
   - タイムアウト: ReVIEW変換の20倍以上（約400分）
   - 複数メールの並列監視

### レート制限
- リクエスト間隔: **5秒**（変更済み）
- 同時実行数: 1（シーケンシャル処理）
- 実行時間制限: なし（夜間制約を撤廃）

### エラーハンドリング
- Selenium例外のキャッチとリトライ
- ネットワークエラー時の自動再試行
- ブラウザクラッシュ時の復旧

### セキュリティ考慮事項
- メールアドレスの暗号化保存
- 一時ファイルの確実な削除
- ブラウザプロファイルの隔離

## 運用ガイドライン

### サーバー負荷への配慮
1. **5秒のクールダウン**を厳守
2. エラー時は指数バックオフ（5秒→10秒→20秒）
3. 大量ファイル処理時は進捗表示で透明性確保

### 将来的なAPI化提案

```
【Win-Win提案書テンプレート】

貴社サービスの価値向上提案

1. 現状の課題
   - 手動操作による効率性の制限
   - 大量ファイル処理のニーズ

2. API化によるメリット
   - サーバー負荷の適切な管理
   - 利用状況の可視化
   - 新たなビジネスモデルの可能性

3. 技術仕様案
   - RESTful API設計
   - 認証とレート制限
   - 非同期処理対応
```

## ファイル構成

```
technical-fountain-series-support-tool/
├── core/
│   ├── preflight/
│   │   ├── __init__.py
│   │   ├── verifier_base.py      # 抽象基底クラス
│   │   ├── word2xhtml_scraper.py # Selenium実装
│   │   ├── batch_processor.py    # バッチ処理管理
│   │   ├── rate_limiter.py       # レート制限
│   │   └── state_manager.py      # 状態管理
│   └── email_monitor.py          # 既存（拡張）
├── gui/
│   ├── dialogs/
│   │   └── preflight_dialog.py   # 結果表示ダイアログ
│   └── main_window_qt6.py        # 既存（ボタン追加）
└── docs/
    ├── PREFLIGHT_CHECK_IMPLEMENTATION.md  # 本文書
    └── WORD2XHTML5_API_REQUEST.md        # API化提案書
```

## テスト計画

### 単体テスト
- Seleniumドライバーのモック
- レート制限のタイミングテスト
- 状態管理の永続性テスト

### 統合テスト
- 実際のWord2XHTML5サービスとの連携
- エラーファイルの検出精度
- 長時間実行の安定性

### 受け入れテスト
- 100ファイルの連続処理
- 中断・再開シナリオ
- エラーレポートの有用性

## リスク管理

### 技術的リスク
- **Selenium依存**: ブラウザ更新による動作不良
  - 対策: WebDriverの自動更新機能
- **サービス仕様変更**: HTML構造の変更
  - 対策: 設定ファイルによる柔軟な対応

### 運用リスク
- **サーバー負荷**: 大量リクエストによる問題
  - 対策: 5秒クールダウンの厳守
- **利用制限**: サービス側での制限追加
  - 対策: API化提案の準備

## スケジュール

- **Phase 1-2**: 3日（基盤構築）
- **Phase 3-4**: 4日（コア機能）
- **Phase 5-6**: 2日（UI/UX）
- **Phase 7**: 1日（将来対応）
- **合計**: 10営業日

## 成功指標

1. **検出精度**: 95%以上のエラーファイル検出率
2. **処理速度**: 
   - アップロード: 1ファイルあたり平均10秒以内
   - 全体処理: 100ファイルで約7時間（メール待機含む）
3. **安定性**: 100ファイル連続処理での成功率90%以上
4. **ユーザビリティ**: 直感的なUI、明確なエラーレポート

## 付録: 倫理的配慮

本機能は既存サービスを本来とは異なる方法で使用するため、以下の倫理的配慮を行う：

1. **最小限の負荷**: 5秒のクールダウン実装
2. **透明性**: 将来的にはAPI利用への移行を提案
3. **相互利益**: サービス提供者にもメリットのある提案準備
4. **代替手段**: 自前実装の検討も並行して進める