# コードブロックはみ出し検出システム 最終仕様書
## 仕様書駆動開発（SDD）用 - 実装準備完了版

### 文書情報
- **バージョン**: 3.0.0（最終版）
- **作成日**: 2025-01-28
- **対象システム**: 技術の泉シリーズ制作支援ツール 拡張機能
- **実装方式**: Phase 1（独立ツール）→ Phase 2（GUI統合）

---

## 1. 概要

### 1.1 目的
技術の泉シリーズのNextPublishing形式PDFにおいて、コードブロック内のテキストが右端からはみ出す問題を自動検出し、編集者の手動確認作業を効率化する。

### 1.2 Phase 1 スコープ（1日実装）
**実装する機能**：
- コマンドラインからPDFファイルを直接指定
- pdfplumberとPyMuPDFの併用による確実な検出
- 灰色背景コードブロックの識別
- テキストはみ出し幅の測定
- わかりやすいテキストレポート出力

**実装しない機能**：
- GUI統合
- 自動修正
- 並列処理
- キャッシュ機能

---

## 2. 技術仕様

### 2.1 必要ライブラリ
```txt
pdfplumber>=0.9.0    # テキストと基本的な図形情報
PyMuPDF>=1.23.0      # 図形の詳細情報（塗りつぶし色等）
```

### 2.2 ディレクトリ構造
```
CodeBlockOverFlowDisposal/
├── overflow_detector.py      # メイン実装（単一ファイル）
├── requirements_addon.txt    # 追加ライブラリ
├── README.md                 # 使用方法
├── test_samples/            # テスト用PDF
│   ├── sample.pdf
│   └── sampleOverflow.pdf
└── reports/                 # レポート出力先（自動生成）
```

### 2.3 コア実装設計
```python
# overflow_detector.py の基本構造

import sys
from pathlib import Path
from datetime import datetime
import pdfplumber
import fitz  # PyMuPDF

class CodeBlockOverflowDetector:
    """コードブロックのはみ出し検出"""
    
    GRAY_COLOR = 0.9  # NextPublishingの標準グレー
    COLOR_TOLERANCE = 0.02
    CODE_BLOCK_MARGIN = 50.0  # 左マージン
    
    def __init__(self):
        self.results = []
    
    def detect_file(self, pdf_path):
        """PDFファイルを解析"""
        # 1. PyMuPDFで灰色矩形を検出
        # 2. pdfplumberでテキスト位置を取得
        # 3. はみ出しを計算
        pass
    
    def find_gray_rectangles_fitz(self, page_fitz):
        """PyMuPDFで灰色背景の矩形を検出"""
        gray_rects = []
        drawings = page_fitz.get_drawings()
        
        for item in drawings:
            if item['type'] == 'f':  # filled shape
                if self._is_gray(item.get('fill')):
                    gray_rects.append(item['rect'])
        
        return gray_rects
    
    def check_text_overflow_plumber(self, page_plumber, rect):
        """pdfplumberでテキストのはみ出しをチェック"""
        # rectの範囲内の文字を取得
        bbox = (rect.x0, rect.y0, rect.x1, rect.y1)
        cropped = page_plumber.within_bbox(bbox)
        
        overflows = []
        if cropped.chars:
            # 行ごとにグループ化
            lines = self._group_chars_by_line(cropped.chars)
            
            for line_num, line_chars in lines.items():
                # 最右端の文字を確認
                rightmost = max(line_chars, key=lambda c: c['x1'])
                overflow_width = rightmost['x1'] - rect.x1
                
                if overflow_width > 0.1:  # 0.1pt以上のはみ出し
                    overflows.append({
                        'line_num': line_num,
                        'overflow_pt': overflow_width,
                        'text': self._extract_line_text(line_chars)[:50]
                    })
        
        return overflows
    
    def generate_report(self):
        """検出結果のレポート生成"""
        # シンプルなテキスト形式で出力
        pass
```

---

## 3. 実装計画

### 3.1 実装手順
1. **技術検証**（30分）
   - sample.pdfでライブラリの動作確認
   - 灰色矩形の検出可否を確認
   - テキスト位置情報の精度確認

2. **基本実装**（3時間）
   - PyMuPDFで灰色矩形検出
   - pdfplumberでテキスト解析
   - はみ出し計算ロジック

3. **レポート機能**（1時間）
   - 結果の整形
   - ファイル出力
   - エラーハンドリング

4. **テストと調整**（1時間）
   - sample.pdfでの動作確認
   - エッジケースの対応
   - パフォーマンス確認

### 3.2 出力仕様
```
=== コードブロックはみ出し検出レポート ===
ファイル: sample.pdf
検出日時: 2025-01-28 10:30:45
総ページ数: 48

■ 検出されたはみ出し: 3件

【ページ 10】
  - 5.5pt はみ出し
  - 該当テキスト: "docker run -it --rm -v /home/user/..."

【ページ 20】
  - 15.3pt はみ出し（要修正）
  - 該当テキスト: "curl -X POST https://api.example.com/v1/..."

【ページ 48】
  - 52.1pt はみ出し（致命的）
  - 該当テキスト: "aws s3 sync s3://my-bucket/very/long/path..."

■ サマリー
  - 微小（<5pt）: 0件
  - 軽微（5-20pt）: 2件
  - 重大（>20pt）: 1件

処理時間: 12.3秒
```

---

## 4. Phase 2 統合計画

### 4.1 既存GUIへの統合方針
- PyQt6ベースの既存GUIにメニュー項目追加
- 「ツール」→「PDFはみ出し検出」メニュー
- 別ウィンドウでレポート表示

### 4.2 統合時の変更点
1. **モジュール化**
   - 単一ファイルを`core/overflow_detector.py`に移動
   - 既存の`core/`ディレクトリ構造に準拠

2. **GUI対応**
   - プログレスバー表示
   - 結果の表形式表示
   - PDF内該当ページへのジャンプ機能

### 4.3 統合作業見積もり
- コード移植: 1時間
- GUI実装: 2時間
- テスト: 1時間

---

## 5. リスクと対策

### 5.1 技術的リスク
- **リスク**: NextPublishing以外のPDFでの誤検出
- **対策**: 灰色の範囲を厳密に定義（0.88-0.92）

### 5.2 性能リスク
- **リスク**: 大容量PDFでの処理時間
- **対策**: 1ページあたり1秒を超えたら警告表示

---

## 6. 成功基準

### 6.1 Phase 1完了条件
- [ ] sample.pdfの48ページのはみ出しを検出
- [ ] 検出精度0.1pt以上
- [ ] 100ページを60秒以内で処理
- [ ] エラー時もクラッシュしない

### 6.2 品質基準
- コードカバレッジ: 不問（Phase 1）
- ドキュメント: README.mdに使用方法記載
- エラーメッセージ: 日本語で分かりやすく

---

## 付録A: 実装チェックリスト

### Phase 1実装時の確認項目
- [ ] ライブラリのインストール確認
- [ ] sample.pdfで技術検証完了
- [ ] 灰色矩形の検出成功
- [ ] テキスト位置の取得成功
- [ ] はみ出し計算の正確性確認
- [ ] レポート出力の確認
- [ ] エラーハンドリングの動作確認
- [ ] 処理時間の測定

### コーディング規約
- [ ] 関数は20行以内
- [ ] 適切なコメント
- [ ] 変数名は分かりやすく
- [ ] マジックナンバーは定数化