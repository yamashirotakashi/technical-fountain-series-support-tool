# AI向け実装計画書：ハイブリッドはみ出し検出システム
## NextPublishing編集支援システム拡張

### 🎯 実装目標と制約

#### システム要件
```yaml
target_system: "NextPublishing編集支援システム（Python実装）"
detection_range: "1pt～100pt以上のはみ出し"
pdf_size_range: "40～400ページ（主に100-200ページ）"
implementation_by: "ClaudeCode（AI）のみ"
human_involvement: "なし"
```

#### 重要な実装原則
1. **既存システムを破壊しない**: 新機能は完全に独立したモジュールとして実装
2. **段階的統合**: まず独立動作を確認してから既存システムに統合
3. **自己検証可能**: AIが実装結果を自己検証できるテストを含む
4. **エラー耐性**: 部分的な失敗でも全体が停止しない設計

### 📋 実装フェーズ

#### Phase 0: 環境確認と準備（必須・最初に実行）
```python
# このフェーズで実行すべきタスク
tasks = [
    "既存システムのディレクトリ構造を確認",
    "必要なライブラリの確認と不足分のリスト作成",
    "テスト用PDFファイルの場所を確認",
    "既存の設定ファイル形式を確認"
]
```

**AIへの指示**: 
- `find . -type f -name "*.py" | head -20` で既存構造を確認
- `requirements.txt` または `setup.py` から依存関係を確認
- 新規必要ライブラリ: `pdfplumber`, `PyMuPDF`, `opencv-python`, `pillow`

#### Phase 1: 独立モジュールの作成
```
overflow_detection/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── hybrid_detector.py      # メインの検出器
│   ├── text_analyzer.py        # テキストベース解析
│   └── visual_analyzer.py      # 視覚ベース解析
├── models/
│   ├── __init__.py
│   └── detection_models.py     # データモデル
├── utils/
│   ├── __init__.py
│   ├── pdf_renderer.py         # PDF→画像変換
│   └── cache_manager.py        # キャッシュ管理
└── config/
    └── default_config.yaml     # デフォルト設定
```

**AIへの実装順序**:
1. まず `models/detection_models.py` を実装（データ構造の定義）
2. 次に `utils/` 配下のユーティリティ
3. その後 `core/` の各アナライザー
4. 最後に全体を統合

#### Phase 2: コア機能の実装詳細

**2.1 データモデル実装**
```python
# models/detection_models.py の構造
@dataclass
class OverflowDetection:
    """
    AIへの注意: 
    - すべてのフィールドにデフォルト値を設定
    - JSON serializable にする
    - 1pt未満の微小なはみ出しも記録できる精度
    """
    page_number: int
    bbox: Tuple[float, float, float, float]
    overflow_width_pt: float  # 小数点以下も重要
    confidence: float  # 0.0-1.0
    detection_method: str
    line_content: str
    timestamp: datetime
```

**2.2 テキストアナライザー実装**
```python
# core/text_analyzer.py の実装指針
class TextAnalyzer:
    """
    AIへの実装指示:
    1. pdfplumberを使用してテキストと文字位置を抽出
    2. 日本語の文字幅を正確に計算（等幅フォントを仮定しない）
    3. エラー時は空の結果を返す（例外を投げない）
    4. 処理時間が1秒を超えたらタイムアウト
    """
```

**2.3 視覚アナライザー実装**
```python
# core/visual_analyzer.py の実装指針
class VisualAnalyzer:
    """
    AIへの実装指示:
    1. PyMuPDFで300DPIでレンダリング
    2. OpenCVでエッジ検出（Canny法）
    3. 1pt単位の精度で検出
    4. メモリ使用量に注意（ページごとに解放）
    """
```

#### Phase 3: パフォーマンス最適化

**3.1 並列処理の実装**
```python
# AIへの指示: 以下の条件で並列処理を実装
parallel_config = {
    "max_workers": 4,  # CPU数に関わらず4固定
    "chunk_size": 10,  # 10ページずつ処理
    "timeout_per_page": 5,  # 5秒でタイムアウト
    "memory_limit_mb": 2048  # 2GBまで
}
```

**3.2 キャッシュ戦略**
```python
# utils/cache_manager.py の実装
"""
AIへの実装指示:
1. ページ単位でキャッシュ（PDFファイルパス + ページ番号がキー）
2. LRUキャッシュ（最大1000ページ分）
3. メモリ使用量が1GBを超えたら古いものから削除
4. プロセス終了時に自動クリア
"""
```

