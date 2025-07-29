# 学習データ検証レポート - 現状分析と改善提案

最終更新: 2025-01-29

## 🔍 現在保存している学習データの分析

### 保存されているデータ項目

```sql
-- 現在のテーブル構造
CREATE TABLE learning_data (
    id INTEGER PRIMARY KEY,
    pdf_path TEXT,           -- PDFファイルパス
    pdf_name TEXT,           -- PDFファイル名
    detected_pages TEXT,     -- 検出されたページ番号のJSON配列 [1, 5, 10]
    confirmed_pages TEXT,    -- ユーザーが確認した正しい溢れページ
    additional_pages TEXT,   -- 見落とされた溢れページ
    false_positives TEXT,    -- 誤検出ページ
    timestamp TEXT,          -- 記録日時
    os_info TEXT,           -- OS情報
    app_version TEXT,       -- アプリバージョン
    user_notes TEXT,        -- ユーザーコメント
    processing_time REAL    -- 処理時間
)
```

## ❌ 現状の問題点と不足データ

### 1. **ページ単位の詳細情報が不足**

現在保存されているのは**ページ番号のみ**で、以下の重要情報が欠落：

```python
# 現状：ページ番号のみ
'detected_pages': [3, 5, 10, 15]

# 必要：詳細な溢れ情報
'detected_pages': [
    {
        'page_number': 3,
        'overflow_regions': [
            {
                'x': 450.5,
                'y': 320.1,
                'width': 85.2,
                'height': 12.5,
                'text': 'System.out.println("This is a very long...',
                'overflow_amount': 15.3,  # pt単位
                'block_type': 'code',     # code/text/table
                'confidence': 0.85
            }
        ],
        'page_width': 515.9,
        'page_height': 728.5,
        'is_even_page': False
    }
]
```

### 2. **視覚的特徴の欠如**

機械学習に必要な特徴量が保存されていない：

```python
# 必要な特徴量
'page_features': {
    'text_density': 0.75,              # テキスト密度
    'code_block_count': 3,             # コードブロック数
    'avg_line_length': 65.2,           # 平均行長
    'max_line_length': 95,             # 最大行長
    'right_margin_violations': 5,       # 右マージン違反数
    'font_variations': ['Consolas', 'Arial'],  # 使用フォント
    'has_tables': False,               # 表の有無
    'has_images': True,                # 画像の有無
    'language': 'python',              # コード言語
    'layout_complexity': 0.6           # レイアウト複雑度
}
```

### 3. **画像データの不在**

Gemini API活用に必要な画像が保存されていない：

```python
# 必要：ページ画像へのリンク
'page_images': {
    3: 'data/images/sample_pdf_page_003.png',
    5: 'data/images/sample_pdf_page_005.png'
}
```

### 4. **コンテキスト情報の不足**

前後のページとの関連性が記録されていない：

```python
# 必要：コンテキスト情報
'context': {
    'previous_page_has_overflow': False,
    'next_page_has_overflow': True,
    'section_type': 'code_listing',  # chapter/code_listing/table
    'continued_from_previous': False,
    'continues_to_next': True
}
```

### 5. **ユーザー修正の詳細不足**

なぜ誤検出/見落としが発生したかの理由が不明：

```python
# 必要：詳細な修正理由
'user_corrections': {
    'false_positives': [
        {
            'page': 10,
            'reason': 'page_number',  # ページ番号の誤検出
            'details': 'ページ番号"105"を溢れと誤認識'
        }
    ],
    'missed_detections': [
        {
            'page': 15,
            'reason': 'subtle_overflow',  # 微妙な溢れ
            'details': '1-2pt程度の微小な溢れを見落とし'
        }
    ]
}
```

## 📊 改善提案：拡張学習データスキーマ

### 新しいテーブル構造

```sql
-- メインテーブル（既存を拡張）
CREATE TABLE learning_data_v2 (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,     -- セッションID
    pdf_path TEXT,
    pdf_name TEXT,
    pdf_hash TEXT,              -- PDFのハッシュ値（重複検出用）
    total_pages INTEGER,
    detected_count INTEGER,
    confirmed_count INTEGER,
    false_positive_count INTEGER,
    missed_count INTEGER,
    timestamp TEXT,
    os_info TEXT,
    app_version TEXT,
    user_notes TEXT,
    processing_time REAL,
    ml_model_version TEXT       -- 使用したMLモデルバージョン
);

-- ページ詳細テーブル（新規）
CREATE TABLE page_detections (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    page_number INTEGER,
    detection_status TEXT,      -- detected/confirmed/false_positive/missed
    page_features TEXT,         -- JSON: 特徴量
    overflow_regions TEXT,      -- JSON: 溢れ領域詳細
    page_image_path TEXT,       -- 画像ファイルパス
    confidence REAL,
    user_feedback TEXT,         -- ユーザーフィードバック詳細
    FOREIGN KEY (session_id) REFERENCES learning_data_v2(session_id)
);

-- 溢れパターンテーブル（新規）
CREATE TABLE overflow_patterns (
    id INTEGER PRIMARY KEY,
    pattern_type TEXT,          -- code_block/long_url/table/equation
    pattern_signature TEXT,     -- パターンのシグネチャ
    occurrence_count INTEGER,
    false_positive_rate REAL,
    last_seen TEXT
);
```

