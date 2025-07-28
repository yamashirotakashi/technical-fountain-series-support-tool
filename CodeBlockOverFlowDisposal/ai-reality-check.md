# 現実的な実装のための制約と判断基準
## ClaudeCode向け - 実際に使われるコードを書くために

### 🎯 実装の現実的な制約

#### 1. NextPublishing PDFの実際の特徴

```python
"""
実際のNextPublishing PDFの特徴（仮定ではなく事実）:

1. コードブロックの特徴
   - 背景色: RGB(0.9, 0.9, 0.9) ± 0.02 のグレー
   - フォント: ほぼ確実に等幅フォント（ConsolasやCourier）
   - フォントサイズ: 9-10pt が標準
   - 行間: 1.2-1.5倍

2. 典型的なはみ出しパターン
   - シェルコマンド: 長いパスやオプション
   - 設定ファイル: 長いURL、設定値
   - ログ出力: タイムスタンプ付きの長い行
   
3. ページレイアウト
   - 1カラム（技術書の標準）
   - コードブロックの幅: 約350pt（本文幅の約90%）
   - 左マージン: 約50pt
"""

# これらの特徴を前提とした実装
NEXTPUBLISHING_CONSTANTS = {
    "code_block": {
        "background_gray": 0.9,
        "tolerance": 0.02,
        "standard_width": 350.0,
        "left_margin": 50.0,
    },
    "font": {
        "standard_size": 10.0,
        "char_width_estimate": 7.2,  # 10ptの等幅フォント
    }
}
```

#### 2. 実際の使用シナリオ

```python
"""
編集者の実際のワークフロー:

1. 原稿PDF（100-200ページ）を受け取る
2. はみ出しチェックを実行
3. レポートを確認
4. 重大なはみ出し（20pt以上）から修正
5. 再度チェック

つまり必要なのは:
- 一度に1ファイルの処理（バッチ処理は不要）
- わかりやすいレポート（ページ番号と行番号）
- 重要度による分類
- 高速な処理（待ち時間を最小に）
"""

class UsageScenario:
    """実際の使用を想定した設計"""
    
    @staticmethod
    def typical_workflow(pdf_path: str) -> None:
        # 1. シンプルな実行
        detector = HybridOverflowDetector()
        result = detector.detect_file(pdf_path)
        
        # 2. 重要なものだけ表示
        critical_overflows = [
            o for o in result.overflows 
            if o.overflow_width_pt >= 20.0
        ]
        
        # 3. 修正が必要なページのリスト
        pages_to_fix = sorted(set(o.page_number for o in critical_overflows))
        print(f"修正が必要なページ: {pages_to_fix}")
```

#### 3. 開発時間とのトレードオフ

```python
"""
実装の優先度（時間制約を考慮）:

第1段階（必須・1日で実装）:
- テキストベース検出のみ
- 基本的なレポート出力
- コマンドライン実行

第2段階（改善・追加1日）:
- 視覚的検証の追加
- キャッシュ機能
- より詳細なレポート

第3段階（もし時間があれば）:
- 並列処理の最適化
- GUI統合
- 自動修正提案
"""

# 最小限の動作する実装（第1段階）
class MinimalDetector:
    """1日で実装可能な最小構成"""
    
    def detect(self, pdf_path: str) -> List[Dict]:
        results = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # グレー背景の矩形を探す
                gray_rects = [
                    r for r in page.rects
                    if self._is_gray(r.get('fill'))
                ]
                
                for rect in gray_rects:
                    # 矩形内のテキストをチェック
                    bbox = (rect['x0'], rect['top'], rect['x1'], rect['bottom'])
                    chars = page.within_bbox(bbox).chars
                    
                    # はみ出しチェック（シンプル）
                    for char in chars:
                        if char['x1'] > rect['x1']:
                            results.append({
                                'page': page.page_number,
                                'overflow': char['x1'] - rect['x1'],
                                'char': char['text']
                            })
        return results
```

### 🚨 実装時の判断基準

#### どの機能を実装すべきかの判断フロー

```mermaid
graph TD
    A[新機能の実装を検討] --> B{仕様書に明記?}
    B -->|Yes| C{既存コードに類似パターン?}
    B -->|No| D[実装しない]
    
    C -->|Yes| E[同じパターンで実装]
    C -->|No| F{1時間以内に実装可能?}
    
    F -->|Yes| G[シンプルに実装]
    F -->|No| H{本当に必要?}
    
    H -->|Yes| I[段階的に実装]
    H -->|No| D
```

#### 具体的な判断例

