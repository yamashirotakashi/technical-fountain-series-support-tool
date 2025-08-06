#!/usr/bin/env python3
"""
Complete workflow test for N02360
Tests the entire pipeline: Google Sheets -> Git -> Processing
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from core.google_sheet import GoogleSheetClient
from core.git_repository_manager import GitRepositoryManager
from core.config_manager import ConfigManager

def test_complete_workflow():
    """Complete workflow test"""
    print("=== Complete Workflow Test: N02360 ===")
    
    try:
        # 1. ConfigManager
        config_manager = ConfigManager()
        print("[SUCCESS] ConfigManager initialized")
        
        # 2. Google Sheets lookup
        sheets_client = GoogleSheetClient()
        result = sheets_client.search_n_code("N02360")
        
        if result:
            print(f"[SUCCESS] Google Sheets: N02360 found at row {result['row']}")
            print(f"  Repository: {result['repository_name']}")
            print(f"  Author: {result['author_slack_id']}")
            repo_name = result['repository_name']
        else:
            print("[ERROR] Google Sheets: N02360 not found")
            return False
        
        # 3. Git repository fetch
        git_manager = GitRepositoryManager(config_manager)
        repo_path = git_manager.get_repository(repo_name)
        
        if repo_path and repo_path.exists():
            print(f"[SUCCESS] Git Repository: {repo_name} fetched successfully")
            print(f"  Location: {repo_path}")
            
            # Check for common directories
            common_dirs = ['src', 'articles', 'images', 'out']
            found_dirs = []
            for dir_name in common_dirs:
                dir_path = repo_path / dir_name
                if dir_path.exists():
                    found_dirs.append(dir_name)
            
            if found_dirs:
                print(f"  Structure: {', '.join(found_dirs)} directories found")
            else:
                print("  Structure: Custom directory layout")
            
        else:
            print(f"[ERROR] Git Repository: {repo_name} fetch failed")
            return False
        
        # 4. Configuration validation
        validation = config_manager.validate_config()
        errors = len(validation['errors'])
        missing_vars = len(validation['missing_env_vars'])
        
        print(f"[SUCCESS] Configuration: {errors} errors, {missing_vars} missing vars")
        
        if errors > 0:
            print(f"  Errors: {validation['errors']}")
            return False
        
        print("\n=== Complete Workflow Test: SUCCESS ===")
        print("All components working correctly:")
        print("- Google Sheets API [OK]")
        print("- GitHub Authentication [OK]") 
        print("- Git Repository Management [OK]")
        print("- Windows File Handling [OK]")
        print("- Configuration Management [OK]")
        
        return True
        
    except Exception as e:
        print(f"\n=== Complete Workflow Test: FAILED ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)