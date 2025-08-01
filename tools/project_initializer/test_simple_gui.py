"""
最小限のPyQt6 GUIテスト
"""
import sys
import os

print("Starting test GUI...")
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt6.QtCore import Qt
    print("PyQt6 imported successfully")
    
    app = QApplication(sys.argv)
    print("QApplication created")
    
    window = QMainWindow()
    window.setWindowTitle("Test GUI")
    window.setGeometry(100, 100, 400, 300)
    
    label = QLabel("PyQt6 is working!", window)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setCentralWidget(label)
    
    window.show()
    print("Window shown")
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")