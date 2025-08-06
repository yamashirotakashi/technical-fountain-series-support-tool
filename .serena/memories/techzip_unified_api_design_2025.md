# TechZip統一API設計書 2025-08-03

## 📋 概要

ユーザー要求に基づき、TECHZIP の各機能を外部から API 呼び出し可能にする統一設計。

### 対象機能
1. **PDF Slack投稿機能** - N-code→Slack投稿の完全自動化
2. **エラーファイル検知機能** - PDF URL検証API化（メール→API移行対応）
3. **ReVIEW変換機能** - 既存WorkflowProcessor機能
4. **将来の機能追加** - 統一フレームワークによる容易な拡張

### 設計方針
- **N-codeベース処理**: 全機能をN-codeをキーとして呼び出し
- **デュアルモード**: 対話モード + パラメータ駆動モード
- **統一インターフェース**: 一貫性のあるAPI設計
- **拡張性**: 新機能追加時のAPI化を容易に

---

## 🏗️ アーキテクチャ設計

### Core API Layer
```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

class ProcessMode(Enum):
    """処理モード"""
    INTERACTIVE = "interactive"    # 対話モード（GUI表示）
    AUTOMATED = "automated"       # 完全自動化モード
    PARAMETERIZED = "parameterized"  # パラメータ駆動モード

class FunctionType(Enum):
    """機能タイプ"""
    REVIEW_CONVERSION = "review_conversion"
    PDF_SLACK_POST = "pdf_slack_post"
    ERROR_DETECTION = "error_detection"
    BATCH_PROCESSING = "batch_processing"

@dataclass
class APIRequest:
    """統一APIリクエスト"""
    function_type: FunctionType
    n_codes: List[str]
    mode: ProcessMode = ProcessMode.AUTOMATED
    parameters: Optional[Dict[str, Any]] = None
    config_override: Optional[Dict[str, Any]] = None

@dataclass
class APIResult:
    """統一APIレスポンス"""
    success: bool
    function_type: FunctionType
    processed_items: List[Dict[str, Any]]
    warnings: List[str]
    errors: List[str]
    processing_time: float
    metadata: Optional[Dict[str, Any]] = None

class TechZipUnifiedAPI:
    """TechZip統一API - 全機能の外部呼び出しエントリポイント"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初期化
        
        Args:
            config_path: 設定ファイルパス（省略時はデフォルト）
        """
        
    def process(self, request: APIRequest) -> APIResult:
        """
        統一処理エントリポイント
        
        Args:
            request: 統一APIリクエスト
            
        Returns:
            処理結果
        """
        
    def process_simple(self, 
                      function_type: FunctionType, 
                      n_codes: Union[str, List[str]], 
                      **kwargs) -> APIResult:
        """
        簡易呼び出しインターフェース
        
        Args:
            function_type: 実行する機能
            n_codes: N-code（文字列 or リスト）
            **kwargs: 追加パラメータ
            
        Returns:
            処理結果
        """
```

---

## 🎯 機能別API詳細設計

### 1. PDF Slack投稿API

#### 基本インターフェース
```python
class SlackPostAPI:
    """PDF Slack投稿専用API"""
    
    def __init__(self, slack_token: Optional[str] = None):
        self.poster = SlackPDFPoster(slack_token)
    
    def post_pdf_by_ncode(self, 
                         n_code: str,
                         mode: ProcessMode = ProcessMode.AUTOMATED,
                         message: Optional[str] = None,
                         channel_override: Optional[str] = None) -> Dict[str, Any]:
        """
        N-codeによるPDF Slack投稿
        
        Args:
            n_code: N-code（例: "N01798"）
            mode: 処理モード
            message: カスタムメッセージ（省略時はデフォルト）
            channel_override: チャネル名の強制指定
            
        Returns:
            {
                "success": bool,
                "n_code": str,
                "channel": str,
                "pdf_path": str,
                "slack_url": str,  # 投稿成功時のURL
                "message": str,
                "errors": List[str]
            }
        """
    
    def post_multiple(self, 
                     n_codes: List[str],
                     mode: ProcessMode = ProcessMode.AUTOMATED,
                     message_template: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        複数N-codeの一括投稿
        
        Returns:
            各N-codeの処理結果リスト
        """
```

