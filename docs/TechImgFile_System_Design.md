# TechImgFile v0.5 システム設計書

**プロジェクト**: TECHZIP統合アプリ  
**作成日**: 2025-08-01  
**バージョン**: 0.5  

## 1. システムアーキテクチャ概要

### 1.1 アーキテクチャ方針
- **レイヤード・アーキテクチャ**: プレゼンテーション、ビジネスロジック、データアクセス層の分離
- **モジュラー設計**: 機能単位での独立性確保
- **依存性注入**: テスタビリティとメンテナンス性の向上
- **非同期処理**: UI応答性の確保

### 1.2 システム全体構成

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Main Window │  │ Progress    │  │ Settings Dialog     │  │
│  │ (Qt6)       │  │ Dialog      │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Workflow    │  │ N-Code      │  │ Image Processor     │  │
│  │ Manager     │  │ Processor   │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Repository  │  │ Processing  │  │ Error Handler       │  │
│  │ Manager     │  │ Options     │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Integration Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Google      │  │ GitHub      │  │ File System         │  │
│  │ Sheets API  │  │ Client      │  │ Handler             │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Config      │  │ Logger      │  │ Validators          │  │
│  │ Manager     │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 2. 詳細コンポーネント設計

### 2.1 Presentation Layer (UI層)

#### 2.1.1 MainWindow (`ui/main_window.py`)
```python
class MainWindow(QMainWindow):
    """メインウィンドウ - Qt6ベース"""
    
    # シグナル定義
    n_code_processing_requested = pyqtSignal(str)
    folder_processing_requested = pyqtSignal(str)
    settings_requested = pyqtSignal()
    
    def __init__(self):
        self.workflow_manager = None  # 依存性注入
        self.settings_manager = None
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """UI要素の初期化"""
        pass
    
    def setup_connections(self):
        """シグナル・スロット接続"""
        pass
    
    def on_n_code_submit(self):
        """N番号処理開始"""
        pass
    
    def on_progress_update(self, progress: int, message: str):
        """進捗更新受信"""
        pass
    
    def on_processing_complete(self, result: ProcessingResult):
        """処理完了受信"""
        pass
```

#### 2.1.2 ProgressDialog (`ui/progress_dialog.py`)
```python
class ProgressDialog(QDialog):
    """進捗表示ダイアログ"""
    
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.is_cancellable = True
    
    def update_progress(self, value: int, message: str):
        """進捗更新"""
        pass
    
    def set_cancellable(self, cancellable: bool):
        """キャンセル可能性設定"""
        pass
```

#### 2.1.3 SettingsDialog (`ui/settings_dialog.py`)
```python
class SettingsDialog(QDialog):
    """設定ダイアログ"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.original_settings = settings
        self.setup_ui()
        self.load_settings()
    
    def validate_settings(self) -> Tuple[bool, List[str]]:
        """設定値バリデーション"""
        pass
    
    def save_settings(self) -> dict:
        """設定保存"""
        pass
```

### 2.2 Business Logic Layer (ビジネスロジック層)

#### 2.2.1 WorkflowManager (`core/workflow_manager.py`)
```python
class WorkflowManager(QObject):
    """ワークフロー制御の中心クラス"""
    
    # シグナル定義
    progress_updated = pyqtSignal(int, str)
    processing_complete = pyqtSignal(object)
    error_occurred = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.n_code_processor = NCodeProcessor()
        self.repository_manager = RepositoryManager()
        self.image_processor = ImageProcessor()
        self.is_processing = False
        self.processing_thread = None
    
    @pyqtSlot(str)
    def execute_n_code_workflow(self, n_code: str):
        """N番号ベースワークフロー実行"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.processing_thread = WorkflowThread(
            n_code, self.n_code_processor, 
            self.repository_manager, self.image_processor
        )
        self.processing_thread.progress_updated.connect(self.progress_updated)
        self.processing_thread.finished.connect(self._on_workflow_finished)
        self.processing_thread.start()
    
    @pyqtSlot(str)
    def execute_folder_workflow(self, folder_path: str):
        """フォルダベースワークフロー実行"""
        pass
    
    def cancel_processing(self):
        """処理キャンセル"""
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.cancel()
```

