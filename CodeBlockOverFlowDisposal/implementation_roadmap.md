# コードブロックはみ出し検出システム 実装ロードマップ

## 📅 全体スケジュール

```
Day 1 (8時間) - Stage 1: 基本実装
├── 午前 (4時間): 環境構築と基本機能
└── 午後 (4時間): テストと完成

Day 2 (4時間) - Stage 2: 技術検証
├── 前半 (2時間): 罫線検出の実験
└── 後半 (2時間): 検証レポート作成

Day 3-4 (条件付き) - Stage 3: 罫線対応
└── Stage 2の結果次第で実施判断
```

---

## 🚀 Stage 1: 基本実装（Day 1）

### 時間割
| 時間 | タスク | 成果物 |
|------|--------|--------|
| 09:00-09:30 | 環境構築 | requirements_addon.txt作成、ライブラリインストール |
| 09:30-10:30 | 基本構造実装 | overflow_detector.py（骨組み） |
| 10:30-12:00 | 灰色矩形検出 | _find_gray_rectangles メソッド完成 |
| 13:00-14:30 | テキスト解析 | _check_text_overflow メソッド完成 |
| 14:30-15:30 | 統合とレポート | detect_file、generate_report メソッド完成 |
| 15:30-16:30 | テスト実行 | sample.pdf での動作確認 |
| 16:30-17:00 | ドキュメント | README.md 作成 |

### チェックポイント
- [ ] 10:30 - 基本構造が動作する
- [ ] 12:00 - 灰色矩形が検出できる
- [ ] 14:30 - はみ出しが判定できる
- [ ] 16:00 - 完全動作確認
- [ ] 17:00 - ドキュメント完成

### 実装手順詳細

#### Step 1: 環境準備（09:00-09:30）
```bash
# 1. requirements_addon.txt 作成
cat > requirements_addon.txt << EOF
pdfplumber>=0.9.0
PyMuPDF>=1.23.0
EOF

# 2. インストール
pip install -r requirements_addon.txt

# 3. 動作確認
python -c "import pdfplumber, fitz; print('OK')"
```

#### Step 2: 基本構造（09:30-10:30）
```python
# overflow_detector.py の作成開始
# - クラス定義
# - 定数定義
# - メソッドスタブ
# - main関数
```

#### Step 3: 中核機能実装（10:30-15:30）
1. **灰色矩形検出**
   - PyMuPDFのget_drawings()使用
   - 色判定ロジック
   - テストコード同時作成

2. **テキスト解析**
   - pdfplumberのwithin_bbox使用
   - 文字位置の正確な取得
   - はみ出し幅の計算

3. **統合処理**
   - 両ライブラリの連携
   - エラーハンドリング
   - レポート生成

#### Step 4: テスト（15:30-16:30）
```bash
# 基本テスト
python overflow_detector.py sample.pdf

# 性能テスト
time python overflow_detector.py large_sample.pdf

# エラーケース
python overflow_detector.py nonexistent.pdf
```

---

## 🔬 Stage 2: 技術検証（Day 2 午前）

### 検証項目
1. **罫線構造の解析**（1時間）
   - sample2.pdf の60ページ詳細解析
   - 罫線パターンの抽出
   - データ構造の理解

2. **検出アルゴリズム検討**（1時間）
   - 矩形判定ロジック
   - 表との区別方法
   - 精度と性能のバランス

3. **実装可能性評価**（1時間）
   - 技術的難易度の評価
   - 必要工数の見積もり
   - リスク評価

4. **レポート作成**（1時間）
   - 検証結果のまとめ
   - Go/No-Go判定
   - Stage 3の詳細計画（Go判定の場合）

### 検証用コード
```python
# border_detection_test.py
def analyze_borders():
    """罫線検出の実験的実装"""
    # 水平線・垂直線の検出
    # 閉じた矩形の判定
    # コードブロックの可能性評価
```

---

## 📊 成功指標

### Stage 1 完了基準
| 項目 | 目標値 | 必須/推奨 |
|------|--------|-----------|
| sample.pdf 48ページ検出 | 成功 | 必須 |
| 処理速度 | 100ページ/分以上 | 必須 |
| メモリ使用量 | 2GB以下 | 推奨 |
| エラー率 | 0% | 必須 |

### Stage 2 判定基準
- **Go判定の条件**
  - 技術的に実現可能
  - 2日以内で実装可能
  - 誤検出率10%以下の見込み

- **No-Go判定の場合**
  - Stage 1の成果物で完了
  - 将来の拡張として文書化

---

## 🛠️ 開発環境

### 必要なツール
- Python 3.8以上
- pip（パッケージ管理）
- テキストエディタ（VS Code推奨）
- Git（バージョン管理）

### ディレクトリ構成
```
CodeBlockOverFlowDisposal/
├── overflow_detector.py      # メイン実装
├── requirements_addon.txt    # 追加ライブラリ
├── README.md                # 使用方法
├── test_samples/            # テスト用PDF
├── reports/                 # 出力レポート
└── tests/                   # テストコード（Stage 1後半）
```

---

## 📝 リスク管理

### Stage 1 のリスク
| リスク | 確率 | 影響 | 対策 |
|--------|------|------|------|
| ライブラリ互換性 | 低 | 中 | 事前検証済み |
| 性能問題 | 低 | 低 | 段階的最適化 |
| 予期しないPDF形式 | 中 | 低 | エラーハンドリング |

### Stage 3 のリスク
| リスク | 確率 | 影響 | 対策 |
|--------|------|------|------|
| 技術的困難 | 高 | 高 | Stage 2で十分検証 |
| 工数超過 | 中 | 中 | 段階的実装 |
| 品質問題 | 中 | 高 | 慎重なテスト |

---

## 🎯 次のアクション

### 実装開始前チェックリスト
- [ ] 仕様書・設計書の最終確認
- [ ] 開発環境の準備
- [ ] sample.pdf の配置確認
- [ ] 作業時間の確保（最低8時間）
- [ ] Pythonバージョン確認（3.8以上）

### Day 1 開始時のコマンド
```bash
# 作業ディレクトリへ移動
cd /mnt/c/Users/tky99/dev/technical-fountain-series-support-tool/CodeBlockOverFlowDisposal

# 仮想環境を有効化（既存のものを使用）
cd ..
source venv/bin/activate
cd CodeBlockOverFlowDisposal

# 開発開始
echo "# Overflow Detector" > overflow_detector.py
```

---

## 📞 サポート

### 技術的な質問
- pdfplumber: 公式ドキュメント参照
- PyMuPDF: fitz.readthedocs.io
- 実装相談: プロジェクトチャンネル

### 判断が必要な場合
- 仕様の解釈
- 優先順位の調整
- Stage 3 の Go/No-Go 判定