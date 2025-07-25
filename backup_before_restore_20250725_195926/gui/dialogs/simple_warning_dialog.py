"""繧ｷ繝ｳ繝励Ν縺ｪ隴ｦ蜻翫ム繧､繧｢繝ｭ繧ｰ・・MessageBox繝吶・繧ｹ・・""
from PyQt6.QtWidgets import QMessageBox, QTextEdit, QVBoxLayout
from PyQt6.QtCore import Qt

def show_warning_dialog(parent, messages, result_type="warning"):
    """
    繧ｷ繝ｳ繝励Ν縺ｪ隴ｦ蜻翫ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ
    
    Args:
        parent: 隕ｪ繧ｦ繧｣繧ｸ繧ｧ繝・ヨ
        messages: 繝｡繝・そ繝ｼ繧ｸ縺ｮ繝ｪ繧ｹ繝・        result_type: "warning" 縺ｾ縺溘・ "error"
    """
    # 繝｡繝・そ繝ｼ繧ｸ繝懊ャ繧ｯ繧ｹ繧剃ｽ懈・
    msg_box = QMessageBox(parent)
    
    # 繧ｿ繧､繝医Ν縺ｨ繧｢繧､繧ｳ繝ｳ繧定ｨｭ螳・    if result_type == "error":
        msg_box.setWindowTitle("螟画鋤繧ｨ繝ｩ繝ｼ")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("螟画鋤蜃ｦ逅・′螟ｱ謨励＠縺ｾ縺励◆")
    else:
        msg_box.setWindowTitle("螟画鋤隴ｦ蜻・)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("螟画鋤蜃ｦ逅・・謌仙粥縺励∪縺励◆縺後∬ｭｦ蜻翫′縺ゅｊ縺ｾ縺・)
    
    # 隧ｳ邏ｰ繝｡繝・そ繝ｼ繧ｸ繧定ｨｭ螳・    detailed_text = "\n".join([f"[{i+1:3d}] {msg}" for i, msg in enumerate(messages)])
    msg_box.setDetailedText(detailed_text)
    
    # 繝懊ち繝ｳ繧定ｨｭ螳・    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
    
    # 繝｢繝ｼ繝繝ｫ縺ｧ陦ｨ遉ｺ
    msg_box.exec()