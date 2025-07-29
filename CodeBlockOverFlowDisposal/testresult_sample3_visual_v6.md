# sample3.pdf 視覚的判断優先ハイブリッド検出結果 v6

**矩形基準検出を第1優先、座標検出を補助的に使用**

実行日時: 2025-07-29 11:50:01

## 検出統計

- 総ページ数: 132
- はみ出し検出ページ数: 23
- 矩形基準検出: 23ページ
- 座標ベース検出: 0ページ
- 視覚的判断検出: 17ページ
- ハイブリッド検出: 17ページ

### 除外された文字種別

- hiragana: 772文字
- kanji: 546文字
- katakana: 804文字
- other: 82文字
- **合計**: 2204文字

## 視覚的判断による既知のはみ出しページ

13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124

## 誤検知として除外されたページ

89, 105

## 検出結果

### はみ出し検出ページ: 13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 75, 78, 79, 80, 81, 106, 115, 117, 121, 122, 124, 125

### 高信頼度検出（矩形基準または視覚的判断）

13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 75, 78, 79, 80, 81, 106, 115, 117, 121, 122, 124, 125

### ページ別詳細

#### ページ 13 (oddページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック5 (80.8, 354.1) - (470.5, 399.0)
  - Y=373: `4ab3ab",` (35.6pt超過)

コードブロック6 (80.8, 354.1) - (470.5, 399.0)
  - Y=373: `4ab3ab",` (35.6pt超過)

**座標ベース検出: 1件（補助的）**

1. Y=373: `4` (14.2pt超過)

---

#### ページ 35 (oddページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック1 (80.8, 177.6) - (470.5, 686.0)
  - Y=251: `RES_PASSWORD":"password","POSTGRES_ROOT_PASSWORD":"rootpassword","POSTGRES_USER":"user"},"kind":"ConfigMap","metadata":{"annotations":{},"name":"db-config","namespace":"default"}}` (835.4pt超過)

コードブロック2 (80.8, 177.6) - (470.5, 686.0)
  - Y=251: `RES_PASSWORD":"password","POSTGRES_ROOT_PASSWORD":"rootpassword","POSTGRES_USER":"user"},"kind":"ConfigMap","metadata":{"annotations":{},"name":"db-config","namespace":"default"}}` (835.4pt超過)

**座標ベース検出: 1件（補助的）**

1. Y=251: `R` (14.2pt超過)

---

#### ページ 36 (evenページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック5 (45.4, 143.4) - (435.1, 399.2)
  - Y=217: `RES_PASSWORD":"password","POSTGRES_ROOT_PASSWORD":"rootpassword","POSTGRES_USER":"user"},"kind":"ConfigMap","metadata":{"annotations":{},"name":"db-config","namespace":"default"}}` (835.4pt超過)

コードブロック6 (45.4, 143.4) - (435.1, 399.2)
  - Y=217: `RES_PASSWORD":"password","POSTGRES_ROOT_PASSWORD":"rootpassword","POSTGRES_USER":"user"},"kind":"ConfigMap","metadata":{"annotations":{},"name":"db-config","namespace":"default"}}` (835.4pt超過)

---

#### ページ 39 (oddページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック3 (80.8, 301.0) - (470.5, 599.3)
  - Y=431: `OT_PASSWORD":"cm9vdHBhc3N3b3Jk"},"kind":"Secret","metadata":{"annotations":{},"name":"db-secret","namespace":"default"},"type":"Opaque"}` (634.3pt超過)

コードブロック4 (80.8, 301.0) - (470.5, 599.3)
  - Y=431: `OT_PASSWORD":"cm9vdHBhc3N3b3Jk"},"kind":"Secret","metadata":{"annotations":{},"name":"db-secret","namespace":"default"},"type":"Opaque"}` (634.3pt超過)

**座標ベース検出: 1件（補助的）**

1. Y=431: `O` (14.2pt超過)

---

