# AI実装の落とし穴回避ガイド
## ClaudeCode向け - 実践的で保守可能な実装のために

### 🚫 よくある実装の落とし穴と回避方法

#### 1. ❌ 動くだけの実装（Quick & Dirty）

**悪い例：**
```python
# ❌ エラーハンドリングなし、マジックナンバー、コメントなし
def detect_overflow(pdf):
    try:
        pages = pdf.pages
        results = []
        for p in pages:
            chars = p.chars
            for c in chars:
                if c['x1'] > 400:  # マジックナンバー
                    results.append(c)
        return results
    except:
        return []  # すべてのエラーを握りつぶす
```

**良い例：**
```python
# ✅ 適切なエラーハンドリング、定数定義、ドキュメント
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# 定数は明確に定義
DEFAULT_CODE_BLOCK_WIDTH = 400.0  # pt
CHAR_POSITION_TOLERANCE = 0.1  # pt

def detect_overflow(pdf_page: pdfplumber.page.Page, 
                   block_width: float = DEFAULT_CODE_BLOCK_WIDTH) -> List[Dict]:
    """
    コードブロックのはみ出しを検出
    
    Args:
        pdf_page: 解析対象のPDFページ
        block_width: コードブロックの幅（pt）
        
    Returns:
        はみ出した文字情報のリスト
        
    Note:
        文字情報が取得できない場合は空リストを返す
    """
    try:
        chars = pdf_page.chars
        if not chars:
            logger.debug(f"No characters found on page {pdf_page.page_number}")
            return []
            
        overflow_chars = []
        for char in chars:
            # 明確な条件判定
            right_edge = char.get('x1', 0)
            if right_edge > block_width + CHAR_POSITION_TOLERANCE:
                overflow_width = right_edge - block_width
                logger.debug(f"Overflow detected: {overflow_width:.1f}pt at line {char.get('y0', 0)}")
                overflow_chars.append(char)
                
        return overflow_chars
        
    except AttributeError as e:
        logger.error(f"Invalid page object: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in overflow detection: {e}")
        return []
```

#### 2. ❌ テストを通すだけの実装

**悪い例：**
```python
# ❌ テストケースに特化した実装
def calculate_overflow_width(line_text, block_width):
    # テストが "test" という文字列を期待している場合
    if line_text == "test":
        return 10.0  # テストが期待する値をハードコード
    
    # 実際の計算は適当
    return len(line_text) * 7 - block_width
```

**良い例：**
```python
# ✅ 汎用的で正確な実装
from typing import Dict, Optional

class FontMetrics:
    """フォントメトリクスの管理"""
    
    # 実際の測定値に基づく
    DEFAULT_CHAR_WIDTHS = {
        'monospace': {
            'ascii': 7.2,      # 実測値
            'fullwidth': 14.4  # 実測値
        }
    }
    
    @classmethod
    def calculate_text_width(cls, text: str, font_info: Dict) -> float:
        """
        テキストの幅を計算
        
        実装の根拠：
        - 等幅フォントでも文字種によって幅が異なる
        - 日本語は基本的に英数字の2倍幅
        """
        font_name = font_info.get('name', 'monospace')
        char_widths = cls.DEFAULT_CHAR_WIDTHS.get(font_name, cls.DEFAULT_CHAR_WIDTHS['monospace'])
        
        total_width = 0.0
        for char in text:
            if ord(char) < 128:  # ASCII
                total_width += char_widths['ascii']
            else:  # 全角文字として扱う
                total_width += char_widths['fullwidth']
                
        return total_width
```

#### 3. ❌ モックでごまかした実装

**悪い例：**
```python
# ❌ 実際の処理をモックで置き換え
class VisualAnalyzer:
    def analyze(self, pdf_path):
        # TODO: 実装する
        return MockResult(overflow_detected=True, width=10.0)
        
class MockResult:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
```

**良い例：**
```python
# ✅ 実際に動作する最小限の実装
class VisualAnalyzer:
    """視覚的解析の実装"""
    
    def __init__(self, dpi: int = 150):  # 開発時は低解像度でも可
        self.dpi = dpi
        self._renderer = None
        
    def analyze(self, pdf_path: str, page_num: int, bbox: Tuple[float, float, float, float]) -> VisualAnalysisResult:
        """
        最小限だが実際に動作する実装
        
        Note:
            初期バージョンでは基本的なエッジ検出のみ
            将来的により高度な手法を追加予定
        """
        # 実際にPDFをレンダリング（低解像度でも動作確認可能）
        image = self._render_page_region(pdf_path, page_num, bbox)
        
        # シンプルだが実際に動作するエッジ検出
        edges = self._simple_edge_detection(image)
        
        # 基本的なはみ出し判定
        overflow_width = self._measure_overflow(edges, bbox)
        
        return VisualAnalysisResult(
            overflow_detected=overflow_width > 0,
            overflow_width_pt=overflow_width,
            confidence=0.7,  # 簡易版なので控えめな信頼度
            method_details={'dpi': self.dpi, 'algorithm': 'simple_edge'}
        )
```

#### 4. ❌ 仕様から妄想した過剰実装

**悪い例：**
```python
# ❌ 要求されていない機能を勝手に追加
class OverflowDetector:
    def __init__(self):
        self.ml_model = self._load_ml_model()  # 機械学習は要求されていない
        self.ocr_engine = self._init_ocr()     # OCRも不要
        self.cloud_backup = self._setup_cloud() # クラウド連携も不要
        
    def detect(self, pdf):
        # 過剰に複雑な処理
        preprocessed = self._ai_preprocess(pdf)
        features = self._extract_deep_features(preprocessed)
        prediction = self.ml_model.predict(features)
        self._upload_to_cloud(prediction)
        return self._post_process_with_nlp(prediction)
```

