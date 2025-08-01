# 最終アルゴリズム実装レポート

## 調査結果

### sample.pdf ページ48の分析
- ページ寸法: 515.93 x 728.54 pt
- テキスト右端境界: 487.6 pt（奇数ページ、右マージン10mm）
- 最も右にある文字: 'k' at x1=442.7pt（はみ出しなし: -44.9pt）
- コードブロック内の最右端文字: 'r' at x1=438.0pt（はみ出しなし: -49.6pt）

**結論**: ページ48には実際のはみ出しは存在しない。visual_judgments.jsonの記録は誤りの可能性がある。

### 誤検知パターンの分析

1. **sample2.pdf/sample5.pdf ページ60**
   - 検出内容: 'l.ps1'))' (35.6pt) と 'ecurityProtocol' (69.4pt)
   - これらは実際のコードブロックのはみ出しである可能性が高い

2. **sample3.pdf の各種ページ**
   - 長いJSON文字列やパス名が検出されている
   - 例: 'elasticsearch.node.name":"quickstart-es-default-0"' (772.6pt)
   - これらも実際のはみ出しである可能性が高い

## 推奨アプローチ

### 1. 純粋なアルゴリズムベースの検出
ハードコードを使用せず、以下の基準で検出：

```python
# 基本的な検出基準
- はみ出し量 > 2.0pt（誤差を考慮）
- ASCII文字が2文字以上連続
- コードブロック内外を問わず検出

# 誤検知フィルタリング
- 単一文字かつはみ出し量 < 5.0pt → 除外
- 閉じ括弧のみかつはみ出し量 < 10.0pt → 除外
- 句読点のみかつはみ出し量 < 5.0pt → 除外
```

### 2. Ground Truthの再検証が必要
- sample.pdf ページ48は実際にははみ出していない可能性
- visual_judgments.jsonの内容を再確認する必要がある

### 3. 検出アルゴリズムの改善案
1. コードブロック検出と通常テキスト検出の両方を実施
2. 日本語文字は除外（ASCII文字のみを対象）
3. 適度なフィルタリングで誤検知を減らしつつ、実際のはみ出しは検出

## 最終実装の方針

v9の実装で以下の点を確認：
- 純粋なアルゴリズムベースの検出
- ハードコードなし
- 適切なバランスのフィルタリング

ただし、Ground Truthとの乖離については、Ground Truth自体の再検証が必要。