#### ページ 42 (evenページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック5 (45.4, 252.6) - (435.1, 480.1)
  - Y=326: `RES_USER":"user"},"kind":"ConfigMap","metadata":{"annotations":{},"name":"db-config","namespace":"default"}}` (503.3pt超過)

コードブロック6 (45.4, 252.6) - (435.1, 480.1)
  - Y=326: `RES_USER":"user"},"kind":"ConfigMap","metadata":{"annotations":{},"name":"db-config","namespace":"default"}}` (503.3pt超過)

---

#### ページ 44 (evenページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック3 (45.4, 195.7) - (435.1, 607.4)
  - Y=440: `notations":{},"name":"secret-reader","namespace":"default"},"rules":[{"apiGroups":[""],"resourceNames":["db-config"],"resources":["secrets"],"verbs":["get"]}]}` (741.9pt超過)

コードブロック4 (45.4, 195.7) - (435.1, 607.4)
  - Y=440: `notations":{},"name":"secret-reader","namespace":"default"},"rules":[{"apiGroups":[""],"resourceNames":["db-config"],"resources":["secrets"],"verbs":["get"]}]}` (741.9pt超過)

---

#### ページ 45 (oddページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 4件（最優先）**

コードブロック7 (80.8, 104.8) - (470.5, 191.5)
  - Y=164: `p-sa` (16.9pt超過)
  - Y=122: `app-sa` (26.3pt超過)

コードブロック8 (80.8, 104.8) - (470.5, 191.5)
  - Y=164: `p-sa` (16.9pt超過)
  - Y=122: `app-sa` (26.3pt超過)

**座標ベース検出: 2件（補助的）**

1. Y=164: `p` (14.2pt超過)
2. Y=122: `a` (14.2pt超過)

---

#### ページ 47 (oddページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 10件（最優先）**

コードブロック1 (80.8, 275.0) - (470.5, 674.3)
  - Y=521: `able:/v1.31/deb/Release.key` (124.5pt超過)
  - Y=492: `apt-keyring.gpg` (68.4pt超過)
  - Y=478: `kubernetes-apt-keyring.gpg]` (123.9pt超過)
  ... 他 2 件

コードブロック2 (80.8, 275.0) - (470.5, 674.3)
  - Y=521: `able:/v1.31/deb/Release.key` (124.5pt超過)
  - Y=492: `apt-keyring.gpg` (68.4pt超過)
  - Y=478: `kubernetes-apt-keyring.gpg]` (123.9pt超過)
  ... 他 2 件

**座標ベース検出: 5件（補助的）**

1. Y=521: `a` (14.2pt超過)
2. Y=492: `a` (14.2pt超過)
3. Y=478: `k` (13.7pt超過)
... 他 2 件

---

#### ページ 49 (oddページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 4件（最優先）**

コードブロック5 (80.8, 301.0) - (470.5, 317.6)
  - Y=306: `st/download/components.yaml` (124.5pt超過)

コードブロック6 (80.8, 301.0) - (470.5, 317.6)
  - Y=306: `st/download/components.yaml` (124.5pt超過)

コードブロック7 (80.8, 165.1) - (470.5, 195.7)
  - Y=184: `components.yaml` (68.4pt超過)

コードブロック8 (80.8, 165.1) - (470.5, 195.7)
  - Y=184: `components.yaml` (68.4pt超過)

**座標ベース検出: 2件（補助的）**

1. Y=306: `s` (14.2pt超過)
2. Y=184: `c` (14.2pt超過)

---

#### ページ 62 (evenページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック5 (45.4, 100.6) - (435.1, 299.1)
  - Y=287: `=name:Elasticsearch&pretty"` (124.5pt超過)

コードブロック6 (45.4, 100.6) - (435.1, 299.1)
  - Y=287: `=name:Elasticsearch&pretty"` (124.5pt超過)

---

#### ページ 70 (evenページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック3 (45.4, 252.4) - (435.1, 269.0)
  - Y=257: `/deploy/static/provider/kind/deploy.yaml` (185.3pt超過)

