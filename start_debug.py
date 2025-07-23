#!/usr/bin/env python3
"""
デバッグモードでアプリケーションを起動
"""
import sys
import logging
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# ログレベルをDEBUGに設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# ルートロガーのレベルをDEBUGに設定
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# すべてのハンドラーのレベルもDEBUGに設定
for handler in logger.handlers:
    handler.setLevel(logging.DEBUG)

print("=== デバッグモードで起動 ===")
print("詳細なログが出力されます")
print("")

# メインアプリケーションを起動
from main import main
main()