# 学習データ活用による精度向上ロードマップ

最終更新: 2025-01-29

## 🎯 現状分析

### 実装済み機能
- ✅ 学習データ収集（SQLiteデータベース）
- ✅ ユーザーフィードバック収集（誤検出・見落とし）
- ✅ 統計情報の計算（精度・再現率・F1スコア）

### 未実装機能
- ❌ 収集したデータを使った検出器の改善
- ❌ パターン学習機能
- ❌ 動的閾値調整

## 📊 学習データ活用戦略

### Phase 1: 基礎的な学習機能実装（2週間）

#### 1.1 パターン分析器の実装（3日）
```python
# core/pattern_analyzer.py
class PatternAnalyzer:
    """学習データからパターンを抽出"""
    
    def analyze_false_positives(self) -> Dict:
        """誤検出パターンの分析"""
        # - 頻繁に誤検出される文字パターン
        # - 特定のレイアウトでの誤検出
        # - ページ位置による傾向
    
    def analyze_missed_detections(self) -> Dict:
        """見落としパターンの分析"""
        # - 検出されにくい溢れのタイプ
        # - 特定のフォント・サイズ
        # - 境界線付近の微妙な溢れ
```

#### 1.2 動的フィルタの実装（4日）
```python
# core/adaptive_filter.py
class AdaptiveFilter:
    """学習データに基づく動的フィルタ"""
    
    def __init__(self, learning_manager):
        self.false_positive_patterns = []
        self.detection_enhancers = []
        
    def update_from_learning_data(self):
        """学習データからフィルタを更新"""
        # 誤検出パターンを除外フィルタに追加
        # 見落としパターンを検出強化
```

#### 1.3 検出器への統合（3日）
```python
# rect_based_detector.py の拡張
class RectBasedOverflowDetector:
    def __init__(self, use_learning=True):
        self.adaptive_filter = None
        if use_learning:
            self.adaptive_filter = AdaptiveFilter(learning_manager)
    
    def detect_file(self, pdf_path):
        # 既存の検出処理
        results = self._original_detection(pdf_path)
        
        # 学習データによるフィルタリング
        if self.adaptive_filter:
            results = self.adaptive_filter.apply(results)
        
        return results
```

#### 1.4 効果測定とフィードバック（4日）
- A/Bテスト機能の実装
- 学習前後の精度比較
- 改善効果のレポート生成

### Phase 2: 高度な機械学習統合（3週間）

#### 2.1 特徴量エンジニアリング（1週間）
```python
# core/feature_extractor.py
class FeatureExtractor:
    """PDFページから機械学習用の特徴量を抽出"""
    
    def extract_features(self, page):
        return {
            'text_density': self._calculate_text_density(page),
            'code_block_ratio': self._calculate_code_block_ratio(page),
            'margin_violations': self._detect_margin_violations(page),
            'font_variations': self._analyze_font_variations(page),
            # ... 20-30の特徴量
        }
```

#### 2.2 軽量MLモデルの導入（1週間）
```python
# core/ml_detector.py
from sklearn.ensemble import RandomForestClassifier
import joblib

class MLOverflowDetector:
    """機械学習ベースの溢れ検出器"""
    
    def __init__(self, model_path=None):
        if model_path and Path(model_path).exists():
            self.model = joblib.load(model_path)
        else:
            self.model = RandomForestClassifier(n_estimators=100)
    
    def train(self, learning_data):
        """学習データでモデルを訓練"""
        X, y = self._prepare_training_data(learning_data)
        self.model.fit(X, y)
        
    def predict(self, page_features):
        """ページの溢れ確率を予測"""
        return self.model.predict_proba(page_features)
```

#### 2.3 ハイブリッド検出システム（1週間）
```python
# core/hybrid_detector.py
class HybridOverflowDetector:
    """ルールベース + ML のハイブリッド検出"""
    
    def __init__(self):
        self.rule_based = RectBasedOverflowDetector()
        self.ml_detector = MLOverflowDetector()
        self.confidence_threshold = 0.7
    
    def detect(self, page):
        # ルールベース検出
        rule_result = self.rule_based.detect(page)
        
        # ML予測
        features = self.feature_extractor.extract(page)
        ml_confidence = self.ml_detector.predict(features)
        
        # 結果の統合
        if rule_result and ml_confidence > self.confidence_threshold:
            return True  # 高信頼度
        elif rule_result or ml_confidence > 0.5:
            return "manual_check"  # 要確認
        else:
            return False
```

### Phase 3: 継続的学習システム（2週間）

#### 3.1 オンライン学習機能（1週間）
```python
# core/online_learner.py
class OnlineLearner:
    """ユーザーフィードバックからリアルタイムで学習"""
    
    def update_from_feedback(self, pdf_path, user_corrections):
        """単一のフィードバックから即座に学習"""
        # インクリメンタルな学習
        # 閾値の微調整
        # パターンの更新
```

#### 3.2 自動改善システム（1週間）
```python
# core/auto_improver.py
class AutoImprover:
    """定期的に精度を分析し自動改善"""
    
    def scheduled_improvement(self):
        """週次/月次での自動改善処理"""
        # 統計分析
        # 閾値最適化
        # モデル再訓練
        # 改善レポート生成
```

## 🎯 期待される効果

### 短期（Phase 1完了時）
- 誤検出率: 現在の50% → 20%以下
- 見落とし率: 現在の10% → 5%以下
- ユーザー満足度: 大幅向上

### 中期（Phase 2完了時）
- 検出精度: 95%以上
- 処理速度: 現状維持（MLは軽量モデル使用）
- 新しいPDFレイアウトへの適応性向上

### 長期（Phase 3完了時）
- 完全自動化された精度改善
- ユーザー介入の最小化
- 99%以上の検出精度

## 📝 実装優先順位

1. **最優先**: Phase 1.1-1.2（パターン分析と動的フィルタ）
   - 即効性が高い
   - 実装コストが低い
   - 既存システムへの影響が少ない

2. **次点**: Phase 1.3-1.4（統合と効果測定）
   - 改善効果の可視化
   - ユーザー信頼性の向上

3. **将来**: Phase 2-3（ML統合と継続学習）
   - 長期的な競争優位性
   - 完全自動化への道筋

## 🚀 次のアクション

1. `core/pattern_analyzer.py` の実装開始
2. 既存の学習データを使った初期分析
3. 最も頻繁な誤検出パターンのトップ10を特定
4. それらを除外する簡易フィルタの実装
5. 効果測定とユーザーテスト