### データ収集の実装

```python
# core/enhanced_learning_manager.py
class EnhancedLearningManager:
    """拡張学習データ管理"""
    
    def collect_page_features(self, page):
        """ページから機械学習用特徴量を収集"""
        features = {
            # テキスト特徴
            'text_density': self._calculate_text_density(page),
            'char_count': len(page.extract_text()),
            'line_count': self._count_lines(page),
            'avg_line_length': self._calculate_avg_line_length(page),
            'max_line_length': self._calculate_max_line_length(page),
            
            # レイアウト特徴
            'code_block_count': self._count_code_blocks(page),
            'code_block_area_ratio': self._calculate_code_area_ratio(page),
            'table_count': self._count_tables(page),
            'image_count': self._count_images(page),
            
            # マージン特徴
            'right_margin_min_distance': self._calculate_min_margin_distance(page),
            'text_near_edge_count': self._count_edge_text(page),
            
            # フォント特徴
            'font_types': self._extract_font_types(page),
            'font_size_variations': self._calculate_font_variations(page),
            
            # 位置特徴
            'is_even_page': page.page_number % 2 == 0,
            'page_position': page.page_number / page.pdf.page_count,  # 0-1
        }
        return features
    
    def save_page_image(self, page, session_id):
        """ページ画像を保存（Gemini用）"""
        image_dir = Path("data/page_images") / session_id
        image_dir.mkdir(parents=True, exist_ok=True)
        
        image_path = image_dir / f"page_{page.page_number:03d}.png"
        
        # ページを画像として保存
        pix = page.to_pixmap(matrix=fitz.Matrix(2, 2))  # 2x解像度
        pix.save(str(image_path))
        
        return str(image_path)
    
    def analyze_detection_context(self, page_num, all_pages):
        """検出コンテキストを分析"""
        context = {
            'previous_page_has_overflow': False,
            'next_page_has_overflow': False,
            'section_type': 'unknown',
            'code_continuation': False
        }
        
        if page_num > 1:
            prev_page = all_pages[page_num - 2]
            context['previous_page_has_overflow'] = self._has_overflow(prev_page)
            context['code_continuation'] = self._is_code_continuation(prev_page)
            
        if page_num < len(all_pages):
            next_page = all_pages[page_num]
            context['next_page_has_overflow'] = self._has_overflow(next_page)
        
        return context
```

## 🎯 データ移行戦略

### Step 1: 既存データの拡張（1週間）

```python
# scripts/migrate_learning_data.py
def migrate_existing_data():
    """既存の学習データを新形式に移行"""
    old_data = load_old_learning_data()
    
    for record in old_data:
        # PDFを再読み込みして特徴量を抽出
        pdf_path = record['pdf_path']
        if Path(pdf_path).exists():
            features = extract_features_from_pdf(pdf_path)
            
            # 新形式で保存
            save_enhanced_data(record, features)
```

### Step 2: 収集システムの更新（3日）

```python
# 結果ダイアログの更新
class EnhancedResultDialog(QDialog):
    def collect_detailed_feedback(self):
        """詳細なフィードバックを収集"""
        feedback = {
            'detection_quality': self.quality_slider.value(),  # 1-5
            'missed_reason': self.missed_reason_combo.currentText(),
            'false_positive_type': self.fp_type_combo.currentText(),
            'additional_comments': self.comment_edit.text()
        }
        return feedback
```

## 📈 期待される効果

### 改善前（現状）
- **学習可能な内容**: ページ番号のパターンのみ
- **精度向上**: 限定的（5-10%程度）
- **Gemini活用**: 不可能

### 改善後
- **学習可能な内容**: 
  - 溢れの視覚的パターン
  - レイアウトと溢れの相関
  - フォント・言語別の特性
- **精度向上**: 大幅改善（30-50%）
- **Gemini活用**: フル活用可能

## 🚀 実装優先順位

1. **最優先**: ページ特徴量の収集実装
   - 既存システムへの影響: 小
   - 効果: 大
   - 実装コスト: 中

2. **次点**: 画像保存機能
   - Gemini統合の前提条件
   - ストレージコスト: 要検討

3. **将来**: コンテキスト分析
   - より高度な学習に必要
   - 実装コスト: 高

## ⚠️ 注意事項

1. **ストレージ容量**
   - 画像保存により容量が増大（1ページ約500KB）
   - 定期的なクリーンアップが必要

2. **プライバシー**
   - PDFの内容が含まれるため取り扱い注意
   - Gemini API使用時は特に配慮

3. **後方互換性**
   - 既存データの移行パスを確保
   - 段階的な移行を推奨