**良い例：**
```python
# ✅ 仕様に忠実な実装
class OverflowDetector:
    """
    コードブロックのはみ出し検出
    
    仕様の要求:
    - PDFからテキスト位置を抽出
    - コードブロック境界との比較
    - 1pt単位の精度
    """
    
    def __init__(self, config: Optional[Dict] = None):
        # 必要最小限の初期化
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
    def detect(self, pdf_path: str, page_num: int) -> List[OverflowInfo]:
        """
        仕様通りの検出処理
        
        実装内容：
        1. PDFページからテキスト情報抽出（pdfplumber使用）
        2. コードブロック識別（背景色またはパターン）
        3. はみ出し計算（文字位置とブロック境界の比較）
        """
        # 仕様に記載された処理のみを実装
        pass
```

### 📋 実装前のチェックリスト

```python
"""
AI実装前に確認すべき事項：

□ 仕様書に明記されている機能か？
  → YESでなければ実装しない

□ 既存システムに同様の機能/パターンがあるか？
  → YESなら同じパターンに従う

□ 外部ライブラリは本当に必要か？
  → 標準ライブラリで代替できないか検討

□ エラーケースを具体的に想定したか？
  → ファイルなし、メモリ不足、不正なPDF等

□ パフォーマンス要件を確認したか？
  → 100ページを30秒以内

□ テストは実際の使用ケースを反映しているか？
  → 実際のPDFファイルでテスト
"""
```

### 🎯 実装の優先順位

```python
# 実装の優先順位を明確に

IMPLEMENTATION_PRIORITY = {
    "MUST_HAVE": [
        "基本的なテキストベース検出",
        "1pt精度でのはみ出し幅計算",
        "エラーハンドリング",
        "基本的なレポート生成",
    ],
    
    "SHOULD_HAVE": [
        "視覚的検証（精度向上のため）",
        "キャッシュ機能",
        "並列処理",
    ],
    
    "NICE_TO_HAVE": [
        "プログレスバー",
        "詳細なログ",
        "設定のバリデーション",
    ],
    
    "DO_NOT_IMPLEMENT": [
        "機械学習/AI機能",
        "クラウド連携",
        "GUI",
        "自動修正機能",
        "他形式への変換",
    ]
}
```

### 🔍 実装の検証方法

```python
# 実装が適切かを検証する具体的な方法

def verify_implementation():
    """
    AI: 実装完了後、以下を確認
    """
    
    # 1. 実際のPDFで動作確認
    test_files = [
        "40_pages_no_overflow.pdf",
        "100_pages_with_overflow.pdf", 
        "200_pages_mixed.pdf"
    ]
    
    # 2. メモリ使用量の確認
    import psutil
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 処理実行
    
    peak_memory = process.memory_info().rss / 1024 / 1024  # MB
    assert peak_memory - initial_memory < 1000  # 1GB以内
    
    # 3. 処理時間の確認
    import time
    start = time.time()
    
    # 100ページの処理
    
    duration = time.time() - start
    assert duration < 30  # 30秒以内
    
    # 4. 精度の確認
    known_overflows = {
        "page_10": 5.5,   # 既知のはみ出し幅
        "page_20": 15.3,
        "page_30": 0.5,   # 微小なはみ出し
    }
    
    # 検出結果と比較
```

### 💡 実装のヒント集

#### データ構造の選択
```python
# ❌ 過剰に複雑なデータ構造
class OverflowData:
    def __init__(self):
        self.tree = BinarySearchTree()
        self.graph = DirectedGraph()
        self.matrix = scipy.sparse.csr_matrix()

# ✅ シンプルで十分な構造
@dataclass
class OverflowInfo:
    page_num: int
    line_num: int
    overflow_width: float
    
    # 必要に応じて追加可能
```

#### 設定の管理
```python
# ❌ 過剰な設定項目
config = {
    "detection": {
        "text": {
            "advanced": {
                "neural_network": {...},
                "fuzzy_logic": {...},
            }
        }
    }
}

# ✅ 必要十分な設定
config = {
    "overflow_threshold_pt": 0.1,
    "detection_dpi": 150,
    "max_parallel_pages": 4,
    "cache_enabled": True
}
```

#### パフォーマンスの考慮
```python
# ❌ 無駄な最適化
def process_page(page):
    # 不要なマルチプロセッシング
    with multiprocessing.Pool(32) as pool:
        chars = pool.map(process_char, page.chars)

# ✅ 適切な最適化
def process_pages(pages):
    # ページ単位で並列化（I/Oバウンドなタスクに適切）
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(process_single_page, pages)
```

### 📝 最終確認事項

```python
"""
実装完了時の最終チェック：

1. 仕様との一致
   - 要求された機能のみ実装されているか
   - 勝手な機能追加はないか

2. エラー処理
   - try-exceptが適切に使われているか
   - エラーメッセージは具体的か

3. パフォーマンス
   - 100ページを30秒で処理できるか
   - メモリ使用量は2GB以内か

4. 保守性
   - コードは読みやすいか
   - 将来の拡張が容易か

5. テスト
   - 実際のPDFでテストしたか
   - エッジケースをカバーしているか
"""
```