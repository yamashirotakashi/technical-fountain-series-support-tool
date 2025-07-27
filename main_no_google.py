"""繝｡繧､繝ｳ繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ - Google Sheets讖溯・辟｡蜉ｹ迚・""
import sys
import os
from pathlib import Path

# 繝励Ο繧ｸ繧ｧ繧ｯ繝医・繝ｫ繝ｼ繝医ョ繧｣繝ｬ繧ｯ繝医Μ繧単ython繝代せ縺ｫ霑ｽ蜉
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 迺ｰ蠅・､画焚繧定ｪｭ縺ｿ霎ｼ縺ｿ
from dotenv import load_dotenv
load_dotenv()

# PyQt6の設定
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from gui.main_window_no_google import MainWindowNoGoogle
from utils.logger import get_logger


def main():
    """繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ繝｡繧､繝ｳ繧ｨ繝ｳ繝医Μ繝ｼ繝昴う繝ｳ繝・""
    logger = get_logger(__name__)
    
    try:
        # Qt Application繧剃ｽ懈・
        app = QApplication(sys.argv)
        app.setApplicationName("謚陦薙・豕峨す繝ｪ繝ｼ繧ｺ蛻ｶ菴懈髪謠ｴ繝・・繝ｫ")
        app.setApplicationVersion("1.0.0")
        
        # DPI繧ｹ繧ｱ繝ｼ繝ｪ繝ｳ繧ｰ繧呈怏蜉ｹ蛹・        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # 繝｡繧､繝ｳ繧ｦ繧｣繝ｳ繝峨え繧剃ｽ懈・
        window = MainWindowNoGoogle()
        window.show()
        
        logger.info("繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧定ｵｷ蜍輔＠縺ｾ縺励◆")
        
        # 繧､繝吶Φ繝医Ν繝ｼ繝励ｒ髢句ｧ・        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ襍ｷ蜍輔お繝ｩ繝ｼ: {e}", exc_info=True)
        
        # 繧ｨ繝ｩ繝ｼ繝繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ
        if 'app' in locals():
            QMessageBox.critical(
                None,
                "襍ｷ蜍輔お繝ｩ繝ｼ",
                f"繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ襍ｷ蜍輔↓螟ｱ謨励＠縺ｾ縺励◆:\n{str(e)}"
            )
        sys.exit(1)


if __name__ == "__main__":
    main()