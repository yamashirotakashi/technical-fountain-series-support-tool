# CodeBlock OverFlow Disposal Mini App 仕様書
**プロジェクト**: PDF右端はみ出し検出スタンドアロンアプリケーション  
**作成日**: 2025-07-29  
**バージョン**: 1.0  
**作成者**: Claude Code  

## 📋 1. プロジェクト概要

### 1.1 目的
CodeBlockOverFlowDisposal Phase 1で開発された OCR ベース右端はみ出し検出システムを元に、TECHZIP統合前の検証用スタンドアロンアプリケーションを開発する。

### 1.2 開発背景
- Phase 1で 71.4% Recall を達成した検出エンジンの実用性検証
- TECHZIP本体への統合前の単体動作確認
- ライブラリ化設計の妥当性検証
- ユーザビリティの事前評価

### 1.3 成功基準
- ✅ 単体アプリとしての安定動作
- ✅ Phase 1と同等の検出性能維持
- ✅ ライブラリ分離可能な構造設計
- ✅ TECHZIP統合の技術的妥当性確認

## 🎯 2. 機能要件

### 2.1 基本機能フロー
```
[起動] → [ファイル選択] → [処理実行] → [結果表示] → [終了]
```

### 2.2 詳細機能仕様

#### 2.2.1 ファイル選択機能 (F001)
**機能名**: PDF ファイル選択  
**説明**: ユーザーが解析対象 PDF ファイルを選択する  

**詳細仕様**:
- ファイルダイアログによる GUI 選択
- 対応拡張子: `.pdf` のみ
- ファイルサイズ制限: 100MB 以下
- 複数ファイル選択: 不可（単一ファイル処理）

**入力**: ユーザーのファイル選択操作  
**出力**: 選択されたファイルパス  
**異常系**: ファイル未選択、非PDFファイル、破損PDFファイル  

#### 2.2.2 はみ出し検出機能 (F002)  
**機能名**: PDF右端はみ出し検出処理  
**説明**: 選択されたPDFファイルに対してはみ出し検出を実行  

**詳細仕様**:
- Phase 1 V3 検出エンジンを使用
- B5判型（515.9 x 728.5pt）前提
- 奇数ページ: 右マージン 10mm
- 偶数ページ: 右マージン 18mm
- ASCII文字のみ検出対象（ord < 128）
- 検出閾値: 0.1pt 超過

**入力**: PDFファイルパス  
**出力**: はみ出し検出結果（ページ番号リスト + 詳細情報）  
**異常系**: PDF読み込みエラー、メモリ不足、処理タイムアウト  

#### 2.2.3 結果表示機能 (F003)
**機能名**: 検出結果表示とコピー機能  
**説明**: はみ出しが検出されたページの一覧を表示し、クリップボードコピーを可能にする  

**詳細仕様**:
- 検出ページの改行区切りリスト表示
- 一括クリップボードコピー機能
- 個別ページ詳細表示（はみ出し文字、位置、量）
- 処理統計表示（処理時間、総ページ数、検出数）

**表示フォーマット例**:
```
検出されたはみ出しページ:
13
35
36
38
42

統計情報:
- 処理時間: 3.2秒
- 総ページ数: 150ページ
- 検出ページ数: 5ページ
- 検出率: 3.3%
```

**入力**: 検出結果データ  
**出力**: GUI表示 + クリップボードデータ  
**異常系**: 結果データ破損、クリップボードアクセスエラー  

### 2.3 補助機能

#### 2.3.1 進捗表示機能 (F004)
- プログレスバーによる処理進捗表示
- 現在処理中のページ番号表示
- キャンセル機能

#### 2.3.2 ログ出力機能 (F005)
- 処理ログのファイル出力
- エラー詳細のログ記録
- デバッグ情報の出力制御

## 🏗️ 3. システム構成

### 3.1 アーキテクチャ設計

