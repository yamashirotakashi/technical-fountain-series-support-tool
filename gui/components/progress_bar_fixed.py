"""騾ｲ謐苓｡ｨ遉ｺ繝舌・繝｢繧ｸ繝･繝ｼ繝ｫ"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot


class ProgressPanel(QWidget):
    """騾ｲ謐苓｡ｨ遉ｺ繝代ロ繝ｫ繧ｦ繧｣繧ｸ繧ｧ繝・ヨ"""
    
    def __init__(self, parent=None):
        """
        ProgressPanel繧貞・譛溷喧
        
        Args:
            parent: 隕ｪ繧ｦ繧｣繧ｸ繧ｧ繝・ヨ
        """
        super().__init__(parent)
        self.total_items = 0
        self.current_item = 0
        self.setup_ui()
    
    def setup_ui(self):
        """UI繧呈ｧ狗ｯ・""
        layout = QVBoxLayout(self)
        
        # 迥ｶ諷九Λ繝吶Ν
        self.status_label = QLabel("蠕・ｩ滉ｸｭ...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #333;
                padding: 2px;
            }
        """)
        
        # 繝励Ο繧ｰ繝ｬ繧ｹ繝舌・
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        # 隧ｳ邏ｰ繝ｩ繝吶Ν
        detail_layout = QHBoxLayout()
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #666;
            }
        """)
        self.time_label = QLabel("")
        self.time_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #666;
            }
        """)
        
        detail_layout.addWidget(self.detail_label)
        detail_layout.addStretch()
        detail_layout.addWidget(self.time_label)
        
        # 繝ｬ繧､繧｢繧ｦ繝医↓霑ｽ蜉
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(detail_layout)
    
    @pyqtSlot(int, int)
    def set_total_items(self, total: int, current: int = 0):
        """
        蜃ｦ逅・☆繧狗ｷ上い繧､繝・Β謨ｰ繧定ｨｭ螳・        
        Args:
            total: 邱上い繧､繝・Β謨ｰ
            current: 迴ｾ蝨ｨ縺ｮ繧｢繧､繝・Β逡ｪ蜿ｷ
        """
        self.total_items = total
        self.current_item = current
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.update_detail_label()
    
    @pyqtSlot(int)
    def update_progress(self, value: int):
        """
        騾ｲ謐励ｒ譖ｴ譁ｰ
        
        Args:
            value: 騾ｲ謐怜､・・-100縺ｾ縺溘・繧｢繧､繝・Β逡ｪ蜿ｷ・・        """
        if self.total_items > 0:
            # 繧｢繧､繝・Β逡ｪ蜿ｷ縺ｨ縺励※蜃ｦ逅・            self.current_item = value
            self.progress_bar.setValue(value)
            percentage = int((value / self.total_items) * 100)
            self.progress_bar.setFormat(f"{percentage}%")
        else:
            # 繝代・繧ｻ繝ｳ繝・・繧ｸ縺ｨ縺励※蜃ｦ逅・            self.progress_bar.setValue(value)
            self.progress_bar.setFormat(f"{value}%")
        
        self.update_detail_label()
    
    @pyqtSlot(str)
    def update_status(self, message: str):
        """
        迥ｶ諷九Γ繝・そ繝ｼ繧ｸ繧呈峩譁ｰ
        
        Args:
            message: 迥ｶ諷九Γ繝・そ繝ｼ繧ｸ
        """
        self.status_label.setText(message)
    
    @pyqtSlot(str)
    def update_time(self, time_str: str):
        """
        邨碁℃譎る俣繧呈峩譁ｰ
        
        Args:
            time_str: 譎る俣譁・ｭ怜・
        """
        self.time_label.setText(time_str)
    
    def update_detail_label(self):
        """隧ｳ邏ｰ繝ｩ繝吶Ν繧呈峩譁ｰ"""
        if self.total_items > 0:
            self.detail_label.setText(f"{self.current_item}/{self.total_items} 蜃ｦ逅・ｸｭ")
        else:
            self.detail_label.setText("")
    
    def reset(self):
        """騾ｲ謐励ｒ繝ｪ繧ｻ繝・ヨ"""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.status_label.setText("蠕・ｩ滉ｸｭ...")
        self.detail_label.setText("")
        self.time_label.setText("")
        self.total_items = 0
        self.current_item = 0
    
    def set_indeterminate(self, is_indeterminate: bool):
        """
        荳咲｢ｺ螳夐ｲ謐励Δ繝ｼ繝峨ｒ險ｭ螳・        
        Args:
            is_indeterminate: 荳咲｢ｺ螳壹Δ繝ｼ繝峨↓縺吶ｋ蝣ｴ蜷・rue
        """
        if is_indeterminate:
            self.progress_bar.setMaximum(0)
            self.progress_bar.setMinimum(0)
        else:
            self.progress_bar.setMaximum(100)
            self.progress_bar.setMinimum(0)