"""メール処理の抽象化モジュール

異なる変換サービスからのメールを適切に処理するための抽象化レイヤー
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
import re
from utils.logger import get_logger


class EmailProcessor(ABC):
    """メール処理の基底クラス
    
    Purpose別の処理内容:
    
    1. purpose='download' (通常のワークフロー):
       - 必要なURL: ZIP形式のダウンロードURL
       - 成功条件: ZIPファイルが正常にダウンロードできる
       - 失敗条件: ZIPファイルが存在しない、またはダウンロードエラー
       
    2. purpose='error_check' (エラーファイル検知):
       - 必要なURL: PDF形式のダウンロードURL（メール内の最後のPDF URL）
       - 成功条件: PDFファイルが存在し、Basic認証後に正常なPDFが返される
       - 失敗条件: 
         * HTMLエラーページが返される（"ファイルの作成に失敗"等）
         * PDFではないコンテンツが返される
         * 404エラー等でファイルが存在しない
       - 注意: すべてのダウンロードURLにはBasic認証（ep_user/Nn7eUTX5）が必要
    """
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def extract_urls(self, email_body: str) -> Dict[str, str]:
        """
        メール本文からすべての利用可能なURLを抽出
        
        Args:
            email_body: メール本文
            
        Returns:
            URLタイプをキーとした辞書 (例: {'zip': 'http://...', 'pdf': 'http://...'})
        """
        pass
    
    @abstractmethod
    def extract_filename(self, email_body: str) -> Optional[str]:
        """
        メール本文からファイル名を抽出
        
        Args:
            email_body: メール本文
            
        Returns:
            ファイル名
        """
        pass
    
    def get_url_for_purpose(self, urls: Dict[str, str], purpose: str) -> Optional[str]:
        """
        目的に応じたURLを取得
        
        Args:
            urls: extract_urlsで取得したURL辞書
            purpose: 'download' または 'error_check'
            
        Returns:
            適切なURL
        """
        if purpose == 'download':
            return urls.get('zip') or urls.get('pdf')
        elif purpose == 'error_check':
            return urls.get('pdf')
        else:
            raise ValueError(f"Unknown purpose: {purpose}")


class Word2XHTML5EmailProcessor(EmailProcessor):
    """Word2XHTML5サービスからのメール処理"""
    
    def extract_urls(self, email_body: str) -> Dict[str, str]:
        """Word2XHTML5メールからURLを抽出"""
        urls = {}
        
        # ZIPファイルのURL
        zip_patterns = [
            r'http://trial\.nextpublishing\.jp/upload_46tate/do_download\?n=[^\s\n\r<>"]+',
            r'http://trial\.nextpublishing\.jp/rapture/do_download\?n=[^\s\n\r<>"]+',
        ]
        
        for pattern in zip_patterns:
            match = re.search(pattern, email_body)
            if match:
                urls['zip'] = match.group(0)
                self.logger.info(f"ZIP URL抽出: {urls['zip'][:80]}...")
                break
        
        # PDFファイルのURL（複数ある場合は最後のものを使用）
        pdf_pattern = r'http://trial\.nextpublishing\.jp/upload_46tate/do_download_pdf\?n=[^\s\n\r<>"]+'
        pdf_matches = re.findall(pdf_pattern, email_body)
        
        if pdf_matches:
            # 最後のPDF URLを使用（ユーザーの指示により）
            urls['pdf'] = pdf_matches[-1]
            self.logger.info(f"PDF URL抽出（{len(pdf_matches)}個中最後）: {urls['pdf'][:80]}...")
        
        # EPUBファイルのURL
        epub_pattern = r'http://trial\.nextpublishing\.jp/upload_46tate/do_download_epub\?n=[^\s\n\r<>"]+'
        epub_match = re.search(epub_pattern, email_body)
        if epub_match:
            urls['epub'] = epub_match.group(0)
            self.logger.info(f"EPUB URL抽出: {urls['epub'][:80]}...")
        
        # GCFファイルのURL
        gcf_pattern = r'http://trial\.nextpublishing\.jp/upload_46tate/do_download_gcf\?n=[^\s\n\r<>"]+'
        gcf_match = re.search(gcf_pattern, email_body)
        if gcf_match:
            urls['gcf'] = gcf_match.group(0)
            self.logger.info(f"GCF URL抽出: {urls['gcf'][:80]}...")
        
        return urls
    
    def extract_filename(self, email_body: str) -> Optional[str]:
        """Word2XHTML5メールからファイル名を抽出"""
        filename_patterns = [
            # ZIPファイル名のパターン
            r'ファイル名：([^\n\r]+\.zip)',
            r'([^\s]+\.zip)',
            # docxファイル名のパターン
            r'ファイル名：([^\n\r]+\.docx)',
            r'ファイル名：([^\n\r]+)',
            r'ファイル：([^\n\r]+\.docx)',
            r'([^\s]+\.docx)',
            # 実際のメール形式に対応
            r'超原稿用紙\s*\n\s*([^\n\r]+\.docx)',
            r'アップロードしていただいた[^\n]*\n\s*([^\n\r]+\.docx)',
        ]
        
        for pattern in filename_patterns:
            match = re.search(pattern, email_body)
            if match:
                filename = match.group(1).strip()
                self.logger.info(f"ファイル名抽出: {filename}")
                return filename
        
        self.logger.warning("ファイル名が見つかりませんでした")
        return None


class ReVIEWEmailProcessor(EmailProcessor):
    """ReVIEW変換サービスからのメール処理"""
    
    def extract_urls(self, email_body: str) -> Dict[str, str]:
        """ReVIEWメールからURLを抽出"""
        urls = {}
        
        # ReVIEW形式用のダウンロードURL
        review_patterns = [
            r'http://trial\.nextpublishing\.jp/upload_46tate/do_download_review\?n=[^\s\n\r<>"]+',
            r'http://trial\.nextpublishing\.jp/rapture/do_download\?n=[^\s\n\r<>"]+',
        ]
        
        for pattern in review_patterns:
            match = re.search(pattern, email_body)
            if match:
                urls['zip'] = match.group(0)
                self.logger.info(f"ReVIEW ZIP URL抽出: {urls['zip'][:80]}...")
                break
        
        # より一般的なZIPパターン
        if 'zip' not in urls:
            zip_pattern = r'(https?://[^\s<>"{}|\\^`\[\]]+\.zip)'
            zip_match = re.search(zip_pattern, email_body)
            if zip_match:
                urls['zip'] = zip_match.group(0)
                self.logger.info(f"一般ZIP URL抽出: {urls['zip'][:80]}...")
        
        return urls
    
    def extract_filename(self, email_body: str) -> Optional[str]:
        """ReVIEWメールからファイル名を抽出"""
        filename_patterns = [
            r'ファイル名：([^\n\r]+\.zip)',
            r'([^\s]+\.zip)',
            r'ファイル名：([^\n\r]+)',
        ]
        
        for pattern in filename_patterns:
            match = re.search(pattern, email_body)
            if match:
                filename = match.group(1).strip()
                self.logger.info(f"ファイル名抽出: {filename}")
                return filename
        
        self.logger.warning("ファイル名が見つかりませんでした")
        return None


def create_email_processor(service_type: str) -> EmailProcessor:
    """
    サービスタイプに応じたEmailProcessorを作成
    
    Args:
        service_type: 'word2xhtml5' または 'review'
        
    Returns:
        適切なEmailProcessorインスタンス
    """
    if service_type == 'word2xhtml5':
        return Word2XHTML5EmailProcessor()
    elif service_type == 'review':
        return ReVIEWEmailProcessor()
    else:
        raise ValueError(f"Unknown service type: {service_type}")