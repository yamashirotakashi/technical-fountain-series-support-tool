#!/usr/bin/env python3
"""
デバッグログレベルを設定するスクリプト
"""
import logging
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import get_logger, setup_logging

# ログレベルをDEBUGに設定
setup_logging()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# すべてのハンドラーのレベルもDEBUGに設定
for handler in logger.handlers:
    handler.setLevel(logging.DEBUG)

print("✓ ログレベルをDEBUGに設定しました")
print("✓ 詳細なエラートレースが出力されます")
print("")
print("アプリケーションを再起動してください:")
print("python main.py")