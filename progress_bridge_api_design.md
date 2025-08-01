# TechBridge Progress Bridge API 基盤設計書

## 🎯 概要

TechBridge書籍進行管理Slackアプリの中核となるProgress Bridge APIの詳細設計書です。既存のFastAPI構造を基盤とし、Google Sheets連携とSlack Bot統合による書籍進行管理システムを実現します。

## 🏗️ システムアーキテクチャ

### レイヤード・アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Slack Bot Interface                      │
│  ┌─────────────┬─────────────┬─────────────────────────────┐ │
│  │ Commands    │ Events      │ Interactive Components     │ │
│  │ /status     │ Mentions    │ Buttons, Modals           │ │
│  │ /update     │ Reactions   │ Slash Command Responses    │ │
│  └─────────────┴─────────────┴─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                 Progress Bridge API (FastAPI)              │
│  ┌─────────────┬─────────────┬─────────────────────────────┐ │
│  │ API Layer   │ Service     │ Background Tasks            │ │
│  │ • Webhooks  │ Layer       │ • Reminder Scheduler        │ │
│  │ • REST APIs │ • Progress  │ • Status Sync               │ │
│  │ • Slack     │ • Sheets    │ • Notification Queue        │ │
│  │ • Auth      │ • Slack     │ • Error Recovery            │ │
│  └─────────────┴─────────────┴─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     Data Layer                              │
│  ┌─────────────┬─────────────┬─────────────────────────────┐ │
│  │ PostgreSQL  │   Redis     │     Google Sheets           │ │
│  │ • Workflows │ • Sessions  │ • Task Management Sheet     │ │
│  │ • Events    │ • Cache     │ • Manual Task Headers       │ │
│  │ • Logs      │ • Queue     │ • Author/Editor Data        │ │
│  └─────────────┴─────────────┴─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│             External Systems Integration                    │
│       [tech] Project    │     [techzip] Project            │
│    • Book Discovery     │   • Conversion Processing       │
│    • Purchase Status    │   • Quality Check               │ │
│    • Webhook Sender     │   • Completion Notification     │ │
└─────────────────────────────────────────────────────────────┘
```

## 📊 拡張データモデル設計

### 1. WorkflowItem拡張 (既存モデルの拡張)

```python
from sqlalchemy import JSON, DateTime, String, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional, Dict, Any

class WorkflowItem(Base):
    """拡張されたWorkflowItemモデル"""
    
    __tablename__ = "workflow_items"

    # 既存フィールド（維持）
    id: Mapped[int] = mapped_column(primary_key=True)
    n_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    book_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    title: Mapped[Optional[str]] = mapped_column(String(200))
    author: Mapped[Optional[str]] = mapped_column(String(100))
    repository_name: Mapped[Optional[str]] = mapped_column(String(100))
    slack_channel: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[ProgressStatus] = mapped_column(SQLEnum(ProgressStatus))
    assigned_editor: Mapped[Optional[str]] = mapped_column(String(50))
    workflow_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # 新規追加フィールド
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    estimated_hours: Mapped[Optional[int]] = mapped_column(Integer)
    actual_hours: Mapped[Optional[int]] = mapped_column(Integer)
    priority: Mapped[int] = mapped_column(Integer, default=3)  # 1:高 3:中 5:低
    tags: Mapped[Optional[str]] = mapped_column(String(500))  # カンマ区切り
    notes: Mapped[Optional[str]] = mapped_column(Text)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # Google Sheets連携
    sheets_row_number: Mapped[Optional[int]] = mapped_column(Integer)
    last_sheets_sync: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Slack統合
    slack_channel_id: Mapped[Optional[str]] = mapped_column(String(20))
    slack_thread_ts: Mapped[Optional[str]] = mapped_column(String(20))  # 進捗管理スレッド
    
    # タイムスタンプ（既存）
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 2. 新規テーブル設計

#### 2.1 WorkflowEvent - イベント履歴

