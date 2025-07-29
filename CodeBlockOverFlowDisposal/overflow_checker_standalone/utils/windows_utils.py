# -*- coding: utf-8 -*-
"""
Windows環境対応ユーティリティ

PowerShell環境での文字コード、BOM、パス処理の問題を解決
"""

import os
import sys
import locale
from pathlib import Path
import logging

def setup_windows_environment():
    """Windows環境の初期設定"""
    if sys.platform == 'win32':
        # UTF-8コードページ設定
        try:
            os.system('chcp 65001')  # UTF-8 code page
        except Exception as e:
            logging.warning(f"コードページ設定に失敗: {e}")
        
        # ロケール設定
        try:
            locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'Japanese_Japan.932')
            except Exception as e:
                logging.warning(f"ロケール設定に失敗: {e}")

def normalize_path(path_str: str) -> Path:
    """Windowsパスの正規化
    
    Args:
        path_str: パス文字列
        
    Returns:
        正規化されたPathオブジェクト
    """
    # バックスラッシュをスラッシュに統一
    normalized = path_str.replace('\\', '/')
    return Path(normalized).resolve()

def ensure_utf8_encoding(text: str) -> str:
    """文字列のUTF-8エンコーディング確保
    
    Args:
        text: 処理する文字列またはバイト列
        
    Returns:
        UTF-8文字列
    """
    if isinstance(text, bytes):
        try:
            return text.decode('utf-8')
        except UnicodeDecodeError:
            # Shift-JISでのデコードを試行
            try:
                return text.decode('shift-jis', errors='ignore')
            except:
                return text.decode('utf-8', errors='ignore')
    return text

def is_windows() -> bool:
    """Windows環境かどうかを判定
    
    Returns:
        Windows環境の場合True
    """
    return sys.platform == 'win32'

def get_user_data_dir() -> Path:
    """ユーザーデータディレクトリを取得
    
    Returns:
        ユーザーデータディレクトリのPath
    """
    if is_windows():
        # Windows: %APPDATA%/OverflowChecker
        appdata = os.environ.get('APPDATA', Path.home())
        user_data = Path(appdata) / "OverflowChecker"
    else:
        # Unix-like: ~/.overflow_checker
        user_data = Path.home() / ".overflow_checker"
    
    user_data.mkdir(parents=True, exist_ok=True)
    return user_data

def get_default_config_path() -> Path:
    """デフォルト設定ファイルパスを取得
    
    Returns:
        設定ファイルのPath
    """
    return get_user_data_dir() / "config.json"

def get_default_db_path() -> Path:
    """デフォルトデータベースファイルパスを取得
    
    Returns:
        データベースファイルのPath
    """
    return get_user_data_dir() / "learning_data.db"

def safe_file_write(file_path: Path, content: str, encoding: str = 'utf-8'):
    """安全なファイル書き込み（Windows BOM対応）
    
    Args:
        file_path: 書き込み先ファイルパス
        content: 書き込み内容
        encoding: エンコーディング（デフォルト: utf-8）
    """
    try:
        # UTF-8 BOM付きで書き込み（Windows PowerShell対応）
        if is_windows() and encoding == 'utf-8':
            with open(file_path, 'w', encoding='utf-8-sig', newline='\n') as f:
                f.write(content)
        else:
            with open(file_path, 'w', encoding=encoding, newline='\n') as f:
                f.write(content)
    except Exception as e:
        logging.error(f"ファイル書き込みエラー ({file_path}): {e}")
        raise

def safe_file_read(file_path: Path, encoding: str = 'utf-8') -> str:
    """安全なファイル読み込み（Windows BOM対応）
    
    Args:
        file_path: 読み込み元ファイルパス
        encoding: エンコーディング（デフォルト: utf-8）
        
    Returns:
        ファイル内容
    """
    try:
        # BOM付きUTF-8を試行
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            # 通常のUTF-8を試行
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Shift-JISを試行
            with open(file_path, 'r', encoding='shift-jis') as f:
                return f.read()
    except Exception as e:
        logging.error(f"ファイル読み込みエラー ({file_path}): {e}")
        raise