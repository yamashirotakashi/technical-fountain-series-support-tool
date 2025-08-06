"""パス解決ユーティリティ - 開発環境とEXE環境の両対応"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Optional

from utils.logger import get_logger


class PathResolver:
    """開発環境とEXE環境の両方で動作するパス解決クラス"""
    
    _logger = None
    _is_exe = getattr(sys, 'frozen', False)
    _base_path = None
    _user_dir = None
    
    @classmethod
    def _get_logger(cls):
        """ロガーの遅延初期化"""
        if cls._logger is None:
            cls._logger = get_logger(__name__)
        return cls._logger
    
    @classmethod
    def is_exe_environment(cls) -> bool:
        """EXE環境かどうかを判定"""
        return cls._is_exe
    
    @classmethod
    def get_base_path(cls) -> Path:
        """
        アプリケーションのベースパスを取得
        
        Returns:
            開発環境: プロジェクトルート
            EXE環境: 実行ファイルのディレクトリ
        """
        if cls._base_path is None:
            if cls._is_exe:
                # EXE環境
                cls._base_path = Path(sys.executable).parent
            else:
                # 開発環境 - utils/path_resolver.pyから2階層上がプロジェクトルート
                cls._base_path = Path(__file__).parent.parent
            
            cls._get_logger().debug(f"Base path: {cls._base_path}")
        
        return cls._base_path
    
    @classmethod
    def get_user_dir(cls) -> Path:
        """
        ユーザー専用ディレクトリを取得（書き込み可能）
        
        Returns:
            ~/.techzip ディレクトリ
        """
        if cls._user_dir is None:
            # Windows環境とWSL環境を判別
            if os.name == 'nt':
                # Windows環境
                cls._user_dir = Path.home() / '.techzip'
            else:
                # WSL/Linux環境: Windows側のユーザーディレクトリを使用
                windows_user = os.environ.get('USER', 'tky99')
                windows_home = Path(f'/mnt/c/Users/{windows_user}')
                if windows_home.exists():
                    cls._user_dir = windows_home / '.techzip'
                else:
                    # フォールバック
                    cls._user_dir = Path.home() / '.techzip'
            
            # ディレクトリが存在しない場合は作成
            if not cls._user_dir.exists():
                cls._user_dir.mkdir(parents=True, exist_ok=True)
                cls._get_logger().info(f"Created user directory: {cls._user_dir}")
        
        return cls._user_dir
    
    @classmethod
    def get_config_path(cls, prefer_user_dir: bool = True) -> Path:
        """
        設定ファイルディレクトリのパスを取得
        
        Args:
            prefer_user_dir: EXE環境でユーザーディレクトリを優先するか
            
        Returns:
            設定ファイルディレクトリのパス
        """
        if cls._is_exe and prefer_user_dir:
            # EXE環境: ユーザーディレクトリ優先
            user_config = cls.get_user_dir() / 'config'
            exe_config = cls.get_base_path() / 'config'
            
            # ユーザーディレクトリが存在する、または作成可能な場合
            if user_config.exists():
                cls._get_logger().debug(f"Using user config directory: {user_config}")
                return user_config
            else:
                # ユーザーディレクトリを作成
                try:
                    user_config.mkdir(parents=True, exist_ok=True)
                    cls._get_logger().info(f"Created user config directory: {user_config}")
                    
                    # EXEディレクトリから初期ファイルをコピー
                    if exe_config.exists():
                        cls._copy_initial_configs(exe_config, user_config)
                    
                    return user_config
                except Exception as e:
                    cls._get_logger().warning(f"Failed to create user config directory: {e}")
                    # フォールバック: EXEディレクトリ
                    return exe_config
        else:
            # 開発環境またはユーザーディレクトリを使わない場合
            return cls.get_base_path() / 'config'
    
    @classmethod
    def get_logs_path(cls) -> Path:
        """
        ログディレクトリのパスを取得（書き込み可能）
        
        Returns:
            ログディレクトリのパス
        """
        if cls._is_exe:
            # EXE環境: 常にユーザーディレクトリ（書き込み権限のため）
            logs_dir = cls.get_user_dir() / 'logs'
        else:
            # 開発環境
            logs_dir = cls.get_base_path() / 'logs'
        
        # ディレクトリが存在しない場合は作成
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True, exist_ok=True)
            cls._get_logger().info(f"Created logs directory: {logs_dir}")
        
        return logs_dir
    
    @classmethod
    def get_temp_path(cls) -> Path:
        """
        一時ファイルディレクトリのパスを取得
        
        Returns:
            一時ファイルディレクトリのパス
        """
        if cls._is_exe:
            # EXE環境: ユーザーディレクトリ
            temp_dir = cls.get_user_dir() / 'temp'
        else:
            # 開発環境
            temp_dir = cls.get_base_path() / 'temp'
        
        # ディレクトリが存在しない場合は作成
        if not temp_dir.exists():
            temp_dir.mkdir(parents=True, exist_ok=True)
            cls._get_logger().debug(f"Created temp directory: {temp_dir}")
        
        return temp_dir
    
    @classmethod
    def resolve_config_file(cls, filename: str, prefer_user_dir: bool = True) -> Optional[Path]:
        """
        設定ファイルのパスを解決
        
        Args:
            filename: ファイル名
            prefer_user_dir: EXE環境でユーザーディレクトリを優先するか
            
        Returns:
            存在するファイルのパス、見つからない場合はNone
        """
        config_dir = cls.get_config_path(prefer_user_dir)
        file_path = config_dir / filename
        
        if file_path.exists():
            return file_path
        
        # EXE環境でユーザーディレクトリにない場合、EXEディレクトリも確認
        if cls._is_exe and prefer_user_dir:
            exe_config = cls.get_base_path() / 'config' / filename
            if exe_config.exists():
                cls._get_logger().debug(f"Found config file in EXE directory: {exe_config}")
                return exe_config
        
        cls._get_logger().warning(f"Config file not found: {filename}")
        return None
    
    @classmethod
    def ensure_file_exists(cls, file_path: Path, template_content: str = None) -> bool:
        """
        ファイルの存在を確認し、存在しない場合はテンプレートを作成
        
        Args:
            file_path: ファイルパス
            template_content: テンプレートの内容
            
        Returns:
            ファイルが利用可能かどうか
        """
        if file_path.exists():
            return True
        
        if template_content:
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(template_content, encoding='utf-8')
                cls._get_logger().info(f"Created template file: {file_path}")
                return True
            except Exception as e:
                cls._get_logger().error(f"Failed to create template file: {e}")
                return False
        
        return False
    
    @classmethod
    def _copy_initial_configs(cls, source_dir: Path, target_dir: Path):
        """初期設定ファイルをコピー"""
        import shutil
        
        # コピーすべきファイルのリスト
        config_files = [
            'gmail_oauth_credentials.json',
            'settings.json',
            '.env.template'
        ]
        
        for filename in config_files:
            source_file = source_dir / filename
            target_file = target_dir / filename
            
            if source_file.exists() and not target_file.exists():
                try:
                    shutil.copy2(source_file, target_file)
                    cls._get_logger().info(f"Copied initial config: {filename}")
                except Exception as e:
                    cls._get_logger().warning(f"Failed to copy {filename}: {e}")
    
    @classmethod
    def get_resource_path(cls, relative_path: str) -> Path:
        """
        リソースファイルのパスを取得（読み取り専用）
        
        Args:
            relative_path: ベースパスからの相対パス
            
        Returns:
            リソースファイルの絶対パス
        """
        return cls.get_base_path() / relative_path