#### 2.2.2 NCodeProcessor (`core/n_code_processor.py`)
```python
@dataclass
class NCodeResult:
    """N番号処理結果"""
    n_code: str
    repository_name: str
    is_valid: bool
    error_message: Optional[str] = None

class NCodeProcessor:
    """N番号処理エンジン"""
    
    def __init__(self, google_sheets_client: GoogleSheetsClient):
        self.google_sheets = google_sheets_client
        self.cache = {}  # 結果キャッシュ
    
    def validate_n_code(self, n_code: str) -> bool:
        """N番号フォーマット検証"""
        pattern = r'^[Nn]\d{4,6}[a-zA-Z]*$'
        return bool(re.match(pattern, n_code.strip()))
    
    def get_repository_name(self, n_code: str) -> NCodeResult:
        """N番号からリポジトリ名取得"""
        # キャッシュ確認
        if n_code in self.cache:
            return self.cache[n_code]
        
        try:
            # バリデーション
            if not self.validate_n_code(n_code):
                return NCodeResult(n_code, "", False, "無効なN番号形式")
            
            # Google Sheets検索
            repo_name = self.google_sheets.get_repository_name(n_code)
            if not repo_name:
                return NCodeResult(n_code, "", False, "リポジトリ名が見つかりません")
            
            result = NCodeResult(n_code, repo_name, True)
            self.cache[n_code] = result
            return result
            
        except Exception as e:
            return NCodeResult(n_code, "", False, f"検索エラー: {str(e)}")
```

#### 2.2.3 RepositoryManager (`core/repository_manager.py`)
```python
@dataclass
class RepositoryInfo:
    """リポジトリ情報"""
    name: str
    local_path: Optional[Path]
    remote_url: str
    is_cloned: bool
    image_folders: List[Path]

class RepositoryManager:
    """Git リポジトリ管理"""
    
    def __init__(self, github_client: GitHubClient, config: dict):
        self.github = github_client
        self.config = config
        self.clone_base_path = Path(config['git']['clone_base_path'])
    
    def find_or_clone_repository(self, repo_name: str) -> RepositoryInfo:
        """リポジトリ検索またはclone"""
        # ローカル検索
        local_path = self._find_local_repository(repo_name)
        if local_path:
            return RepositoryInfo(
                name=repo_name,
                local_path=local_path,
                remote_url=f"https://github.com/irdtechbook/{repo_name}.git",
                is_cloned=True,
                image_folders=self._find_image_folders(local_path)
            )
        
        # GitHub clone
        try:
            cloned_path = self._clone_repository(repo_name)
            return RepositoryInfo(
                name=repo_name,
                local_path=cloned_path,
                remote_url=f"https://github.com/irdtechbook/{repo_name}.git",
                is_cloned=True,
                image_folders=self._find_image_folders(cloned_path)
            )
        except Exception as e:
            return RepositoryInfo(
                name=repo_name,
                local_path=None,
                remote_url=f"https://github.com/irdtechbook/{repo_name}.git",
                is_cloned=False,
                image_folders=[]
            )
    
    def _find_local_repository(self, repo_name: str) -> Optional[Path]:
        """ローカルリポジトリ検索"""
        search_paths = [
            self.clone_base_path / repo_name,
            self.clone_base_path / "irdtechbook" / repo_name,
            Path("G:/マイドライブ/[git]") / repo_name  # TECHZIP互換
        ]
        
        for path in search_paths:
            if path.exists() and (path / ".git").exists():
                return path
        
        return None
    
    def _clone_repository(self, repo_name: str) -> Path:
        """GitHub からリポジトリをclone"""
        clone_url = f"https://github.com/irdtechbook/{repo_name}.git"
        target_path = self.clone_base_path / repo_name
        
        # クローン先ディレクトリ作成
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Git clone実行
        cmd = ["git", "clone", clone_url, str(target_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Clone failed: {result.stderr}")
        
        return target_path
    
    def _find_image_folders(self, repo_path: Path) -> List[Path]:
        """画像フォルダ検出"""
        patterns = [
            "images/**",
            "img/**", 
            "assets/images/**",
            "src/images/**",
            "static/images/**",
            "resources/images/**"
        ]
        
        found_folders = []
        for pattern in patterns:
            for path in repo_path.glob(pattern):
                if path.is_dir() and self._contains_images(path):
                    found_folders.append(path)
        
        return found_folders
    
    def _contains_images(self, folder_path: Path) -> bool:
        """フォルダに画像ファイルが含まれるか確認"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        for file_path in folder_path.iterdir():
            if file_path.suffix.lower() in image_extensions:
                return True
        return False
    
    def commit_and_push(self, repo_path: Path, message: str = None) -> bool:
        """変更をcommit & push"""
        if not message:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"画像処理完了 - TechImgFile v0.5 ({timestamp})"
        
        try:
            # Git add
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            
            # Git commit
            subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
            
            # Git push
            subprocess.run(["git", "push"], cwd=repo_path, check=True)
            
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Git operation failed: {e}")
            return False
```

