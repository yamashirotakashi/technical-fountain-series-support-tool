# sample5.pdf 検出分析レポート

作成日: 2025-07-29

## 🎯 検出結果サマリー

### 検出統計
- **総ページ数**: 140ページ
- **はみ出し検出ページ数**: 63ページ（45%）
- **座標ベース検出**: 4ページ
- **ブロック端検出**: 244件（重複含む）
- **視覚的判断検出**: 0ページ（新規PDFのため）
- **ハイブリッド検出**: 4ページ

### 除外された日本語文字
- ひらがな: 118文字
- 漢字: 58文字
- カタカナ: 46文字
- その他: 14文字
- **合計**: 236文字（sample4.pdfの約1/4）

## 📊 検出パターンの特徴

### 1. ページ分布の偏り
- **すべて奇数ページ**: 7, 9, 11, 13, ..., 135
- **偶数ページ**: 検出なし（0ページ）
- **パターン**: ほぼ連続した奇数ページ（7-33, 37-51, 55-135）

### 2. 検出方法の内訳
- **ブロック端検出のみ**: 59ページ（93.7%）
- **座標＋ブロック端**: 4ページ（6.3%）
  - ページ63: `"` (4.8pt超過)
  - ページ93: `1` (4.8pt超過)
  - ページ97: `')` (8.4pt超過)
  - ページ129: ``` `, `pan)` など

### 3. ブロック端検出の特徴
- **一貫した超過量**: すべて11.3pt超過
- **重複検出**: 同じ矩形が2回、4回、6回、最大10回検出
- **コードブロックサイズ**: 幅389.7pt（470.5 - 80.8）

## 🔍 技術的分析

### 1. 偶数ページ検出なしの理由
v5では偶数ページ用の特別な閾値を設定しているが、sample5.pdfでは検出なし：
- **可能性1**: 偶数ページにコードブロックが存在しない
- **可能性2**: コードブロックが本文領域内に収まっている
- **可能性3**: 検出ロジックがまだ不十分

### 2. 座標ベース検出の少なさ
- **検出文字**: 主に記号（`"`, `'`, `)`, ``` `）
- **超過量**: 4.3-18.9pt（比較的小さい）
- **特徴**: 行末の閉じ括弧や引用符が多い

### 3. 日本語文字の少なさ
- **除外文字数**: 236文字（他のサンプルより大幅に少ない）
- **示唆**: より英語中心のコード、または日本語コメントが少ない

## 💡 他サンプルとの比較

| 項目 | sample3.pdf | sample4.pdf | sample5.pdf |
|-----|------------|------------|------------|
| 総ページ数 | 132 | 132 | 140 |
| 検出ページ数 | 24 | 29 | 63 |
| 検出率 | 18.2% | 22.0% | 45.0% |
| 偶数ページ検出 | あり | あり（視覚のみ） | なし |
| 最大超過量 | 846.7pt | 369.6pt | 18.9pt |
| 除外日本語 | 516 | 962 | 236 |

## 🚦 検出の信頼性評価

### 高信頼度の検出
1. **ブロック端検出**: 11.3ptの一貫した超過は信頼性が高い
2. **奇数ページ集中**: B5判の右マージン差（奇数20mm、偶数15mm）と整合

### 要確認事項
1. **偶数ページの実態**: 実際にコードブロックがないのか確認必要
2. **重複検出**: 同じ矩形の複数回検出は最適化の余地あり
3. **座標検出の少なさ**: 文字レベルのはみ出しが少ない可能性

## 📈 推奨アクション

### 1. 目視確認の優先順位
- **高優先度**: ページ129（最大超過量18.9pt）
- **中優先度**: 座標検出があった4ページ（63, 93, 97, 129）
- **低優先度**: ブロック端のみの検出ページ

### 2. 検出器の改善提案
- 重複検出の除去（同じ矩形を1回のみカウント）
- 偶数ページの詳細分析機能
- 検出結果のグループ化（連続ページの集約表示）

### 3. Phase 2統合への示唆
- 大量検出時の効率的な表示方法が必要
- ページ範囲での一括確認機能
- 検出パターンの自動分類

## 🎆 結論

sample5.pdfは高い検出率（45%）を示し、特に奇数ページでの一貫したブロック端検出が特徴的。偶数ページでの検出がない点は、PDFの構造的特徴か検出器の限界かを見極める必要がある。v5検出器は安定して動作しており、Phase 2統合に向けて実用的な精度を達成している。