```python
# ケース1: プログレスバーの実装
"""
判断:
- 仕様書に明記? → No
- 既存システムにある? → 要確認
- 1時間で実装可能? → Yes (tqdmを使えば)
- 本当に必要? → 100-200ページなら数十秒で終わる

結論: 実装しない（ログ出力で十分）
"""

# ケース2: キャッシュ機能
"""
判断:
- 仕様書に明記? → Yes
- 既存システムにある? → 要確認  
- 1時間で実装可能? → No
- 本当に必要? → 同じPDFを何度もチェックする場合は有用

結論: 第2段階で実装（最初はなしでも動く）
"""

# ケース3: エラーハンドリング
"""
判断:
- 仕様書に明記? → Yes
- 必須? → Yes（PDFが壊れている場合もある）

結論: 最初から実装
"""
```

### 📊 現実的なテストデータ

```python
# tests/create_realistic_test_pdfs.py
"""
実際のNextPublishingに近いテストPDFを生成
"""

def create_realistic_test_pdf():
    """
    現実的なテストケース:
    
    1. 正常なコードブロック（はみ出しなし）
    2. わずかなはみ出し（1-2pt）
    3. 中程度のはみ出し（10-20pt）  
    4. 深刻なはみ出し（50pt以上）
    5. 日本語コメント付きコード
    """
    
    test_cases = {
        "normal_command": "$ ls -la /home/user/documents",
        
        "slight_overflow": "$ docker run -it --rm -v /home/user/very/long/path/to/project:/app node:latest",
        
        "moderate_overflow": "$ curl -X POST https://api.example.com/v1/users/1234/actions/update -H 'Authorization: Bearer very_long_token_string'",
        
        "severe_overflow": "$ aws s3 sync s3://my-bucket/very/long/path/to/files/ /local/extremely/long/path/to/destination/directory/ --exclude '*.tmp' --include '*.log'",
        
        "japanese_mixed": "$ echo '設定ファイルのパス: /etc/application/config/production/settings.yaml' >> log.txt"
    }
```

### 🔍 実装の妥当性チェック

```python
def implementation_sanity_check():
    """
    AI: 実装が現実的かをチェックする関数
    各実装完了時に実行すること
    """
    
    checks = {
        "complexity": {
            "question": "1つの関数が50行を超えていないか？",
            "bad_sign": "100行を超える関数がある",
            "fix": "機能を分割する"
        },
        
        "dependencies": {
            "question": "追加したライブラリは本当に必要か？",
            "bad_sign": "5個以上の新規ライブラリ",
            "fix": "標準ライブラリで代替"
        },
        
        "performance": {
            "question": "100ページを1分以内に処理できるか？",
            "bad_sign": "1ページ1秒以上かかる",
            "fix": "アルゴリズムを見直す"
        },
        
        "error_handling": {
            "question": "エラー時にクラッシュしないか？",
            "bad_sign": "except: pass がある",
            "fix": "具体的なエラー処理"
        },
        
        "testability": {
            "question": "単体テストが書けるか？",
            "bad_sign": "モックだらけのテスト",
            "fix": "依存性注入を使う"
        }
    }
    
    return checks
```

### 💭 実装時の自問自答

```python
"""
コードを書く前に自問すべき5つの質問:

1. このコードは来週の自分が読んで理解できるか？
   → できない場合はコメントを追加

2. このエラーケースは実際に起こりうるか？
   → 起こりえない想定のエラー処理は不要

3. この最適化は本当に効果があるか？
   → 計測していない最適化は悪

4. この機能は誰が使うのか？
   → 使用者が不明な機能は実装しない

5. もっとシンプルな方法はないか？
   → 常により単純な解決策を探す
"""

# 良い例：シンプルで明確
def is_code_block(rect):
    """グレー背景かどうかを判定"""
    color = rect.get('fill')
    if not color or len(color) != 3:
        return False
    
    # グレーの判定（R≈G≈B かつ 0.85-0.95の範囲）
    r, g, b = color
    is_gray = abs(r - g) < 0.05 and abs(g - b) < 0.05
    is_right_shade = 0.85 < r < 0.95
    
    return is_gray and is_right_shade

# 悪い例：過度に複雑
def is_code_block_complex(rect, ai_model, color_space='RGB'):
    """AIモデルを使った高度な判定（過剰）"""
    # 機械学習は不要...
```

### 📝 最終チェックリスト

```bash
# 実装完了時のチェックコマンド

# 1. 基本的な動作確認
python -m overflow_detection.cli sample.pdf

# 2. 処理時間の確認  
time python -m overflow_detection.cli large_sample.pdf

# 3. メモリ使用量の確認
/usr/bin/time -v python -m overflow_detection.cli large_sample.pdf

# 4. エラーケースの確認
python -m overflow_detection.cli non_existent.pdf
python -m overflow_detection.cli corrupted.pdf
python -m overflow_detection.cli empty.pdf

# 5. インポートの確認（循環参照チェック）
python -c "import overflow_detection; print('OK')"
```