#!/usr/bin/env python3
"""
テスト用ZIPファイルを作成
"""
import zipfile
from pathlib import Path

# テストファイルを作成
test_file = Path("test_content.txt")
test_file.write_text("This is a test file for NextPublishing upload verification.\n")

# ZIPファイルを作成
zip_path = Path("test_upload.zip")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(test_file, test_file.name)

print(f"✅ ZIPファイル作成完了: {zip_path}")
print(f"   サイズ: {zip_path.stat().st_size} bytes")

# テストファイルを削除
test_file.unlink()