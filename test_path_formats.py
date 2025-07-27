#!/usr/bin/env python3
"""
パス形式の確認
"""
from pathlib import Path

def test_path_formats():
    """複数のパス形式をテスト"""
    
    print("=== パス形式確認テスト ===")
    
    # 複数のパス形式を試す
    paths_to_test = [
        "G:/.shortcut-targets-by-id/0B6euJ_grVeOeMnJLU1IyUWgxeWM/NP-IRD",
        "G:\\.shortcut-targets-by-id\\0B6euJ_grVeOeMnJLU1IyUWgxeWM\\NP-IRD",
        "G:/.shortcut-targets-by-id/0B6euJ_grVeOeMnJLU1IyUWgxeWM/NP-IRD/",
        "/mnt/g/.shortcut-targets-by-id/0B6euJ_grVeOeMnJLU1IyUWgxeWM/NP-IRD"
    ]
    
    for i, path_str in enumerate(paths_to_test, 1):
        print(f"\n{i}. テストパス: {path_str}")
        
        try:
            path = Path(path_str)
            print(f"   正規化後: {path}")
            
            if path.exists():
                print(f"   ✅ 存在する")
                
                # Nフォルダがあるか確認
                n_folders = [d for d in path.iterdir() if d.is_dir() and d.name.startswith('N')]
                print(f"   Nフォルダ数: {len(n_folders)}個")
                
                if n_folders:
                    n_folders.sort()
                    print(f"   最初の5個: {[f.name for f in n_folders[:5]]}")
                
            else:
                print(f"   ❌ 存在しない")
                
        except Exception as e:
            print(f"   ❌ エラー: {e}")
    
    # 設定ファイルのパスも確認
    print(f"\n5. 設定ファイルのパス確認:")
    try:
        from core.word_processor import WordProcessor
        wp = WordProcessor()
        # word_processor.pyで使用されているパスを確認
        print("   word_processor.pyで使用されているパス形式を確認...")
        
    except Exception as e:
        print(f"   WordProcessor読み込みエラー: {e}")

if __name__ == "__main__":
    test_path_formats()