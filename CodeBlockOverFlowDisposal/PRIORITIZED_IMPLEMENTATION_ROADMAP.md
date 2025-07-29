# CodeBlockOverFlowDisposal 優先順位付き実装ロードマップ

最終更新: 2025-01-29

## 🎯 実装優先順位

1. **Windowsネイティブ環境での単独アプリ実行**（最優先）
2. **溢れ学習パターンの実装**（ML・Gemini活用）
3. **TECHZIPへの統合**（最後）

---

## 📌 Phase 1: Windowsネイティブ単独アプリ化（2-3週間）

### 目標
仮想環境（venv）を使わずに、Windows PowerShellから直接実行できる単独アプリケーションとして動作させる。

### Step 1.1: 依存関係の最小化とバンドル（3日）

#### システムPython対応
```powershell
# install_standalone.ps1
Write-Host "=== 溢れチェッカー スタンドアロン版セットアップ ===" -ForegroundColor Cyan

# Python存在確認
$pythonVersion = python --version 2>$null
if (-not $pythonVersion) {
    Write-Host "エラー: Pythonがインストールされていません" -ForegroundColor Red
    Write-Host "https://www.python.org からPython 3.9以上をインストールしてください" -ForegroundColor Yellow
    exit 1
}

# 必須ライブラリのグローバルインストール
Write-Host "必須ライブラリをインストール中..." -ForegroundColor Yellow
$requiredLibs = @(
    "PyQt6>=6.4.0",
    "pdfplumber>=0.9.0",
    "PyPDF2>=3.0.1",
    "pytesseract>=0.3.10",
    "Pillow>=9.3.0",
    "numpy>=1.21.0"
)

foreach ($lib in $requiredLibs) {
    pip install --user $lib
}
```

#### ポータブル版の作成
```python
# build_portable.py
import PyInstaller.__main__
import shutil
from pathlib import Path

def build_portable_app():
    """ポータブル実行ファイルの作成"""
    
    # PyInstallerでexe化
    PyInstaller.__main__.run([
        'overflow_checker_standalone/run_ultimate.py',
        '--name=OverflowChecker',
        '--windowed',
        '--icon=assets/overflow_checker.ico',
        '--add-data=overflow_checker_standalone;overflow_checker_standalone',
        '--collect-all=pdfplumber',
        '--collect-all=PyQt6',
        '--hidden-import=pytesseract',
        '--onefile',  # 単一実行ファイル
        '--noupx'     # 圧縮なし（起動高速化）
    ])
    
    # Tesseractバンドル版の作成
    create_tesseract_bundle()
```

### Step 1.2: Tesseract OCRの組み込み（4日）

#### オプション1: Tesseractポータブル版の同梱
```python
# utils/tesseract_portable.py
import os
import zipfile
import urllib.request
from pathlib import Path

class TesseractPortable:
    """ポータブル版Tesseract管理"""
    
    TESSERACT_URL = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0/tesseract-portable.zip"
    
    def __init__(self):
        self.app_dir = Path(__file__).parent.parent
        self.tesseract_dir = self.app_dir / "tesseract-portable"
        
    def ensure_tesseract(self):
        """Tesseractの存在確認とセットアップ"""
        if not self.tesseract_dir.exists():
            self.download_portable_tesseract()
        
        # 環境変数を一時的に設定
        os.environ['TESSERACT_CMD'] = str(self.tesseract_dir / "tesseract.exe")
        return True
    
    def download_portable_tesseract(self):
        """ポータブル版をダウンロード"""
        print("Tesseract OCRをダウンロード中...")
        urllib.request.urlretrieve(self.TESSERACT_URL, "tesseract.zip")
        
        with zipfile.ZipFile("tesseract.zip", 'r') as zip_ref:
            zip_ref.extractall(self.app_dir)
        
        os.remove("tesseract.zip")
```

#### オプション2: 純粋なPython OCR実装へのフォールバック
```python
# core/fallback_detector.py
from PIL import Image
import numpy as np

class FallbackTextDetector:
    """Tesseractが使えない場合の簡易テキスト検出"""
    
    def detect_text_regions(self, image_path):
        """画像からテキスト領域を検出（簡易版）"""
        # エッジ検出ベースの簡易実装
        # 精度は劣るが、依存関係なし
        pass
```

### Step 1.3: 実行環境の簡素化（3日）

#### 直接実行可能なランチャー作成
```batch
@echo off
REM overflow_checker.bat - Windows用ランチャー

:: Pythonパスの自動検出
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo エラー: Pythonが見つかりません
    echo https://www.python.org からインストールしてください
    pause
    exit /b 1
)

:: アプリケーション起動
cd /d "%~dp0"
python overflow_checker_standalone\run_ultimate.py %*
```

#### PowerShell版ランチャー
```powershell
# overflow_checker.ps1
param(
    [string]$PdfPath = ""
)

# スクリプトディレクトリに移動
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Python確認
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "エラー: Pythonが見つかりません" -ForegroundColor Red
    exit 1
}

# アプリ起動
if ($PdfPath) {
    python overflow_checker_standalone\run_ultimate.py --pdf $PdfPath
} else {
    python overflow_checker_standalone\run_ultimate.py
}
```

