#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tesseract OCR設定テストスクリプト
Tesseractが正しく設定されているか確認
"""

import os
import sys
import subprocess
from pathlib import Path

def test_tesseract():
    print("=== Tesseract OCR設定テスト ===\n")
    
    # 1. 環境変数TESSERACT_CMDの確認
    print("1. 環境変数TESSERACT_CMDの確認:")
    tesseract_cmd = os.environ.get('TESSERACT_CMD')
    if tesseract_cmd:
        print(f"   TESSERACT_CMD = {tesseract_cmd}")
        if Path(tesseract_cmd).exists():
            print("   ✓ ファイルが存在します")
        else:
            print("   ✗ ファイルが見つかりません")
    else:
        print("   ✗ TESSERACT_CMDが設定されていません")
    print()
    
    # 2. システムPATHの確認
    print("2. システムPATHでtesseractを検索:")
    try:
        result = subprocess.run(['where', 'tesseract'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            paths = result.stdout.strip().split('\n')
            for path in paths:
                if path:
                    print(f"   ✓ 見つかりました: {path}")
        else:
            print("   ✗ PATHにtesseractが見つかりません")
    except Exception as e:
        print(f"   ✗ whereコマンドエラー: {e}")
    print()
    
    # 3. 一般的なインストール場所の確認
    print("3. 一般的なインストール場所の確認:")
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"$LOCALAPPDATA\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"$LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe"),
    ]
    
    found_paths = []
    for path in common_paths:
        if Path(path).exists():
            print(f"   ✓ 存在: {path}")
            found_paths.append(path)
        else:
            print(f"   ✗ 不在: {path}")
    print()
    
    # 4. pytesseractの設定確認
    print("4. pytesseractの設定確認:")
    try:
        import pytesseract
        print("   ✓ pytesseractがインポートできました")
        
        # 既存の設定を確認
        current_cmd = getattr(pytesseract.pytesseract, 'tesseract_cmd', None)
        print(f"   現在の設定: {current_cmd}")
        
        # 見つかったパスがあれば設定を試みる
        if found_paths:
            pytesseract.pytesseract.tesseract_cmd = found_paths[0]
            print(f"   設定を更新: {found_paths[0]}")
        elif tesseract_cmd and Path(tesseract_cmd).exists():
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            print(f"   環境変数から設定: {tesseract_cmd}")
        
        # バージョン確認
        try:
            version = pytesseract.get_tesseract_version()
            print(f"   ✓ Tesseractバージョン: {version}")
            print("\n✅ Tesseractは正常に動作しています！")
            return True
        except Exception as e:
            print(f"   ✗ バージョン取得エラー: {e}")
            
    except ImportError:
        print("   ✗ pytesseractがインストールされていません")
        print("   実行: pip install pytesseract")
    except Exception as e:
        print(f"   ✗ エラー: {e}")
    
    print("\n❌ Tesseractの設定に問題があります。")
    print("\n解決方法:")
    print("1. Tesseractをインストール: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. インストール後、環境変数TESSERACT_CMDにtesseract.exeのフルパスを設定")
    print("3. または、このスクリプトを管理者権限で実行")
    
    return False

if __name__ == "__main__":
    # 仮想環境からutils/tesseract_config.pyを使用
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from utils.tesseract_config import configure_tesseract
        print("utils.tesseract_config.configure_tesseract()を実行中...\n")
        configure_tesseract()
    except Exception as e:
        print(f"configure_tesseract()エラー: {e}\n")
    
    success = test_tesseract()
    sys.exit(0 if success else 1)