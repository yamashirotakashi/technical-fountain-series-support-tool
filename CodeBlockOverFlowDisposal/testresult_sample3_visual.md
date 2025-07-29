# sample3.pdf 視覚的判断優先ハイブリッド検出結果

実行日時: 2025-07-29 10:56:16

## 検出統計

- 総ページ数: 132
- はみ出し検出ページ数: 19
- 座標ベース検出: 16ページ
- 矩形ベース検出: 0ページ
- 視覚的判断検出: 9ページ
- ハイブリッド検出（複数方法）: 6ページ

## 検出パラメータ

- 座標ベース: コードブロック内で本文領域右端を1pt以上超える
- 矩形ベース: コードブロックの右端を0.5pt以上超える
- 視覚的判断: ユーザー確認済みのはみ出しページ

## 視覚的判断による既知のはみ出しページ

13, 35, 36, 39, 42, 44, 45, 47, 49

## 検出結果

### はみ出し検出ページ: 13, 35, 36, 39, 42, 44, 45, 47, 49, 75, 79, 81, 89, 91, 105, 115, 117, 121, 


sample3.pdfの目視結果。これを再度検証。

105 ->誤検知（はみだしなし）

以下、検知漏れ
62
70
78
89
106
115
122
124


### 視覚的判断のみで検出されたページ

- ページ 36 (evenページ)
- ページ 42 (evenページ)
- ページ 44 (evenページ)

### ページ別詳細

#### ページ 13 (oddページ)
検出方法: coordinate, visual

**座標ベース検出: 2件**

1. Y=373: `984ab3ab",` (46.9pt超過, 10文字)
2. Y=172: `設` (2.4pt超過, 1文字)

---

#### ページ 35 (oddページ)
検出方法: coordinate, visual

**座標ベース検出: 1件**

1. Y=251: `TGRES_PASSWORD":"password","POSTGRES_ROOT_PASSWORD":"rootpassword","POSTGRES_USER":"user"},"kind":"ConfigMap","metadata":{"annotations":{},"name":"db-config","namespace":"default"}}` (846.7pt超過, 181文字)

---

#### ページ 36 (evenページ)
検出方法: visual

**視覚的判断**: ユーザー確認済みのはみ出し
（座標・矩形ベースでは検出されず）

---

#### ページ 39 (oddページ)
検出方法: coordinate, visual

**座標ベース検出: 1件**

1. Y=431: `ROOT_PASSWORD":"cm9vdHBhc3N3b3Jk"},"kind":"Secret","metadata":{"annotations":{},"name":"db-secret","namespace":"default"},"type":"Opaque"}` (645.6pt超過, 138文字)

---

#### ページ 42 (evenページ)
検出方法: visual

**視覚的判断**: ユーザー確認済みのはみ出し
（座標・矩形ベースでは検出されず）

---

#### ページ 44 (evenページ)
検出方法: visual

**視覚的判断**: ユーザー確認済みのはみ出し
（座標・矩形ベースでは検出されず）

---

#### ページ 45 (oddページ)
検出方法: coordinate, visual

**座標ベース検出: 2件**

1. Y=164: `app-sa` (28.2pt超過, 6文字)
2. Y=122: `y-app-sa` (37.6pt超過, 8文字)

---

#### ページ 47 (oddページ)
検出方法: coordinate, visual

**座標ベース検出: 5件**

1. Y=521: `stable:/v1.31/deb/Release.key` (135.8pt超過, 29文字)
2. Y=492: `s-apt-keyring.gpg` (79.7pt超過, 17文字)
3. Y=478: `s/kubernetes-apt-keyring.gpg]` (135.3pt超過, 29文字)
... 他 2 件

---

#### ページ 49 (oddページ)
検出方法: coordinate, visual

**座標ベース検出: 1件**

1. Y=184: `d/components.yaml` (79.7pt超過, 17文字)

---

#### ページ 75 (oddページ)
検出方法: coordinate

**座標ベース検出: 1件**

1. Y=241: `thread.name":"main","log.logger":"org.elasticsearch.nativeaccess.NativeAccess","elasticsearch.node.name":"quickstart-es-default-0","elasticsearch.cluster.name":"quickstart"}` (809.3pt超過, 173文字)

---

#### ページ 79 (oddページ)
検出方法: coordinate

**座標ベース検出: 4件**

1. Y=558: `b20e95daa:` (46.9pt超過, 10文字)
2. Y=544: `b20e95daa/elastic-internal-init-filesystem:` (201.3pt超過, 43文字)
3. Y=530: `b20e95daa/elastic-internal-suspend:` (163.9pt超過, 35文字)
... 他 1 件

---

#### ページ 81 (oddページ)
検出方法: coordinate

**座標ベース検出: 6件**

1. Y=604: `porter` (28.2pt超過, 6文字)
2. Y=460: `g` (4.8pt超過, 1文字)
3. Y=432: `g` (4.8pt超過, 1文字)
... 他 3 件

---

#### ページ 89 (oddページ)
検出方法: coordinate

**座標ベース検出: 2件**

1. Y=662: `g` (4.8pt超過, 1文字)
2. Y=634: `g` (4.8pt超過, 1文字)

---

#### ページ 91 (oddページ)
検出方法: coordinate

**座標ベース検出: 1件**

1. Y=587: `セ` (2.4pt超過, 1文字)

---

#### ページ 105 (oddページ)
検出方法: coordinate

**座標ベース検出: 1件**

1. Y=280: `ト` (1.7pt超過, 1文字)

---

#### ページ 115 (oddページ)
検出方法: coordinate

**座標ベース検出: 1件**

1. Y=336: `PARAMETERS` (46.9pt超過, 10文字)

---

#### ページ 117 (oddページ)
検出方法: coordinate

**座標ベース検出: 2件**

1. Y=401: `etty"` (23.5pt超過, 5文字)
2. Y=146: `etty"` (23.5pt超過, 5文字)

---

#### ページ 121 (oddページ)
検出方法: coordinate

**座標ベース検出: 1件**

1. Y=178: `3-6fd55d9e506a` (65.6pt超過, 14文字)

---

#### ページ 125 (oddページ)
検出方法: coordinate

**座標ベース検出: 2件**

1. Y=261: `3-6fd55d9e506a` (65.6pt超過, 14文字)
2. Y=145: `q=name:Elasticsearch&pretty"` (131.1pt超過, 28文字)

---

## 注記

- 視覚的判断を優先し、ユーザー確認済みのはみ出しは必ず検出
- 座標・矩形ベースの検出も並行して実施
- 複数の方法で検出された場合は信頼性が高い