#### Phase 4: 既存システムとの統合

**4.1 統合ポイントの特定**
```python
# AIへの指示: 以下のパターンを既存コードから探す
integration_patterns = [
    "class.*Validator",  # 既存の検証クラス
    "def.*validate.*pdf",  # PDF検証関数
    "def.*check.*",  # チェック関数
    "class.*Analyzer"  # 解析クラス
]
```

**4.2 統合アダプター作成**
```python
# integration/adapter.py
class OverflowDetectionAdapter:
    """
    AIへの実装指示:
    1. 既存システムのインターフェースに合わせる
    2. 新機能の有効/無効を設定で切り替え可能に
    3. 既存の検証結果に追加する形で結果を返す
    4. エラー時は既存システムの動作を妨げない
    """
```

### 🧪 テスト実装

#### テストケース生成
```python
# tests/test_overflow_detection.py
"""
AIへのテスト実装指示:
1. 最小限のテストPDFを生成するコードを含める
2. 1pt, 5pt, 10pt, 50ptのはみ出しをそれぞれテスト
3. 日本語テキストのテストケースを必ず含める
4. 100ページのPDFでのパフォーマンステスト
"""
```

#### 自己検証スクリプト
```python
# scripts/self_verify.py
"""
AIが実装後に自己検証するためのスクリプト
実行すると以下を確認:
1. すべてのモジュールがimport可能か
2. 基本的な検出が動作するか
3. メモリリークがないか
4. 処理時間が許容範囲内か
"""
```

### 📊 設定ファイル

```yaml
# config/default_config.yaml
overflow_detection:
  # 検出戦略
  strategy: "adaptive"  # adaptive, text_only, visual_only, hybrid_sequential, hybrid_parallel
  
  # 検出閾値
  thresholds:
    micro: 1.0    # 1pt - 微小なはみ出し
    minor: 5.0    # 5pt - 軽微なはみ出し  
    major: 20.0   # 20pt - 重大なはみ出し
    critical: 50.0 # 50pt - 致命的なはみ出し
  
  # パフォーマンス設定
  performance:
    max_parallel_pages: 4
    timeout_per_page: 5.0
    cache_enabled: true
    cache_size_mb: 1024
    
  # 検出精度
  accuracy:
    text_dpi: 150
    visual_dpi: 300
    edge_detection_threshold: [50, 150]
    
  # レポート設定
  reporting:
    include_preview: true
    max_preview_length: 100
    severity_colors:
      micro: "#FFEB3B"
      minor: "#FF9800"
      major: "#F44336"
      critical: "#B71C1C"
```

### 🚨 エラーハンドリング指針

```python
# AIへの重要な指示: 以下のエラーハンドリングを必ず実装

error_handling_rules = {
    "FileNotFoundError": "空の検出結果を返す",
    "MemoryError": "視覚検出をスキップしてテキストのみで継続",
    "TimeoutError": "そのページをスキップして次へ",
    "PDFReadError": "エラーログを記録して空の結果を返す",
    "Any other Exception": "ログに記録して処理を継続"
}
```

### 📝 実装チェックリスト

AIが各フェーズで確認すべき項目:

- [ ] Phase 0: 環境確認完了
- [ ] Phase 1: ディレクトリ構造作成完了
- [ ] Phase 2: コア機能実装完了
- [ ] Phase 3: 最適化実装完了
- [ ] Phase 4: 統合完了
- [ ] テスト: 自己検証スクリプト成功
- [ ] ドキュメント: docstring完備

### 💡 AIへの実装ヒント

1. **import文の順序**: 標準ライブラリ → サードパーティ → ローカルモジュール
2. **型ヒント**: すべての関数に型ヒントを付ける（Python 3.8+）
3. **ログ出力**: `logging`モジュールを使用、print文は使わない
4. **設定読み込み**: YAMLファイルは`safe_load`を使用
5. **リソース管理**: `with`文を使用してリソースを確実に解放

### 🎬 実装開始コマンド

```bash
# AIはこの順序で実装を開始
mkdir -p overflow_detection/{core,models,utils,config,tests}
touch overflow_detection/__init__.py
# 以降、上記の構造に従って実装
```