#### 2.2.4 ImageProcessor (`core/image_processor.py`)
```python
@dataclass
class ProcessingOptions:
    """画像処理オプション"""
    remove_profile: bool = False
    grayscale: bool = False
    change_resolution: bool = True
    resize: bool = True
    backup: bool = True
    png_to_jpg: bool = True
    max_pixels: int = 4000000  # 400万画素
    resolution: int = 100

@dataclass
class ProcessingResult:
    """処理結果"""
    total_files: int
    processed_files: int
    failed_files: int
    processing_time: float
    errors: List[str]

class ImageProcessor(QObject):
    """画像処理エンジン"""
    
    progress_updated = pyqtSignal(int, str)
    
    def __init__(self):
        super().__init__()
        self.supported_formats = {'.jpg', '.jpeg', '.png'}
    
    def process_folder(self, folder_path: Path, options: ProcessingOptions) -> ProcessingResult:
        """フォルダ内画像の一括処理"""
        start_time = time.time()
        
        # 画像ファイル収集
        image_files = list(self._collect_image_files(folder_path))
        total_files = len(image_files)
        
        if total_files == 0:
            return ProcessingResult(0, 0, 0, 0, ["画像ファイルが見つかりません"])
        
        processed = 0
        failed = 0
        errors = []
        
        for i, image_path in enumerate(image_files):
            try:
                # 進捗更新
                progress = int((i / total_files) * 100)
                self.progress_updated.emit(progress, f"処理中: {image_path.name}")
                
                # 画像処理実行
                success = self._process_single_image(image_path, options)
                if success:
                    processed += 1
                else:
                    failed += 1
                
            except Exception as e:
                failed += 1
                errors.append(f"{image_path.name}: {str(e)}")
        
        processing_time = time.time() - start_time
        self.progress_updated.emit(100, "処理完了")
        
        return ProcessingResult(total_files, processed, failed, processing_time, errors)
    
    def _collect_image_files(self, folder_path: Path) -> Generator[Path, None, None]:
        """画像ファイル収集（再帰的）"""
        for file_path in folder_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                # バックアップフォルダは除外
                if "backup" not in file_path.parts and "PNG" not in file_path.parts:
                    yield file_path
    
    def _process_single_image(self, image_path: Path, options: ProcessingOptions) -> bool:
        """単一画像処理"""
        try:
            # バックアップ作成
            if options.backup:
                self._create_backup(image_path)
            
            # PNG→JPG変換
            if options.png_to_jpg and image_path.suffix.lower() == '.png':
                image_path = self._convert_png_to_jpg(image_path, options)
            
            # 画像処理
            with Image.open(image_path) as img:
                modified = False
                
                # プロファイル除去
                if options.remove_profile and 'icc_profile' in img.info:
                    img.info.pop('icc_profile')
                    modified = True
                
                # グレースケール変換
                if options.grayscale and img.mode != 'L':
                    img = img.convert('L')
                    modified = True
                
                # リサイズ
                if options.resize:
                    img, resized = self._resize_image(img, options.max_pixels)
                    if resized:
                        modified = True
                
                # 解像度設定
                dpi_setting = (options.resolution, options.resolution) if options.change_resolution else img.info.get("dpi", (72, 72))
                
                # 保存
                if modified or options.change_resolution:
                    img.save(image_path, dpi=dpi_setting)
            
            return True
            
        except Exception as e:
            logging.error(f"Image processing failed for {image_path}: {e}")
            return False
    
    def _create_backup(self, image_path: Path):
        """バックアップ作成"""
        backup_dir = image_path.parent / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / image_path.name
        shutil.copy2(image_path, backup_path)
    
    def _convert_png_to_jpg(self, png_path: Path, options: ProcessingOptions) -> Path:
        """PNG→JPG変換"""
        # PNGバックアップ
        png_backup_dir = png_path.parent / "PNG"
        png_backup_dir.mkdir(exist_ok=True)
        shutil.copy2(png_path, png_backup_dir / png_path.name)
        
        # JPG変換
        jpg_path = png_path.with_suffix('.jpg')
        with Image.open(png_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            dpi_setting = (options.resolution, options.resolution)
            img.save(jpg_path, "JPEG", dpi=dpi_setting)
        
        # 元PNG削除
        png_path.unlink()
        return jpg_path
    
    def _resize_image(self, img: Image.Image, max_pixels: int) -> Tuple[Image.Image, bool]:
        """画像リサイズ"""
        width, height = img.size
        current_pixels = width * height
        
        if current_pixels <= max_pixels:
            return img, False
        
        # アスペクト比維持リサイズ
        aspect_ratio = width / height
        new_width = int((max_pixels * aspect_ratio) ** 0.5)
        new_height = int(max_pixels / new_width)
        
        # 画素数調整
        while new_width * new_height > max_pixels and new_width > 0:
            new_width -= 1
            new_height = int(max_pixels / new_width) if new_width != 0 else 0
        
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        return resized_img, True
```