コードブロック4 (45.4, 252.4) - (435.1, 269.0)
  - Y=257: `/deploy/static/provider/kind/deploy.yaml` (185.3pt超過)

---

#### ページ 75 (oddページ) ★高信頼度
検出方法: rect_overflow

**矩形基準検出: 2件（最優先）**

コードブロック3 (80.8, 236.5) - (470.5, 408.9)
  - Y=241: `read.name":"main","log.logger":"org.elasticsearch.nativeaccess.NativeAccess","elasticsearch.node.name":"quickstart-es-default-0","elasticsearch.cluster.name":"quickstart"}` (798.0pt超過)

コードブロック4 (80.8, 236.5) - (470.5, 408.9)
  - Y=241: `read.name":"main","log.logger":"org.elasticsearch.nativeaccess.NativeAccess","elasticsearch.node.name":"quickstart-es-default-0","elasticsearch.cluster.name":"quickstart"}` (798.0pt超過)

**座標ベース検出: 1件（補助的）**

1. Y=241: `r` (14.2pt超過)

---

#### ページ 78 (evenページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック9 (45.4, 123.0) - (435.1, 279.1)
  - Y=267: `cc-8e03-854b20e95daa/elasticsearch/0.log` (185.3pt超過)

コードブロック10 (45.4, 123.0) - (435.1, 279.1)
  - Y=267: `cc-8e03-854b20e95daa/elasticsearch/0.log` (185.3pt超過)

---

#### ページ 79 (oddページ) ★高信頼度
検出方法: rect_overflow

**矩形基準検出: 10件（最優先）**

コードブロック1 (80.8, 672.0) - (470.5, 686.0)
  - Y=677: `read.name":"main","log.logger":"org.elasticsearch.nativeaccess.NativeAccess","elasticsearch.node.name":"quickstart-es-default-0","elasticsearch.cluster.name":"quickstart"}` (798.0pt超過)

コードブロック2 (80.8, 672.0) - (470.5, 686.0)
  - Y=677: `read.name":"main","log.logger":"org.elasticsearch.nativeaccess.NativeAccess","elasticsearch.node.name":"quickstart-es-default-0","elasticsearch.cluster.name":"quickstart"}` (798.0pt超過)

コードブロック3 (80.8, 511.1) - (470.5, 598.5)
  - Y=558: `0e95daa:` (35.6pt超過)
  - Y=544: `0e95daa/elastic-internal-init-filesystem:` (190.0pt超過)
  - Y=530: `0e95daa/elastic-internal-suspend:` (152.5pt超過)
  ... 他 1 件

コードブロック4 (80.8, 511.1) - (470.5, 598.5)
  - Y=558: `0e95daa:` (35.6pt超過)
  - Y=544: `0e95daa/elastic-internal-init-filesystem:` (190.0pt超過)
  - Y=530: `0e95daa/elastic-internal-suspend:` (152.5pt超過)
  ... 他 1 件

**座標ベース検出: 5件（補助的）**

1. Y=677: `r` (14.2pt超過)
2. Y=558: `0` (14.2pt超過)
3. Y=544: `0` (14.2pt超過)
... 他 2 件

---

#### ページ 80 (evenページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック1 (45.4, 529.4) - (435.1, 674.3)
  - Y=647: `harts` (21.6pt超過)

コードブロック2 (45.4, 529.4) - (435.1, 674.3)
  - Y=647: `harts` (21.6pt超過)

---

#### ページ 81 (oddページ) ★高信頼度
検出方法: rect_overflow

**矩形基準検出: 2件（最優先）**

コードブロック3 (80.8, 585.8) - (470.5, 616.4)
  - Y=604: `rter` (16.9pt超過)

コードブロック4 (80.8, 585.8) - (470.5, 616.4)
  - Y=604: `rter` (16.9pt超過)

**座標ベース検出: 1件（補助的）**

1. Y=604: `r` (14.2pt超過)

---