```
┌─────────────────────────────────────┐
│           Mini App Layer            │
├─────────────────────────────────────┤
│  GUI Layer (PyQt5)                 │
│  - MainWindow                       │
│  - FileSelector                     │
│  - ResultDisplay                    │
│  - ProgressDialog                   │
├─────────────────────────────────────┤
│  Application Layer                  │
│  - AppController                    │
│  - FileHandler                      │
│  - ResultFormatter                  │
├─────────────────────────────────────┤
│  Library Layer (再利用可能)          │
│  - OCRBasedOverflowDetector         │
│  - FalsePositiveFilters             │
│  - ConfigManager                    │
└─────────────────────────────────────┘
```

### 3.2 モジュール設計

#### 3.2.1 コアライブラリ（再利用対象）
```python
# overflow_detection_lib/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── detector.py           # MaximumOCRDetectorV3 ベース
│   ├── filters.py            # FalsePositiveFilters
│   └── config.py             # ConfigManager
├── models/
│   ├── __init__.py
│   ├── result.py             # DetectionResult データクラス
│   └── settings.py           # Settings データクラス
└── utils/
    ├── __init__.py
    ├── file_utils.py         # PDF ファイル操作
    └── validation.py         # 入力検証
```

#### 3.2.2 アプリケーション層
```python
# mini_app/
├── __init__.py
├── controllers/
│   ├── __init__.py
│   └── app_controller.py     # メインコントローラー
├── views/
│   ├── __init__.py
│   ├── main_window.py        # メインウィンドウ
│   ├── file_selector.py      # ファイル選択ダイアログ
│   ├── result_display.py     # 結果表示ウィンドウ
│   └── progress_dialog.py    # 進捗表示ダイアログ
├── models/
│   ├── __init__.py
│   └── app_state.py          # アプリケーション状態管理
└── utils/
    ├── __init__.py
    ├── clipboard.py          # クリップボード操作
    └── logger.py             # ログ管理
```

### 3.3 データフロー設計

```
[User Input] 
    ↓
[FileSelector] → [Validation] → [File Path]
    ↓
[AppController] → [OCRBasedOverflowDetector] → [Detection Results]
    ↓
[ResultFormatter] → [ResultDisplay] → [Clipboard Copy]
```

## 🖥️ 4. GUI 設計

### 4.1 メインウィンドウ設計

#### 4.1.1 レイアウト構成
```
┌─────────────────────────────────────────────────────────┐
│ PDF はみ出し検出ツール                          [_][□][×] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📁 ファイル選択                                         │
│  ┌─────────────────────────────────────┐ [参照...]      │
│  │ 選択されたファイル: (なし)              │               │
│  └─────────────────────────────────────┘               │
│                                                         │
│  ⚙️  処理オプション                                      │
│  ☑ 詳細ログ出力    ☑ 処理統計表示                      │
│                                                         │
│                        [検出開始]                        │
│                                                         │
│  📊 検出結果                                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 検出されたはみ出しページ:                            │ │
│  │                                                     │ │
│  │ (結果がここに表示されます)                           │ │
│  │                                                     │ │
│  │                                                     │ │
│  │                                                     │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  [詳細表示]  [クリップボードにコピー]  [クリア]  [終了]  │
│                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  ステータス: 待機中                               v1.0   │
└─────────────────────────────────────────────────────────┘
```

#### 4.1.2 コンポーネント仕様

**ファイル選択エリア**:
- ラベル: 現在選択されているファイル名表示
- ボタン: ファイル選択ダイアログ起動
- ドラッグ&ドロップ対応（オプション）

**処理オプションエリア**:
- チェックボックス: 詳細ログ出力
- チェックボックス: 処理統計表示
- 将来拡張用のオプション領域

**結果表示エリア**:
- テキストエリア: 検出結果の表示
- フォント: 等幅フォント（Consolas, Monaco等）
- スクロールバー: 縦スクロール対応
- 選択可能: テキスト選択・コピー対応

**操作ボタンエリア**:
- 検出開始: メイン処理の実行
- 詳細表示: 詳細結果ウィンドウの表示
- クリップボードにコピー: 結果の一括コピー
- クリア: 結果エリアのクリア
- 終了: アプリケーション終了

### 4.2 進捗表示ダイアログ

