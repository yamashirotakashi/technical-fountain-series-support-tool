# コードブロックはみ出し検出システム 設計書

## 1. システム概要

### 1.1 アーキテクチャ
```
┌─────────────────────────────────────────┐
│          メインアプリケーション           │
│         overflow_detector.py            │
├─────────────┬───────────────┬───────────┤
│  PDF解析層  │   検出エンジン │ レポート層│
├─────────────┼───────────────┼───────────┤
│  PyMuPDF    │  検出ロジック  │  出力整形 │
│ pdfplumber  │  はみ出し計算  │ ファイル出力│
└─────────────┴───────────────┴───────────┘
```

### 1.2 データフロー
```
入力PDF → 図形抽出 → 灰色矩形検出 → テキスト解析 
        → はみ出し判定 → 結果集約 → レポート出力
```

---

## 2. 詳細設計

### 2.1 クラス構造

```python
class CodeBlockOverflowDetector:
    """メインクラス - コードブロックのはみ出し検出"""
    
    # 定数定義
    GRAY_COLOR = 0.9          # NextPublishingの標準グレー
    COLOR_TOLERANCE = 0.02    # 色の許容誤差
    MIN_OVERFLOW = 0.1        # 最小はみ出し幅（pt）
    
    def __init__(self):
        """初期化"""
        self.results = []     # 検出結果の保存
        self.errors = []      # エラー情報の保存
    
    def detect_file(self, pdf_path: Path) -> List[int]:
        """PDFファイルを解析してはみ出しページを検出"""
        
    def _find_gray_rectangles(self, page_fitz) -> List[fitz.Rect]:
        """PyMuPDFで灰色背景の矩形を検出"""
        
    def _check_text_overflow(self, page_plumber, rect: fitz.Rect) -> bool:
        """pdfplumberでテキストのはみ出しをチェック"""
        
    def _is_gray_color(self, color: Tuple[float, ...]) -> bool:
        """色が灰色かどうか判定"""
        
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """検出結果のレポート生成"""
```

### 2.2 メソッド詳細設計

#### 2.2.1 detect_file メソッド
```python
def detect_file(self, pdf_path: Path) -> List[int]:
    """
    PDFファイルを解析してはみ出しページを検出
    
    Args:
        pdf_path: 解析対象のPDFファイルパス
        
    Returns:
        はみ出しが検出されたページ番号のリスト（1-indexed）
    """
    overflow_pages = []
    
    # PyMuPDFでPDFを開く
    doc_fitz = fitz.open(pdf_path)
    
    # pdfplumberでも開く
    with pdfplumber.open(pdf_path) as pdf_plumber:
        # 各ページを処理
        for page_num in range(len(doc_fitz)):
            page_fitz = doc_fitz[page_num]
            page_plumber = pdf_plumber.pages[page_num]
            
            # 灰色矩形を検出
            gray_rects = self._find_gray_rectangles(page_fitz)
            
            # 各矩形でテキストオーバーフローをチェック
            for rect in gray_rects:
                if self._check_text_overflow(page_plumber, rect):
                    overflow_pages.append(page_num + 1)  # 1-indexed
                    break  # このページは既に検出済み
    
    doc_fitz.close()
    return sorted(list(set(overflow_pages)))
```

#### 2.2.2 _find_gray_rectangles メソッド
```python
def _find_gray_rectangles(self, page_fitz) -> List[fitz.Rect]:
    """
    PyMuPDFで灰色背景の矩形を検出
    
    Args:
        page_fitz: PyMuPDFのページオブジェクト
        
    Returns:
        灰色矩形のリスト
    """
    gray_rects = []
    
    # 図形情報を取得
    drawings = page_fitz.get_drawings()
    
    for item in drawings:
        # 塗りつぶし図形のみ対象
        if item['type'] == 'f':  # 'f' = filled
            fill_color = item.get('fill')
            
            # 灰色かどうか判定
            if fill_color and self._is_gray_color(fill_color):
                # fitz.Rectオブジェクトに変換
                rect = fitz.Rect(item['rect'])
                gray_rects.append(rect)
    
    return gray_rects
```