### Step 1.4: インストーラーなし配布版（2日）

#### ZIPアーカイブ配布
```
OverflowChecker_v1.0_Windows/
├── OverflowChecker.exe     # PyInstallerで作成
├── overflow_checker.bat     # バッチランチャー
├── overflow_checker.ps1     # PowerShellランチャー
├── tesseract-portable/      # Tesseractポータブル版
│   └── tesseract.exe
├── data/                    # 学習データ
│   └── learning.db
├── config/                  # 設定ファイル
│   └── settings.json
└── README.txt              # 使用方法
```

### Step 1.5: 自動更新機能（3日）

```python
# utils/auto_updater.py
import requests
import json
from packaging import version

class AutoUpdater:
    """GitHub Releasesからの自動更新"""
    
    GITHUB_API = "https://api.github.com/repos/your-repo/overflow-checker/releases/latest"
    
    def check_update(self, current_version):
        """新バージョンチェック"""
        try:
            response = requests.get(self.GITHUB_API)
            latest = response.json()
            
            if version.parse(latest['tag_name']) > version.parse(current_version):
                return latest
        except:
            pass
        return None
    
    def download_update(self, release_info):
        """更新ファイルのダウンロード"""
        # バックグラウンドでダウンロード
        # 次回起動時に適用
```

---

## 📊 Phase 2: 溢れ学習パターン実装（4-5週間）

### 目標
機械学習とGemini APIを活用した高度な学習システムの実装。

### Step 2.1: ローカルML実装（1週間）

#### 軽量MLモデルの選定と実装
```python
# core/ml/lightweight_model.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import joblib
import numpy as np

class LightweightOverflowModel:
    """軽量な機械学習モデル"""
    
    def __init__(self):
        # シンプルで高速なモデル
        self.model = LogisticRegression(max_iter=1000)
        self.feature_extractor = FeatureExtractor()
        
    def extract_features(self, page_data):
        """ページから特徴量を抽出"""
        features = {
            'text_density': self._calc_text_density(page_data),
            'right_margin_distance': self._calc_margin_distance(page_data),
            'char_count_in_danger_zone': self._count_danger_zone_chars(page_data),
            'code_block_presence': self._has_code_block(page_data),
            'avg_line_length': self._calc_avg_line_length(page_data),
            # 10-15個の特徴量
        }
        return np.array(list(features.values()))
    
    def train_incremental(self, new_data):
        """インクリメンタル学習"""
        # オンライン学習対応
        X, y = self._prepare_data(new_data)
        self.model.partial_fit(X, y)
```

### Step 2.2: Gemini API統合（1週間）

#### Gemini活用の画像解析
```python
# core/ml/gemini_analyzer.py
import google.generativeai as genai
from PIL import Image
import io

class GeminiOverflowAnalyzer:
    """Gemini APIを使った高度な溢れ解析"""
    
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        
    async def analyze_page(self, page_image):
        """ページ画像の詳細解析"""
        prompt = """
        この技術書のページ画像を分析してください：
        1. コードブロックからテキストがはみ出していないか
        2. 右マージンを超えている文字がないか
        3. レイアウトの問題点
        
        JSON形式で回答：
        {
            "has_overflow": boolean,
            "overflow_regions": [{"x": int, "y": int, "width": int, "height": int}],
            "confidence": float,
            "suggestions": string
        }
        """
        
        response = await self.model.generate_content_async([prompt, page_image])
        return self._parse_response(response.text)
    
    async def learn_from_feedback(self, page_image, user_correction):
        """ユーザーフィードバックからの学習"""
        prompt = f"""
        前回の解析が間違っていました。
        ユーザーの修正: {user_correction}
        
        このパターンを学習し、今後の検出精度を向上させるための
        ルールを提案してください。
        """
        
        response = await self.model.generate_content_async([prompt, page_image])
        return self._extract_rules(response.text)
```

### Step 2.3: ハイブリッド学習システム（2週間）

#### ローカルMLとGeminiの統合
```python
# core/ml/hybrid_learner.py
import asyncio
from typing import List, Dict

class HybridLearningSystem:
    """ローカルMLとGemini APIのハイブリッドシステム"""
    
    def __init__(self, gemini_api_key=None):
        self.local_model = LightweightOverflowModel()
        self.gemini = GeminiOverflowAnalyzer(gemini_api_key) if gemini_api_key else None
        self.ensemble_weights = {'local': 0.7, 'gemini': 0.3}
        
    async def detect_with_learning(self, pdf_path):
        """学習機能付き検出"""
        results = []
        
        for page in self.extract_pages(pdf_path):
            # ローカルML予測
            local_pred = self.local_model.predict(page)
            
            # 不確実な場合のみGemini使用（コスト削減）
            if 0.3 < local_pred < 0.7 and self.gemini:
                gemini_pred = await self.gemini.analyze_page(page.image)
                final_pred = self._ensemble_prediction(local_pred, gemini_pred)
            else:
                final_pred = local_pred
                
            results.append({
                'page': page.number,
                'overflow_probability': final_pred,
                'method': 'hybrid'
            })
            
        return results
    
    def active_learning(self):
        """能動学習 - 最も不確実なサンプルを選択"""
        uncertain_samples = self.get_uncertain_predictions()
        return uncertain_samples[:10]  # ユーザーに確認を求める
```

