#!/usr/bin/env python3
"""Qt6でのQStyleアイコンの正しい使い方を調査"""

from PyQt6.QtWidgets import QApplication, QStyle
import sys

app = QApplication(sys.argv)

# スタイルオブジェクトを取得
style = app.style()

print("=== Qt6 QStyle調査 ===")
print(f"スタイルクラス: {style.__class__.__name__}")
print(f"利用可能な属性:")

# SP_ で始まる属性を探す
for attr in dir(style):
    if attr.startswith('SP_'):
        print(f"  - {attr}")

print("\n=== QStyle.StandardPixmap の内容 ===")
if hasattr(QStyle, 'StandardPixmap'):
    for attr in dir(QStyle.StandardPixmap):
        if not attr.startswith('_'):
            print(f"  - {attr}")
else:
    print("QStyle.StandardPixmap が見つかりません")

print("\n=== 正しい使い方の例 ===")
try:
    # Qt6での正しい方法
    icon = style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
    print(f"✓ style.standardIcon(QStyle.StandardPixmap.SP_DirIcon) -> {icon}")
except Exception as e:
    print(f"✗ エラー: {e}")

# app.exec() は呼ばない（調査のみ）