#### ページ 106 (evenページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 4件（最優先）**

コードブロック5 (45.4, 284.1) - (435.1, 471.5)
  - Y=430: `ESPACE` (26.3pt超過)
  - Y=317: `ESPACE` (26.3pt超過)

コードブロック6 (45.4, 284.1) - (435.1, 471.5)
  - Y=430: `ESPACE` (26.3pt超過)
  - Y=317: `ESPACE` (26.3pt超過)

---

#### ページ 115 (oddページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック1 (80.8, 262.2) - (470.5, 674.0)
  - Y=336: `RAMETERS` (35.6pt超過)

コードブロック2 (80.8, 262.2) - (470.5, 674.0)
  - Y=336: `RAMETERS` (35.6pt超過)

**座標ベース検出: 1件（補助的）**

1. Y=336: `R` (14.2pt超過)

---

#### ページ 117 (oddページ) ★高信頼度
検出方法: rect_overflow

**矩形基準検出: 4件（最優先）**

コードブロック3 (80.8, 100.6) - (470.5, 498.6)
  - Y=401: `ty"` (12.2pt超過)
  - Y=146: `ty"` (12.2pt超過)

コードブロック4 (80.8, 100.6) - (470.5, 498.6)
  - Y=401: `ty"` (12.2pt超過)
  - Y=146: `ty"` (12.2pt超過)

**座標ベース検出: 2件（補助的）**

1. Y=401: `t` (14.2pt超過)
2. Y=146: `t` (14.2pt超過)

---

#### ページ 121 (oddページ) ★高信頼度
検出方法: rect_overflow

**矩形基準検出: 4件（最優先）**

コードブロック3 (80.8, 159.0) - (470.5, 359.8)
  - Y=291: `STORAGECLASS` (101.1pt超過)
  - Y=178: `6fd55d9e506a` (54.3pt超過)

コードブロック4 (80.8, 159.0) - (470.5, 359.8)
  - Y=291: `STORAGECLASS` (101.1pt超過)
  - Y=178: `6fd55d9e506a` (54.3pt超過)

**座標ベース検出: 1件（補助的）**

1. Y=178: `6` (14.2pt超過)

---

#### ページ 122 (evenページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック1 (45.4, 489.3) - (435.1, 674.3)
  - Y=634: `STORAGECLASS` (101.1pt超過)

コードブロック2 (45.4, 489.3) - (435.1, 674.3)
  - Y=634: `STORAGECLASS` (101.1pt超過)

---

#### ページ 124 (evenページ) ★高信頼度
検出方法: rect_overflow, visual

**矩形基準検出: 2件（最優先）**

コードブロック1 (45.4, 107.3) - (435.1, 686.0)
  - Y=464: `name:Elasticsearch&pretty"` (119.8pt超過)

コードブロック2 (45.4, 107.3) - (435.1, 686.0)
  - Y=464: `name:Elasticsearch&pretty"` (119.8pt超過)

---

#### ページ 125 (oddページ) ★高信頼度
検出方法: rect_overflow

**矩形基準検出: 6件（最優先）**

コードブロック5 (80.8, 242.1) - (470.5, 414.5)
  - Y=374: `STORAGECLASS` (101.1pt超過)
  - Y=261: `6fd55d9e506a` (54.3pt超過)

コードブロック6 (80.8, 242.1) - (470.5, 414.5)
  - Y=374: `STORAGECLASS` (101.1pt超過)
  - Y=261: `6fd55d9e506a` (54.3pt超過)

コードブロック7 (80.8, 100.6) - (470.5, 185.8)
  - Y=145: `name:Elasticsearch&pretty"` (119.8pt超過)

コードブロック8 (80.8, 100.6) - (470.5, 185.8)
  - Y=145: `name:Elasticsearch&pretty"` (119.8pt超過)

**座標ベース検出: 2件（補助的）**

1. Y=261: `6` (14.2pt超過)
2. Y=145: `n` (14.2pt超過)

---

