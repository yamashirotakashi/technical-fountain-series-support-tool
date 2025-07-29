#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Install Dependencies for CodeBlockOverFlowDisposal
PDFplumberとnumpyをユーザー環境にインストール
"""

import subprocess
import sys
import os

def install_with_break_system_packages():
    """システムパッケージを破壊するリスクを承知でインストール"""
    packages = ['pdfplumber', 'numpy']
    
    print("CodeBlockOverFlowDisposal - 依存関係インストール")
    print("=" * 60)
    print("⚠️  警告: 外部管理環境への強制インストールを実行します")
    print("⚠️  WSL環境では通常安全ですが、自己責任で実行してください")
    print("=" * 60)
    
    for package in packages:
        print(f"\n📦 {package} をインストール中...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '--break-system-packages', package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package} インストール成功")
            else:
                print(f"❌ {package} インストール失敗:")
                print(result.stderr)
        except Exception as e:
            print(f"❌ {package} インストールエラー: {e}")
    
    print("\n🔍 インストール確認:")
    for package in packages:
        try:
            if package == 'pdfplumber':
                import pdfplumber
                print(f"✅ {package} インポート成功")
            elif package == 'numpy':
                import numpy
                print(f"✅ {package} インポート成功")
        except ImportError:
            print(f"❌ {package} インポート失敗")

def test_installation():
    """インストール結果をテスト"""
    print("\n🧪 Maximum OCR Detector テスト実行:")
    try:
        import pdfplumber
        import numpy as np
        print("✅ 全依存関係利用可能")
        print("🚀 maximum_ocr_detector.py の実行準備完了")
        return True
    except ImportError as e:
        print(f"❌ 依存関係不足: {e}")
        return False

if __name__ == "__main__":
    install_with_break_system_packages()
    if test_installation():
        print("\n🎯 次のステップ:")
        print("python CodeBlockOverFlowDisposal/maximum_ocr_detector.py [PDF files]")
    else:
        print("\n⚠️  手動インストールが必要な場合があります")
        print("pip install --break-system-packages pdfplumber numpy")