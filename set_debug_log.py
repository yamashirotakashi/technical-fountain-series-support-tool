#!/usr/bin/env python3
"""
繝・ヰ繝・げ繝ｭ繧ｰ繝ｬ繝吶Ν繧定ｨｭ螳壹☆繧九せ繧ｯ繝ｪ繝励ヨ
"""
import logging
import sys
from pathlib import Path

# 繝励Ο繧ｸ繧ｧ繧ｯ繝医Ν繝ｼ繝医ｒPython繝代せ縺ｫ霑ｽ蜉
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import get_logger, setup_logging

# 繝ｭ繧ｰ繝ｬ繝吶Ν繧奪EBUG縺ｫ險ｭ螳・setup_logging()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 縺吶∋縺ｦ縺ｮ繝上Φ繝峨Λ繝ｼ縺ｮ繝ｬ繝吶Ν繧・EBUG縺ｫ險ｭ螳・for handler in logger.handlers:
    handler.setLevel(logging.DEBUG)

print("笨・繝ｭ繧ｰ繝ｬ繝吶Ν繧奪EBUG縺ｫ險ｭ螳壹＠縺ｾ縺励◆")
print("笨・隧ｳ邏ｰ縺ｪ繧ｨ繝ｩ繝ｼ繝医Ξ繝ｼ繧ｹ縺悟・蜉帙＆繧後∪縺・)
print("")
print("繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧貞・襍ｷ蜍輔＠縺ｦ縺上□縺輔＞:")
print("python main.py")