### 2.3 Integration Layer (統合層)

#### 2.3.1 GoogleSheetsClient (`integrations/google_sheets.py`)
```python
class GoogleSheetsClient:
    """Google Sheets API クライアント"""
    
    def __init__(self, credentials_path: str, sheet_id: str):
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """認証処理"""
        scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_path, scope
        )
        self.service = build('sheets', 'v4', credentials=creds)
    
    def get_repository_name(self, n_code: str) -> Optional[str]:
        """N番号からリポジトリ名取得"""
        try:
            # シート検索
            range_name = 'Sheet1!A:B'  # A列：N番号、B列：リポジトリ名
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            for row in values:
                if len(row) >= 2 and row[0].strip().upper() == n_code.upper():
                    return row[1].strip()
            
            return None
            
        except Exception as e:
            logging.error(f"Google Sheets API error: {e}")
            raise
```

#### 2.3.2 GitHubClient (`integrations/github_client.py`)
```python
class GitHubClient:
    """GitHub API クライアント"""
    
    def __init__(self, token: str, user: str = "irdtechbook"):
        self.token = token
        self.user = user
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def repository_exists(self, repo_name: str) -> bool:
        """リポジトリ存在確認"""
        url = f"https://api.github.com/repos/{self.user}/{repo_name}"
        response = requests.get(url, headers=self.headers)
        return response.status_code == 200
    
    def get_repository_info(self, repo_name: str) -> dict:
        """リポジトリ情報取得"""
        url = f"https://api.github.com/repos/{self.user}/{repo_name}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise RuntimeError(f"Repository not found: {repo_name}")
```

### 2.4 Infrastructure Layer (インフラ層)

#### 2.4.1 ConfigManager (`utils/config.py`)
```python
class ConfigManager:
    """設定管理"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """設定ファイル読み込み"""
        if not self.config_path.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Config load error: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> dict:
        """デフォルト設定作成"""
        default_config = {
            "app": {
                "name": "TechImgFile",
                "version": "0.5",
                "log_level": "INFO"
            },
            "git": {
                "github_token": "",
                "clone_base_path": str(Path.home() / "Git" / "Repositories"),
                "default_user": "irdtechbook",
                "auto_commit": True,
                "auto_push": True
            },
            "google_sheets": {
                "sheet_id": "17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ",
                "credentials_path": "config/credentials.json",
                "n_code_column": "A",
                "repo_name_column": "B"
            },
            "image_processing": {
                "default_resolution": 100,
                "max_pixels_mp": 400,
                "create_backup": True,
                "backup_folder_name": "backup",
                "supported_formats": [".jpg", ".jpeg", ".png"],
                "png_to_jpg": True,
                "remove_profile": False,
                "grayscale": False
            },
            "ui": {
                "theme": "system",
                "window_size": [900, 700],
                "auto_detect_folders": True,
                "confirm_operations": True
            }
        }
        
        # 設定ファイル保存
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: dict = None):
        """設定保存"""
        if config:
            self.config = config
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def get(self, key_path: str, default=None):
        """設定値取得（ドット記法対応）"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
```

## 3. 非同期処理とスレッド設計

