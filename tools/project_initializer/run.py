#!/usr/bin/env python3
"""
技術の泉シリーズプロジェクト初期化ツール - エントリーポイント
"""

import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# メインウィンドウを実行
from main_window import main

if __name__ == "__main__":
    main()