#### 2.2.3 _check_text_overflow メソッド
```python
def _check_text_overflow(self, page_plumber, rect: fitz.Rect) -> bool:
    """
    pdfplumberでテキストのはみ出しをチェック
    
    Args:
        page_plumber: pdfplumberのページオブジェクト
        rect: チェック対象の矩形（PyMuPDFのRect）
        
    Returns:
        はみ出しがある場合True
    """
    # 矩形の境界ボックスを取得
    bbox = (rect.x0, rect.y0, rect.x1, rect.y1)
    
    # 矩形内のテキストを抽出
    cropped = page_plumber.within_bbox(bbox)
    
    if cropped.chars:
        # 各文字の位置をチェック
        for char in cropped.chars:
            # 右端の座標を確認
            char_right = char['x1']
            
            # はみ出し幅を計算
            overflow = char_right - rect.x1
            
            if overflow > self.MIN_OVERFLOW:
                return True
    
    return False
```

### 2.3 エラーハンドリング

```python
def detect_file(self, pdf_path: Path) -> List[int]:
    """エラーハンドリングを含む実装"""
    overflow_pages = []
    
    try:
        # ファイル存在確認
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
        
        # メイン処理（前述）
        # ...
        
    except FileNotFoundError as e:
        self.errors.append(str(e))
        print(f"エラー: {e}")
        return []
        
    except Exception as e:
        self.errors.append(f"予期しないエラー: {str(e)}")
        print(f"エラー: PDFの処理中に問題が発生しました - {e}")
        return []
    
    finally:
        # リソースのクリーンアップ
        if 'doc_fitz' in locals():
            doc_fitz.close()
```

---

## 3. コマンドライン インターフェース

### 3.1 使用方法
```bash
# 基本的な使用
python overflow_detector.py sample.pdf

# 出力ファイル指定
python overflow_detector.py sample.pdf -o report.txt

# ヘルプ表示
python overflow_detector.py -h
```

### 3.2 実装
```python
def main():
    """コマンドラインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="技術の泉シリーズPDFのコードブロックはみ出し検出"
    )
    parser.add_argument('pdf_file', help='検査対象のPDFファイル')
    parser.add_argument('-o', '--output', help='レポート出力先ファイル')
    
    args = parser.parse_args()
    
    # 検出器の初期化と実行
    detector = CodeBlockOverflowDetector()
    
    print(f"解析中: {args.pdf_file}")
    overflow_pages = detector.detect_file(Path(args.pdf_file))
    
    # レポート生成
    report = detector.generate_report(Path(args.output) if args.output else None)
    print(report)
```

---

## 4. パフォーマンス最適化

### 4.1 メモリ管理
- ページごとに処理してメモリを解放
- 大きなPDFでもメモリ使用量を一定に保つ

### 4.2 処理速度
- 必要最小限の情報のみ抽出
- 早期終了（ページ内で最初のはみ出しを検出したら次へ）

---

## 5. テスト計画

### 5.1 単体テスト項目
1. `_is_gray_color`: 色判定の精度
2. `_find_gray_rectangles`: 矩形検出の正確性
3. `_check_text_overflow`: はみ出し判定の精度

### 5.2 統合テスト項目
1. sample.pdfでの動作確認（48ページ検出）
2. 空のPDFでのエラーハンドリング
3. 100ページ以上のPDFでの性能測定

---

## 6. 将来の拡張性

### 6.1 Stage 3対応の準備
```python
class CodeBlockDetector(ABC):
    """抽象基底クラス - 将来の拡張用"""
    @abstractmethod
    def detect_blocks(self, page) -> List[Rect]:
        pass

class GrayBackgroundDetector(CodeBlockDetector):
    """灰色背景検出（現在の実装）"""
    
class BorderedBlockDetector(CodeBlockDetector):
    """罫線囲み検出（Stage 3で実装）"""
```

### 6.2 設定の外部化
```python
# config.json の例
{
    "detection": {
        "gray_color": 0.9,
        "color_tolerance": 0.02,
        "min_overflow": 0.1
    },
    "performance": {
        "max_pages_warning": 500,
        "timeout_seconds": 300
    }
}
```