"""蜃ｦ逅・婿蠑城∈謚槭ム繧､繧｢繝ｭ繧ｰ"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QRadioButton,
                             QButtonGroup, QLabel, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal


class ProcessModeDialog(QDialog):
    """蜃ｦ逅・婿蠑擾ｼ亥ｾ捺擂譁ｹ蠑・API譁ｹ蠑擾ｼ峨ｒ驕ｸ謚槭☆繧九ム繧､繧｢繝ｭ繧ｰ"""
    
    # 蜃ｦ逅・婿蠑上・螳夂ｾｩ
    MODE_TRADITIONAL = "traditional"
    MODE_API = "api"
    
    # 繧ｷ繧ｰ繝翫Ν
    mode_selected = pyqtSignal(str)  # 驕ｸ謚槭＆繧後◆蜃ｦ逅・婿蠑・    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_mode = self.MODE_TRADITIONAL  # 繝・ヵ繧ｩ繝ｫ繝医・蠕捺擂譁ｹ蠑・        self.setup_ui()
    
    def setup_ui(self):
        """UI繧呈ｧ狗ｯ・""
        self.setWindowTitle("蜃ｦ逅・婿蠑上・驕ｸ謚・)
        self.setModal(True)
        self.setFixedSize(400, 250)
        
        # 繝｡繧､繝ｳ繝ｬ繧､繧｢繧ｦ繝・        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 隱ｬ譏弱Λ繝吶Ν
        description = QLabel(
            "螟画鋤蜃ｦ逅・・譁ｹ蠑上ｒ驕ｸ謚槭＠縺ｦ縺上□縺輔＞縲・n"
            "蠕捺擂譁ｹ蠑・ 繝｡繝ｼ繝ｫ邨檎罰縺ｧ繝輔ぃ繧､繝ｫ繧帝∽ｿ｡\n"
            "API譁ｹ蠑・ 逶ｴ謗･API繧剃ｽｿ逕ｨ縺励※鬮倬溷､画鋤"
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # 繝ｩ繧ｸ繧ｪ繝懊ち繝ｳ繧ｰ繝ｫ繝ｼ繝・        group_box = QGroupBox("蜃ｦ逅・婿蠑・)
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)
        
        # 繝懊ち繝ｳ繧ｰ繝ｫ繝ｼ繝・        self.button_group = QButtonGroup()
        
        # 蠕捺擂譁ｹ蠑上Λ繧ｸ繧ｪ繝懊ち繝ｳ
        self.traditional_radio = QRadioButton("蠕捺擂譁ｹ蠑擾ｼ医Γ繝ｼ繝ｫ邨檎罰・・)
        self.traditional_radio.setChecked(True)  # 繝・ヵ繧ｩ繝ｫ繝医〒驕ｸ謚・        self.button_group.addButton(self.traditional_radio)
        group_layout.addWidget(self.traditional_radio)
        
        # 蠕捺擂譁ｹ蠑上・隱ｬ譏・        traditional_desc = QLabel(
            "  窶｢ 繝｡繝ｼ繝ｫ縺ｧ繝輔ぃ繧､繝ｫ繧帝∽ｿ｡\n"
            "  窶｢ 霑比ｿ｡繧貞ｾ・▲縺ｦ邨先棡繧貞叙蠕予n"
            "  窶｢ 螳牙ｮ壽ｧ縺碁ｫ倥＞"
        )
        traditional_desc.setStyleSheet("QLabel { margin-left: 20px; color: #666; }")
        group_layout.addWidget(traditional_desc)
        
        # 繧ｹ繝壹・繧ｹ
        group_layout.addSpacing(10)
        
        # API譁ｹ蠑上Λ繧ｸ繧ｪ繝懊ち繝ｳ
        self.api_radio = QRadioButton("API譁ｹ蠑擾ｼ育峩謗･螟画鋤・・)
        self.button_group.addButton(self.api_radio)
        group_layout.addWidget(self.api_radio)
        
        # API譁ｹ蠑上・隱ｬ譏・        api_desc = QLabel(
            "  窶｢ API繧堤峩謗･菴ｿ逕ｨ\n"
            "  窶｢ 鬮倬溷・逅・′蜿ｯ閭ｽ\n"
            "  窶｢ 隧ｳ邏ｰ縺ｪ隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ繧貞叙蠕・
        )
        api_desc.setStyleSheet("QLabel { margin-left: 20px; color: #666; }")
        group_layout.addWidget(api_desc)
        
        layout.addWidget(group_box)
        
        # 繧ｹ繝壹・繧ｹ
        layout.addStretch()
        
        # 繝懊ち繝ｳ
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # OK繝懊ち繝ｳ
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        # 繧ｭ繝｣繝ｳ繧ｻ繝ｫ繝懊ち繝ｳ
        cancel_button = QPushButton("繧ｭ繝｣繝ｳ繧ｻ繝ｫ")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 繧ｹ繧ｿ繧､繝ｫ繧定ｨｭ螳・        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
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
            QRadioButton {
                font-size: 10pt;
                padding: 5px;
            }
            QPushButton {
                min-width: 80px;
                padding: 5px 15px;
            }
        """)
    
    def get_selected_mode(self) -> str:
        """驕ｸ謚槭＆繧後◆蜃ｦ逅・婿蠑上ｒ蜿門ｾ・""
        if self.traditional_radio.isChecked():
            return self.MODE_TRADITIONAL
        else:
            return self.MODE_API
    
    def accept(self):
        """OK繝懊ち繝ｳ縺梧款縺輔ｌ縺滓凾縺ｮ蜃ｦ逅・""
        self.selected_mode = self.get_selected_mode()
        self.mode_selected.emit(self.selected_mode)
        super().accept()