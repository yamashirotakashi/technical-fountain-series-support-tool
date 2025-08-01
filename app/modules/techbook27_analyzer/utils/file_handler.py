"""
ファイルハンドラーモジュール
単一責任: ファイル操作の抽象化
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional
import logging


logger = logging.getLogger(__name__)


class FileHandler:
    """ファイル操作を管理するクラス"""
    
    def __init__(self):
        """初期化"""
        self.backup_dirs = {"プロファイル除外前", "サイズ修正前", "PNG", "OVER"}
        
    def create_backup(self, source_path: str, backup_type: str) -> Optional[str]:
        """
        ファイルのバックアップを作成
        
        Args:
            source_path: バックアップ元のファイルパス
            backup_type: バックアップタイプ（フォルダ名に使用）
            
        Returns:
            Optional[str]: バックアップ先のパス（失敗時はNone）
        """
        try:
            source = Path(source_path)
            if not source.exists():
                return None
                
            # バックアップディレクトリを作成
            backup_dir = source.parent / backup_type
            backup_dir.mkdir(exist_ok=True)
            
            # バックアップ先パス
            backup_path = backup_dir / source.name
            
            # コピー実行
            shutil.copy2(source, backup_path)
            logger.info(f"バックアップ作成: {backup_path}")
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"バックアップ作成エラー: {source_path} - {str(e)}")
            return None
            
    def create_directory_backup(self, source_dir: str, backup_base: str, 
                              relative_to: Optional[str] = None) -> Optional[str]:
        """
        ディレクトリ構造を保持したバックアップを作成
        
        Args:
            source_dir: バックアップ元のディレクトリ
            backup_base: バックアップベースディレクトリ
            relative_to: 相対パスの基準ディレクトリ
            
        Returns:
            Optional[str]: バックアップ先のパス
        """
        try:
            source = Path(source_dir)
            backup_base_path = Path(backup_base)
            
            # 相対パスを計算
            if relative_to:
                rel_path = source.relative_to(relative_to)
            else:
                rel_path = source.name
                
            # バックアップ先パス
            backup_path = backup_base_path / rel_path
            backup_path.mkdir(parents=True, exist_ok=True)
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"ディレクトリバックアップエラー: {str(e)}")
            return None
            
    def list_files(self, directory: str, extensions: List[str], 
                   exclude_dirs: Optional[List[str]] = None) -> List[Path]:
        """
        指定された拡張子のファイルをリスト化
        
        Args:
            directory: 検索ディレクトリ
            extensions: 対象拡張子のリスト
            exclude_dirs: 除外するディレクトリ名のリスト
            
        Returns:
            List[Path]: ファイルパスのリスト
        """
        if exclude_dirs is None:
            exclude_dirs = list(self.backup_dirs)
            
        files = []
        dir_path = Path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            return files
            
        # 拡張子を小文字に統一
        extensions_lower = [ext.lower() for ext in extensions]
        
        for file_path in dir_path.rglob("*"):
            # 除外ディレクトリのチェック
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
                
            if file_path.is_file() and file_path.suffix.lower() in extensions_lower:
                files.append(file_path)
                
        return files
        
    def safe_delete(self, file_path: str) -> bool:
        """
        ファイルを安全に削除
        
        Args:
            file_path: 削除するファイルのパス
            
        Returns:
            bool: 削除成功フラグ
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                logger.info(f"ファイル削除: {file_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"ファイル削除エラー: {file_path} - {str(e)}")
            return False
            
    def get_file_info(self, file_path: str) -> dict:
        """
        ファイル情報を取得
        
        Args:
            file_path: ファイルパス
            
        Returns:
            dict: ファイル情報
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {}
                
            stat = path.stat()
            return {
                'name': path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': path.suffix,
                'parent': str(path.parent)
            }
            
        except Exception as e:
            logger.error(f"ファイル情報取得エラー: {file_path} - {str(e)}")
            return {}