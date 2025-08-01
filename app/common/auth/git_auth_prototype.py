"""
Git認証プロトタイプ
Phase 0-2: 各種Git認証方式の技術検証
"""
import os
import subprocess
import platform
from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass
from pathlib import Path
import logging
import keyring
import json
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


@dataclass
class GitCredentials:
    """Git認証情報"""
    username: str
    password: str
    auth_type: str = "token"
    
    def to_dict(self) -> Dict[str, str]:
        """辞書形式に変換"""
        return {
            "username": self.username,
            "password": self.password,
            "auth_type": self.auth_type
        }


class AuthMethod(ABC):
    """認証方式の基底クラス"""
    
    @abstractmethod
    def authenticate(self) -> Tuple[bool, Optional[GitCredentials], str]:
        """
        認証を試行
        
        Returns:
            Tuple[成功フラグ, 認証情報, エラーメッセージ]
        """
        pass
        
    @abstractmethod
    def get_name(self) -> str:
        """認証方式名を取得"""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """この認証方式が利用可能か確認"""
        pass


class PersonalAccessTokenAuth(AuthMethod):
    """Personal Access Token認証"""
    
    def __init__(self):
        self.service_name = "TECHGATE_GIT_AUTH"
        
    def get_name(self) -> str:
        return "Personal Access Token"
        
    def is_available(self) -> bool:
        """常に利用可能"""
        return True
        
    def authenticate(self) -> Tuple[bool, Optional[GitCredentials], str]:
        """PAT認証を試行"""
        try:
            # 環境変数から取得を試行
            username = os.environ.get("GIT_USERNAME")
            token = os.environ.get("GIT_TOKEN")
            
            if username and token:
                logger.info("環境変数から認証情報を取得")
                return True, GitCredentials(username, token, "token"), ""
                
            # Keyringから取得を試行
            try:
                stored_creds = keyring.get_password(self.service_name, "git_credentials")
                if stored_creds:
                    creds_dict = json.loads(stored_creds)
                    logger.info("Keyringから認証情報を取得")
                    return True, GitCredentials(**creds_dict), ""
            except Exception as e:
                logger.debug(f"Keyring取得エラー: {e}")
                
            return False, None, "認証情報が見つかりません"
            
        except Exception as e:
            return False, None, f"PAT認証エラー: {str(e)}"
            
    def save_credentials(self, creds: GitCredentials) -> bool:
        """認証情報を保存"""
        try:
            keyring.set_password(
                self.service_name,
                "git_credentials",
                json.dumps(creds.to_dict())
            )
            logger.info("認証情報をKeyringに保存")
            return True
        except Exception as e:
            logger.error(f"認証情報保存エラー: {e}")
            return False


