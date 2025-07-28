# AI実装ガイド：段階的実装手順
## ClaudeCode向け具体的実装指示

### 🚀 実装開始前の確認事項

```bash
# AI: 最初に以下のコマンドを実行して環境を確認

# 1. Pythonバージョン確認
python --version  # 3.8以上であること

# 2. 既存プロジェクト構造の確認
find . -name "*.py" -type f | grep -E "(pdf|valid|check)" | head -20

# 3. 既存の依存関係確認
if [ -f "requirements.txt" ]; then
    cat requirements.txt
elif [ -f "setup.py" ]; then
    grep -A 20 "install_requires" setup.py
elif [ -f "pyproject.toml" ]; then
    grep -A 20 "dependencies" pyproject.toml
fi

# 4. テストPDFの存在確認
find . -name "*.pdf" -type f | head -5
```

### 📦 Step 1: パッケージ構造の作成

```bash
# AI: 以下のコマンドを順番に実行

# ベースディレクトリ作成
mkdir -p overflow_detection/{core,models,utils,reporting,integration,config,tests}

# 各ディレクトリに__init__.pyを作成
touch overflow_detection/__init__.py
touch overflow_detection/core/__init__.py
touch overflow_detection/models/__init__.py
touch overflow_detection/utils/__init__.py
touch overflow_detection/reporting/__init__.py
touch overflow_detection/integration/__init__.py
touch overflow_detection/tests/__init__.py

# 基本ファイルの作成
touch overflow_detection/__version__.py
touch overflow_detection/cli.py
touch overflow_detection/api.py
```

### 📝 Step 2: 基本ファイルの実装

#### 2.1 バージョン情報
```python
# overflow_detection/__version__.py
"""
AIへの実装指示:
シンプルなバージョン情報ファイル
"""
__version__ = "0.1.0"
__author__ = "NextPublishing Editor Team"
__description__ = "Hybrid overflow detection system for code blocks in PDF"
```

#### 2.2 パッケージ初期化
```python
# overflow_detection/__init__.py
"""
AIへの実装指示:
1. バージョン情報をインポート
2. 主要クラスを公開
3. ログ設定の初期化
"""
from .__version__ import __version__, __author__, __description__
import logging

# ログ設定
logging.getLogger(__name__).addHandler(logging.NullHandler())

# 遅延インポート（循環参照を避ける）
def get_detector():
    from .core.detector import HybridOverflowDetector
    return HybridOverflowDetector

__all__ = ['__version__', 'get_detector']
```

### 🏗️ Step 3: モデルクラスの実装

#### 3.1 データモデル
```python
# overflow_detection/models/detection.py
"""
AIへの実装指示:
1. Python 3.8+ のdataclassを使用
2. 型ヒントを完全に付与
3. JSON変換メソッドを含める
4. __str__と__repr__を実装
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
from enum import Enum
import json

class Severity(Enum):
    """はみ出しの重要度"""
    MICRO = "micro"      # < 1pt
    MINOR = "minor"      # 1-5pt
    MODERATE = "moderate" # 5-20pt
    MAJOR = "major"      # 20-50pt
    CRITICAL = "critical" # > 50pt
    
    @classmethod
    def from_width(cls, width_pt: float) -> 'Severity':
        """幅から重要度を判定"""
        if width_pt < 1.0:
            return cls.MICRO
        elif width_pt < 5.0:
            return cls.MINOR
        elif width_pt < 20.0:
            return cls.MODERATE
        elif width_pt < 50.0:
            return cls.MAJOR
        else:
            return cls.CRITICAL

@dataclass
class CodeBlock:
    """コードブロック情報"""
    page_number: int
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)
    text: str
    background_color: Optional[Tuple[float, float, float]] = None
    
    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]
    
    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]

@dataclass
class OverflowInfo:
    """はみ出し情報"""
    line_number: int
    line_text: str
    overflow_width_pt: float
    category: Severity
    confidence: float
    detection_source: str  # "text", "visual", "consensus"
    bbox: Tuple[float, float, float, float]
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = asdict(self)
        data['category'] = self.category.value
        return data

# 実装を続ける...
```

