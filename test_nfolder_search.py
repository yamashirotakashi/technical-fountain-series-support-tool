#!/usr/bin/env python3
"""
Nフォルダ検索の修正テスト
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.slack_pdf_poster import SlackPDFPoster

def test_nfolder_search():
    """Nフォルダ検索テスト"""
    
    print("=== Nフォルダ検索修正テスト ===")
    
    try:
        # SlackPDFPosterを初期化
        poster = SlackPDFPoster()
        
        # テストするNコード
        test_codes = ["N01798", "N09999", "N00001", "N99999"]
        
        print("\n1. Nフォルダ検索テスト:")
        for ncode in test_codes:
            print(f"\n  {ncode}:")
            
            # Nフォルダ検索
            n_folder = poster.find_ncode_folder(ncode)
            if n_folder:
                print(f"    ✅ Nフォルダ発見: {n_folder}")
                
                # outフォルダの確認
                out_folder = n_folder / "out"
                if out_folder.exists():
                    print(f"    ✅ outフォルダ存在: {out_folder}")
                    
                    # PDFファイルの確認
                    pdf_files = list(out_folder.glob("*.pdf"))
                    if pdf_files:
                        print(f"    ✅ PDFファイル発見: {len(pdf_files)}個")
                        for pdf in pdf_files:
                            print(f"      - {pdf.name}")
                    else:
                        print("    ❌ PDFファイルなし")
                else:
                    print(f"    ❌ outフォルダなし")
            else:
                print(f"    ❌ Nフォルダなし")
        
        print("\n2. 統合PDFファイル検索テスト:")
        for ncode in test_codes:
            print(f"\n  {ncode}:")
            pdf_path = poster.find_pdf_file(ncode)
            if pdf_path:
                print(f"    ✅ PDF発見: {pdf_path}")
            else:
                print(f"    ❌ PDF見つからず")
        
        print("\n3. ベースパス確認:")
        base_path = Path("G:/.shortcut-targets-by-id/0B6euJ_grVeOeMnJLU1IyUWgxeWM/NP-IRD")
        if base_path.exists():
            print(f"  ✅ ベースパス存在: {base_path}")
            
            # NP-IRD配下のNフォルダ一覧（最初の10個）
            n_folders = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith('N')]
            n_folders.sort()
            
            print(f"  Nフォルダ数: {len(n_folders)}個")
            print("  最初の10個:")
            for folder in n_folders[:10]:
                print(f"    - {folder.name}")
            
            if len(n_folders) > 10:
                print(f"    ... (他{len(n_folders)-10}個)")
                
        else:
            print(f"  ❌ ベースパス不存在: {base_path}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nfolder_search()