"""
Git認証マネージャー
実際のアプリケーションで使用する認証管理クラス
"""
import os
import logging
from typing import Optional, Callable, Dict
from dataclasses import dataclass
import keyring
import json
import subprocess
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class AuthConfig:
    """認証設定"""
    enable_pat: bool = True
    enable_gcm: bool = True
    enable_windows: bool = True
    max_retry: int = 3
    timeout: int = 30


class GitAuthManager:
    """Git認証を管理するクラス"""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        """
        Args:
            config: 認証設定
        """
        self.config = config or AuthConfig()
        self.service_name = "TECHGATE_GIT"
        self._cached_credentials = None
        self._retry_count = 0
        
    def get_credentials(self) -> Optional[Dict[str, str]]:
        """
        認証情報を取得（キャッシュ優先）
        
        Returns:
            認証情報の辞書 or None
        """
        # キャッシュチェック
        if self._cached_credentials:
            return self._cached_credentials
            
        # 1. 環境変数
        if self.config.enable_pat:
            creds = self._get_from_env()
            if creds:
                self._cached_credentials = creds
                return creds
                
        # 2. Keyring
        creds = self._get_from_keyring()
        if creds:
            self._cached_credentials = creds
            return creds
            
        # 3. Git Credential Manager
        if self.config.enable_gcm:
            creds = self._get_from_gcm()
            if creds:
                self._cached_credentials = creds
                # Keyringに保存
                self._save_to_keyring(creds)
                return creds
                
        return None
        
    def save_credentials(self, username: str, password: str) -> bool:
        """
        認証情報を保存
        
        Args:
            username: ユーザー名
            password: パスワード/トークン
            
        Returns:
            保存成功フラグ
        """
        creds = {
            "username": username,
            "password": password,
            "auth_type": "token"
        }
        
        success = self._save_to_keyring(creds)
        if success:
            self._cached_credentials = creds
            
        return success
        
    def clear_credentials(self) -> bool:
        """認証情報をクリア"""
        try:
            keyring.delete_password(self.service_name, "credentials")
            self._cached_credentials = None
            return True
        except Exception as e:
            logger.error(f"認証情報削除エラー: {e}")
            return False
            
    def test_connection(self, repo_url: str = "https://github.com") -> bool:
        """
        Git接続をテスト
        
        Args:
            repo_url: テスト対象のリポジトリURL
            
        Returns:
            接続成功フラグ
        """
        try:
            # git ls-remoteでテスト
            result = subprocess.run(
                ["git", "ls-remote", repo_url],
                capture_output=True,
                timeout=self.config.timeout,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"接続テストエラー: {e}")
            return False
            
    def execute_with_retry(self, git_command: list, 
                          on_auth_fail: Optional[Callable] = None) -> subprocess.CompletedProcess:
        """
        リトライ機能付きGitコマンド実行
        
        Args:
            git_command: 実行するgitコマンド
            on_auth_fail: 認証失敗時のコールバック
            
        Returns:
            実行結果
        """
        for attempt in range(self.config.max_retry):
            try:
                # 認証情報を環境変数に設定
                env = os.environ.copy()
                creds = self.get_credentials()
                
                if creds:
                    # 認証情報を環境変数に設定
                    if "GIT_USERNAME" not in env:
                        env["GIT_USERNAME"] = creds.get("username", "")
                    if "GIT_PASSWORD" not in env:
                        env["GIT_PASSWORD"] = creds.get("password", "")
                    
                    # Git credential helperの設定確認
                    cred_helper_check = subprocess.run(
                        ["git", "config", "--get", "credential.helper"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    # credential helperが設定されていない場合
                    if cred_helper_check.returncode != 0:
                        # 一時的にcredential helperを設定
                        subprocess.run(
                            ["git", "config", "--global", "credential.helper", "manager"],
                            check=False
                        )
                    
                    # 認証が必要なコマンドの場合、credential helperまたは環境変数経由で認証
                    # URLに認証情報を埋め込まない安全な方式を使用
                    
                result = subprocess.run(
                    git_command,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=self.config.timeout
                )
                
                if result.returncode == 0:
                    self._retry_count = 0
                    return result
                    
                # 認証エラーの場合
                if "authentication failed" in result.stderr.lower():
                    logger.warning(f"認証失敗 (試行 {attempt + 1}/{self.config.max_retry})")
                    
                    # キャッシュクリア
                    self._cached_credentials = None
                    
                    # コールバック実行
                    if on_auth_fail:
                        new_creds = on_auth_fail()
                        if new_creds:
                            self.save_credentials(
                                new_creds.get("username"),
                                new_creds.get("password")
                            )
                            continue
                            
                return result
                
            except subprocess.TimeoutExpired:
                logger.error(f"タイムアウト (試行 {attempt + 1}/{self.config.max_retry})")
                if attempt == self.config.max_retry - 1:
                    raise
                    
        # 最大リトライ回数に達した
        raise Exception(f"最大リトライ回数({self.config.max_retry})に達しました")
        
    def _get_from_env(self) -> Optional[Dict[str, str]]:
        """環境変数から認証情報を取得"""
        username = os.environ.get("GIT_USERNAME")
        password = os.environ.get("GIT_TOKEN") or os.environ.get("GITHUB_TOKEN")
        
        if username and password:
            logger.info("環境変数から認証情報を取得")
            return {
                "username": username,
                "password": password,
                "auth_type": "env"
            }
        return None
        
    def _get_from_keyring(self) -> Optional[Dict[str, str]]:
        """Keyringから認証情報を取得"""
        try:
            stored = keyring.get_password(self.service_name, "credentials")
            if stored:
                logger.info("Keyringから認証情報を取得")
                return json.loads(stored)
        except Exception as e:
            logger.debug(f"Keyring取得エラー: {e}")
        return None
        
    def _save_to_keyring(self, creds: Dict[str, str]) -> bool:
        """Keyringに認証情報を保存"""
        try:
            keyring.set_password(
                self.service_name,
                "credentials",
                json.dumps(creds)
            )
            logger.info("認証情報をKeyringに保存")
            return True
        except Exception as e:
            logger.error(f"Keyring保存エラー: {e}")
            return False
            
    def _get_from_gcm(self) -> Optional[Dict[str, str]]:
        """Git Credential Managerから認証情報を取得"""
        try:
            # GCMの存在確認
            check = subprocess.run(
                ["git", "credential-manager", "--version"],
                capture_output=True,
                check=False
            )
            
            if check.returncode != 0:
                return None
                
            # 認証情報取得
            process = subprocess.Popen(
                ["git", "credential", "fill"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, _ = process.communicate(
                input="protocol=https\nhost=github.com\n"
            )
            
            if process.returncode == 0 and stdout:
                creds = {}
                for line in stdout.strip().split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        creds[key] = value
                        
                if 'username' in creds and 'password' in creds:
                    logger.info("GCMから認証情報を取得")
                    return {
                        "username": creds['username'],
                        "password": creds['password'],
                        "auth_type": "gcm"
                    }
                    
        except Exception as e:
            logger.debug(f"GCM取得エラー: {e}")
            
        return None