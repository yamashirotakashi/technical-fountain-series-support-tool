"""ファイル操作管理モジュール"""
import os
import shutil
import tempfile
import zipfile
import json
from pathlib import Path
from typing import Optional, List, Dict

from utils.logger import get_logger
from utils.config import get_config
from core.git_repository_manager import GitRepositoryManager


class FileManager:
    """ファイル操作を管理するクラス"""
    
    def __init__(self):
        """FileManagerを初期化"""
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.logger.info(f"一時ディレクトリを作成: {self.temp_dir}")
        
        # GitRepositoryManagerを初期化
        self.git_manager = GitRepositoryManager()
        
        # フォルダ設定ファイルのパス
        self.settings_file = Path.home() / ".techzip" / "folder_settings.json"
    
    def find_repository_folder(self, repo_name: str, prefer_remote: bool = True) -> Optional[Path]:
        """
        リポジトリフォルダを検索（リモート優先、ローカルフォールバック）
        
        Args:
            repo_name: リポジトリ名
            prefer_remote: リモートを優先するか（デフォルト: True）
        
        Returns:
            リポジトリフォルダのパス（見つからない場合はNone）
        """
        if prefer_remote:
            # リモートリポジトリから取得を試みる
            self.logger.info(f"リモートリポジトリから取得を試行: {repo_name}")
            repo_path = self.git_manager.get_repository(repo_name)
            
            if repo_path:
                self.logger.info(f"リモートリポジトリを使用: {repo_path}")
                return repo_path
            else:
                self.logger.warning("リモート取得失敗、ローカルにフォールバック")
        
        # ローカルから検索（フォールバックまたはprefer_remote=Falseの場合）
        base_path = Path(self.config.get('paths.git_base'))
        self.logger.info(f"ローカルリポジトリ検索: {repo_name} in {base_path}")
        
        if not base_path.exists():
            self.logger.error(f"ベースパスが存在しません: {base_path}")
            return None
        
        # 直接のパスをチェック
        repo_path = base_path / repo_name
        if repo_path.exists() and repo_path.is_dir():
            self.logger.info(f"ローカルリポジトリフォルダを発見: {repo_path}")
            return repo_path
        
        # サブディレクトリも検索
        for item in base_path.iterdir():
            if item.is_dir() and item.name == repo_name:
                self.logger.info(f"ローカルリポジトリフォルダを発見: {item}")
                return item
        
        self.logger.warning(f"リポジトリフォルダが見つかりません: {repo_name}")
        return None
    
    def find_work_folder(self, repo_path: Path) -> Optional[Path]:
        """
        作業フォルダ（.re, config.yml, catalog.ymlを含む）を検索
        
        Args:
            repo_path: リポジトリのパス
        
        Returns:
            作業フォルダのパス（見つからない場合はNone）
        """
        self.logger.info(f"作業フォルダ検索開始: {repo_path}")
        
        required_files = {'config.yml', 'catalog.yml'}
        
        # リポジトリ直下をチェック
        if self._check_work_folder(repo_path, required_files):
            return repo_path
        
        # サブディレクトリを検索（最大2階層まで）
        for root, dirs, files in os.walk(repo_path):
            # 深さ制限
            depth = len(Path(root).relative_to(repo_path).parts)
            if depth > 2:
                dirs.clear()
                continue
            
            path = Path(root)
            if self._check_work_folder(path, required_files):
                self.logger.info(f"作業フォルダを発見: {path}")
                return path
        
        self.logger.warning("作業フォルダが見つかりません")
        return None
    
    def _check_work_folder(self, path: Path, required_files: set) -> bool:
        """
        フォルダが作業フォルダの条件を満たすかチェック
        
        Args:
            path: チェックするパス
            required_files: 必須ファイルのセット
        
        Returns:
            条件を満たす場合True
        """
        if not path.is_dir():
            return False
        
        # .reファイルの存在確認
        has_re_file = any(f.suffix == '.re' for f in path.iterdir() if f.is_file())
        
        # 必須ファイルの存在確認
        existing_files = {f.name for f in path.iterdir() if f.is_file()}
        has_required_files = required_files.issubset(existing_files)
        
        return has_re_file and has_required_files
    
    def create_zip(self, folder_path: Path, zip_name: Optional[str] = None) -> Path:
        """
        フォルダをZIP圧縮
        
        Args:
            folder_path: 圧縮するフォルダのパス
            zip_name: ZIPファイル名（省略時はフォルダ名.zip）
        
        Returns:
            作成されたZIPファイルのパス
        """
        if zip_name is None:
            zip_name = f"{folder_path.name}.zip"
        
        zip_path = self.temp_dir / zip_name
        self.logger.info(f"ZIP作成開始: {folder_path} -> {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(folder_path.parent)
                    zipf.write(file_path, arcname)
        
        self.logger.info(f"ZIP作成完了: {zip_path} (サイズ: {zip_path.stat().st_size:,} bytes)")
        return zip_path
    
    def extract_zip(self, zip_path: Path, target_path: Path) -> List[Path]:
        """
        ZIPファイルを展開
        
        Args:
            zip_path: ZIPファイルのパス
            target_path: 展開先のパス
        
        Returns:
            展開されたファイルのパスリスト
        """
        self.logger.info(f"ZIP展開開始: {zip_path} -> {target_path}")
        
        # ターゲットディレクトリを作成
        target_path.mkdir(parents=True, exist_ok=True)
        
        extracted_files = []
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for info in zipf.filelist:
                extracted_path = target_path / info.filename
                zipf.extract(info, target_path)
                if not info.is_dir():
                    extracted_files.append(extracted_path)
        
        self.logger.info(f"ZIP展開完了: {len(extracted_files)}個のファイルを展開")
        return extracted_files
    
    def get_output_folder(self, n_code: str) -> Path:
        """
        出力先フォルダのパスを取得
        
        Args:
            n_code: Nコード
        
        Returns:
            出力先フォルダのパス
        """
        output_base = Path(self.config.get('paths.output_base'))
        output_folder = output_base / n_code / "本文"
        return output_folder
    
    def cleanup_temp_files(self):
        """一時ファイルをクリーンアップ"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.logger.info("一時ファイルをクリーンアップしました")
        except Exception as e:
            self.logger.error(f"一時ファイルのクリーンアップに失敗: {e}")
    
    def _load_folder_settings(self) -> Dict[str, str]:
        """保存されたフォルダ設定を読み込む"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"フォルダ設定ファイルの読み込みエラー: {e}")
        return {}
    
    def get_saved_work_folder(self, repo_name: str, repo_path: Path) -> Optional[Path]:
        """
        保存された作業フォルダ設定を取得
        
        Args:
            repo_name: リポジトリ名
            repo_path: リポジトリのルートパス
            
        Returns:
            保存された作業フォルダのパス（存在しない場合はNone）
        """
        settings = self._load_folder_settings()
        
        if repo_name in settings:
            saved_path = Path(settings[repo_name])
            # パスが存在し、リポジトリ内にあることを確認
            if saved_path.exists() and str(saved_path).startswith(str(repo_path)):
                self.logger.info(f"保存された作業フォルダを使用: {saved_path}")
                return saved_path
            else:
                self.logger.warning(f"保存された作業フォルダが無効: {saved_path}")
        
        return None
    
    def find_work_folder_interactive(self, repo_path: Path, repo_name: str) -> Optional[Path]:
        """
        作業フォルダを対話的に検索（保存された設定を優先）
        
        Args:
            repo_path: リポジトリのパス
            repo_name: リポジトリ名
            
        Returns:
            選択された作業フォルダのパス（キャンセルされた場合はNone）
        """
        # まず保存された設定を確認
        saved_folder = self.get_saved_work_folder(repo_name, repo_path)
        
        # 保存された設定がない場合は自動検出を試みる
        if not saved_folder:
            saved_folder = self.find_work_folder(repo_path)
        
        return saved_folder
    
    def __del__(self):
        """デストラクタ"""
        self.cleanup_temp_files()