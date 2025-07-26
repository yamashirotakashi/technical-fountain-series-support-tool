"""隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ繝繧､繧｢繝ｭ繧ｰ"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QLabel, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap, QFont


class WarningDialog(QDialog):
    """API蜃ｦ逅・・隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ繧定｡ｨ遉ｺ縺吶ｋ繝繧､繧｢繝ｭ繧ｰ"""
    
    def __init__(self, messages: list, result_type: str = "warning", parent=None):
        """
        Args:
            messages: 陦ｨ遉ｺ縺吶ｋ隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ縺ｮ繝ｪ繧ｹ繝・            result_type: "warning" (荳驛ｨ謌仙粥) 縺ｾ縺溘・ "error" (螟ｱ謨・
            parent: 隕ｪ繧ｦ繧｣繧ｸ繧ｧ繝・ヨ
        """
        super().__init__(parent)
        self.messages = messages
        self.result_type = result_type
        self.setup_ui()
    
    def setup_ui(self):
        """UI繧呈ｧ狗ｯ・""
        # 繧ｿ繧､繝医Ν險ｭ螳・        if self.result_type == "error":
            self.setWindowTitle("螟画鋤繧ｨ繝ｩ繝ｼ")
            icon_type = "error"
            title_text = "螟画鋤蜃ｦ逅・′螟ｱ謨励＠縺ｾ縺励◆"
            description = "莉･荳九・繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆・・
        else:
            self.setWindowTitle("螟画鋤隴ｦ蜻・)
            icon_type = "warning"
            title_text = "螟画鋤蜃ｦ逅・・謌仙粥縺励∪縺励◆縺後∬ｭｦ蜻翫′縺ゅｊ縺ｾ縺・
            description = "莉･荳九・隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ繧堤｢ｺ隱阪＠縺ｦ縺上□縺輔＞・・
        
        self.setModal(True)
        self.setMinimumSize(700, 500)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # 繧ｷ繧ｹ繝・Β繧ｵ繧ｦ繝ｳ繝峨ｒ蜀咲函・医お繝ｩ繝ｼ縺ｾ縺溘・隴ｦ蜻企浹・・        from PyQt6.QtWidgets import QApplication
        if self.result_type == "error":
            QApplication.beep()  # 繧ｨ繝ｩ繝ｼ髻ｳ
        
        # 繝繧､繧｢繝ｭ繧ｰ繧剃ｸｭ螟ｮ縺ｫ陦ｨ遉ｺ
        if self.parent():
            self.move(
                self.parent().x() + (self.parent().width() - 700) // 2,
                self.parent().y() + (self.parent().height() - 500) // 2
            )
        
        # 繝｡繧､繝ｳ繝ｬ繧､繧｢繧ｦ繝・        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 繝倥ャ繝繝ｼ驛ｨ蛻・        header_layout = QHBoxLayout()
        
        # 繧｢繧､繧ｳ繝ｳ
        icon_label = QLabel()
        if icon_type == "error":
            icon_label.setPixmap(self.style().standardPixmap(
                self.style().SP_MessageBoxCritical
            ).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setPixmap(self.style().standardPixmap(
                self.style().SP_MessageBoxWarning
            ).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(icon_label)
        
        # 繧ｿ繧､繝医Ν縺ｨ隱ｬ譏・        text_layout = QVBoxLayout()
        
        title_label = QLabel(title_text)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        text_layout.addWidget(desc_label)
        
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 繝｡繝・そ繝ｼ繧ｸ陦ｨ遉ｺ繧ｨ繝ｪ繧｢
        group_box = QGroupBox("繝｡繝・そ繝ｼ繧ｸ隧ｳ邏ｰ")
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)
        
        # 繝・く繧ｹ繝医お繝・ぅ繝・ヨ・郁ｪｭ縺ｿ蜿悶ｊ蟆ら畑・・        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        
        # 繝｡繝・そ繝ｼ繧ｸ繧呈紛蠖｢縺励※陦ｨ遉ｺ
        formatted_messages = []
        for i, msg in enumerate(self.messages, 1):
            # ReVIEW縺ｮ隴ｦ蜻翫Γ繝・そ繝ｼ繧ｸ縺ｮ蠖｢蠑上ｒ隕九ｄ縺吶￥謨ｴ蠖｢
            if "WARN" in msg:
                # 隴ｦ蜻翫Ξ繝吶Ν縺ｨ繝｡繝・そ繝ｼ繧ｸ繧貞・髮｢
                formatted_msg = msg.replace("笞", "").strip()
                formatted_messages.append(f"[{i:3d}] {formatted_msg}")
            else:
                formatted_messages.append(f"[{i:3d}] {msg}")
        
        self.text_edit.setPlainText("\n".join(formatted_messages))
        
        # 繝輔か繝ｳ繝郁ｨｭ螳夲ｼ育ｭ牙ｹ・ヵ繧ｩ繝ｳ繝茨ｼ・        font = QFont("Consolas, Monaco, 'Courier New', monospace")
        font.setPointSize(9)
        self.text_edit.setFont(font)
        
        group_layout.addWidget(self.text_edit)
        layout.addWidget(group_box)
        
        # 邨ｱ險域ュ蝣ｱ
        if len(self.messages) > 1:
            stats_label = QLabel(f"蜷郁ｨ・ {len(self.messages)} 莉ｶ縺ｮ繝｡繝・そ繝ｼ繧ｸ")
            stats_label.setStyleSheet("QLabel { color: #666; }")
            layout.addWidget(stats_label)
        
        # 繝懊ち繝ｳ
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 繧ｯ繝ｪ繝・・繝懊・繝峨↓繧ｳ繝斐・繝懊ち繝ｳ
        self.copy_button = QPushButton("繧ｯ繝ｪ繝・・繝懊・繝峨↓繧ｳ繝斐・")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        # 髢峨§繧九・繧ｿ繝ｳ
        self.close_button = QPushButton("髢峨§繧・)
        self.close_button.clicked.connect(self.accept)
        self.close_button.setDefault(True)
        button_layout.addWidget(self.close_button)
        
        # 繝・ヰ繝・げ・壹・繧ｿ繝ｳ縺ｮ迥ｶ諷九ｒ遒ｺ隱・        print(f"[DEBUG] 繧ｳ繝斐・繝懊ち繝ｳ譛牙柑: {self.copy_button.isEnabled()}")
        print(f"[DEBUG] 髢峨§繧九・繧ｿ繝ｳ譛牙柑: {self.close_button.isEnabled()}")
        
        layout.addLayout(button_layout)
        
        # 髢峨§繧九・繧ｿ繝ｳ縺ｫ繝輔か繝ｼ繧ｫ繧ｹ繧定ｨｭ螳・        self.close_button.setFocus()
        
        # 繧ｹ繧ｿ繧､繝ｫ險ｭ螳・        self.setStyleSheet("""
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
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton {
                min-width: 100px;
                padding: 5px 15px;
            }
        """)
    
    @pyqtSlot()
    def copy_to_clipboard(self):
        """繝｡繝・そ繝ｼ繧ｸ繧偵け繝ｪ繝・・繝懊・繝峨↓繧ｳ繝斐・"""
        try:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(self.text_edit.toPlainText())
            
            # 繝懊ち繝ｳ縺ｮ繝・く繧ｹ繝医ｒ荳譎ら噪縺ｫ螟画峩
            sender = self.sender()
            if sender:
                original_text = sender.text()
                sender.setText("繧ｳ繝斐・縺励∪縺励◆・・)
                sender.setEnabled(False)
                
                # 2遘貞ｾ後↓蜈・↓謌ｻ縺・                from PyQt6.QtCore import QTimer
                QTimer.singleShot(2000, lambda: (
                    sender.setText(original_text),
                    sender.setEnabled(True)
                ))
        except Exception as e:
            print(f"繧ｯ繝ｪ繝・・繝懊・繝峨さ繝斐・繧ｨ繝ｩ繝ｼ: {e}")