#### 4.2.1 レイアウト構成
```
┌─────────────────────────────────────┐
│ PDF 処理中...                 [×] │
├─────────────────────────────────────┤
│                                     │
│  ファイル: sample.pdf               │
│  進捗: ████████░░░ 75%              │
│  現在のページ: 112 / 150            │
│  処理時間: 00:02:34                 │
│                                     │
│              [キャンセル]            │
│                                     │
└─────────────────────────────────────┘
```

#### 4.2.2 機能仕様
- プログレスバー: 0-100% の進捗表示
- ページ情報: 現在ページ / 総ページ数
- 処理時間: 経過時間の表示
- キャンセル機能: 処理の中止
- モーダルダイアログ: メイン画面の操作無効化

### 4.3 詳細結果ウィンドウ

#### 4.3.1 レイアウト構成
```
┌───────────────────────────────────────────────────────────┐
│ 検出詳細結果                                        [×] │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  📄 ファイル情報                                          │
│  ファイル名: sample.pdf                                   │
│  総ページ数: 150                                          │
│  処理時間: 3.24秒                                         │
│                                                           │
│  📊 検出統計                                              │
│  検出ページ数: 5 / 150 (3.3%)                            │
│  平均はみ出し量: 2.1pt                                    │
│  最大はみ出し量: 5.7pt (Page 38)                         │
│                                                           │
│  📋 詳細結果                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │Page │ はみ出し文字 │ 位置(pt) │ はみ出し量 │ 信頼度 │   │
│  ├─────┼─────────────┼─────────┼───────────┼────────┤   │
│  │ 13  │ function()  │ 487.2   │ +1.8pt    │ High   │   │
│  │ 35  │ "           │ 489.1   │ +1.2pt    │ High   │   │
│  │ 36  │ }           │ 490.5   │ +2.6pt    │ High   │   │
│  │ 38  │ console.log │ 492.8   │ +5.7pt    │ High   │   │
│  │ 42  │ ->          │ 488.9   │ +1.4pt    │ Med    │   │
│  └─────┴─────────────┴─────────┴───────────┴────────┘   │
│                                                           │
│  [CSV出力]  [詳細ログ表示]  [閉じる]                      │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## 🔧 5. API 設計（ライブラリ化前提）

### 5.1 コアライブラリAPI

#### 5.1.1 OCRBasedOverflowDetector クラス
```python
class OCRBasedOverflowDetector:
    """OCRベースはみ出し検出器（Phase 1 V3ベース）"""
    
    def __init__(self, config: DetectionConfig = None):
        """
        Args:
            config: 検出設定（デフォルト: config.json から読み込み）
        """
    
    def detect(self, pdf_path: Path) -> DetectionResult:
        """
        PDF ファイルのはみ出し検出を実行
        
        Args:
            pdf_path: PDF ファイルのパス
            
        Returns:
            DetectionResult: 検出結果
            
        Raises:
            FileNotFoundError: PDF ファイルが存在しない
            PDFProcessingError: PDF 処理エラー
            InvalidPDFError: 不正な PDF ファイル
        """
    
    def detect_async(self, pdf_path: Path, 
                    progress_callback: Callable[[int, int], None] = None,
                    cancel_token: CancelToken = None) -> DetectionResult:
        """
        非同期でのはみ出し検出実行
        
        Args:
            pdf_path: PDF ファイルのパス
            progress_callback: 進捗通知コールバック (current_page, total_pages)
            cancel_token: キャンセルトークン
            
        Returns:
            DetectionResult: 検出結果
        """
    
    @property
    def config(self) -> DetectionConfig:
        """現在の検出設定を取得"""
    
    @config.setter  
    def config(self, value: DetectionConfig) -> None:
        """検出設定を更新"""
