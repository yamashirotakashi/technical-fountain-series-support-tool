"""繝輔ぃ繧､繝ｫ謫堺ｽ懃ｮ｡逅・Δ繧ｸ繝･繝ｼ繝ｫ"""
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
    """繝輔ぃ繧､繝ｫ謫堺ｽ懊ｒ邂｡逅・☆繧九け繝ｩ繧ｹ"""
    
    def __init__(self):
        """FileManager繧貞・譛溷喧"""
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.logger.info(f"荳譎ゅョ繧｣繝ｬ繧ｯ繝医Μ繧剃ｽ懈・: {self.temp_dir}")
        
        # GitRepositoryManager繧貞・譛溷喧
        self.git_manager = GitRepositoryManager()
        
        # 繝輔か繝ｫ繝險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ繝代せ
        self.settings_file = Path.home() / ".techzip" / "folder_settings.json"
    
    def find_repository_folder(self, repo_name: str, prefer_remote: bool = True) -> Optional[Path]:
        """
        繝ｪ繝昴ず繝医Μ繝輔か繝ｫ繝繧呈､懃ｴ｢・医Μ繝｢繝ｼ繝亥━蜈医√Ο繝ｼ繧ｫ繝ｫ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ・・        
        Args:
            repo_name: 繝ｪ繝昴ず繝医Μ蜷・            prefer_remote: 繝ｪ繝｢繝ｼ繝医ｒ蜆ｪ蜈医☆繧九°・医ョ繝輔か繝ｫ繝・ True・・        
        Returns:
            繝ｪ繝昴ず繝医Μ繝輔か繝ｫ繝縺ｮ繝代せ・郁ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷医・None・・        """
        if prefer_remote:
            # 繝ｪ繝｢繝ｼ繝医Μ繝昴ず繝医Μ縺九ｉ蜿門ｾ励ｒ隧ｦ縺ｿ繧・            self.logger.info(f"繝ｪ繝｢繝ｼ繝医Μ繝昴ず繝医Μ縺九ｉ蜿門ｾ励ｒ隧ｦ陦・ {repo_name}")
            repo_path = self.git_manager.get_repository(repo_name)
            
            if repo_path:
                self.logger.info(f"繝ｪ繝｢繝ｼ繝医Μ繝昴ず繝医Μ繧剃ｽｿ逕ｨ: {repo_path}")
                return repo_path
            else:
                self.logger.warning("繝ｪ繝｢繝ｼ繝亥叙蠕怜､ｱ謨励√Ο繝ｼ繧ｫ繝ｫ縺ｫ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ")
        
        # 繝ｭ繝ｼ繧ｫ繝ｫ縺九ｉ讀懃ｴ｢・医ヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ縺ｾ縺溘・prefer_remote=False縺ｮ蝣ｴ蜷茨ｼ・        base_path = Path(self.config.get('paths.git_base'))
        self.logger.info(f"繝ｭ繝ｼ繧ｫ繝ｫ繝ｪ繝昴ず繝医Μ讀懃ｴ｢: {repo_name} in {base_path}")
        
        if not base_path.exists():
            self.logger.error(f"繝吶・繧ｹ繝代せ縺悟ｭ伜惠縺励∪縺帙ｓ: {base_path}")
            return None
        
        # 逶ｴ謗･縺ｮ繝代せ繧偵メ繧ｧ繝・け
        repo_path = base_path / repo_name
        if repo_path.exists() and repo_path.is_dir():
            self.logger.info(f"繝ｭ繝ｼ繧ｫ繝ｫ繝ｪ繝昴ず繝医Μ繝輔か繝ｫ繝繧堤匱隕・ {repo_path}")
            return repo_path
        
        # 繧ｵ繝悶ョ繧｣繝ｬ繧ｯ繝医Μ繧よ､懃ｴ｢
        for item in base_path.iterdir():
            if item.is_dir() and item.name == repo_name:
                self.logger.info(f"繝ｭ繝ｼ繧ｫ繝ｫ繝ｪ繝昴ず繝医Μ繝輔か繝ｫ繝繧堤匱隕・ {item}")
                return item
        
        self.logger.warning(f"繝ｪ繝昴ず繝医Μ繝輔か繝ｫ繝縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ: {repo_name}")
        return None
    
    def find_work_folder(self, repo_path: Path) -> Optional[Path]:
        """
        菴懈･ｭ繝輔か繝ｫ繝・・re, config.yml, catalog.yml繧貞性繧・峨ｒ讀懃ｴ｢
        
        Args:
            repo_path: 繝ｪ繝昴ず繝医Μ縺ｮ繝代せ
        
        Returns:
            菴懈･ｭ繝輔か繝ｫ繝縺ｮ繝代せ・郁ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷医・None・・        """
        self.logger.info(f"菴懈･ｭ繝輔か繝ｫ繝讀懃ｴ｢髢句ｧ・ {repo_path}")
        
        required_files = {'config.yml', 'catalog.yml'}
        
        # 繝ｪ繝昴ず繝医Μ逶ｴ荳九ｒ繝√ぉ繝・け
        if self._check_work_folder(repo_path, required_files):
            return repo_path
        
        # 繧ｵ繝悶ョ繧｣繝ｬ繧ｯ繝医Μ繧呈､懃ｴ｢・域怙螟ｧ2髫主ｱ､縺ｾ縺ｧ・・        for root, dirs, files in os.walk(repo_path):
            # 豺ｱ縺募宛髯・            depth = len(Path(root).relative_to(repo_path).parts)
            if depth > 2:
                dirs.clear()
                continue
            
            path = Path(root)
            if self._check_work_folder(path, required_files):
                self.logger.info(f"菴懈･ｭ繝輔か繝ｫ繝繧堤匱隕・ {path}")
                return path
        
        self.logger.warning("菴懈･ｭ繝輔か繝ｫ繝縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ")
        return None
    
    def _check_work_folder(self, path: Path, required_files: set) -> bool:
        """
        繝輔か繝ｫ繝縺御ｽ懈･ｭ繝輔か繝ｫ繝縺ｮ譚｡莉ｶ繧呈ｺ縺溘☆縺九メ繧ｧ繝・け
        
        Args:
            path: 繝√ぉ繝・け縺吶ｋ繝代せ
            required_files: 蠢・医ヵ繧｡繧､繝ｫ縺ｮ繧ｻ繝・ヨ
        
        Returns:
            譚｡莉ｶ繧呈ｺ縺溘☆蝣ｴ蜷・rue
        """
        if not path.is_dir():
            return False
        
        # .re繝輔ぃ繧､繝ｫ縺ｮ蟄伜惠遒ｺ隱・        has_re_file = any(f.suffix == '.re' for f in path.iterdir() if f.is_file())
        
        # 蠢・医ヵ繧｡繧､繝ｫ縺ｮ蟄伜惠遒ｺ隱・        existing_files = {f.name for f in path.iterdir() if f.is_file()}
        has_required_files = required_files.issubset(existing_files)
        
        return has_re_file and has_required_files
    
    def create_zip(self, folder_path: Path, zip_name: Optional[str] = None) -> Path:
        """
        繝輔か繝ｫ繝繧短IP蝨ｧ邵ｮ
        
        Args:
            folder_path: 蝨ｧ邵ｮ縺吶ｋ繝輔か繝ｫ繝縺ｮ繝代せ
            zip_name: ZIP繝輔ぃ繧､繝ｫ蜷搾ｼ育怐逡･譎ゅ・繝輔か繝ｫ繝蜷・zip・・        
        Returns:
            菴懈・縺輔ｌ縺飮IP繝輔ぃ繧､繝ｫ縺ｮ繝代せ
        """
        if zip_name is None:
            zip_name = f"{folder_path.name}.zip"
        
        zip_path = self.temp_dir / zip_name
        self.logger.info(f"ZIP菴懈・髢句ｧ・ {folder_path} -> {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(folder_path.parent)
                    zipf.write(file_path, arcname)
        
        self.logger.info(f"ZIP菴懈・螳御ｺ・ {zip_path} (繧ｵ繧､繧ｺ: {zip_path.stat().st_size:,} bytes)")
        return zip_path
    
    def extract_zip(self, zip_path: Path, target_path: Path) -> List[Path]:
        """
        ZIP繝輔ぃ繧､繝ｫ繧貞ｱ暮幕
        
        Args:
            zip_path: ZIP繝輔ぃ繧､繝ｫ縺ｮ繝代せ
            target_path: 螻暮幕蜈医・繝代せ
        
        Returns:
            螻暮幕縺輔ｌ縺溘ヵ繧｡繧､繝ｫ縺ｮ繝代せ繝ｪ繧ｹ繝・        """
        self.logger.info(f"ZIP螻暮幕髢句ｧ・ {zip_path} -> {target_path}")
        
        # 繧ｿ繝ｼ繧ｲ繝・ヨ繝・ぅ繝ｬ繧ｯ繝医Μ繧剃ｽ懈・
        target_path.mkdir(parents=True, exist_ok=True)
        
        extracted_files = []
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for info in zipf.filelist:
                extracted_path = target_path / info.filename
                zipf.extract(info, target_path)
                if not info.is_dir():
                    extracted_files.append(extracted_path)
        
        self.logger.info(f"ZIP螻暮幕螳御ｺ・ {len(extracted_files)}蛟九・繝輔ぃ繧､繝ｫ繧貞ｱ暮幕")
        return extracted_files
    
    def get_output_folder(self, n_code: str) -> Path:
        """
        蜃ｺ蜉帛・繝輔か繝ｫ繝縺ｮ繝代せ繧貞叙蠕・        
        Args:
            n_code: N繧ｳ繝ｼ繝・        
        Returns:
            蜃ｺ蜉帛・繝輔か繝ｫ繝縺ｮ繝代せ
        """
        output_base = Path(self.config.get('paths.output_base'))
        output_folder = output_base / n_code / "譛ｬ譁・
        return output_folder
    
    def cleanup_temp_files(self):
        """荳譎ゅヵ繧｡繧､繝ｫ繧偵け繝ｪ繝ｼ繝ｳ繧｢繝・・"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.logger.info("荳譎ゅヵ繧｡繧､繝ｫ繧偵け繝ｪ繝ｼ繝ｳ繧｢繝・・縺励∪縺励◆")
        except Exception as e:
            self.logger.error(f"荳譎ゅヵ繧｡繧､繝ｫ縺ｮ繧ｯ繝ｪ繝ｼ繝ｳ繧｢繝・・縺ｫ螟ｱ謨・ {e}")
    
    def _load_folder_settings(self) -> Dict[str, str]:
        """菫晏ｭ倥＆繧後◆繝輔か繝ｫ繝險ｭ螳壹ｒ隱ｭ縺ｿ霎ｼ繧"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"繝輔か繝ｫ繝險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ隱ｭ縺ｿ霎ｼ縺ｿ繧ｨ繝ｩ繝ｼ: {e}")
        return {}
    
    def get_saved_work_folder(self, repo_name: str, repo_path: Path) -> Optional[Path]:
        """
        菫晏ｭ倥＆繧後◆菴懈･ｭ繝輔か繝ｫ繝險ｭ螳壹ｒ蜿門ｾ・        
        Args:
            repo_name: 繝ｪ繝昴ず繝医Μ蜷・            repo_path: 繝ｪ繝昴ず繝医Μ縺ｮ繝ｫ繝ｼ繝医ヱ繧ｹ
            
        Returns:
            菫晏ｭ倥＆繧後◆菴懈･ｭ繝輔か繝ｫ繝縺ｮ繝代せ・亥ｭ伜惠縺励↑縺・ｴ蜷医・None・・        """
        settings = self._load_folder_settings()
        
        if repo_name in settings:
            saved_path = Path(settings[repo_name])
            # 繝代せ縺悟ｭ伜惠縺励√Μ繝昴ず繝医Μ蜀・↓縺ゅｋ縺薙→繧堤｢ｺ隱・            if saved_path.exists() and str(saved_path).startswith(str(repo_path)):
                self.logger.info(f"菫晏ｭ倥＆繧後◆菴懈･ｭ繝輔か繝ｫ繝繧剃ｽｿ逕ｨ: {saved_path}")
                return saved_path
            else:
                self.logger.warning(f"菫晏ｭ倥＆繧後◆菴懈･ｭ繝輔か繝ｫ繝縺檎┌蜉ｹ: {saved_path}")
        
        return None
    
    def find_work_folder_interactive(self, repo_path: Path, repo_name: str) -> Optional[Path]:
        """
        菴懈･ｭ繝輔か繝ｫ繝繧貞ｯｾ隧ｱ逧・↓讀懃ｴ｢・井ｿ晏ｭ倥＆繧後◆險ｭ螳壹ｒ蜆ｪ蜈茨ｼ・        
        Args:
            repo_path: 繝ｪ繝昴ず繝医Μ縺ｮ繝代せ
            repo_name: 繝ｪ繝昴ず繝医Μ蜷・            
        Returns:
            驕ｸ謚槭＆繧後◆菴懈･ｭ繝輔か繝ｫ繝縺ｮ繝代せ・医く繝｣繝ｳ繧ｻ繝ｫ縺輔ｌ縺溷ｴ蜷医・None・・        """
        # 縺ｾ縺壻ｿ晏ｭ倥＆繧後◆險ｭ螳壹ｒ遒ｺ隱・        saved_folder = self.get_saved_work_folder(repo_name, repo_path)
        
        # 菫晏ｭ倥＆繧後◆險ｭ螳壹′縺ｪ縺・ｴ蜷医・閾ｪ蜍墓､懷・繧定ｩｦ縺ｿ繧・        if not saved_folder:
            saved_folder = self.find_work_folder(repo_path)
        
        return saved_folder
    
    def __del__(self):
        """繝・せ繝医Λ繧ｯ繧ｿ"""
        self.cleanup_temp_files()