#### 使用例
```python
# 基本的な投稿
slack_api = SlackPostAPI()
result = slack_api.post_pdf_by_ncode("N01798")

if result["success"]:
    print(f"投稿成功: {result['slack_url']}")
else:
    print(f"投稿失敗: {result['errors']}")

# カスタムメッセージ付き投稿
result = slack_api.post_pdf_by_ncode(
    "N01798", 
    message="最新版PDF完成しました！",
    mode=ProcessMode.AUTOMATED
)

# 一括投稿
results = slack_api.post_multiple(["N01798", "N02345", "N03456"])
for result in results:
    print(f"{result['n_code']}: {'成功' if result['success'] else '失敗'}")
```

### 2. エラーファイル検知API

#### 基本インターフェース
```python
class ErrorDetectionAPI:
    """エラーファイル検知専用API"""
    
    def __init__(self):
        self.validator = ErrorCheckValidator()
    
    def check_n_code_status(self, n_code: str) -> Dict[str, Any]:
        """
        N-codeの処理状況チェック
        
        Args:
            n_code: チェック対象のN-code
            
        Returns:
            {
                "success": bool,
                "n_code": str,
                "status": str,  # "processing", "completed", "error", "not_found"
                "pdf_url": Optional[str],
                "is_error": bool,
                "error_reason": Optional[str],
                "last_checked": str,  # ISO format timestamp
                "metadata": Dict[str, Any]
            }
        """
    
    def monitor_n_codes(self, 
                       n_codes: List[str],
                       check_interval: int = 300) -> Dict[str, Any]:
        """
        複数N-codeの継続監視（API版メール監視の代替）
        
        Args:
            n_codes: 監視対象N-codeリスト
            check_interval: チェック間隔（秒）
            
        Returns:
            {
                "monitoring_id": str,
                "n_codes": List[str],
                "results": List[Dict],
                "summary": {
                    "total": int,
                    "completed": int,
                    "errors": int,
                    "processing": int
                }
            }
        """
    
    def validate_pdf_urls(self, url_map: Dict[str, str]) -> Dict[str, Any]:
        """
        PDF URL一括検証（既存機能のAPI化）
        
        Args:
            url_map: {filename: pdf_url} のマッピング
            
        Returns:
            検証結果の詳細レポート
        """
```

#### 使用例
```python
# 単体チェック
error_api = ErrorDetectionAPI()
status = error_api.check_n_code_status("N01798")

if status["status"] == "error":
    print(f"エラー検出: {status['error_reason']}")
elif status["status"] == "completed":
    print("処理完了")

# 複数監視（メール監視の代替）
monitor_result = error_api.monitor_n_codes(["N01798", "N02345", "N03456"])
print(f"監視ID: {monitor_result['monitoring_id']}")
print(f"完了: {monitor_result['summary']['completed']}")
```

### 3. 統合ReVIEW変換API

#### 基本インターフェース
```python
class ReviewConversionAPI:
    """ReVIEW変換専用API"""
    
    def convert_by_ncode(self, 
                        n_code: str,
                        mode: ProcessMode = ProcessMode.AUTOMATED,
                        conversion_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        N-codeによるReVIEW変換
        
        Args:
            n_code: 変換対象N-code
            mode: 処理モード
            conversion_params: 変換パラメータ
                {
                    "process_type": "api|gmail_api|traditional",
                    "auto_download": bool,
                    "post_to_slack": bool,
                    "email_notification": bool
                }
                
        Returns:
            変換結果の詳細
        """
    
    def convert_files_direct(self, 
                           file_paths: List[Path],
                           output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        ファイル直接変換（N-code不要）
        
        Args:
            file_paths: 変換対象ファイルリスト
            output_dir: 出力ディレクトリ
            
        Returns:
            変換結果
        """
```

---

## 🔄 統合ワークフロー設計

