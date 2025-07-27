#!/usr/bin/env python3
"""
Slack PDF投稿機能のテストケース
仕様書駆動開発のためのテストファースト実装
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile
from pathlib import Path

# テスト対象のインポート
from src.slack_pdf_poster import SlackPDFPoster


class TestSlackPDFPoster(unittest.TestCase):
    """SlackPDFPosterクラスのテストケース"""
    
    def setUp(self):
        """テストの初期設定"""
        self.poster = SlackPDFPoster()
    
    def test_extract_channel_number_valid_n_code(self):
        """正常なN番号から4桁を抽出できること"""
        test_cases = [
            ("N01234", "1234"),
            ("n01234", "1234"),
            ("N12345", "2345"),  # 5桁以上の場合は下4桁
            ("N00001", "0001"),  # ゼロパディング保持
        ]
        
        for n_code, expected in test_cases:
            result = self.poster.extract_channel_number(n_code)
            self.assertEqual(result, expected, f"Failed for {n_code}")
    
    def test_extract_channel_number_invalid_input(self):
        """不正な入力に対して適切にエラーハンドリングすること"""
        invalid_inputs = [
            "",            # 空文字
            "N123",        # 4桁未満
            "1234",        # Nなし
            "NABCD",       # 数字以外
        ]
        
        for invalid_input in invalid_inputs:
            with self.assertRaises(ValueError):
                self.poster.extract_channel_number(invalid_input)
        
        # Noneは別途テスト
        with self.assertRaises((ValueError, TypeError)):
            self.poster.extract_channel_number(None)
    
    def test_find_slack_channel_found(self):
        """チャネルが見つかる場合のテスト"""
        mock_slack_integration = Mock()
        mock_slack_integration.get_bot_channels.return_value = [
            {"name": "n1234-test-book"},
            {"name": "n5678-another-book"},
            {"name": "general"},
        ]
        
        self.poster.slack_integration = mock_slack_integration
        result = self.poster.find_slack_channel("1234")
        self.assertEqual(result, "n1234-test-book")
    
    def test_find_slack_channel_not_found(self):
        """チャネルが見つからない場合のテスト"""
        mock_slack_integration = Mock()
        mock_slack_integration.get_bot_channels.return_value = [
            {"name": "n5678-another-book"},
            {"name": "general"},
        ]
        
        self.poster.slack_integration = mock_slack_integration
        result = self.poster.find_slack_channel("1234")
        self.assertIsNone(result)
    
    def test_find_pdf_file_single_file(self):
        """PDFファイルが1つある場合のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # N番号フォルダ構造を作成
            n_folder = Path(tmpdir) / "N01234"
            out_folder = n_folder / "out"
            out_folder.mkdir(parents=True)
            
            # PDFファイルを作成
            pdf_path = out_folder / "test_book.pdf"
            pdf_path.write_text("dummy pdf content")
            
            result = self.poster.find_pdf_file(str(n_folder))
            self.assertEqual(result, str(pdf_path))
    
    def test_find_pdf_file_multiple_files(self):
        """複数のPDFファイルがある場合、最新のものを選択すること"""
        with tempfile.TemporaryDirectory() as tmpdir:
            n_folder = Path(tmpdir) / "N01234"
            out_folder = n_folder / "out"
            out_folder.mkdir(parents=True)
            
            # 複数のPDFファイルを作成（タイムスタンプを変えて）
            import time
            pdf1 = out_folder / "old.pdf"
            pdf1.write_text("old")
            time.sleep(0.1)
            
            pdf2 = out_folder / "new.pdf"
            pdf2.write_text("new")
            
            result = self.poster.find_pdf_file(str(n_folder))
            self.assertEqual(result, str(pdf2))
    
    def test_find_pdf_file_not_found(self):
        """PDFファイルが見つからない場合のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            n_folder = Path(tmpdir) / "N01234"
            n_folder.mkdir()
            
            result = self.poster.find_pdf_file(str(n_folder))
            self.assertIsNone(result)
    
    def test_show_confirmation_dialog_approved(self):
        """確認ダイアログでOKが押された場合のテスト"""
        # このテストはGUI部分なので、統合テストで実行
        pass
    
    def test_post_to_slack_success(self):
        """Slack投稿が成功する場合のテスト"""
        mock_slack_integration = Mock()
        mock_slack_integration.post_pdf_to_channel.return_value = {
            "success": True,
            "channel": "n1234-test-book",
            "file_id": "F12345",
            "permalink": "https://slack.com/..."
        }
        
        self.poster.slack_integration = mock_slack_integration
        success, result_msg = self.poster.post_to_slack(
            "/path/to/test.pdf",
            "n1234-test-book",
            "テストメッセージ"
        )
        
        self.assertTrue(success)
    
    def test_post_to_slack_failure(self):
        """Slack投稿が失敗する場合のテスト"""
        mock_slack_integration = Mock()
        mock_slack_integration.post_pdf_to_channel.return_value = {
            "success": False,
            "error": "Bot is not in channel",
            "action_required": "Bot招待が必要",
            "instruction": "招待手順..."
        }
        
        self.poster.slack_integration = mock_slack_integration
        success, error_msg = self.poster.post_to_slack(
            "/path/to/test.pdf",
            "n1234-test-book",
            "テストメッセージ"
        )
        
        self.assertFalse(success)
        self.assertIn("Bot is not in channel", error_msg)
    
    def test_integration_workflow(self):
        """統合ワークフローのテスト"""
        # 1. N番号入力
        # 2. チャネル検索
        # 3. PDFファイル検索
        # 4. 確認ダイアログ
        # 5. Slack投稿
        # この一連の流れをテスト
        pass


class TestPDFPostDialog(unittest.TestCase):
    """PDF投稿確認ダイアログのテストケース"""
    
    def test_dialog_initialization(self):
        """ダイアログの初期化テスト"""
        # dialog = PDFPostDialog(
        #     "/path/to/test.pdf",
        #     "n1234-test-book",
        #     "デフォルトメッセージ"
        # )
        # 
        # self.assertEqual(dialog.pdf_path, "/path/to/test.pdf")
        # self.assertEqual(dialog.channel, "n1234-test-book")
        # self.assertEqual(dialog.message_edit.text(), "デフォルトメッセージ")
        pass
    
    def test_dialog_message_editing(self):
        """メッセージ編集のテスト"""
        # dialog = PDFPostDialog(
        #     "/path/to/test.pdf",
        #     "n1234-test-book",
        #     "デフォルトメッセージ"
        # )
        # 
        # dialog.message_edit.setText("編集後のメッセージ")
        # self.assertEqual(dialog.get_message(), "編集後のメッセージ")
        pass


if __name__ == "__main__":
    unittest.main()