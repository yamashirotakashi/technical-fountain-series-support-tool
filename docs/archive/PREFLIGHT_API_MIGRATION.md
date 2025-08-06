# Pre-flight Check API移行ガイド

## 概要
Pre-flight Check機能は現在Seleniumによるスクレイピングで実装されていますが、将来的にWord2XHTML5サービスがAPIを提供した場合にスムーズに移行できるよう設計されています。

## アーキテクチャ

### Strategy Pattern
```
PreflightVerifier (Abstract Base)
    ├── Word2XhtmlScrapingVerifier (現在の実装)
    └── Word2XhtmlApiVerifier (将来の実装)
```

### Factory Pattern
`VerifierFactory`クラスが環境変数や設定に基づいて適切な実装を選択します。

## 移行手順

### 1. 環境変数の設定
```bash
# API モードを有効化
export PREFLIGHT_MODE=api

# APIキーを設定
export WORD2XHTML_API_KEY=your_api_key_here
```

### 2. 設定ファイル（オプション）
`config/settings.json` に以下を追加：
```json
{
    "preflight": {
        "mode": "api",
        "api_key": "your_api_key_here",
        "api_base_url": "https://api.nextpublishing.jp/v1/word2xhtml"
    }
}
```

### 3. コードの変更不要
- `BatchProcessor`は自動的に適切なVerifierを使用
- GUIやワーカースレッドの変更は不要

## API仕様（想定）

### エンドポイント

#### 1. ファイル送信
```
POST /submit
Content-Type: multipart/form-data

Parameters:
- file: Wordファイル
- email: 結果送信先メールアドレス

Response:
{
    "job_id": "unique_job_identifier",
    "status": "processing"
}
```

#### 2. ステータス確認（バッチ）
```
POST /status/batch
Content-Type: application/json

Body:
{
    "job_ids": ["job1", "job2", "job3"]
}

Response:
{
    "job1": {
        "status": "completed",
        "download_url": "/download/job1"
    },
    "job2": {
        "status": "failed",
        "error": "Invalid document format"
    },
    "job3": {
        "status": "processing"
    }
}
```

#### 3. 結果ダウンロード
```
GET /download/{job_id}

Response:
- 成功時: PDFファイル（バイナリ）
- 失敗時: 404 Not Found
```

## 利点

### 1. パフォーマンス向上
- Seleniumの起動オーバーヘッドがない
- 並列処理が容易
- レスポンスが高速

### 2. 信頼性向上
- ブラウザ依存の問題がない
- ChromeDriverの更新不要
- より安定した動作

### 3. スケーラビリティ
- サーバー側でのキューイング
- レート制限の適切な管理
- バッチ処理の最適化

## 移行時の注意点

### 1. 互換性の維持
- 既存のメール監視機能との併用
- エラーハンドリングの一貫性
- UI/UXの変更を最小限に

### 2. フォールバック
- API障害時の自動フォールバック
- 設定による明示的な切り替え
- ログによる動作モードの明確化

### 3. テスト
- モックAPIサーバーでのテスト
- 移行前後の結果比較
- パフォーマンステスト

## 実装状況

### 完了
- ✅ Abstract Base Class (`PreflightVerifier`)
- ✅ Scraping実装 (`Word2XhtmlScrapingVerifier`)
- ✅ API実装の雛形 (`Word2XhtmlApiVerifier`)
- ✅ Factory実装 (`VerifierFactory`)
- ✅ 環境変数による切り替え

### 未実装
- ⏳ 実際のAPIエンドポイントとの接続
- ⏳ APIレスポンスの詳細な処理
- ⏳ エラーリトライ機構
- ⏳ APIヘルスチェック

## まとめ
現在の実装は将来のAPI移行を考慮した設計になっており、APIが提供された際には最小限の設定変更で移行可能です。