```python
class WorkflowEvent(Base):
    """ワークフローイベント履歴"""
    
    __tablename__ = "workflow_events"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_item_id: Mapped[int] = mapped_column(ForeignKey("workflow_items.id"), index=True)
    event_type: Mapped[EventType] = mapped_column(SQLEnum(EventType))
    previous_status: Mapped[Optional[ProgressStatus]] = mapped_column(SQLEnum(ProgressStatus))
    new_status: Mapped[Optional[ProgressStatus]] = mapped_column(SQLEnum(ProgressStatus))
    source: Mapped[WebhookSource] = mapped_column(SQLEnum(WebhookSource))
    trigger_user: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

#### 2.2 ReminderSchedule - 督促スケジュール

```python
class ReminderSchedule(Base):
    """督促スケジュール管理"""
    
    __tablename__ = "reminder_schedules"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_item_id: Mapped[int] = mapped_column(ForeignKey("workflow_items.id"), index=True)
    reminder_type: Mapped[str] = mapped_column(String(50))  # "due_date", "overdue", "milestone"
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    target_channel: Mapped[str] = mapped_column(String(50))
    target_user: Mapped[Optional[str]] = mapped_column(String(100))
    message_template: Mapped[str] = mapped_column(String(50), default="default")
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

#### 2.3 SlackMessage - Slack投稿履歴

```python
class SlackMessage(Base):
    """Slack投稿履歴"""
    
    __tablename__ = "slack_messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_item_id: Mapped[int] = mapped_column(ForeignKey("workflow_items.id"), index=True)
    channel_id: Mapped[str] = mapped_column(String(20))
    message_ts: Mapped[str] = mapped_column(String(20))
    thread_ts: Mapped[Optional[str]] = mapped_column(String(20))
    message_type: Mapped[str] = mapped_column(String(50))  # "status_update", "reminder", "completion"
    content: Mapped[str] = mapped_column(Text)
    reactions: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

## 🔗 API エンドポイント設計

### 1. Progress Management APIs

```python
# app/api/v1/progress.py

@router.get("/", response_model=List[WorkflowItemResponse])
async def get_all_workflows(
    status: Optional[ProgressStatus] = None,
    assigned_editor: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
) -> List[WorkflowItem]:
    """全ワークフローアイテムの取得"""

@router.get("/{n_number}", response_model=WorkflowItemDetailResponse)
async def get_workflow_by_n_number(
    n_number: str,
    db: AsyncSession = Depends(get_async_db)
) -> WorkflowItem:
    """特定のワークフローアイテムの詳細取得"""

@router.post("/", response_model=WorkflowItemResponse)
async def create_workflow_item(
    item: WorkflowItemCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: str = Depends(get_current_user)
) -> WorkflowItem:
    """新規ワークフローアイテムの作成"""

@router.put("/{n_number}/status", response_model=WorkflowItemResponse)
async def update_workflow_status(
    n_number: str,
    status_update: StatusUpdateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: str = Depends(get_current_user)
) -> WorkflowItem:
    """ステータス更新（イベント記録付き）"""

@router.get("/{n_number}/events", response_model=List[WorkflowEventResponse])
async def get_workflow_events(
    n_number: str,
    db: AsyncSession = Depends(get_async_db)
) -> List[WorkflowEvent]:
    """ワークフローイベント履歴の取得"""
```

### 2. Webhook Endpoints

```python
# app/api/v1/webhooks.py

@router.post("/tech/book-discovered")
async def handle_tech_book_discovered(
    payload: TechBookDiscoveredPayload,
    signature: str = Header(alias="X-Tech-Signature"),
    db: AsyncSession = Depends(get_async_db)
):
    """[tech]からの書籍発見通知"""

@router.post("/tech/book-purchased")
async def handle_tech_book_purchased(
    payload: TechBookPurchasedPayload,
    signature: str = Header(alias="X-Tech-Signature"),
    db: AsyncSession = Depends(get_async_db)
):
    """[tech]からの購入完了通知"""

@router.post("/techzip/conversion-completed")
async def handle_techzip_conversion_completed(
    payload: TechzipConversionPayload,
    signature: str = Header(alias="X-Techzip-Signature"),
    db: AsyncSession = Depends(get_async_db)
):
    """[techzip]からの変換完了通知"""
```

### 3. Slack Integration APIs

```python
# app/api/v1/slack.py

