"""
TechBridge ProjectInitializer - バージョン管理ユーティリティ
バージョンの自動増分と管理を行う
"""

import re
from pathlib import Path
from typing import Tuple

class VersionManager:
    """バージョン管理クラス"""
    
    def __init__(self, main_file: str = "main_exe.py"):
        self.main_file = Path(main_file)
        
    def get_current_version(self) -> str:
        """現在のバージョンを取得"""
        if not self.main_file.exists():
            raise FileNotFoundError(f"{self.main_file} not found")
        
        content = self.main_file.read_text(encoding='utf-8')
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        
        if match:
            return match.group(1)
        else:
            raise ValueError("Version not found in main_exe.py")
    
    def increment_version(self, increment_type: str = "minor") -> str:
        """バージョンを増分"""
        current = self.get_current_version()
        major, minor = self._parse_version(current)
        
        if increment_type == "major":
            new_version = f"{major + 1}.0"
        elif increment_type == "minor":
            new_version = f"{major}.{minor + 1}"
        else:
            raise ValueError("increment_type must be 'major' or 'minor'")
        
        self._update_version_in_file(new_version)
        return new_version
    
    def _parse_version(self, version: str) -> Tuple[int, int]:
        """バージョン文字列を解析"""
        parts = version.split('.')
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
        else:
            raise ValueError(f"Invalid version format: {version}")
    
    def _update_version_in_file(self, new_version: str):
        """ファイル内のバージョンを更新"""
        content = self.main_file.read_text(encoding='utf-8')
        
        # __version__ の更新
        content = re.sub(
            r'__version__\s*=\s*["\']([^"\']+)["\']',
            f'__version__ = "{new_version}"',
            content
        )
        
        # ドキュメント内のバージョンも更新
        content = re.sub(
            r'エントリーポイント v[\d.]+',
            f'エントリーポイント v{new_version}',
            content
        )
        
        self.main_file.write_text(content, encoding='utf-8')
        print(f"✅ Version updated to v{new_version}")
    
    def get_version_info(self) -> dict:
        """バージョン情報を取得"""
        current = self.get_current_version()
        major, minor = self._parse_version(current)
        
        return {
            "current": current,
            "major": major,
            "minor": minor,
            "next_minor": f"{major}.{minor + 1}",
            "next_major": f"{major + 1}.0"
        }

def main():
    """コマンドライン実行用"""
    import sys
    
    vm = VersionManager()
    
    if len(sys.argv) == 1:
        # 現在のバージョン情報を表示
        info = vm.get_version_info()
        print("=" * 50)
        print("TechBridge ProjectInitializer - Version Info")
        print("=" * 50)
        print(f"Current Version: v{info['current']}")
        print(f"Next Minor:      v{info['next_minor']}")
        print(f"Next Major:      v{info['next_major']}")
        print()
        print("Usage:")
        print("  python version_manager.py minor   # 0.1増加")
        print("  python version_manager.py major   # 1.0増加")
        
    elif len(sys.argv) == 2:
        increment_type = sys.argv[1].lower()
        if increment_type in ["minor", "major"]:
            old_version = vm.get_current_version()
            new_version = vm.increment_version(increment_type)
            print(f"Version updated: v{old_version} → v{new_version}")
        else:
            print("Error: increment_type must be 'minor' or 'major'")
            sys.exit(1)
    else:
        print("Error: Too many arguments")
        sys.exit(1)

if __name__ == "__main__":
    main()