"""GitHub繝ｪ繝昴ず繝医Μ邂｡逅・Δ繧ｸ繝･繝ｼ繝ｫ"""
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
    """GitHub繝ｪ繝昴ず繝医Μ縺ｮ繧ｯ繝ｭ繝ｼ繝ｳ縺ｨ繧ｭ繝｣繝・す繝･邂｡逅・ｒ陦後≧繧ｯ繝ｩ繧ｹ"""
    
    def __init__(self):
        """GitRepositoryManager繧貞・譛溷喧"""
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # 繧ｭ繝｣繝・す繝･繝・ぅ繝ｬ繧ｯ繝医Μ縺ｮ險ｭ螳・        self.cache_dir = Path.home() / ".techzip" / "repo_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # GitHub險ｭ螳壹・隱ｭ縺ｿ霎ｼ縺ｿ
        self.github_user = self.config.get('github.default_user', 'irdtechbook')
        self.github_token = os.environ.get('GITHUB_TOKEN', self.config.get('github.token'))
        
        self.logger.info(f"GitRepositoryManager蛻晄悄蛹門ｮ御ｺ・(繧ｭ繝｣繝・す繝･: {self.cache_dir})")
    
    def get_repository(self, repo_name: str, force_update: bool = False) -> Optional[Path]:
        """
        繝ｪ繝昴ず繝医Μ繧貞叙蠕暦ｼ医Μ繝｢繝ｼ繝亥━蜈医√Ο繝ｼ繧ｫ繝ｫ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ・・        
        Args:
            repo_name: 繝ｪ繝昴ず繝医Μ蜷・            force_update: 蠑ｷ蛻ｶ逧・↓譛譁ｰ迚医ｒ蜿門ｾ励☆繧九°
        
        Returns:
            繝ｪ繝昴ず繝医Μ縺ｮ繝ｭ繝ｼ繧ｫ繝ｫ繝代せ・亥叙蠕怜､ｱ謨玲凾縺ｯNone・・        """
        self.logger.info(f"繝ｪ繝昴ず繝医Μ蜿門ｾ鈴幕蟋・ {repo_name}")
        
        # 縺ｾ縺壹Μ繝｢繝ｼ繝医°繧牙叙蠕励ｒ隧ｦ縺ｿ繧・        remote_path = self._get_from_remote(repo_name, force_update)
        if remote_path:
            return remote_path
        
        # 繝ｪ繝｢繝ｼ繝亥叙蠕怜､ｱ謨玲凾縺ｯ繝ｭ繝ｼ繧ｫ繝ｫ縺ｫ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ
        self.logger.info("繝ｪ繝｢繝ｼ繝亥叙蠕怜､ｱ謨励√Ο繝ｼ繧ｫ繝ｫ縺ｫ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ")
        local_path = self._get_from_local(repo_name)
        
        return local_path
    
    def _get_from_remote(self, repo_name: str, force_update: bool = False) -> Optional[Path]:
        """
        GitHub縺九ｉ繝ｪ繝昴ず繝医Μ繧貞叙蠕・        
        Args:
            repo_name: 繝ｪ繝昴ず繝医Μ蜷・            force_update: 蠑ｷ蛻ｶ譖ｴ譁ｰ繝輔Λ繧ｰ
        
        Returns:
            繧ｯ繝ｭ繝ｼ繝ｳ縺励◆繝ｪ繝昴ず繝医Μ縺ｮ繝代せ・亥､ｱ謨玲凾縺ｯNone・・        """
        cache_path = self.cache_dir / repo_name
        
        # 繧ｭ繝｣繝・す繝･縺悟ｭ伜惠縺励∝ｼｷ蛻ｶ譖ｴ譁ｰ縺ｧ縺ｪ縺・ｴ蜷・        if cache_path.exists() and not force_update:
            self.logger.info(f"繧ｭ繝｣繝・す繝･繧剃ｽｿ逕ｨ: {cache_path}")
            # git pull縺ｧ譖ｴ譁ｰ繧定ｩｦ縺ｿ繧・            if self._update_repository(cache_path):
                return cache_path
        
        # 譁ｰ隕上け繝ｭ繝ｼ繝ｳ縺ｾ縺溘・蠑ｷ蛻ｶ譖ｴ譁ｰ
        return self._clone_repository(repo_name, cache_path)
    
    def _clone_repository(self, repo_name: str, target_path: Path) -> Optional[Path]:
        """
        繝ｪ繝昴ず繝医Μ繧偵け繝ｭ繝ｼ繝ｳ
        
        Args:
            repo_name: 繝ｪ繝昴ず繝医Μ蜷・            target_path: 繧ｯ繝ｭ繝ｼ繝ｳ蜈医・繝代せ
        
        Returns:
            繧ｯ繝ｭ繝ｼ繝ｳ縺励◆繝代せ・亥､ｱ謨玲凾縺ｯNone・・        """
        # 譌｢蟄倥・繝・ぅ繝ｬ繧ｯ繝医Μ縺後≠繧句ｴ蜷医・蜑企勁
        if target_path.exists():
            shutil.rmtree(target_path)
        
        # GitHub URL縺ｮ讒狗ｯ・        if self.github_token:
            # 繝医・繧ｯ繝ｳ縺後≠繧句ｴ蜷医・隱崎ｨｼ莉倥″URL
            clone_url = f"https://{self.github_token}@github.com/{self.github_user}/{repo_name}.git"
        else:
            # 繝医・繧ｯ繝ｳ縺後↑縺・ｴ蜷医・騾壼ｸｸ縺ｮURL
            clone_url = f"https://github.com/{self.github_user}/{repo_name}.git"
        
        try:
            self.logger.info(f"繝ｪ繝昴ず繝医Μ繧偵け繝ｭ繝ｼ繝ｳ荳ｭ: {repo_name}")
            
            # 繧ｻ繧ｭ繝･繝ｪ繝・ぅ縺ｮ縺溘ａ縲√ヨ繝ｼ繧ｯ繝ｳ繧偵・繧ｹ繧ｯ縺励※繝ｭ繧ｰ蜃ｺ蜉・            safe_url = clone_url.replace(self.github_token, "***") if self.github_token else clone_url
            self.logger.debug(f"Clone URL: {safe_url}")
            
            # git clone繧貞ｮ溯｡・            result = subprocess.run(
                ["git", "clone", clone_url, str(target_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5蛻・・繧ｿ繧､繝繧｢繧ｦ繝・            )
            
            if result.returncode == 0:
                self.logger.info(f"繧ｯ繝ｭ繝ｼ繝ｳ謌仙粥: {target_path}")
                return target_path
            else:
                self.logger.error(f"繧ｯ繝ｭ繝ｼ繝ｳ螟ｱ謨・ {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("繧ｯ繝ｭ繝ｼ繝ｳ繧ｿ繧､繝繧｢繧ｦ繝・)
            return None
        except Exception as e:
            self.logger.error(f"繧ｯ繝ｭ繝ｼ繝ｳ繧ｨ繝ｩ繝ｼ: {e}")
            return None
    
    def _update_repository(self, repo_path: Path) -> bool:
        """
        譌｢蟄倥・繝ｪ繝昴ず繝医Μ繧呈峩譁ｰ
        
        Args:
            repo_path: 繝ｪ繝昴ず繝医Μ縺ｮ繝代せ
        
        Returns:
            譖ｴ譁ｰ謌仙粥譎５rue
        """
        try:
            self.logger.info(f"繝ｪ繝昴ず繝医Μ繧呈峩譁ｰ荳ｭ: {repo_path}")
            
            # git pull繧貞ｮ溯｡・            result = subprocess.run(
                ["git", "pull"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=120  # 2蛻・・繧ｿ繧､繝繧｢繧ｦ繝・            )
            
            if result.returncode == 0:
                self.logger.info("繝ｪ繝昴ず繝医Μ譖ｴ譁ｰ謌仙粥")
                return True
            else:
                self.logger.warning(f"繝ｪ繝昴ず繝医Μ譖ｴ譁ｰ螟ｱ謨・ {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"繝ｪ繝昴ず繝医Μ譖ｴ譁ｰ繧ｨ繝ｩ繝ｼ: {e}")
            return False
    
    def _get_from_local(self, repo_name: str) -> Optional[Path]:
        """
        繝ｭ繝ｼ繧ｫ繝ｫGoogle Drive縺九ｉ繝ｪ繝昴ず繝医Μ繧貞叙蠕暦ｼ医ヵ繧ｩ繝ｼ繝ｫ繝舌ャ繧ｯ・・        
        Args:
            repo_name: 繝ｪ繝昴ず繝医Μ蜷・        
        Returns:
            繝ｭ繝ｼ繧ｫ繝ｫ繝ｪ繝昴ず繝医Μ縺ｮ繝代せ・郁ｦ九▽縺九ｉ縺ｪ縺・ｴ蜷医・None・・        """
        base_path = Path(self.config.get('paths.git_base'))
        self.logger.info(f"繝ｭ繝ｼ繧ｫ繝ｫ讀懃ｴ｢: {repo_name} in {base_path}")
        
        if not base_path.exists():
            self.logger.error(f"繝ｭ繝ｼ繧ｫ繝ｫ繝吶・繧ｹ繝代せ縺悟ｭ伜惠縺励∪縺帙ｓ: {base_path}")
            return None
        
        # 逶ｴ謗･縺ｮ繝代せ繧偵メ繧ｧ繝・け
        repo_path = base_path / repo_name
        if repo_path.exists() and repo_path.is_dir():
            self.logger.info(f"繝ｭ繝ｼ繧ｫ繝ｫ繝ｪ繝昴ず繝医Μ繧堤匱隕・ {repo_path}")
            return repo_path
        
        # 繧ｵ繝悶ョ繧｣繝ｬ繧ｯ繝医Μ繧よ､懃ｴ｢
        for item in base_path.iterdir():
            if item.is_dir() and item.name == repo_name:
                self.logger.info(f"繝ｭ繝ｼ繧ｫ繝ｫ繝ｪ繝昴ず繝医Μ繧堤匱隕・ {item}")
                return item
        
        self.logger.warning(f"繝ｭ繝ｼ繧ｫ繝ｫ繝ｪ繝昴ず繝医Μ縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ: {repo_name}")
        return None
    
    def clear_cache(self, repo_name: Optional[str] = None):
        """
        繧ｭ繝｣繝・す繝･繧偵け繝ｪ繧｢
        
        Args:
            repo_name: 迚ｹ螳壹・繝ｪ繝昴ず繝医Μ蜷搾ｼ育怐逡･譎ゅ・蜈ｨ繧ｭ繝｣繝・す繝･・・        """
        if repo_name:
            cache_path = self.cache_dir / repo_name
            if cache_path.exists():
                shutil.rmtree(cache_path)
                self.logger.info(f"繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繧｢: {repo_name}")
        else:
            # 蜈ｨ繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繧｢
            for item in self.cache_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
            self.logger.info("蜈ｨ繧ｭ繝｣繝・す繝･繧偵け繝ｪ繧｢縺励∪縺励◆")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        繧ｭ繝｣繝・す繝･諠・ｱ繧貞叙蠕・        
        Returns:
            繧ｭ繝｣繝・す繝･諠・ｱ縺ｮ霎樊嶌
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