class GitCredentialManagerAuth(AuthMethod):
    """Git Credential Manager認証"""
    
    def get_name(self) -> str:
        return "Git Credential Manager"
        
    def is_available(self) -> bool:
        """GCMがインストールされているか確認"""
        try:
            result = subprocess.run(
                ["git", "credential-manager", "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except:
            return False
            
    def authenticate(self) -> Tuple[bool, Optional[GitCredentials], str]:
        """GCM認証を試行"""
        if not self.is_available():
            return False, None, "Git Credential Managerが利用できません"
            
        try:
            # GCMから認証情報を取得
            process = subprocess.Popen(
                ["git", "credential", "fill"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # GitHubの情報を入力
            input_data = "protocol=https\nhost=github.com\n"
            stdout, stderr = process.communicate(input=input_data)
            
            if process.returncode == 0 and stdout:
                # 出力をパース
                creds = {}
                for line in stdout.strip().split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        creds[key] = value
                        
                if 'username' in creds and 'password' in creds:
                    return True, GitCredentials(
                        creds['username'],
                        creds['password'],
                        "gcm"
                    ), ""
                    
            return False, None, "GCMから認証情報を取得できませんでした"
            
        except Exception as e:
            return False, None, f"GCM認証エラー: {str(e)}"


class WindowsCredentialAuth(AuthMethod):
    """Windows資格情報マネージャー認証"""
    
    def get_name(self) -> str:
        return "Windows Credential Manager"
        
    def is_available(self) -> bool:
        """Windowsプラットフォームか確認"""
        return platform.system() == "Windows"
        
    def authenticate(self) -> Tuple[bool, Optional[GitCredentials], str]:
        """Windows資格情報から認証情報を取得"""
        if not self.is_available():
            return False, None, "Windowsプラットフォームではありません"
            
        try:
            # cmdkeyを使用して資格情報を検索
            result = subprocess.run(
                ["cmdkey", "/list:git:https://github.com"],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0 and "github.com" in result.stdout:
                # 資格情報が存在する場合、git configから情報を取得
                username_result = subprocess.run(
                    ["git", "config", "--global", "user.name"],
                    capture_output=True,
                    text=True
                )
                
                if username_result.returncode == 0:
                    username = username_result.stdout.strip()
                    # 実際のパスワードはgit操作時に自動的に使用される
                    return True, GitCredentials(
                        username,
                        "[Windows資格情報で管理]",
                        "windows"
                    ), ""
                    
            return False, None, "Windows資格情報が見つかりません"
            
        except Exception as e:
            return False, None, f"Windows認証エラー: {str(e)}"


class GitAuthPrototype:
    """Git認証プロトタイプ - 複数の認証方式を検証"""
    
    def __init__(self):
        """初期化"""
        self.auth_methods: List[AuthMethod] = [
            PersonalAccessTokenAuth(),
            GitCredentialManagerAuth(),
            WindowsCredentialAuth()
        ]
        self.current_credentials: Optional[GitCredentials] = None
        
    def test_all_methods(self) -> Dict[str, Dict]:
        """
        全ての認証方式をテスト
        
        Returns:
            各認証方式のテスト結果
        """
        results = {}
        
        for method in self.auth_methods:
            method_name = method.get_name()
            logger.info(f"テスト開始: {method_name}")
            
            # 利用可能性チェック
            is_available = method.is_available()
            
            if is_available:
                # 認証試行
                success, creds, error = method.authenticate()
                
                results[method_name] = {
                    "available": True,
                    "success": success,
                    "error": error if not success else None,
                    "credentials": creds.to_dict() if creds else None
                }
                
                # 最初に成功した認証情報を保持
                if success and not self.current_credentials:
                    self.current_credentials = creds
            else:
                results[method_name] = {
                    "available": False,
                    "success": False,
                    "error": "この環境では利用できません",
                    "credentials": None
                }
                
            logger.info(f"テスト完了: {method_name} - {results[method_name]}")
            
        return results
        
    def test_git_operation(self, repo_url: str = "https://github.com/octocat/Hello-World.git") -> Dict[str, any]:
        """
        実際のGit操作でテスト
        
        Args:
            repo_url: テスト用リポジトリURL
            
        Returns:
            テスト結果
        """
        result = {
            "clone_test": False,
            "error": None,
            "auth_method": None
        }
        
        if not self.current_credentials:
            result["error"] = "利用可能な認証情報がありません"
            return result
            
        try:
            # テスト用の一時ディレクトリ
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                # 環境変数またはGit credential helperを使用
                if self.current_credentials.auth_type in ["token", "gcm"]:
                    # Git credential helperを使用した安全な認証
                    # 認証情報は環境変数またはGitの設定で管理
                    import shutil
                    
                    # Git credential helperの設定を確認
                    git_cred_helper = subprocess.run(
                        ["git", "config", "--get", "credential.helper"],
                        capture_output=True,
                        text=True
                    )
                    
                    if git_cred_helper.returncode != 0:
                        # credential helperが設定されていない場合は設定
                        subprocess.run(
                            ["git", "config", "--global", "credential.helper", "manager"],
                            check=False
                        )
                    
                    # 環境変数を設定してgit cloneを実行
                    env = os.environ.copy()
                    env["GIT_USERNAME"] = self.current_credentials.username
                    env["GIT_PASSWORD"] = self.current_credentials.password
                    
                    # URLには認証情報を含めない
                    auth_url = repo_url
                else:
                    auth_url = repo_url
                    env = os.environ.copy()
                    
                # git cloneを試行（環境変数を使用）
                process = subprocess.run(
                    ["git", "clone", "--depth", "1", auth_url, temp_dir],
                    capture_output=True,
                    text=True,
                    env=env
                )
                
                if process.returncode == 0:
                    result["clone_test"] = True
                    result["auth_method"] = self.current_credentials.auth_type
                else:
                    result["error"] = process.stderr
                    
        except Exception as e:
            result["error"] = str(e)
            
        return result
        
    def save_preferred_method(self, creds: GitCredentials) -> bool:
        """推奨認証方式を保存"""
        pat_auth = PersonalAccessTokenAuth()
        return pat_auth.save_credentials(creds)
        
    def generate_report(self, test_results: Dict) -> str:
        """テスト結果のレポートを生成"""
        report = ["# Git認証プロトタイプ 技術検証レポート\n"]
        report.append("## テスト結果サマリー\n")
        
        # 成功した認証方式
        successful_methods = [
            name for name, result in test_results.items()
            if result.get("success", False)
        ]
        
        if successful_methods:
            report.append("### ✅ 成功した認証方式")
            for method in successful_methods:
                report.append(f"- {method}")
        else:
            report.append("### ❌ 成功した認証方式なし")
            
        report.append("\n## 詳細結果\n")
        
        for method_name, result in test_results.items():
            report.append(f"### {method_name}")
            report.append(f"- 利用可能: {'✅' if result['available'] else '❌'}")
            report.append(f"- 認証成功: {'✅' if result['success'] else '❌'}")
            if result.get("error"):
                report.append(f"- エラー: {result['error']}")
            report.append("")
            
        # セキュリティ推奨事項
        report.append("## セキュリティ推奨事項\n")
        report.append("1. Personal Access Tokenは最小権限で作成")
        report.append("2. 認証情報は暗号化して保存（Keyring使用）")
        report.append("3. 環境変数使用時は.envファイルをgitignoreに追加")
        report.append("4. Windows資格情報マネージャーの定期的な確認")
        
        return "\n".join(report)


# テスト実行用のヘルパー関数
def run_prototype_test():
    """プロトタイプテストを実行"""
    logging.basicConfig(level=logging.INFO)
    
    prototype = GitAuthPrototype()
    
    # 全認証方式をテスト
    print("Git認証方式のテストを開始します...\n")
    test_results = prototype.test_all_methods()
    
    # レポート生成
    report = prototype.generate_report(test_results)
    print(report)
    
    # Git操作テスト
    if prototype.current_credentials:
        print("\n実際のGit操作をテストします...")
        git_test = prototype.test_git_operation()
        print(f"Git clone テスト: {'✅ 成功' if git_test['clone_test'] else '❌ 失敗'}")
        if git_test.get("error"):
            print(f"エラー: {git_test['error']}")
            
    return test_results


if __name__ == "__main__":
    run_prototype_test()