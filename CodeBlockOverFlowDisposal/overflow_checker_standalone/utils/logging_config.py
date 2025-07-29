# -*- coding: utf-8 -*-
"""
ログ設定の統一管理
デバッグログを抑制し、必要な情報のみを出力
"""

import logging
import os

def configure_logging():
    """アプリケーション全体のログ設定"""
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # pdfplumberのログを抑制
    logging.getLogger('pdfplumber').setLevel(logging.WARNING)
    logging.getLogger('pdfminer').setLevel(logging.WARNING)
    logging.getLogger('pdfminer.pdfparser').setLevel(logging.WARNING)
    logging.getLogger('pdfminer.pdfdocument').setLevel(logging.WARNING)
    logging.getLogger('pdfminer.pdfpage').setLevel(logging.WARNING)
    logging.getLogger('pdfminer.pdfinterp').setLevel(logging.WARNING)
    logging.getLogger('pdfminer.converter').setLevel(logging.WARNING)
    logging.getLogger('pdfminer.cmapdb').setLevel(logging.WARNING)
    logging.getLogger('pdfminer.layout').setLevel(logging.WARNING)
    
    # PyPDF2のログを抑制
    logging.getLogger('PyPDF2').setLevel(logging.WARNING)
    
    # PILのログを抑制
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    # 環境変数の設定も確認
    os.environ['PDFPLUMBER_LOGGING'] = 'WARNING'
    os.environ['PYPDF_LOGLEVEL'] = 'WARNING'