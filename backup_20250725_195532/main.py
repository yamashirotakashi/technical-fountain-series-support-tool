#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""謚陦難ｿｽE豕峨す繝ｪ繝ｼ繧ｺ蛻ｶ菴懈髪謠ｴ繝・・ｽE繝ｫ - 繧ｨ繝ｳ繝医Μ繝ｼ繝昴う繝ｳ繝・""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# .env繝輔ぃ繧､繝ｫ繧定ｪｭ縺ｿ霎ｼ繧
load_dotenv()

# 繝励Ο繧ｸ繧ｧ繧ｯ繝茨ｿｽE繝ｫ繝ｼ繝医ョ繧｣繝ｬ繧ｯ繝医Μ繧単ython繝代せ縺ｫ霑ｽ蜉
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow
from utils.logger import get_logger


def main():
    """繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ繧ｨ繝ｳ繝医Μ繝ｼ繝昴う繝ｳ繝・""
    # 繝ｭ繧ｬ繝ｼ繧抵ｿｽE譛溷喧
    logger = get_logger(__name__)
    logger.info("繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧定ｵｷ蜍輔＠縺ｾ縺・)
    
    # High DPI蟇ｾ蠢懶ｼ・t6縺ｧ縺ｯ閾ｪ蜍慕噪縺ｫ譛牙柑・・    # Qt6縺ｧ縺ｯ縺薙ｌ繧峨・螻樊ｧ縺ｯ蜑企勁縺輔ｌ縺ｦ縺・ｋ縺溘ａ縲∬ｨｭ螳壻ｸ崎ｦ・    
    # 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧剃ｽ懶ｿｽE
    app = QApplication(sys.argv)
    app.setApplicationName("謚陦難ｿｽE豕峨す繝ｪ繝ｼ繧ｺ蛻ｶ菴懈髪謠ｴ繝・・ｽE繝ｫ")
    app.setOrganizationName("Technical Fountain")
    
    # 繧ｹ繧ｿ繧､繝ｫ繧定ｨｭ螳・    app.setStyle("Fusion")
    
    # 繝｡繧､繝ｳ繧ｦ繧｣繝ｳ繝峨え繧剃ｽ懶ｿｽE縺励※陦ｨ遉ｺ
    window = MainWindow()
    window.show()
    
    logger.info("繝｡繧､繝ｳ繧ｦ繧｣繝ｳ繝峨え繧定｡ｨ遉ｺ縺励∪縺励◆")
    
    # 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧貞ｮ溯｡・    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧ｨ繝ｩ繝ｼ: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()