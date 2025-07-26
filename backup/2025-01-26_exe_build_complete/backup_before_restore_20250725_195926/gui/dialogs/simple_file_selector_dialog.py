"""繧ｷ繝ｳ繝励Ν縺ｪ繝輔ぃ繧､繝ｫ驕ｸ謚槭ム繧､繧｢繝ｭ繧ｰ"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QCheckBox, QPushButton, QLabel, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt


class SimpleFileSelectorDialog(QDialog):
    """繝輔ぃ繧､繝ｫ驕ｸ謚樒畑縺ｮ繧ｷ繝ｳ繝励Ν縺ｪ繝繧､繧｢繝ｭ繧ｰ"""
    
    def __init__(self, file_list, parent=None):
        super().__init__(parent)
        self.file_list = file_list
        self.checkboxes = []
        self.selected_files = []
        self._init_ui()
        
    def _init_ui(self):
        """UI蛻晄悄蛹・""
        self.setWindowTitle("繝輔ぃ繧､繝ｫ驕ｸ謚・)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout()
        
        # 繧ｿ繧､繝医Ν
        title = QLabel("繝壹・繧ｹ繝医☆繧九ヵ繧｡繧､繝ｫ繧帝∈謚槭＠縺ｦ縺上□縺輔＞:")
        layout.addWidget(title)
        
        # 繧ｹ繧ｯ繝ｭ繝ｼ繝ｫ繧ｨ繝ｪ繧｢
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # 繝√ぉ繝・け繝懊ャ繧ｯ繧ｹ菴懈・
        for file_path in self.file_list:
            checkbox = QCheckBox(file_path.name)
            checkbox.setChecked(True)  # 繝・ヵ繧ｩ繝ｫ繝医〒蜈ｨ驕ｸ謚・            checkbox.file_path = file_path  # 繝輔ぃ繧､繝ｫ繝代せ繧剃ｿ晄戟
            self.checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # 繝懊ち繝ｳ
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("蜈ｨ縺ｦ驕ｸ謚・)
        select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("蜈ｨ縺ｦ隗｣髯､")
        deselect_all_btn.clicked.connect(self._deselect_all)
        button_layout.addWidget(deselect_all_btn)
        
        button_layout.addStretch()
        
        paste_btn = QPushButton("繝輔ぃ繧､繝ｫ繧偵・繝ｼ繧ｹ繝・)
        paste_btn.clicked.connect(self._on_paste)
        button_layout.addWidget(paste_btn)
        
        cancel_btn = QPushButton("繧ｭ繝｣繝ｳ繧ｻ繝ｫ")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def _select_all(self):
        """蜈ｨ縺ｦ驕ｸ謚・""
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)
            
    def _deselect_all(self):
        """蜈ｨ縺ｦ隗｣髯､"""
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
            
    def _on_paste(self):
        """繝壹・繧ｹ繝医・繧ｿ繝ｳ謚ｼ荳・""
        self.selected_files = [
            cb.file_path for cb in self.checkboxes if cb.isChecked()
        ]
        if not self.selected_files:
            # 菴輔ｂ驕ｸ謚槭＆繧後※縺・↑縺・ｴ蜷医・菴輔ｂ縺励↑縺・            return
        self.accept()
        
    def get_selected_files(self):
        """驕ｸ謚槭＆繧後◆繝輔ぃ繧､繝ｫ繧貞叙蠕・""
        return self.selected_files