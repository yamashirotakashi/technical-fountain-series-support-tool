# -*- coding: utf-8 -*-
"""
Tesseract OCR設定ユーティリティ
Windows環境でのTesseractパス設定を管理
"""

import os
import sys
import logging
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)

def configure_tesseract():
    """Tesseract OCRのパスを設定"""
    
    # Windows環境の場合
    if sys.platform == 'win32':
        # まず環境変数TESSERACT_CMDをチェック
        env_path = os.environ.get('TESSERACT_CMD')
        if env_path and Path(env_path).exists():
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = env_path
            logger.info(f"環境変数TESSERACT_CMDからTesseractパスを設定: {env_path}")
            # 環境変数PATHにも追加
            tesseract_dir = os.path.dirname(env_path)
            if tesseract_dir not in os.environ['PATH']:
                os.environ['PATH'] = tesseract_dir + os.pathsep + os.environ['PATH']
            return True
        
        # 一般的なインストール先を試行
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Tesseract-OCR\tesseract.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
        ]
        
        # 環境変数を展開
        possible_paths = [os.path.expandvars(path) for path in possible_paths]
        
        # whereコマンドでシステムパスからも探す
        try:
            result = subprocess.run(['where', 'tesseract'], capture_output=True, text=True)
            if result.returncode == 0:
                where_path = result.stdout.strip().split('\n')[0]
                if where_path and Path(where_path).exists():
                    possible_paths.insert(0, where_path)
                    logger.info(f"whereコマンドでTesseractを検出: {where_path}")
        except Exception as e:
            logger.debug(f"whereコマンド実行エラー: {e}")
        
        # 存在するパスを探す
        tesseract_path = None
        for path in possible_paths:
            logger.debug(f"Tesseractパスチェック: {path}")
            if Path(path).exists():
                tesseract_path = path
                logger.info(f"Tesseractが見つかりました: {path}")
                break
        
        if tesseract_path:
            # pytesseractに直接パスを設定
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
            # 環境変数PATHにディレクトリを追加
            tesseract_dir = os.path.dirname(tesseract_path)
            if tesseract_dir not in os.environ['PATH']:
                os.environ['PATH'] = tesseract_dir + os.pathsep + os.environ['PATH']
                logger.info(f"PATHに追加: {tesseract_dir}")
            
            # 環境変数TESSERACT_CMDも設定（他のプロセスのため）
            os.environ['TESSERACT_CMD'] = tesseract_path
            
            logger.info(f"Tesseract OCRパスを設定: {tesseract_path}")
            
            # 実際に動作するか確認
            try:
                version = pytesseract.get_tesseract_version()
                logger.info(f"Tesseract動作確認成功: バージョン {version}")
                return True
            except Exception as e:
                logger.error(f"Tesseractの動作確認に失敗: {e}")
                return False
        else:
            logger.error("Tesseract OCRが見つかりません。")
            logger.error("インストール確認方法:")
            logger.error("1. コマンドプロンプトで 'where tesseract' を実行")
            logger.error("2. インストールされていない場合: https://github.com/UB-Mannheim/tesseract/wiki")
            logger.error("3. 環境変数TESSERACT_CMDにtesseract.exeのフルパスを設定")
            return False
    
    # Windows以外の環境
    return True

def check_tesseract_installation():
    """Tesseractのインストール状態を確認"""
    try:
        import pytesseract
        
        # まずパス設定を試行
        if not configure_tesseract():
            return False
        
        # バージョン確認
        version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract OCR検出成功: バージョン {version}")
        return True
        
    except Exception as e:
        logger.error(f"Tesseract OCR確認エラー: {e}")
        return False