```

#### 5.1.2 DetectionResult データクラス
```python
@dataclass
class DetectionResult:
    """検出結果データクラス"""
    
    # 基本情報
    pdf_path: Path
    total_pages: int
    processing_time: float
    detection_timestamp: datetime
    
    # 検出結果
    detected_pages: List[int]
    detection_details: List[OverflowDetail]
    
    # 統計情報
    detection_count: int
    detection_rate: float
    avg_overflow_amount: float
    max_overflow_amount: float
    
    # 品質情報
    confidence_scores: List[float]
    processing_warnings: List[str]
    
    def to_page_list(self) -> str:
        """改行区切りのページリスト文字列を生成"""
        
    def to_detailed_report(self) -> str:
        """詳細レポート文字列を生成"""
        
    def to_csv(self) -> str:
        """CSV 形式の詳細データを生成"""
```

#### 5.1.3 OverflowDetail データクラス
```python
@dataclass
class OverflowDetail:
    """個別はみ出し詳細データ"""
    
    page_number: int
    overflow_text: str
    x_position: float
    y_position: float
    overflow_amount: float
    confidence: ConfidenceLevel
    char_count: int
    
    def __str__(self) -> str:
        """文字列表現（ログ出力用）"""
```

### 5.2 設定管理 API

#### 5.2.1 DetectionConfig クラス
```python
@dataclass
class DetectionConfig:
    """検出設定データクラス"""
    
    # PDF 設定
    pdf_size: PDFSize
    margins: MarginSettings
    
    # 検出設定
    overflow_threshold_pt: float = 0.1
    measurement_error_threshold_pt: float = 0.5
    max_page_number_digits: int = 3
    
    # フィルタ設定  
    protected_symbols: List[str]
    excluded_extensions: List[str]
    powershell_min_length: int = 10
    
    # 品質設定
    max_function_complexity: int = 15
    min_test_coverage_percent: int = 80
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'DetectionConfig':
        """設定ファイルから読み込み"""
        
    def to_file(self, config_path: Path) -> None:
        """設定ファイルに保存"""
```

## ⚠️ 6. エラーハンドリング設計

### 6.1 例外階層設計

```python
class OverflowDetectionError(Exception):
    """はみ出し検出関連の基底例外"""
    pass

class PDFProcessingError(OverflowDetectionError):
    """PDF 処理エラー"""
    pass

class InvalidPDFError(PDFProcessingError):
    """不正な PDF ファイル"""
    pass

class ConfigurationError(OverflowDetectionError):
    """設定エラー"""
    pass

class ProcessingTimeoutError(OverflowDetectionError):
    """処理タイムアウト"""
    pass
```

### 6.2 エラーハンドリング方針

#### 6.2.1 GUI レベル
- ユーザーフレンドリーなエラーメッセージ表示
- エラー詳細のログファイル出力
- 処理続行可能な軽微エラーの警告表示
- 重篤エラーの適切な終了処理

#### 6.2.2 ライブラリレベル
- 明確な例外タイプの提供
- エラー原因の詳細情報提供
- 回復可能エラーの明示
- ログ出力による詳細トレース

### 6.3 具体的エラーケース

| エラーケース | 例外タイプ | GUI での対応 | ログ出力 |
|-------------|-----------|-------------|----------|
| PDF ファイル未選択 | ValueError | 警告ダイアログ | INFO |
| PDF ファイル不存在 | FileNotFoundError | エラーダイアログ | ERROR |
| PDF 読み込みエラー | InvalidPDFError | エラーダイアログ + 対処法 | ERROR |
| メモリ不足 | MemoryError | エラーダイアログ + 終了 | CRITICAL |
| 処理タイムアウト | ProcessingTimeoutError | 確認ダイアログ | WARNING |
| 設定ファイルエラー | ConfigurationError | デフォルト設定で続行 | WARNING |

## 🧪 7. テスト計画

### 7.1 テスト戦略

#### 7.1.1 単体テスト
- **対象**: ライブラリレイヤー全体
- **フレームワーク**: pytest  
- **カバレッジ目標**: 90% 以上
- **実行頻度**: 毎回のコミット前

#### 7.1.2 統合テスト
- **対象**: アプリケーションレイヤー
- **フレームワーク**: pytest + PyQt5 テストユーティリティ
- **カバレッジ目標**: 80% 以上
- **実行頻度**: 毎回のビルド時

#### 7.1.3 UI テスト
- **対象**: GUI コンポーネント
- **手法**: 手動テスト + 自動化スクリプト
- **カバレッジ**: 主要フロー 100%
- **実行頻度**: リリース前

#### 7.1.4 性能テスト
- **対象**: 検出処理性能
- **測定項目**: 処理時間、メモリ使用量、CPU 使用率
- **基準**: Phase 1 と同等性能
- **実行頻度**: 主要機能変更時

### 7.2 テストケース設計

#### 7.2.1 機能テスト
```python
def test_file_selection():
    """ファイル選択機能のテスト"""
    # 正常ケース: 有効なPDFファイル選択
    # 異常ケース: 非PDFファイル選択
    # 異常ケース: 存在しないファイル