#### 3.2 例外クラス
```python
# overflow_detection/models/exceptions.py
"""
AIへの実装指示:
1. 基底クラスから階層的に定義
2. エラーコードとリカバリーアクションを含める
3. 詳細なエラーメッセージ
"""
class OverflowDetectionError(Exception):
    """基底例外クラス"""
    error_code: str = "E0000"
    recovery_action: str = "none"
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

# 具体的な例外クラス...
```

### 🔧 Step 4: ユーティリティの実装

#### 4.1 キャッシュマネージャー
```python
# overflow_detection/utils/cache_manager.py
"""
AIへの実装指示:
1. メモリとディスクの2層キャッシュ
2. スレッドセーフな実装
3. 自動クリーンアップ機能
"""
import os
import pickle
import hashlib
import time
from pathlib import Path
from typing import Optional, Any, Dict
from functools import lru_cache
import threading

class CacheManager:
    """
    AI実装の重要ポイント:
    - _lockを使ってスレッドセーフに
    - weakrefで自動メモリ管理
    - atexit.registerでクリーンアップ
    """
    
    def __init__(self, cache_dir: Path = Path(".overflow_cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self._memory_cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        # クリーンアップの登録
        import atexit
        atexit.register(self.cleanup)
```

### 🎯 Step 5: コア機能の実装

#### 5.1 テキストアナライザー
```python
# overflow_detection/core/text_analyzer.py
"""
AIへの段階的実装指示:

1. 最初にインポートとクラス定義
2. 次にヘルパーメソッド（_で始まる）
3. 最後にパブリックメソッド
4. 各メソッドは20行以内に収める
"""
import pdfplumber
from typing import List, Dict, Tuple, Optional
import logging
from ..models.detection import CodeBlock, OverflowInfo, Severity

logger = logging.getLogger(__name__)

class TextAnalyzer:
    """テキストベースはみ出し検出"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        AI: configはNoneでもデフォルト値で動作するように
        """
        self.config = config or self._default_config()
        
    def analyze_page(self, page: pdfplumber.page.Page) -> List[OverflowInfo]:
        """
        ページ解析のメイン関数
        
        AI実装フロー:
        1. try-exceptで全体をラップ
        2. コードブロック検出
        3. 各ブロックでオーバーフロー検出
        4. エラー時は空リストを返す
        """
        try:
            code_blocks = self._detect_code_blocks(page)
            overflows = []
            
            for block in code_blocks:
                block_overflows = self._check_block_overflow(block, page)
                overflows.extend(block_overflows)
                
            return overflows
            
        except Exception as e:
            logger.error(f"Page analysis failed: {e}")
            return []
```

### 🧪 Step 6: テストの実装

#### 6.1 テスト用PDFジェネレーター
```python
# overflow_detection/tests/fixtures/pdf_generator.py
"""
AIへの実装指示:
最小限のテストPDFを生成するユーティリティ
reportlabは使わず、PyMuPDFで生成
"""
import fitz  # PyMuPDF
from pathlib import Path

def create_test_pdf_with_overflow(
    output_path: Path,
    overflow_width_pt: float = 10.0
) -> None:
    """
    テスト用PDFを生成
    
    AI実装ポイント:
    1. A4サイズ（595x842pt）
    2. グレー背景のコードブロック
    3. 指定幅のはみ出しを含む
    """
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    
    # コードブロックの背景（グレー）
    rect = fitz.Rect(50, 100, 400, 200)
    page.draw_rect(rect, color=(0.9, 0.9, 0.9), fill=(0.9, 0.9, 0.9))
    
    # はみ出すテキストを追加
    long_text = "x" * int((350 + overflow_width_pt) / 7)  # 約7pt/文字
    page.insert_text((55, 120), long_text, fontsize=10)
    
    doc.save(output_path)
    doc.close()
```

#### 6.2 基本的な単体テスト
```python
# overflow_detection/tests/test_core/test_detection.py
"""
AIへの実装指示:
pytestを使用
fixtureで共通の準備
パラメトライズドテストで複数ケース
"""
import pytest
from pathlib import Path
from overflow_detection.core.detector import HybridOverflowDetector

class TestHybridDetection:
    
    @pytest.fixture
    def detector(self):
        """テスト用検出器"""
        return HybridOverflowDetector()
    