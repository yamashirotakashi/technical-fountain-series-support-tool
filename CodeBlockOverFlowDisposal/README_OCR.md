# コードブロックはみ出し検出システム - OCR版

## 概要
技術の泉シリーズ（B5判）のPDFにおいて、本文幅を逸脱しているテキストをOCRで検出するツールです。

## 特徴
- OCRベースの高精度なテキスト位置検出
- B5判（182×257mm）のレイアウトに対応
- 左右ページで異なるマージン設定に対応
  - 左ページ（偶数）: 左20mm / 右15mm
  - 右ページ（奇数）: 左15mm / 右20mm
- 日本語・英語混在のテキストに対応

## インストール

### 1. Python依存関係
```bash
pip install -r requirements_ocr.txt
```

### 2. Tesseract OCRのインストール

#### Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

#### Windows:
1. [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki)からダウンロード
2. インストール時に日本語データファイルを選択

#### macOS:
```bash
brew install tesseract
brew install tesseract-lang
```

## 使用方法

### 基本的な使用
```bash
python overflow_detector_ocr.py sample.pdf
```

### レポート出力
```bash
python overflow_detector_ocr.py sample.pdf -o report.txt
```

### 言語設定の変更
```bash
python overflow_detector_ocr.py sample.pdf --lang eng  # 英語のみ
python overflow_detector_ocr.py sample.pdf --lang jpn  # 日本語のみ
```

## 出力例
```
=== コードブロックはみ出し検出結果 (OCR版) ===
ファイル: sample.pdf
検出日時: 2025-01-28 10:30:45
ページサイズ: B5 (182×257mm)
左ページマージン: 左20mm / 右15mm
右ページマージン: 左15mm / 右20mm

本文幅からはみ出しているページ:
10, 20, 48

検出数: 3ページ
処理時間: 45.2秒
```

## 技術詳細

### レイアウト仕様
- **ページサイズ**: B5（182×257mm）
- **解像度**: 300 DPI
- **マージン**:
  - 見開きを考慮して左右で異なる設定
  - ノド（綴じ側）: 20mm
  - 小口（開き側）: 15mm

### 検出アルゴリズム
1. PDFを300DPIで画像化
2. Tesseract OCRでテキストと位置情報を抽出
3. 各テキストボックスの右端座標を計算
4. 本文エリアの右端を超えるテキストを検出

### パフォーマンス
- 処理速度: 約2-3秒/ページ（環境依存）
- メモリ使用量: 約200-300MB/100ページ

## トラブルシューティング

### OCRが日本語を認識しない
```bash
# 言語データの確認
tesseract --list-langs

# 日本語データがない場合は再インストール
sudo apt-get install tesseract-ocr-jpn
```

### 処理が遅い
- 画像解像度を下げる（ただし精度低下の可能性）
- マルチスレッド処理の実装を検討

### メモリ不足
- ページごとに処理し、メモリを解放
- より小さいバッチサイズで処理

## 制限事項
- OCRの精度は元PDFの品質に依存
- 傾いたテキストや手書き文字は検出困難
- 処理時間はページ数に比例

## 今後の改善案
1. マルチスレッド処理による高速化
2. 検出精度の調整オプション
3. 詳細なデバッグモードの追加
4. GUI版の開発