```

```python
def test_overflow_detection():
    """はみ出し検出機能のテスト"""
    # 正常ケース: 既知の結果を持つPDFでの検出
    # 境界ケース: はみ出しなしのPDF
    # 異常ケース: 破損PDFファイル
```

#### 7.2.2 性能テスト
```python
def test_detection_performance():
    """検出性能のテスト"""
    # 大容量PDF (100ページ以上) での処理時間測定
    # メモリ使用量の監視
    # プログレス更新の確認
```

#### 7.2.3 UI テスト
```python 
def test_main_window_interaction():
    """メインウィンドウ操作のテスト"""
    # ファイル選択ダイアログの動作
    # 検出結果の表示
    # クリップボードコピー機能
```

## 🔗 8. TECHZIP 統合計画

### 8.1 統合アーキテクチャ

#### 8.1.1 統合方式
```
TECHZIP Main Application
├── GUI Layer (PyQt5/Qt6)
│   ├── 既存機能タブ
│   └── 📋 品質チェックタブ ← 新規追加
│       ├── PDF選択エリア  
│       ├── はみ出し検出結果
│       └── Word変換後自動検査
├── Application Layer  
│   ├── 既存アプリケーションロジック
│   └── 🔧 OverflowDetectionService ← 新規追加
└── Library Layer
    ├── 既存共通ライブラリ
    └── 📚 overflow_detection_lib ← Phase 1から移植
```

#### 8.1.2 統合インターフェース
```python
class TechZipOverflowIntegration:
    """TECHZIP統合用インターフェース"""
    
    def integrate_pdf_check_tab(self, main_window: QMainWindow) -> None:
        """品質チェックタブをTECHZIPメインウィンドウに追加"""
        
    def register_post_conversion_hook(self, word_converter: WordConverter) -> None:
        """Word変換後の自動検査フックを登録"""
        
    def get_detection_service(self) -> OverflowDetectionService:
        """検出サービスインスタンスを取得"""
```

### 8.2 統合スケジュール

#### Phase 2.1: ライブラリ分離 (予想工数: 8時間)
- [x] overflow_detection_lib パッケージ作成
- [ ] Mini App からのライブラリ分離
- [ ] 独立したライブラリとしての動作確認
- [ ] TECHZIPプロジェクトへのライブラリ配置

#### Phase 2.2: GUI統合 (予想工数: 12時間)  
- [ ] TECHZIP メインウィンドウへのタブ追加
- [ ] 既存設定システムとの統合
- [ ] 既存ログシステムとの統合
- [ ] 統合テストの実施

#### Phase 2.3: ワークフロー統合 (予想工数: 6時間)
- [ ] Word変換後の自動検査フック実装
- [ ] 検出結果の報告機能追加  
- [ ] 品質レポート生成機能
- [ ] エンドツーエンドテストの実施

### 8.3 統合リスク分析

| リスク要因 | 影響度 | 発生確率 | 対策 |
|-----------|--------|---------|------|
| TECHZIP UI フレームワーク不一致 | High | Low | 事前調査による互換性確認 |  
| 性能劣化（GUI統合時） | Medium | Medium | 非同期処理による UI ブロック回避 |
| 設定ファイル競合 | Medium | High | 設定統合仕様の詳細設計 |
| 既存機能への影響 | High | Low | 独立性確保によるリスク最小化 |

## 📋 9. 実装計画

### 9.1 開発フェーズ

#### Phase A: ライブラリ分離 (2日)
```
Day 1: 
- [ ] overflow_detection_lib パッケージ構造作成
- [ ] Phase 1 V3コードのライブラリ化
- [ ] API設計の実装

