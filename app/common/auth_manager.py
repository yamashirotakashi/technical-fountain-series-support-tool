"""
統一認証管理システム
Phase 1-3: Git認証情報の共有とセキュアな保存
"""
import os
import json
import keyring
from typing import Dict, Optional, Any, List
from pathlib import Path
import threading
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64


class AuthManager:
    """統一された認証管理クラス"""
    
    _instance = None
    _lock = threading.Lock()
    
    # サービス名
    SERVICE_NAME = "TECHGATE"
    
    # 認証タイプ
    AUTH_TYPE_GIT = "git"
    AUTH_TYPE_GOOGLE = "google"
    AUTH_TYPE_EMAIL = "email"
    
    def __new__(cls):
        """シングルトンパターンの実装"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        """初期化"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.project_root = Path(__file__).parent.parent.parent
        self.auth_cache_file = self.project_root / "config" / ".auth_cache"
        self.encryption_key = self._get_or_create_key()
        self.fernet = Fernet(self.encryption_key)
        self._cache = {}
        self._load_cache()
        
    def _get_or_create_key(self) -> bytes:
        """暗号化キーの取得または作成"""
        key_name = f"{self.SERVICE_NAME}_ENCRYPTION_KEY"
        
        try:
            # keyringから取得を試みる
            stored_key = keyring.get_password(self.SERVICE_NAME, key_name)
            
            if stored_key:
                return base64.b64decode(stored_key.encode())
            else:
                # 新しいキーを生成して保存
                new_key = Fernet.generate_key()
                keyring.set_password(
                    self.SERVICE_NAME,
                    key_name,
                    base64.b64encode(new_key).decode()
                )
                return new_key
        except Exception as e:
            # keyringが使用できない場合はファイルベースのフォールバック
            print(f"Keyring not available, using file-based storage: {e}")
            key_file = self.project_root / "config" / ".encryption_key"
            key_file.parent.mkdir(exist_ok=True)
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                new_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(new_key)
                # ファイル権限を設定（WSLでは効果が限定的）
                import os
                os.chmod(key_file, 0o600)
                return new_key
            
    def _load_cache(self):
        """キャッシュの読み込み"""
        if self.auth_cache_file.exists():
            try:
                with open(self.auth_cache_file, 'rb') as f:
                    encrypted_data = f.read()
                    decrypted_data = self.fernet.decrypt(encrypted_data)
                    self._cache = json.loads(decrypted_data.decode())
            except Exception as e:
                print(f"キャッシュ読み込みエラー: {e}")
                self._cache = {}
                
    def _save_cache(self):
        """キャッシュの保存"""
        try:
            # ディレクトリ作成
            self.auth_cache_file.parent.mkdir(exist_ok=True)
            
            # 暗号化して保存
            data = json.dumps(self._cache).encode()
            encrypted_data = self.fernet.encrypt(data)
            
            with open(self.auth_cache_file, 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            print(f"キャッシュ保存エラー: {e}")
            
    def store_credentials(self, auth_type: str, identifier: str, 
                         credentials: Dict[str, str]) -> bool:
        """
        認証情報の保存
        
        Args:
            auth_type: 認証タイプ (git, google, email)
            identifier: 識別子 (URLやアカウント名)
            credentials: 認証情報の辞書
            
        Returns:
            成功フラグ
        """
        try:
            # keyringに保存を試みる
            key = f"{auth_type}:{identifier}"
            value = json.dumps(credentials)
            
            try:
                keyring.set_password(self.SERVICE_NAME, key, value)
            except Exception as e:
                # keyringが使用できない場合はキャッシュのみに保存
                print(f"Keyring storage failed, using cache only: {e}")
            
            # キャッシュに記録
            if auth_type not in self._cache:
                self._cache[auth_type] = {}
            self._cache[auth_type][identifier] = {
                "stored_at": datetime.now().isoformat(),
                "last_used": None
            }
            self._save_cache()
            
            return True
            
        except Exception as e:
            print(f"認証情報保存エラー: {e}")
            return False
            
    def get_credentials(self, auth_type: str, identifier: str) -> Optional[Dict[str, str]]:
        """
        認証情報の取得
        
        Args:
            auth_type: 認証タイプ
            identifier: 識別子
            
        Returns:
            認証情報の辞書またはNone
        """
        try:
            # keyringから取得を試みる
            key = f"{auth_type}:{identifier}"
            value = None
            
            try:
                value = keyring.get_password(self.SERVICE_NAME, key)
            except Exception as e:
                # keyringが使用できない場合はキャッシュから取得
                print(f"Keyring retrieval failed, checking cache: {e}")
            
            if value:
                # 最終使用日時を更新
                if auth_type in self._cache and identifier in self._cache[auth_type]:
                    self._cache[auth_type][identifier]["last_used"] = datetime.now().isoformat()
                    self._save_cache()
                    
                return json.loads(value)
                
        except Exception as e:
            print(f"認証情報取得エラー: {e}")
            
        return None
        
    def delete_credentials(self, auth_type: str, identifier: str) -> bool:
        """
        認証情報の削除
        
        Args:
            auth_type: 認証タイプ
            identifier: 識別子
            
        Returns:
            成功フラグ
        """
        try:
            # keyringから削除を試みる
            key = f"{auth_type}:{identifier}"
            
            try:
                keyring.delete_password(self.SERVICE_NAME, key)
            except Exception as e:
                # keyringが使用できない場合はスキップ
                print(f"Keyring deletion failed, continuing: {e}")
            
            # キャッシュから削除
            if auth_type in self._cache and identifier in self._cache[auth_type]:
                del self._cache[auth_type][identifier]
                self._save_cache()
                
            return True
            
        except Exception as e:
            print(f"認証情報削除エラー: {e}")
            return False
            
    def list_stored_credentials(self, auth_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        保存されている認証情報のリスト取得
        
        Args:
            auth_type: 認証タイプ（指定しない場合は全て）
            
        Returns:
            認証情報のメタデータリスト
        """
        result = []
        
        if auth_type:
            if auth_type in self._cache:
                for identifier, meta in self._cache[auth_type].items():
                    result.append({
                        "auth_type": auth_type,
                        "identifier": identifier,
                        "stored_at": meta.get("stored_at"),
                        "last_used": meta.get("last_used")
                    })
        else:
            for auth_type, identifiers in self._cache.items():
                for identifier, meta in identifiers.items():
                    result.append({
                        "auth_type": auth_type,
                        "identifier": identifier,
                        "stored_at": meta.get("stored_at"),
                        "last_used": meta.get("last_used")
                    })
                    
        return result
        
    def get_git_credentials(self, repo_url: str) -> Optional[Dict[str, str]]:
        """Git認証情報の取得（便利メソッド）"""
        return self.get_credentials(self.AUTH_TYPE_GIT, repo_url)
        
    def store_git_credentials(self, repo_url: str, username: str, password: str) -> bool:
        """Git認証情報の保存（便利メソッド）"""
        return self.store_credentials(
            self.AUTH_TYPE_GIT,
            repo_url,
            {"username": username, "password": password}
        )
        
    def get_google_credentials(self, account: str) -> Optional[Dict[str, str]]:
        """Google認証情報の取得（便利メソッド）"""
        return self.get_credentials(self.AUTH_TYPE_GOOGLE, account)
        
    def store_google_credentials(self, account: str, credentials_path: str) -> bool:
        """Google認証情報の保存（便利メソッド）"""
        return self.store_credentials(
            self.AUTH_TYPE_GOOGLE,
            account,
            {"credentials_path": credentials_path}
        )
        
    def get_email_credentials(self, email: str) -> Optional[Dict[str, str]]:
        """メール認証情報の取得（便利メソッド）"""
        return self.get_credentials(self.AUTH_TYPE_EMAIL, email)
        
    def store_email_credentials(self, email: str, app_password: str) -> bool:
        """メール認証情報の保存（便利メソッド）"""
        return self.store_credentials(
            self.AUTH_TYPE_EMAIL,
            email,
            {"email": email, "app_password": app_password}
        )
        
    def cleanup_old_credentials(self, days: int = 90) -> int:
        """
        古い認証情報のクリーンアップ
        
        Args:
            days: 最終使用からの経過日数
            
        Returns:
            削除した認証情報の数
        """
        deleted = 0
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for auth_type in list(self._cache.keys()):
            for identifier in list(self._cache[auth_type].keys()):
                meta = self._cache[auth_type][identifier]
                last_used = meta.get("last_used")
                
                if last_used:
                    last_used_date = datetime.fromisoformat(last_used)
                    if last_used_date < cutoff_date:
                        if self.delete_credentials(auth_type, identifier):
                            deleted += 1
                            
        return deleted


# グローバルインスタンス
auth_manager = AuthManager()


# 使用例
if __name__ == "__main__":
    # Git認証情報の保存
    auth_manager.store_git_credentials(
        "https://github.com/user/repo.git",
        "username",
        "password_or_token"
    )
    
    # Git認証情報の取得
    creds = auth_manager.get_git_credentials("https://github.com/user/repo.git")
    if creds:
        print(f"Username: {creds['username']}")
        
    # 保存されている認証情報のリスト
    stored = auth_manager.list_stored_credentials()
    for item in stored:
        print(f"{item['auth_type']}: {item['identifier']}")