### マルチファンクション API
```python
class TechZipWorkflowAPI:
    """複数機能を組み合わせたワークフローAPI"""
    
    def complete_workflow(self, 
                         n_code: str,
                         workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        完全ワークフロー実行
        
        Args:
            n_code: 処理対象N-code
            workflow_config: ワークフロー設定
                {
                    "review_conversion": bool,
                    "error_detection": bool,
                    "slack_posting": bool,
                    "email_notification": bool,
                    "auto_retry": bool,
                    "retry_count": int
                }
                
        Returns:
            全体処理結果
        """
        
    def batch_workflow(self, 
                      n_codes: List[str],
                      workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        バッチワークフロー実行
        
        Args:
            n_codes: 処理対象N-codeリスト
            workflow_config: ワークフロー設定
            
        Returns:
            バッチ処理結果
        """
```

### 使用例: 完全自動化ワークフロー
```python
# 完全自動化設定
workflow_config = {
    "review_conversion": True,
    "error_detection": True,
    "slack_posting": True,
    "email_notification": False,
    "auto_retry": True,
    "retry_count": 3
}

# 単体実行
workflow_api = TechZipWorkflowAPI()
result = workflow_api.complete_workflow("N01798", workflow_config)

# バッチ実行
batch_result = workflow_api.batch_workflow(
    ["N01798", "N02345", "N03456"], 
    workflow_config
)

print(f"バッチ処理: {batch_result['summary']['success_count']}/{batch_result['summary']['total_count']} 成功")
```

---

## 📊 設定管理システム

### 統一設定フォーマット
```yaml
# techzip_api_config.yaml
techzip_api:
  # 基本設定
  temp_dir: "/tmp/techzip_api"
  log_level: "INFO"
  max_concurrent: 3
  
  # 認証設定
  credentials:
    slack_token: "${SLACK_BOT_TOKEN}"
    api_username: "${TECHZIP_API_USER}"
    api_password: "${TECHZIP_API_PASS}"
    gmail_credentials: "path/to/gmail_creds.json"
  
  # 機能別設定
  slack_posting:
    default_message: "修正後のPDFです。ご確認よろしくお願いします。"
    auto_channel_detection: true
    fallback_channel: "general"
    
  error_detection:
    check_interval: 300  # 5分
    timeout: 30
    retry_count: 3
    
  review_conversion:
    auto_download: true
    temp_cleanup: true
    processing_timeout: 3600  # 1時間
    
  # ワークフロー設定
  workflows:
    default:
      review_conversion: true
      error_detection: true
      slack_posting: true
      email_notification: false
    
    development:
      review_conversion: true
      error_detection: false
      slack_posting: false
      email_notification: true
```

---

## 🚀 実装計画

### Phase 1: 基盤構築（1週間）
1. **統一API基底クラス実装**
   - TechZipUnifiedAPI
   - APIRequest/APIResult データクラス
   - 設定管理システム

2. **個別API実装**
   - SlackPostAPI（SlackPDFPoster のラッパー）
   - ErrorDetectionAPI（ErrorCheckValidator のラッパー）
   - ReviewConversionAPI（WorkflowProcessor分解後クラスのラッパー）

### Phase 2: 統合機能（1週間）
1. **ワークフローAPI実装**
   - TechZipWorkflowAPI
   - 複合処理ロジック
   - エラーハンドリング

2. **テストスイート構築**
   - 単体テスト
   - 統合テスト
   - API呼び出しテスト

### Phase 3: 外部統合（1週間）
1. **外部呼び出し最適化**
   - パフォーマンス最適化
   - リソース管理
   - 同期/非同期対応

2. **ドキュメント整備**
   - API仕様書
   - 使用例集
   - 移行ガイド

---

## 📈 期待効果

### 技術的効果
- **外部統合**: 他アプリからの呼び出し可能
- **自動化**: 人手介入の最小化
- **拡張性**: 新機能のAPI化が容易
- **保守性**: 統一インターフェースによる管理

### ビジネス効果
- **効率化**: バッチ処理による時間短縮
- **品質向上**: 自動エラー検出と通知
- **運用改善**: 監視とログによる透明性
- **開発速度**: 新機能開発の加速

---

## 🎯 成功指標

### 技術指標
- **API呼び出し成功率**: >95%
- **レスポンス時間**: 平均<10秒
- **同時処理数**: 最大5並列
- **エラー率**: <5%

### 運用指標
- **外部統合数**: 3プロジェクト以上
- **バッチ処理効率**: 70%時間短縮
- **自動化率**: 人手介入<20%
- **満足度**: 開発者フィードバック>4.0/5.0