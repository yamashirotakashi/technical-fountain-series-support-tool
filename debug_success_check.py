#!/usr/bin/env python3
"""
成功パターンのデバッグチェック
"""

# upload_result.htmlの内容を読み込む
with open("upload_result.html", "r", encoding="utf-8") as f:
    content = f.read()

print("=== HTMLコンテンツの解析 ===")
print(f"文字数: {len(content)}")
print()

# バイト列として表示
print("=== 最初の200バイト ===")
print(content[:200])
print()

# 文字化けしている文字列を探す
if "完了" in content:
    print("✅ '完了' が見つかりました")
    
if "アップロード" in content:
    print("✅ 'アップロード' が見つかりました")

# 文字化けパターンを探す
mojibake_patterns = [
    "ã¢ããã­ã¼ããå®äºãã¾ããã",
    "変換",
    "完了"
]

for pattern in mojibake_patterns:
    if pattern in content:
        print(f"✅ パターン検出: {pattern}")
        # パターンの周辺を表示
        idx = content.find(pattern)
        print(f"   位置: {idx}")
        print(f"   周辺: ...{content[max(0, idx-20):idx+len(pattern)+20]}...")