Day 2:
- [ ] 単体テスト実装
- [ ] パフォーマンステスト
- [ ] ドキュメント作成
```

#### Phase B: GUI アプリケーション (3日)
```
Day 1:
- [ ] メインウィンドウ実装
- [ ] ファイル選択機能実装

Day 2: 
- [ ] 検出処理統合
- [ ] 結果表示機能実装
- [ ] 進捗表示機能実装

Day 3:
- [ ] 詳細表示ウィンドウ実装
- [ ] エラーハンドリング実装
- [ ] 全体統合テスト
```

#### Phase C: 品質保証・最適化 (1日)
```
Day 1:
- [ ] コードレビュー  
- [ ] 性能最適化
- [ ] ユーザビリティテスト
- [ ] ドキュメント完成
```

### 9.2 技術仕様

#### 9.2.1 開発環境
- **Python**: 3.8+
- **GUI フレームワーク**: PyQt5 (TECHZIP互換性)
- **PDF処理**: pdfplumber 0.9+
- **テストフレームワーク**: pytest 7.0+
- **コード品質**: flake8, black, mypy

#### 9.2.2 システム要件
- **OS**: Windows 10/11 (プライマリ), macOS (セカンダリ)
- **メモリ**: 最小 2GB, 推奨 4GB
- **ストレージ**: 100MB (アプリ本体 + 依存関係)
- **PDF ファイル**: 最大 100MB まで対応

### 9.3 品質基準

#### 9.3.1 性能基準
- **処理速度**: 100ページ/10秒以下
- **メモリ使用量**: 500MB 以下
- **起動時間**: 3秒以下
- **応答時間**: UI操作1秒以下

#### 9.3.2 品質基準  
- **テストカバレッジ**: 90% 以上
- **複雑度**: 関数あたり15以下
- **重複率**: 5% 以下
- **型ヒント**: 95% 以上

## 📚 10. リリース計画

### 10.1 バージョニング方針
- **Major (X.0.0)**: アーキテクチャ変更、非互換性変更
- **Minor (0.X.0)**: 新機能追加、互換性維持
- **Patch (0.0.X)**: バグ修正、性能改善

### 10.2 リリーススケジュール
- **v1.0.0-alpha**: ライブラリ分離完了 (開発開始から1週間)
- **v1.0.0-beta**: GUI アプリケーション完成 (開発開始から2週間)  
- **v1.0.0**: 品質保証完了、リリース (開発開始から3週間)
- **v1.1.0**: TECHZIP統合完了 (v1.0.0から4週間後)

### 10.3 成果物
- [ ] 実行可能アプリケーション (exe/app)
- [ ] ライブラリパッケージ (wheel)
- [ ] 技術ドキュメント
- [ ] ユーザーマニュアル  
- [ ] TECHZIP統合ガイド

---

## 📋 付録

### A. 用語集
- **はみ出し**: PDF右端マージンを超えて配置された文字
- **検出閾値**: はみ出し判定の最小距離（0.1pt）
- **Phase 1**: 基礎検出エンジン開発フェーズ
- **Phase 2**: TECHZIP統合フェーズ  
- **B5判型**: 515.9 x 728.5pt のPDFサイズ

### B. 参考資料
- `/CodeBlockOverFlowDisposal/maximum_ocr_detector_v3.py`
- `/CodeBlockOverFlowDisposal/FINAL_IMPLEMENTATION_STRUCTURE.md`
- `/CodeBlockOverFlowDisposal/config.json`
- `/CLAUDE.md` (TECHZIP プロジェクト設定)

### C. 変更履歴
| バージョン | 日付 | 変更内容 | 担当者 |
|-----------|------|---------|--------|
| 1.0 | 2025-07-29 | 初版作成 | Claude Code |

---

**仕様書承認**: 未承認  
**技術レビュー**: 未実施  
**ステータス**: ドラフト