"""シンプルな警告ダイアログ（QMessageBoxベース）"""
from PyQt6.QtWidgets import QMessageBox, QTextEdit, QVBoxLayout
from PyQt6.QtCore import Qt

def show_warning_dialog(parent, messages, result_type="warning"):
    """
    シンプルな警告ダイアログを表示
    
    Args:
        parent: 親ウィジェット
        messages: メッセージのリスト
        result_type: "warning" または "error"
    """
    # メッセージボックスを作成
    msg_box = QMessageBox(parent)
    
    # タイトルとアイコンを設定
    if result_type == "error":
        msg_box.setWindowTitle("変換エラー")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("変換処理が失敗しました")
    else:
        msg_box.setWindowTitle("変換警告")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("変換処理は成功しましたが、警告があります")
    
    # 詳細メッセージを設定
    detailed_text = "\n".join([f"[{i+1:3d}] {msg}" for i, msg in enumerate(messages)])
    msg_box.setDetailedText(detailed_text)
    
    # ボタンを設定
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
    
    # モーダルで表示
    msg_box.exec()