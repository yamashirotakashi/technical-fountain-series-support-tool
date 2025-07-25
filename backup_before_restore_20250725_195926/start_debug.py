#!/usr/bin/env python3
"""
繝・ヰ繝・げ繝｢繝ｼ繝峨〒繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧定ｵｷ蜍・"""
import sys
import logging
from pathlib import Path

# 繝励Ο繧ｸ繧ｧ繧ｯ繝医Ν繝ｼ繝医ｒPython繝代せ縺ｫ霑ｽ蜉
sys.path.insert(0, str(Path(__file__).parent))

# 繝ｭ繧ｰ繝ｬ繝吶Ν繧奪EBUG縺ｫ險ｭ螳・logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# 繝ｫ繝ｼ繝医Ο繧ｬ繝ｼ縺ｮ繝ｬ繝吶Ν繧奪EBUG縺ｫ險ｭ螳・logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 縺吶∋縺ｦ縺ｮ繝上Φ繝峨Λ繝ｼ縺ｮ繝ｬ繝吶Ν繧・EBUG縺ｫ險ｭ螳・for handler in logger.handlers:
    handler.setLevel(logging.DEBUG)

print("=== 繝・ヰ繝・げ繝｢繝ｼ繝峨〒襍ｷ蜍・===")
print("隧ｳ邏ｰ縺ｪ繝ｭ繧ｰ縺悟・蜉帙＆繧後∪縺・)
print("")

# 繝｡繧､繝ｳ繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧定ｵｷ蜍・from main import main
main()