@router.post("/commands/status")
async def handle_slack_status_command(
    request: SlackCommandRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """/status スラッシュコマンド処理"""

@router.post("/commands/update")
async def handle_slack_update_command(
    request: SlackCommandRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """/update スラッシュコマンド処理"""

@router.post("/events")
async def handle_slack_events(
    event: SlackEventRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Slack Events API処理"""

@router.post("/interactive")
async def handle_slack_interactive(
    payload: SlackInteractivePayload,
    db: AsyncSession = Depends(get_async_db)
):
    """Slackインタラクティブコンポーネント処理"""
```

## 🔧 Service Layer設計

### 1. WorkflowService - ワークフロー管理

```python
# app/services/workflow.py

class WorkflowService:
    """ワークフロー管理サービス"""
    
    def __init__(self, db: AsyncSession, slack_service: SlackService, sheets_service: GoogleSheetsService):
        self.db = db
        self.slack_service = slack_service
        self.sheets_service = sheets_service
    
    async def create_workflow_item(self, data: WorkflowItemCreate, source: WebhookSource) -> WorkflowItem:
        """ワークフローアイテム作成"""
        # 1. データベースに保存
        # 2. Google Sheetsに同期
        # 3. Slackチャンネル作成（必要に応じて）
        # 4. 初期督促スケジュール設定
    
    async def update_status(self, n_number: str, new_status: ProgressStatus, 
                          source: WebhookSource, user: Optional[str] = None) -> WorkflowItem:
        """ステータス更新処理"""
        # 1. 現在の状態取得
        # 2. 遷移可能性チェック
        # 3. データベース更新
        # 4. イベント記録
        # 5. Slack通知
        # 6. Google Sheets同期
        # 7. 督促スケジュール再計算
    
    async def sync_with_sheets(self, n_number: Optional[str] = None) -> Dict[str, Any]:
        """Google Sheetsとの同期"""
        # 1. Sheetsからデータ取得
        # 2. 差分検出
        # 3. データベース更新
        # 4. 同期ログ記録
    
    async def check_overdue_items(self) -> List[WorkflowItem]:
        """期限切れアイテムのチェック"""
        # 1. 期限切れアイテム検索
        # 2. 督促通知の要否判定
        # 3. エスカレーション処理
```

### 2. ReminderService - 督促管理

```python
# app/services/reminder.py

class ReminderService:
    """督促管理サービス"""
    
    async def schedule_reminders(self, workflow_item: WorkflowItem) -> List[ReminderSchedule]:
        """督促スケジュール設定"""
        # 1. 現在のステータスに基づく督促ルール取得
        # 2. 期限ベースの督促スケジュール生成
        # 3. データベース保存
    
    async def send_due_reminders(self) -> Dict[str, Any]:
        """期限督促の送信"""
        # 1. 送信対象の督促取得
        # 2. メッセージテンプレート生成
        # 3. Slack送信
        # 4. 送信結果記録
    
    async def escalate_overdue_items(self) -> Dict[str, Any]:
        """期限切れエスカレーション"""
        # 1. エスカレーション対象取得
        # 2. 管理者チャンネルに通知
        # 3. 督促頻度の調整
```

### 3. SlackService拡張

```python
# app/services/slack.py (既存の拡張)

class SlackService:
    """Slack連携サービス（拡張版）"""
    
    async def send_status_update_notification(self, workflow_item: WorkflowItem, 
                                            previous_status: ProgressStatus) -> Dict[str, Any]:
        """ステータス更新通知"""
        # 1. 通知チャンネル決定
        # 2. メッセージ生成（リッチフォーマット）
        # 3. Slack送信
        # 4. 投稿履歴記録
    
    async def send_reminder_message(self, reminder: ReminderSchedule) -> Dict[str, Any]:
        """督促メッセージ送信"""
        # 1. メッセージテンプレート取得
        # 2. 動的データ埋め込み
        # 3. インタラクティブボタン追加
        # 4. Slack送信
    
    async def create_project_channel(self, workflow_item: WorkflowItem) -> Dict[str, Any]:
        """プロジェクト専用チャンネル作成"""
        # 1. チャンネル名生成
        # 2. Slackチャンネル作成
        # 3. 初期メンバー招待
        # 4. ピン留めメッセージ投稿
    
    async def handle_interactive_component(self, payload: SlackInteractivePayload) -> Dict[str, Any]:
        """インタラクティブコンポーネント処理"""
        # 1. アクション種別判定
        # 2. 対応する処理実行
        # 3. レスポンス生成
```

## 🕒 Background Tasks設計

### 1. Celery Beat設定

```python
# app/tasks/scheduler.py

from celery import Celery
from celery.schedules import crontab

celery_app = Celery("techbridge")

celery_app.conf.beat_schedule = {
    # 督促チェック（毎時）
    'check-reminders': {
        'task': 'app.tasks.reminder.check_and_send_reminders',
        'schedule': crontab(minute=0),  # 毎時0分
    },
    
    # Google Sheets同期（4時間毎）
    'sync-sheets': {
        'task': 'app.tasks.sync.sync_with_google_sheets',
        'schedule': crontab(minute=0, hour='*/4'),  # 4時間毎
    },
    
    # 期限切れチェック（毎日9:00）
    'check-overdue': {
        'task': 'app.tasks.reminder.check_overdue_items',
        'schedule': crontab(hour=9, minute=0),  # 毎日9:00
    },
    
    # 統計レポート（毎週月曜9:00）
    'weekly-report': {
        'task': 'app.tasks.reports.generate_weekly_report',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # 毎週月曜9:00
    },
}
```

### 2. Background Task実装

```python
# app/tasks/reminder.py

@celery_app.task
async def check_and_send_reminders():
    """督促チェックと送信"""
    # 1. 送信対象の督促取得
    # 2. ReminderServiceで送信処理
    # 3. 結果ログ記録

@celery_app.task  
async def check_overdue_items():
    """期限切れアイテムチェック"""
    # 1. 期限切れアイテム取得
    # 2. エスカレーション処理
    # 3. 管理者通知

# app/tasks/sync.py

@celery_app.task
async def sync_with_google_sheets():
    """Google Sheets同期"""
    # 1. WorkflowServiceで同期処理
    # 2. 差分レポート生成
    # 3. エラー時の管理者通知
```

## 🔒 認証・認可設計

### 1. API Key認証

```python
# app/core/security.py

class APIKeyAuth:
    """API Key認証"""
    
    def __init__(self, api_keys: List[str]):
        self.api_keys = set(api_keys)
    
    async def __call__(self, api_key: str = Header(alias="X-API-Key")) -> str:
        if api_key not in self.api_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return api_key
```

### 2. Slack署名検証

```python
# app/core/slack_auth.py

class SlackSignatureAuth:
    """Slack署名検証"""
    
    def __init__(self, signing_secret: str):
        self.signing_secret = signing_secret
    
    async def verify_request(self, 
                           timestamp: str = Header(alias="X-Slack-Request-Timestamp"),
                           signature: str = Header(alias="X-Slack-Signature"),
                           body: bytes = Body()) -> bool:
        # Slack署名検証ロジック
        # 1. タイムスタンプ検証（5分以内）
        # 2. 署名生成と比較
        # 3. 検証結果返却
```

## 📊 エラーハンドリング・ロギング

### 1. 構造化ログ

```python
# app/core/logging.py

import structlog

def setup_logging():
    """構造化ログ設定"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

### 2. カスタム例外

```python
# app/core/exceptions.py

class TechBridgeException(Exception):
    """基底例外クラス"""
    pass

class WorkflowItemNotFound(TechBridgeException):
    """ワークフローアイテム未発見"""
    pass

class InvalidStatusTransition(TechBridgeException):
    """無効なステータス遷移"""
    pass

class SlackAPIError(TechBridgeException):
    """Slack API エラー"""
    pass

class GoogleSheetsError(TechBridgeException):
    """Google Sheets エラー"""
    pass
```

## 🧪 テスト戦略

### 1. テスト構成

```python
# tests/conftest.py

@pytest_asyncio.fixture
async def async_db_session():
    """テスト用データベースセッション"""
    # テスト用データベース設定
    
@pytest.fixture
def mock_slack_client():
    """Slackクライアントモック"""
    # Slack API呼び出しのモック

@pytest.fixture  
def mock_sheets_service():
    """Google Sheetsサービスモック"""
    # Google Sheets API呼び出しのモック
```

### 2. テストケース例

```python
# tests/test_workflow_service.py

class TestWorkflowService:
    """ワークフローサービステスト"""
    
    async def test_create_workflow_item(self, async_db_session, mock_slack_client):
        """ワークフローアイテム作成テスト"""
        # 1. テストデータ準備
        # 2. サービス実行
        # 3. 結果検証
        # 4. 副作用確認（Slack通知等）
    
    async def test_status_transition(self, async_db_session):
        """ステータス遷移テスト"""
        # 1. 正常遷移テスト
        # 2. 無効遷移テスト
        # 3. イベント記録確認
```

## 🚀 デプロイメント設計

### 1. Docker Compose構成

```yaml
# docker-compose.yml

version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/techbridge
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./config:/app/config

  worker:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/techbridge
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  scheduler:
    build: .
    command: celery -A app.tasks.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/techbridge
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=techbridge
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 2. 環境変数設定

```bash
# .env.production

# API設定
PROJECT_NAME=TechBridge
VERSION=1.0.0
API_V1_STR=/api/v1
ENVIRONMENT=production

# セキュリティ
SECRET_KEY=your-production-secret-key
API_KEYS=key1,key2,key3

# データベース
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/techbridge
REDIS_URL=redis://localhost:6379/0

# Slack
SLACK_BOT_TOKEN=xoxb-your-production-slack-bot-token
SLACK_SIGNING_SECRET=your-production-slack-signing-secret

# Google Sheets
GOOGLE_SHEETS_ID=your-production-sheets-id
GOOGLE_SERVICE_ACCOUNT_KEY=path/to/service-account.json

# 外部システム
TECH_WEBHOOK_SECRET=your-tech-webhook-secret
TECHZIP_WEBHOOK_SECRET=your-techzip-webhook-secret
TECHZIP_API_ENDPOINT=https://api.techzip.production.com

# 監視
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
LOG_LEVEL=INFO
```

## 📈 監視・メトリクス

### 1. Prometheus メトリクス

```python
# app/core/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# リクエストメトリクス
REQUEST_COUNT = Counter('techbridge_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('techbridge_request_duration_seconds', 'Request duration')

# ワークフローメトリクス  
WORKFLOW_STATUS_GAUGE = Gauge('techbridge_workflow_status_count', 'Workflow items by status', ['status'])
REMINDER_SENT_COUNTER = Counter('techbridge_reminders_sent_total', 'Total reminders sent', ['type'])

# 外部API メトリクス
SLACK_API_CALLS = Counter('techbridge_slack_api_calls_total', 'Slack API calls', ['method', 'status'])
SHEETS_API_CALLS = Counter('techbridge_sheets_api_calls_total', 'Google Sheets API calls', ['method', 'status'])
```

### 2. ヘルスチェック

```python
# app/api/health.py (拡張)

@router.get("/detailed")
async def detailed_health(db: AsyncSession = Depends(get_async_db)):
    """詳細ヘルスチェック"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # データベース接続チェック
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis接続チェック
    # Slack API接続チェック
    # Google Sheets API接続チェック
    
    return health_status
```

## 🎯 実装フェーズ計画

### Phase 1: 基盤実装 (1週間)

1. **Day 1-2**: データモデル拡張
   - WorkflowItem拡張
   - 新規テーブル作成
   - マイグレーション実装

2. **Day 3-4**: API エンドポイント実装
   - Progress Management APIs
   - Webhook エンドポイント
   - 基本認証・認可

3. **Day 5-7**: Service Layer実装
   - WorkflowService基本機能
   - SlackService拡張
   - エラーハンドリング

### Phase 2: Slack Bot統合 (1週間)

1. **Day 1-3**: Slack Commands実装
   - /status, /update コマンド
   - Events API処理
   - Interactive Components

2. **Day 4-5**: 通知システム実装
   - ステータス更新通知
   - 基本督促機能
   - チャンネル管理

3. **Day 6-7**: Google Sheets連携
   - 同期機能実装
   - 差分検出システム
   - 手動同期API

### Phase 3: 自動化・最適化 (1週間)

1. **Day 1-3**: Background Tasks
   - Celery設定
   - 定期タスク実装
   - 督促スケジューラー

2. **Day 4-5**: 監視・ロギング
   - 構造化ログ設定
   - メトリクス実装
   - ヘルスチェック拡張

3. **Day 6-7**: テスト・デプロイ
   - テストケース実装
   - Docker設定
   - CI/CD パイプライン

### Phase 4: 機能拡張 (任意)

- ダッシュボード UI
- 統計レポート機能
- カスタマイズ設定
- パフォーマンス最適化

## 🔗 既存システム統合方式

### [tech]プロジェクト統合

```python
# [tech]プロジェクト側に追加するWebhook送信コード例

import requests
import hmac
import hashlib

class TechBridgeWebhook:
    """TechBridge Progress Bridge API へのWebhook送信"""
    
    def __init__(self, endpoint: str, secret: str):
        self.endpoint = endpoint
        self.secret = secret
    
    def send_book_discovered(self, book_data: dict):
        """書籍発見通知"""
        payload = {
            "event_type": "book_discovered",
            "data": book_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._send_webhook("/webhook/tech/book-discovered", payload)
    
    def send_book_purchased(self, book_data: dict):
        """購入完了通知"""  
        payload = {
            "event_type": "book_purchased", 
            "data": book_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._send_webhook("/webhook/tech/book-purchased", payload)
    
    def _send_webhook(self, endpoint: str, payload: dict):
        """Webhook送信（署名付き）"""
        payload_json = json.dumps(payload)
        signature = hmac.new(
            self.secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "Content-Type": "application/json",
            "X-Tech-Signature": f"sha256={signature}"
        }
        
        response = requests.post(
            f"{self.endpoint}{endpoint}",
            data=payload_json,
            headers=headers
        )
        response.raise_for_status()
```

### [techzip]プロジェクト統合

```python
# [techzip]プロジェクト側に追加するAPI呼び出しコード例

class TechBridgeClient:
    """TechBridge Progress Bridge API クライアント"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
    
    def notify_conversion_completed(self, n_number: str, file_path: str):
        """変換完了通知"""
        payload = {
            "n_number": n_number,
            "conversion_completed_at": datetime.utcnow().isoformat(),
            "output_file_path": file_path,
            "metadata": {
                "conversion_tool": "techzip",
                "version": "1.0.0"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/webhook/techzip/conversion-completed",
            json=payload,
            headers={"X-API-Key": self.api_key}
        )
        response.raise_for_status()
    
    def update_status(self, n_number: str, new_status: str):
        """手動ステータス更新"""
        response = requests.put(
            f"{self.base_url}/api/v1/progress/{n_number}/status",
            json={"status": new_status, "source": "techzip"},
            headers={"X-API-Key": self.api_key}
        )
        response.raise_for_status()
```

## 📋 設定ファイル例

### 1. メッセージテンプレート

```json
// config/message_templates.json

{
  "status_update": {
    "discovered": {
      "title": "📚 新しい書籍を発見しました",
      "template": "「{title}」（{author}）を発見しました。\n次のステップ: 購入検討",
      "color": "#36a64f"
    },
    "purchased": {
      "title": "💰 書籍を購入しました", 
      "template": "「{title}」の購入が完了しました。\n次のステップ: 著者へ原稿依頼",
      "color": "#ff9500"
    },
    "completed": {
      "title": "✅ 書籍制作が完了しました",
      "template": "「{title}」の制作が完了しました！\n期間: {duration}日\n編集者: {editor}",
      "color": "#2eb886"
    }
  },
  
  "reminders": {
    "due_soon": {
      "title": "⚠️ 期限が近づいています",
      "template": "「{title}」の期限まで{days_remaining}日です。\n現在のステータス: {status}\n担当: {assigned_editor}"
    },
    "overdue": {
      "title": "🚨 期限を過ぎています", 
      "template": "「{title}」が期限を{days_overdue}日過ぎています。\n至急対応をお願いします。\n担当: {assigned_editor}"
    }
  }
}
```

### 2. 督促ルール設定

```json
// config/reminder_rules.json

{
  "reminder_rules": {
    "manuscript_requested": {
      "due_date_offset_days": 7,
      "reminders": [
        {"days_before": 3, "channels": ["author"], "template": "due_soon"},
        {"days_before": 1, "channels": ["author", "editor"], "template": "due_soon"},
        {"days_after": 1, "channels": ["editor", "management"], "template": "overdue"},
        {"days_after": 3, "channels": ["management"], "template": "overdue"}
      ]
    },
    "first_proof": {
      "due_date_offset_days": 5,
      "reminders": [
        {"days_before": 2, "channels": ["editor"], "template": "due_soon"},
        {"days_after": 1, "channels": ["editor", "management"], "template": "overdue"}
      ]
    }
  }
}
```

この設計書に基づいて、段階的にProgress Bridge APIの実装を進めることで、TechBridge書籍進行管理システムの中核となる統合レイヤーが構築できます。既存のFastAPI構造を最大限活用し、最小限の改修で[tech]と[techzip]プロジェクトとの統合を実現します。