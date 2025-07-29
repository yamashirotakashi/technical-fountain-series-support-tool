#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立版溢れチェッカーの簡易テストスクリプト

絶対インポートを使用した基本動作確認
"""

import sys
import os
from pathlib import Path

# パス設定
project_root = Path(__file__).parent
standalone_dir = project_root / "overflow_checker_standalone"
sys.path.insert(0, str(standalone_dir))

def test_core_modules():
    """コアモジュールの基本テスト（絶対インポート）"""
    print("=== コアモジュールテスト ===")
    
    # Windows utilities
    try:
        import utils.windows_utils as wu
        print("✓ windows_utils インポート成功")
        
        # 基本機能テスト
        test_path = "C:\\Users\\test\\file.pdf"
        normalized = wu.normalize_path(test_path)
        print(f"✓ パス正規化テスト成功")
        
        # エンコーディングテスト
        test_text = "テストファイル.pdf"
        encoded = wu.ensure_utf8_encoding(test_text)
        print(f"✓ UTF-8エンコーディングテスト成功")
        
        # データディレクトリテスト
        data_dir = wu.get_user_data_dir()
        print(f"✓ ユーザーデータディレクトリ: {data_dir}")
        
    except Exception as e:
        print(f"✗ windows_utils テスト失敗: {e}")
        return False
    
    # Learning manager  
    try:
        import core.learning_manager as lm
        print("✓ learning_manager インポート成功")
        
        # テスト用データベース
        test_db_path = Path("/tmp/test_simple.db")
        manager = lm.WindowsLearningDataManager(test_db_path)
        print("✓ Learning manager初期化成功")
        
        # 統計取得
        stats = manager.get_learning_statistics()
        print(f"✓ 統計取得成功: {stats['total_cases']}件")
        
        # テスト学習データ保存
        test_data = {
            'pdf_path': '/tmp/test.pdf',
            'pdf_name': 'test.pdf',
            'detected_pages': [1, 3, 5],
            'confirmed_pages': [1, 3],
            'additional_pages': [7],
            'false_positives': [5],
            'user_notes': 'テストデータ',
            'app_version': '1.0.0',
            'processing_time': 1.5
        }
        
        success = manager.save_learning_data(test_data)
        if success:
            print("✓ 学習データ保存成功")
        else:
            print("✗ 学習データ保存失敗")
        
        # 統計再取得
        updated_stats = manager.get_learning_statistics()
        print(f"✓ 更新後統計: {updated_stats['total_cases']}件")
        
        # クリーンアップ
        if test_db_path.exists():
            test_db_path.unlink()
            
    except Exception as e:
        print(f"✗ learning_manager テスト失敗: {e}")
        return False
    
    # PDF processor
    try:
        import core.pdf_processor as pp
        print("✓ pdf_processor インポート成功")
        
        # ProcessingResult テスト
        test_pdf_path = Path("/tmp/test.pdf")
        result = pp.ProcessingResult(test_pdf_path)
        print(f"✓ ProcessingResult作成: {result.pdf_name}")
        
        # 溢れページ追加テスト
        overflow_data = {
            'overflow_text': 'サンプル溢れテキスト',
            'overflow_amount': 4.2,
            'confidence': 0.88,
            'y_position': 710.5
        }
        result.add_overflow_page(2, overflow_data)
        print(f"✓ 溢れページ追加: {result.detection_count}件")
        
        # サマリー取得
        summary = result.get_summary()
        print(f"✓ サマリー取得: {summary['overflow_count']}件の溢れ")
        
        # PDF processor初期化
        config = {
            'detection_sensitivity': 'medium',
            'enable_learning': True,
            'windows_environment': False  # Linux環境
        }
        processor = pp.PDFOverflowProcessor(config)
        print("✓ PDFOverflowProcessor初期化成功")
        
    except Exception as e:
        print(f"✗ pdf_processor テスト失敗: {e}")
        return False
    
    return True

def test_ocr_integration():
    """OCR検出器統合テスト"""
    print("\n=== OCR統合テスト ===")
    
    try:
        # 既存のOCR検出器をインポート
        sys.path.append(str(project_root))
        from overflow_detection_lib.core.detector import OCRBasedOverflowDetector
        print("✓ OCR検出器インポート成功")
        
        detector = OCRBasedOverflowDetector()
        version = getattr(detector, 'version', 'unknown')
        integration_status = getattr(detector, 'integration_status', 'unknown')
        print(f"✓ OCR検出器初期化: version {version}, status {integration_status}")
        
        # エラーハンドリング確認
        try:
            result = detector.detect_overflow_pages('nonexistent.pdf')
            print("✗ 予期しない成功（存在しないファイル）")
            return False
        except Exception:
            print("✓ 存在しないファイルのエラーハンドリング正常")
        
        return True
        
    except Exception as e:
        print(f"✗ OCR統合テスト失敗: {e}")
        return False

def test_package_structure():
    """パッケージ構造テスト"""
    print("\n=== パッケージ構造テスト ===")
    
    required_files = [
        standalone_dir / "__init__.py",
        standalone_dir / "main.py",
        standalone_dir / "utils" / "__init__.py",
        standalone_dir / "utils" / "windows_utils.py",
        standalone_dir / "core" / "__init__.py",
        standalone_dir / "core" / "pdf_processor.py",
        standalone_dir / "core" / "learning_manager.py",
        standalone_dir / "gui" / "__init__.py",
        standalone_dir / "gui" / "main_window.py",
        standalone_dir / "gui" / "result_dialog.py",
        standalone_dir / "requirements.txt",
        standalone_dir / "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✓ ファイル存在: {file_path.name}")
    
    if missing_files:
        print("✗ 不足ファイル:")
        for missing in missing_files:
            print(f"  - {missing}")
        return False
    
    print("✓ 全必要ファイルが存在")
    return True

def main():
    """メインテスト実行"""
    print("独立版溢れチェッカー - 簡易テスト開始")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Standalone directory: {standalone_dir}")
    print("=" * 60)
    
    tests = [
        ("パッケージ構造", test_package_structure),
        ("コアモジュール", test_core_modules),
        ("OCR統合", test_ocr_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n--- {test_name}テスト ---")
            if test_func():
                print(f"✅ {test_name} テスト: 成功")
                passed += 1
            else:
                print(f"❌ {test_name} テスト: 失敗")
        except Exception as e:
            print(f"❌ {test_name} テスト: 例外発生 - {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 60)
    print(f"テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 全テスト成功! アプリケーション基盤が正常に動作します。")
        print("\n次のステップ:")
        print("1. PyQt6をインストール: pip install PyQt6")
        print("2. Tesseract OCRをインストール")
        print("3. Windows PowerShell環境での実行テスト")
        return 0
    else:
        print("❌ 一部テストに失敗しました。問題を修正してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())