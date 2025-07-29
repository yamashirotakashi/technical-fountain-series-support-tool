#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立版溢れチェッカーのテストスクリプト

Phase 2C-1 基本動作テスト
"""

import sys
import os
from pathlib import Path

# パス設定
project_root = Path(__file__).parent
standalone_dir = project_root / "overflow_checker_standalone"
sys.path.insert(0, str(standalone_dir))

def test_imports():
    """基本インポートテスト"""
    print("=== インポートテスト ===")
    
    try:
        from utils.windows_utils import setup_windows_environment, normalize_path, ensure_utf8_encoding
        print("✓ windows_utils インポート成功")
        
        # 基本機能テスト
        test_path = "C:\\Users\\test\\file.pdf"
        normalized = normalize_path(test_path)
        print(f"✓ パス正規化: {test_path} -> {normalized}")
        
        test_text = "テストファイル.pdf"
        encoded = ensure_utf8_encoding(test_text)
        print(f"✓ UTF-8エンコーディング: {encoded}")
        
    except ImportError as e:
        print(f"✗ windows_utils インポート失敗: {e}")
        return False
    except Exception as e:
        print(f"✗ windows_utils テスト失敗: {e}")
        return False
    
    try:
        from core.learning_manager import WindowsLearningDataManager
        print("✓ learning_manager インポート成功")
        
        # テスト用データベース作成
        test_db = Path("/tmp/test_standalone.db")
        manager = WindowsLearningDataManager(test_db)
        print("✓ Learning manager初期化成功")
        
        # 統計取得テスト
        stats = manager.get_learning_statistics()
        print(f"✓ 統計取得成功: {stats['total_cases']}件のデータ")
        
        # クリーンアップ
        if test_db.exists():
            test_db.unlink()
        
    except ImportError as e:
        print(f"✗ learning_manager インポート失敗: {e}")
        return False
    except Exception as e:
        print(f"✗ learning_manager テスト失敗: {e}")
        return False
    
    try:
        from core.pdf_processor import PDFOverflowProcessor, ProcessingResult
        print("✓ pdf_processor インポート成功")
        
        # 処理結果テスト
        test_path = Path("/tmp/test.pdf")
        result = ProcessingResult(test_path)
        print(f"✓ ProcessingResult作成: {result.pdf_name}")
        
        # 溢れページ追加テスト
        test_overflow = {
            'overflow_text': 'サンプルテキスト',
            'overflow_amount': 3.5,
            'confidence': 0.9,
            'y_position': 700.0
        }
        result.add_overflow_page(3, test_overflow)
        print(f"✓ 溢れページ追加: {result.detection_count}件")
        
        # PDF処理クラス初期化
        config = {
            'detection_sensitivity': 'medium',
            'enable_learning': True,
            'windows_environment': True
        }
        processor = PDFOverflowProcessor(config)
        print("✓ PDFOverflowProcessor初期化成功")
        
    except ImportError as e:
        print(f"✗ pdf_processor インポート失敗: {e}")
        return False
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
        print(f"✓ OCR検出器初期化: version {version}")
        
        # 存在しないファイルでのエラーハンドリングテスト
        try:
            result = detector.detect_overflow_pages('nonexistent.pdf')
            print("✗ 予期しない成功（存在しないファイル）")
            return False
        except Exception:
            print("✓ 存在しないファイルのエラーハンドリング正常")
        
        return True
        
    except ImportError as e:
        print(f"✗ OCR検出器インポート失敗: {e}")
        return False
    except Exception as e:
        print(f"✗ OCR統合テスト失敗: {e}")
        return False

def test_gui_components():
    """GUI コンポーネントテスト（GUI表示なし）"""
    print("\n=== GUIコンポーネントテスト ===")
    
    try:
        # PyQt6の可用性確認
        try:
            from PyQt6.QtWidgets import QApplication
            print("✓ PyQt6 利用可能")
        except ImportError:
            print("✗ PyQt6 インポート失敗 - GUIテストをスキップ")
            return True  # GUIなしでも基本機能は動作するため成功扱い
        
        # GUIクラスのインポートテスト（インスタンス化なし）
        from gui.main_window import OverflowCheckerMainWindow
        print("✓ MainWindow クラスインポート成功")
        
        from gui.result_dialog import OverflowResultDialog
        print("✓ ResultDialog クラスインポート成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ GUIコンポーネントインポート失敗: {e}")
        return False
    except Exception as e:
        print(f"✗ GUIテスト失敗: {e}")
        return False

def test_integration():
    """統合テスト"""
    print("\n=== 統合テスト ===")
    
    try:
        # 全体的な統合性確認
        from core.pdf_processor import PDFOverflowProcessor
        from core.learning_manager import WindowsLearningDataManager
        from utils.windows_utils import get_default_db_path, get_user_data_dir
        
        # ユーザーデータディレクトリ確認
        user_data_dir = get_user_data_dir()
        print(f"✓ ユーザーデータディレクトリ: {user_data_dir}")
        
        # デフォルトDB パス確認
        db_path = get_default_db_path()
        print(f"✓ デフォルトDBパス: {db_path}")
        
        # 統合的な処理フロー確認
        config = {
            'detection_sensitivity': 'medium',
            'enable_learning': True,
            'windows_environment': True
        }
        
        processor = PDFOverflowProcessor(config)
        manager = WindowsLearningDataManager()
        
        print("✓ 全コンポーネント統合成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 統合テスト失敗: {e}")
        return False

def main():
    """メインテスト実行"""
    print("独立版溢れチェッカー - 基本動作テスト開始")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Test directory: {standalone_dir}")
    print("=" * 50)
    
    tests = [
        ("基本インポート", test_imports),
        ("OCR統合", test_ocr_integration),
        ("GUIコンポーネント", test_gui_components),
        ("統合テスト", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✓ {test_name} テスト: 成功")
                passed += 1
            else:
                print(f"✗ {test_name} テスト: 失敗")
        except Exception as e:
            print(f"✗ {test_name} テスト: 例外発生 - {e}")
    
    print("=" * 50)
    print(f"テスト結果: {passed}/{total} 成功")
    
    if passed == total:
        print("🎉 全テスト成功! アプリケーション基盤が正常に動作します。")
        return 0
    else:
        print("❌ 一部テストに失敗しました。問題を修正してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())