### Step 2.4: 自動改善エンジン（1週間）

```python
# core/ml/auto_improver.py
class AutoImprovementEngine:
    """継続的な自動改善システム"""
    
    def __init__(self):
        self.performance_tracker = PerformanceTracker()
        self.rule_generator = RuleGenerator()
        
    def scheduled_improvement(self):
        """定期的な改善処理（日次/週次）"""
        # 1. パフォーマンス分析
        metrics = self.performance_tracker.get_metrics()
        
        # 2. 問題パターンの特定
        problem_patterns = self.identify_problem_patterns(metrics)
        
        # 3. 新ルール生成
        new_rules = self.rule_generator.generate(problem_patterns)
        
        # 4. A/Bテスト
        self.run_ab_test(new_rules)
        
        # 5. 最良ルールの採用
        self.adopt_best_rules()
```

---

## 🔧 Phase 3: TECHZIPへの統合（2-3週間）

### 目標
単独アプリとして完成した溢れチェッカーをTECHZIPに統合。

### Step 3.1: APIラッパーの作成（3日）

```python
# techzip_integration/overflow_checker_api.py
from pathlib import Path
import subprocess
import json

class OverflowCheckerAPI:
    """TECHZIPから呼び出すためのAPI"""
    
    def __init__(self, exe_path=None):
        if exe_path:
            self.exe_path = exe_path
        else:
            # 同梱版を使用
            self.exe_path = Path(__file__).parent / "bin" / "OverflowChecker.exe"
    
    def check_pdf(self, pdf_path, callback=None):
        """外部プロセスとして実行"""
        cmd = [str(self.exe_path), "--json", "--pdf", str(pdf_path)]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 非同期で進捗を取得
        for line in process.stdout:
            if line.startswith("PROGRESS:"):
                if callback:
                    callback(json.loads(line[9:]))
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            return json.loads(stdout)
        else:
            raise Exception(f"Overflow check failed: {stderr}")
```

### Step 3.2: GUI統合（4日）

```python
# gui/components/overflow_check_button.py
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QThread, pyqtSignal

class OverflowCheckThread(QThread):
    """バックグラウンド実行スレッド"""
    progress = pyqtSignal(dict)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, api, pdf_path):
        super().__init__()
        self.api = api
        self.pdf_path = pdf_path
        
    def run(self):
        try:
            result = self.api.check_pdf(
                self.pdf_path,
                callback=lambda p: self.progress.emit(p)
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

# gui/main_window.py への追加
def add_overflow_check_button(self):
    """InputPanelに溢れチェックボタンを追加"""
    self.overflow_button = QPushButton("リスト溢れチェック")
    self.overflow_button.setIcon(QIcon("assets/overflow_check.png"))
    self.overflow_button.clicked.connect(self.on_overflow_check)
    
    # レイアウトに追加
    self.button_layout.addWidget(self.overflow_button)
```

### Step 3.3: 設定統合（3日）

```json
// config/settings.json への追加
{
    "overflow_checker": {
        "enabled": true,
        "exe_path": "./bin/OverflowChecker.exe",
        "use_gemini": false,
        "gemini_api_key": "",
        "auto_check_after_conversion": true,
        "learning_mode": "local"
    }
}
```

### Step 3.4: 配布とインストーラー（4日）

```python
# build_integrated.py
"""統合版TECHZIPのビルドスクリプト"""

def build_techzip_with_overflow():
    # 1. 溢れチェッカーをビルド
    build_overflow_checker()
    
    # 2. TECHZIPに組み込み
    copy_to_techzip()
    
    # 3. 統合版インストーラー作成
    create_installer()
```

---

## 📅 実装スケジュール

### Month 1: Windowsネイティブ単独アプリ
- Week 1: 依存関係整理とポータブル化
- Week 2: Tesseract対応と実行環境簡素化
- Week 3: 配布版作成とテスト

### Month 2-3: 学習システム実装
- Week 4-5: ローカルML実装
- Week 6: Gemini API統合
- Week 7-8: ハイブリッドシステム
- Week 9: 自動改善エンジン

### Month 3-4: TECHZIP統合
- Week 10: APIラッパーとGUI統合
- Week 11: 設定統合とテスト
- Week 12: 配布版作成とリリース

## 🎯 成功指標

### Phase 1完了時
- ✅ 仮想環境不要で動作
- ✅ ダブルクリックで起動
- ✅ 5MB以下の配布サイズ（Tesseract別）

### Phase 2完了時
- ✅ 検出精度95%以上
- ✅ 誤検出率5%以下
- ✅ 学習による継続的改善

### Phase 3完了時
- ✅ TECHZIPからワンクリック実行
- ✅ シームレスな統合
- ✅ 既存機能への影響なし