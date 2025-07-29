#!/usr/bin/env python3
"""
視覚的判断データを更新するスクリプト
"""

import json
from pathlib import Path

def update_judgments():
    """sample4.pdfの検出漏れページを追加"""
    config_file = Path("visual_judgments.json")
    
    # 既存データを読み込むか、新規作成
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            'known_overflows': {
                'sample.pdf': [48],
                'sample2.pdf': [128, 129],
                'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124]
            },
            'false_positives': {
                'sample3.pdf': [89, 105]
            }
        }
    
    # sample4.pdfの検出漏れページを追加
    if 'sample4.pdf' not in data['known_overflows']:
        data['known_overflows']['sample4.pdf'] = []
    
    # ページ30, 38, 76を追加
    for page in [30, 38, 76]:
        if page not in data['known_overflows']['sample4.pdf']:
            data['known_overflows']['sample4.pdf'].append(page)
    
    # ソート
    data['known_overflows']['sample4.pdf'].sort()
    
    # 保存
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("視覚的判断データを更新しました:")
    print(f"sample4.pdf: {data['known_overflows']['sample4.pdf']}")

if __name__ == "__main__":
    update_judgments()