# Phase 2 実装計画書
**CodeBlockOverFlowDisposal Phase 2: 78%目標達成とGUI統合**

## 📋 Phase 1完了状況の確認

### ✅ 達成事項
- **技術的基盤**: OCRベース検出アルゴリズム完成
- **品質基準**: CRITICAL: 0件、HIGH: 0件、テスト通過率: 100%
- **構造改善**: 複雑度20 → 5以下、FilterChainパターン採用
- **実測性能**: Recall 71.4%, Precision 83.3%
- **ライブラリ化**: `overflow_detection_lib`パッケージ構造完成

### 🎯 Phase 2目標設定

**主要目標**: Recall 71.4% → 78% (Phase 1目標達成)  
**副次目標**: GUI統合による実用性向上  
**最終目標**: TECHZIP統合による自動品質チェック機能

## 🚀 Phase 2-A: アルゴリズム改善 (78%達成)

### 現状分析
- **不足**: 6.6ポイント (78% - 71.4%)
- **見逃しページ**: 8ページ（28ページ中20ページ検出済み）
- **改善必要**: 約2ページの追加検出

### 技術的アプローチ

#### 1. **画像要素統合検出**
```python
class ImageElementDetector:
    """画像・図表からのはみ出し検出"""
    
    def detect_image_overflows(self, page) -> List[OverflowDetail]:
        """
        - 図表キャプションのはみ出し
        - 画像内テキスト（OCR連携）
        - 表組みの列幅はみ出し
        """
```

#### 2. **動的マージン調整**
```python
class AdaptiveMarginCalculator:
    """ページレイアウトに応じた動的マージン計算"""
    
    def calculate_adaptive_margin(self, page, page_num) -> float:
        """
        - ヘッダー・フッター検出
        - 段組み判定
        - コードブロック範囲認識
        """
```

#### 3. **コンテキスト認識フィルタ**
```python
class ContextAwareFilter:
    """文脈を考慮した高度フィルタリング"""
    
    def is_valid_overflow(self, text, context) -> bool:
        """
        - 前後文脈の解析
        - プログラミング言語固有パターン
        - 技術書特有の構造認識
        """
```

### 実装優先度
1. **HIGH**: 動的マージン調整 (推定+3-4ポイント効果)
2. **MEDIUM**: コンテキスト認識フィルタ (推定+2-3ポイント効果)
3. **LOW**: 画像要素統合検出 (推定+1-2ポイント効果)

## 🖥️ Phase 2-B: GUI統合実装

### アーキテクチャ設計

#### メインウィンドウ構成
```
┌─────────────────────────────────────┐
│ CodeBlock Overflow Detection v2.0  │
├─────────────────────────────────────┤
│ [📁 File Select] [⚙️ Settings]      │
├─────────────────────────────────────┤
│ ┌─ Detection Progress ─────────────┐ │
│ │ Processing: sample.pdf           │ │
│ │ ████████████████░░░░ 80%         │ │
│ │ Page 45/88 - 12 overflows found │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ ┌─ Results Summary ──────────────────┐│
│ │ Total Pages: 88                   ││
│ │ Detected Pages: 12 (13.6%)       ││
│ │ Recall: 78.2% | Precision: 91.3% ││
│ │                                   ││
│ │ [📋 Copy Pages] [💾 Export CSV]   ││
│ │ [🔍 View Details] [📊 Report]     ││
│ └───────────────────────────────────┘│
└─────────────────────────────────────┘
```

#### 技術スタック
- **GUI Framework**: PyQt6 (最新版、高DPI対応)
- **レイアウト**: QVBoxLayout + QHBoxLayout
- **非同期処理**: QThread (UI応答性確保)
- **設定管理**: QSettings (永続化)

### 実装計画

#### Phase 2-B1: 基本GUI (1-2日)
```python
class MainWindow(QMainWindow):
    def __init__(self):
        # ファイル選択エリア
        # 進捗表示エリア  
        # 結果表示エリア
        # ステータスバー
```

#### Phase 2-B2: 非同期処理 (1日)
```python
class DetectionWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    detection_completed = pyqtSignal(object)
    
    def run(self):
        # バックグラウンドでの検出処理
        # 進捗シグナル送信
```

#### Phase 2-B3: 結果表示 (1日)
```python
class ResultViewer(QWidget):
    def __init__(self):
        # ページリスト表示
        # 詳細情報表示
        # エクスポート機能
```

## 🔗 Phase 2-C: TECHZIP統合

### 統合アーキテクチャ

#### 1. **タブ統合**
```python
# main.py に追加
class QualityCheckTab(QWidget):
    """品質チェックタブ"""
    
    def __init__(self):
        self.detector = MaximumOCRDetectorV3()
        self.setup_ui()
    
    def check_pdf_quality(self, pdf_path):
        """PDFの品質チェック実行"""
```

#### 2. **後処理フック**
```python
# Word変換完了後の自動チェック
def post_conversion_hook(word_file_path):
    """変換完了後の自動品質チェック"""
    pdf_path = word_file_path.with_suffix('.pdf')
    if pdf_path.exists():
        detector = MaximumOCRDetectorV3()
        result = detector.detect_overflows(pdf_path)
        if result.detection_count > 0:
            show_quality_warning(result)
```

#### 3. **設定統合**
```json
// settings.json に追加
{
    "quality_check": {
        "auto_check_enabled": true,
        "threshold_pt": 0.1,
        "show_details": true,
        "export_results": false
    }
}
```

## 📅 実装スケジュール

### Week 1: アルゴリズム改善
- **Day 1-2**: 動的マージン調整実装
- **Day 3-4**: コンテキスト認識フィルタ実装  
- **Day 5**: 性能検証・78%達成確認

### Week 2: GUI統合
- **Day 1-2**: 基本GUIフレームワーク
- **Day 3**: 非同期処理・進捗表示
- **Day 4**: 結果表示・エクスポート機能
- **Day 5**: 統合テスト・UI/UX調整

### Week 3: TECHZIP統合
- **Day 1-2**: タブ統合・設定連携
- **Day 3**: 後処理フック実装
- **Day 4**: 統合テスト・品質確認
- **Day 5**: ドキュメント・リリース準備

## 🎯 成功基準

### Phase 2-A成功基準
- ✅ **Recall ≥ 78%** (Phase 1目標達成)
- ✅ **Precision ≥ 80%** (品質維持)
- ✅ **処理時間 ≤ 既存+20%** (性能劣化制限)

### Phase 2-B成功基準  
- ✅ **直感的UI** (技術者以外でも使用可能)
- ✅ **応答性** (100ページ処理で10秒以内応答)
- ✅ **エラーハンドリング** (わかりやすいエラーメッセージ)

### Phase 2-C成功基準
- ✅ **シームレス統合** (既存ワークフローを阻害しない)
- ✅ **設定連携** (TECHZIP設定との整合性)
- ✅ **後処理自動化** (手動操作なしの品質チェック)

## 🔄 Phase 3予告

Phase 2完了後は以下を予定：
- **機械学習統合**: より高精度な検出（85%目標）
- **クラウド連携**: 大容量PDF対応
- **多言語対応**: 英語技術書への対応拡張

---

**Phase 2開始準備完了 - 78%目標達成に向けた技術的挑戦を開始**