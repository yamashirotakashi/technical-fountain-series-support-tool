"""蜈･蜉帙ヱ繝阪Ν繝｢繧ｸ繝･繝ｼ繝ｫ"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QGroupBox)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from utils.validators import Validators


class InputPanel(QWidget):
    """N繧ｳ繝ｼ繝牙・蜉帙ヱ繝阪Ν繧ｦ繧｣繧ｸ繧ｧ繝・ヨ"""
    
    # 繧ｫ繧ｹ繧ｿ繝繧ｷ繧ｰ繝翫Ν
    process_requested = pyqtSignal(list)  # N繧ｳ繝ｼ繝峨・繝ｪ繧ｹ繝医ｒ騾∽ｿ｡
    settings_requested = pyqtSignal()  # 險ｭ螳壹・繧ｿ繝ｳ繧ｯ繝ｪ繝・け
    
    def __init__(self, parent=None):
        """
        InputPanel繧貞・譛溷喧
        
        Args:
            parent: 隕ｪ繧ｦ繧｣繧ｸ繧ｧ繝・ヨ
        """
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI繧呈ｧ狗ｯ・""
        layout = QVBoxLayout(self)
        
        # 繧ｰ繝ｫ繝ｼ繝励・繝・け繧ｹ
        group_box = QGroupBox("N繧ｳ繝ｼ繝牙・蜉・)
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        group_layout = QVBoxLayout(group_box)
        
        # 隱ｬ譏弱Λ繝吶Ν
        description_label = QLabel(
            "蜃ｦ逅・＠縺溘＞N繧ｳ繝ｼ繝峨ｒ蜈･蜉帙＠縺ｦ縺上□縺輔＞縲・n"
            "隍・焚縺ｮ繧ｳ繝ｼ繝峨・繧ｫ繝ｳ繝橸ｼ・・峨√ち繝悶√せ繝壹・繧ｹ縲√∪縺溘・謾ｹ陦後〒蛹ｺ蛻・▲縺ｦ縺上□縺輔＞縲・n"
            "萓・ N00001, N00002 縺ｾ縺溘・ N00001[Tab]N00002 縺ｾ縺溘・蜷・｡後↓1縺､縺壹▽"
        )
        description_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        
        # 蜈･蜉帙お繝ｪ繧｢
        self.n_code_input = QTextEdit()
        self.n_code_input.setMaximumHeight(100)
        self.n_code_input.setPlaceholderText("N00001, N00002, N00003...")
        self.n_code_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12pt;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
            }
        """)
        
        # 繝懊ち繝ｳ繝ｬ繧､繧｢繧ｦ繝・        button_layout = QHBoxLayout()
        
        # 蜃ｦ逅・幕蟋九・繧ｿ繝ｳ
        self.process_button = QPushButton("蜃ｦ逅・幕蟋・)
        self.process_button.clicked.connect(self.on_process_clicked)
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # 繧ｯ繝ｪ繧｢繝懊ち繝ｳ
        self.clear_button = QPushButton("繧ｯ繝ｪ繧｢")
        self.clear_button.clicked.connect(self.clear_input)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c01005;
            }
        """)
        
        # 險ｭ螳壹・繧ｿ繝ｳ
        self.settings_button = QPushButton("險ｭ螳・)
        self.settings_button.clicked.connect(self.on_settings_clicked)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0960aa;
            }
        """)
        
        # 繝懊ち繝ｳ繧帝・鄂ｮ
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addStretch()
        
        # 繧ｰ繝ｫ繝ｼ繝励Ξ繧､繧｢繧ｦ繝医↓霑ｽ蜉
        group_layout.addWidget(description_label)
        group_layout.addWidget(self.n_code_input)
        group_layout.addLayout(button_layout)
        
        # 繝｡繧､繝ｳ繝ｬ繧､繧｢繧ｦ繝医↓霑ｽ蜉
        layout.addWidget(group_box)
        layout.addStretch()
    
    def get_n_codes(self) -> list:
        """
        蜈･蜉帙＆繧後◆N繧ｳ繝ｼ繝峨・繝ｪ繧ｹ繝医ｒ蜿門ｾ・        
        Returns:
            譛牙柑縺ｪN繧ｳ繝ｼ繝峨・繝ｪ繧ｹ繝・        """
        text = self.n_code_input.toPlainText()
        valid_codes, _ = Validators.validate_n_codes(text)
        return valid_codes
    
    def validate_input(self) -> bool:
        """
        蜈･蜉帙ｒ讀懆ｨｼ
        
        Returns:
            讀懆ｨｼ縺梧・蜉溘＠縺溷ｴ蜷・rue
        """
        text = self.n_code_input.toPlainText()
        valid_codes, errors = Validators.validate_n_codes(text)
        
        if not text.strip():
            self.show_error("N繧ｳ繝ｼ繝峨ｒ蜈･蜉帙＠縺ｦ縺上□縺輔＞縲・)
            return False
        
        if errors:
            error_message = "蜈･蜉帙お繝ｩ繝ｼ:\n" + "\n".join(errors)
            self.show_error(error_message)
            return False
        
        if not valid_codes:
            self.show_error("譛牙柑縺ｪN繧ｳ繝ｼ繝峨′蜈･蜉帙＆繧後※縺・∪縺帙ｓ縲・)
            return False
        
        return True
    
    def on_process_clicked(self):
        """蜃ｦ逅・幕蟋九・繧ｿ繝ｳ縺後け繝ｪ繝・け縺輔ｌ縺滓凾縺ｮ蜃ｦ逅・""
        if self.validate_input():
            n_codes = self.get_n_codes()
            self.process_requested.emit(n_codes)
    
    def clear_input(self):
        """蜈･蜉帙ｒ繧ｯ繝ｪ繧｢"""
        self.n_code_input.clear()
    
    def on_settings_clicked(self):
        """險ｭ螳壹・繧ｿ繝ｳ縺後け繝ｪ繝・け縺輔ｌ縺滓凾縺ｮ蜃ｦ逅・""
        self.settings_requested.emit()
    
    def show_error(self, message: str):
        """繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ繧定｡ｨ遉ｺ"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "蜈･蜉帙お繝ｩ繝ｼ", message)
    
    def set_enabled(self, enabled: bool):
        """繝代ロ繝ｫ縺ｮ譛牙柑/辟｡蜉ｹ繧定ｨｭ螳・""
        self.process_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
        self.n_code_input.setEnabled(enabled)