### 3.1 WorkflowThread (`core/workflow_thread.py`)
```python
class WorkflowThread(QThread):
    """ワークフロー実行スレッド"""
    
    progress_updated = pyqtSignal(int, str)
    step_completed = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str, str)
    
    def __init__(self, n_code: str, n_code_processor: NCodeProcessor,
                 repository_manager: RepositoryManager, 
                 image_processor: ImageProcessor):
        super().__init__()
        self.n_code = n_code
        self.n_code_processor = n_code_processor
        self.repository_manager = repository_manager
        self.image_processor = image_processor
        self.is_cancelled = False
    
    def run(self):
        """メイン処理"""
        try:
            # Step 1: N番号処理
            self.progress_updated.emit(10, "N番号を処理中...")
            n_code_result = self.n_code_processor.get_repository_name(self.n_code)
            
            if not n_code_result.is_valid:
                self.error_occurred.emit("N番号エラー", n_code_result.error_message)
                return
            
            self.step_completed.emit("n_code_processing", {
                "n_code": self.n_code,
                "repository_name": n_code_result.repository_name
            })
            
            if self.is_cancelled:
                return
            
            # Step 2: リポジトリ取得
            self.progress_updated.emit(30, "リポジトリを取得中...")
            repo_info = self.repository_manager.find_or_clone_repository(
                n_code_result.repository_name
            )
            
            if not repo_info.local_path:
                self.error_occurred.emit("リポジトリエラー", "リポジトリの取得に失敗しました")
                return
            
            self.step_completed.emit("repository_acquisition", {
                "repository_info": repo_info
            })
            
            if self.is_cancelled:
                return
            
            # Step 3: 画像処理
            self.progress_updated.emit(50, "画像処理を開始中...")
            
            # 画像処理の進捗を中継
            self.image_processor.progress_updated.connect(
                lambda progress, msg: self.progress_updated.emit(50 + progress // 2, msg)
            )
            
            for image_folder in repo_info.image_folders:
                processing_options = ProcessingOptions()  # 設定から取得
                result = self.image_processor.process_folder(image_folder, processing_options)
                
                self.step_completed.emit("image_processing", {
                    "folder": str(image_folder),
                    "result": result
                })
                
                if self.is_cancelled:
                    return
            
            # Step 4: Git操作
            self.progress_updated.emit(90, "変更をコミット中...")
            commit_success = self.repository_manager.commit_and_push(
                repo_info.local_path,
                f"画像処理完了: {self.n_code}"
            )
            
            self.step_completed.emit("git_operations", {
                "commit_success": commit_success
            })
            
            self.progress_updated.emit(100, "処理完了")
            
        except Exception as e:
            self.error_occurred.emit("予期せぬエラー", str(e))
    
    def cancel(self):
        """処理キャンセル"""
        self.is_cancelled = True
```

## 4. エラーハンドリング戦略

### 4.1 エラー分類
```python
class TechImgFileError(Exception):
    """基底例外クラス"""
    pass

class NCodeError(TechImgFileError):
    """N番号関連エラー"""
    pass

class RepositoryError(TechImgFileError):
    """リポジトリ関連エラー"""
    pass

class ImageProcessingError(TechImgFileError):
    """画像処理関連エラー"""
    pass

class ConfigurationError(TechImgFileError):
    """設定関連エラー"""
    pass
```

### 4.2 エラーハンドラー (`core/error_handler.py`)
```python
class ErrorHandler:
    """集中エラーハンドリング"""
    
    @staticmethod
    def handle_error(error: Exception, context: str = "") -> Tuple[str, str, str]:
        """エラー処理とメッセージ生成"""
        if isinstance(error, NCodeError):
            level = "warning"
            title = "N番号エラー"
            message = str(error)
        elif isinstance(error, RepositoryError):
            level = "error"
            title = "リポジトリエラー"
            message = f"リポジトリ操作に失敗しました: {str(error)}"
        elif isinstance(error, ImageProcessingError):
            level = "error"
            title = "画像処理エラー"
            message = f"画像処理中にエラーが発生しました: {str(error)}"
        elif isinstance(error, ConfigurationError):
            level = "error"
            title = "設定エラー"
            message = f"設定に問題があります: {str(error)}"
        else:
            level = "critical"
            title = "予期せぬエラー"
            message = f"予期せぬエラーが発生しました: {str(error)}"
        
        # ログ出力
        logging.error(f"[{context}] {title}: {message}")
        
        return level, title, message
```

## 5. テスト設計

### 5.1 テスト構成
```
tests/
├── unit/
│   ├── test_n_code_processor.py
│   ├── test_repository_manager.py
│   ├── test_image_processor.py
│   └── test_config_manager.py
├── integration/
│   ├── test_workflow_integration.py
│   └── test_ui_integration.py
└── fixtures/
    ├── test_images/
    └── test_configs/
```

### 5.2 モックとテストダブル
```python
# テスト用モック
class MockGoogleSheetsClient:
    def get_repository_name(self, n_code: str) -> Optional[str]:
        mock_data = {
            "N02279": "test-repository",
            "N12345": "another-repo"
        }
        return mock_data.get(n_code.upper())

class MockGitHubClient:
    def repository_exists(self, repo_name: str) -> bool:
        return repo_name in ["test-repository", "another-repo"]
```

この設計書により、TechImgFile v0.5は保守性・拡張性・テスタビリティを確保した堅牢なアーキテクチャを実現します。