"""GitHubリポジトリ管理モジュール"""
import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from utils.logger import get_logger
from utils.config import get_config


class GitRepositoryManager:
    """GitHubリポジトリのクローンとキャッシュ管理を行うクラス"""
    
    def __init__(self):
        """GitRepositoryManagerを初期化"""
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # キャッシュディレクトリの設定
        self.cache_dir = Path.home() / ".techzip" / "repo_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # GitHub設定の読み込み
        self.github_user = self.config.get('github.default_user', 'irdtechbook')
        self.github_token = os.environ.get('GITHUB_TOKEN', self.config.get('github.token'))
        
        self.logger.info(f"GitRepositoryManager初期化完了 (キャッシュ: {self.cache_dir})")
    
    def get_repository(self, repo_name: str, force_update: bool = False) -> Optional[Path]:
        """
        リポジトリを取得（リモート優先、ローカルフォールバック）
        
        Args:
            repo_name: リポジトリ名
            force_update: 強制的に最新版を取得するか
        
        Returns:
            リポジトリのローカルパス（取得失敗時はNone）
        """
        self.logger.info(f"リポジトリ取得開始: {repo_name}")
        
        # まずリモートから取得を試みる
        remote_path = self._get_from_remote(repo_name, force_update)
        if remote_path:
            return remote_path
        
        # リモート取得失敗時はローカルにフォールバック
        self.logger.info("リモート取得失敗、ローカルにフォールバック")
        local_path = self._get_from_local(repo_name)
        
        return local_path
    
    def _get_from_remote(self, repo_name: str, force_update: bool = False) -> Optional[Path]:
        """
        GitHubからリポジトリを取得
        
        Args:
            repo_name: リポジトリ名
            force_update: 強制更新フラグ
        
        Returns:
            クローンしたリポジトリのパス（失敗時はNone）
        """
        cache_path = self.cache_dir / repo_name
        
        # キャッシュが存在し、強制更新でない場合
        if cache_path.exists() and not force_update:
            self.logger.info(f"キャッシュを使用: {cache_path}")
            # git pullで更新を試みる
            if self._update_repository(cache_path):
                return cache_path
        
        # 新規クローンまたは強制更新
        return self._clone_repository(repo_name, cache_path)
    
    def _clone_repository(self, repo_name: str, target_path: Path) -> Optional[Path]:
        """
        リポジトリをクローン
        
        Args:
            repo_name: リポジトリ名
            target_path: クローン先のパス
        
        Returns:
            クローンしたパス（失敗時はNone）
        """
        # 既存のディレクトリがある場合は削除
        if target_path.exists():
            shutil.rmtree(target_path)
        
        # GitHub URLの構築
        if self.github_token:
            # トークンがある場合は認証付きURL
            clone_url = f"https://{self.github_token}@github.com/{self.github_user}/{repo_name}.git"
        else:
            # トークンがない場合は通常のURL
            clone_url = f"https://github.com/{self.github_user}/{repo_name}.git"
        
        try:
            self.logger.info(f"リポジトリをクローン中: {repo_name}")
            
            # セキュリティのため、トークンをマスクしてログ出力
            safe_url = clone_url.replace(self.github_token, "***") if self.github_token else clone_url
            self.logger.debug(f"Clone URL: {safe_url}")
            
            # git cloneを実行
            result = subprocess.run(
                ["git", "clone", clone_url, str(target_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5分のタイムアウト
            )
            
            if result.returncode == 0:
                self.logger.info(f"クローン成功: {target_path}")
                return target_path
            else:
                self.logger.error(f"クローン失敗: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("クローンタイムアウト")
            return None
        except Exception as e:
            self.logger.error(f"クローンエラー: {e}")
            return None
    
    def _update_repository(self, repo_path: Path) -> bool:
        """
        既存のリポジトリを更新
        
        Args:
            repo_path: リポジトリのパス
        
        Returns:
            更新成功時True
        """
        try:
            self.logger.info(f"リポジトリを更新中: {repo_path}")
            
            # git pullを実行
            result = subprocess.run(
                ["git", "pull"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=120  # 2分のタイムアウト
            )
            
            if result.returncode == 0:
                self.logger.info("リポジトリ更新成功")
                return True
            else:
                self.logger.warning(f"リポジトリ更新失敗: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"リポジトリ更新エラー: {e}")
            return False
    
    def _get_from_local(self, repo_name: str) -> Optional[Path]:
        """
        ローカルGoogle Driveからリポジトリを取得（フォールバック）
        
        Args:
            repo_name: リポジトリ名
        
        Returns:
            ローカルリポジトリのパス（見つからない場合はNone）
        """
        base_path = Path(self.config.get('paths.git_base'))
        self.logger.info(f"ローカル検索: {repo_name} in {base_path}")
        
        if not base_path.exists():
            self.logger.error(f"ローカルベースパスが存在しません: {base_path}")
            return None
        
        # 直接のパスをチェック
        repo_path = base_path / repo_name
        if repo_path.exists() and repo_path.is_dir():
            self.logger.info(f"ローカルリポジトリを発見: {repo_path}")
            return repo_path
        
        # サブディレクトリも検索
        for item in base_path.iterdir():
            if item.is_dir() and item.name == repo_name:
                self.logger.info(f"ローカルリポジトリを発見: {item}")
                return item
        
        self.logger.warning(f"ローカルリポジトリが見つかりません: {repo_name}")
        return None
    
    def clear_cache(self, repo_name: Optional[str] = None):
        """
        キャッシュをクリア
        
        Args:
            repo_name: 特定のリポジトリ名（省略時は全キャッシュ）
        """
        if repo_name:
            cache_path = self.cache_dir / repo_name
            if cache_path.exists():
                shutil.rmtree(cache_path)
                self.logger.info(f"キャッシュクリア: {repo_name}")
        else:
            # 全キャッシュクリア
            for item in self.cache_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
            self.logger.info("全キャッシュをクリアしました")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        キャッシュ情報を取得
        
        Returns:
            キャッシュ情報の辞書
        """
        info = {
            'cache_dir': str(self.cache_dir),
            'repositories': []
        }
        
        if self.cache_dir.exists():
            for item in self.cache_dir.iterdir():
                if item.is_dir() and (item / '.git').exists():
                    repo_info = {
                        'name': item.name,
                        'path': str(item),
                        'size': sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                    }
                    info['repositories'].append(repo_info)
        
        info['total_size'] = sum(r['size'] for r in info['repositories'])
        info['repository_count'] = len(info['repositories'])
        
        return info