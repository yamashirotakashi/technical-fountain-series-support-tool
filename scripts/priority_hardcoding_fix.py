#!/usr/bin/env python3
"""
重要なハードコーディング修正スクリプト
検出された59個のハードコーディングから最も重要なものを優先的に修正
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.slack_pdf_poster import HardcodingDetector, ConfigManager
import re


class PriorityHardcodingFixer:
    """重要なハードコーディングを優先的に修正"""
    
    def __init__(self):
        self.detector = HardcodingDetector()
        self.config_manager = ConfigManager()
        
        # 重要度の高いハードコーディングパターン
        self.priority_patterns = {
            'nextpub_base_url': {
                'pattern': r'http://trial\.nextpublishing\.jp/upload_46tate/',
                'replacement': 'self.config_manager.get("api.nextpublishing.base_url")',
                'category': 'urls'
            },
            'nextpub_username': {
                'pattern': r'"ep_user"',
                'replacement': 'self.config_manager.get("api.nextpublishing.username")',
                'category': 'credentials'
            },
            'nextpub_password': {
                'pattern': r'"Nn7eUTX5"',
                'replacement': 'self.config_manager.get("api.nextpublishing.password")',
                'category': 'credentials'
            },
            'slack_api_url': {
                'pattern': r'https://slack\.com/api',
                'replacement': 'self.config_manager.get("api.slack.api_base_url")',
                'category': 'urls'
            },
            'timeout_30': {
                'pattern': r'timeout=30',
                'replacement': 'timeout=self.config_manager.get("api.nextpublishing.timeout", 30)',
                'category': 'magic_numbers'
            }
        }
    
    def scan_priority_files(self):
        """重要ファイルのハードコーディングをスキャン"""
        priority_files = [
            Path("src/slack_pdf_poster.py"),
            Path("services/error_check_validator.py"),
            Path("core/api_processor.py"),
            Path("services/nextpublishing_service.py"),
            Path("core/preflight/word2xhtml_scraper.py")
        ]
        
        results = {}
        for file_path in priority_files:
            if file_path.exists():
                scan_result = self.detector.scan_file(file_path)
                if scan_result:
                    results[str(file_path)] = scan_result
                    
        return results
    
    def generate_fix_recommendations(self, scan_results):
        """修正推奨事項を生成"""
        recommendations = []
        
        for file_path, categories in scan_results.items():
            file_recommendations = {
                'file': file_path,
                'fixes': []
            }
            
            # 重要度順に修正を推奨
            for pattern_name, pattern_info in self.priority_patterns.items():
                pattern = pattern_info['pattern']
                replacement = pattern_info['replacement']
                category = pattern_info['category']
                
                if category in categories:
                    for detection in categories[category]:
                        if re.search(pattern, detection):
                            file_recommendations['fixes'].append({
                                'pattern': pattern_name,
                                'original': detection,
                                'suggested_fix': replacement,
                                'category': category,
                                'priority': 'HIGH'
                            })
            
            if file_recommendations['fixes']:
                recommendations.append(file_recommendations)
        
        return recommendations
    
    def apply_basic_fixes(self, file_path, fixes):
        """基本的な修正を適用（デモンストレーション用）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            for fix in fixes:
                pattern = fix['pattern']
                if pattern == 'nextpub_base_url':
                    # 単純な文字列置換として実装（実際は構文解析が必要）
                    old_pattern = r'"http://trial\.nextpublishing\.jp/upload_46tate/"'
                    new_pattern = 'self.config_manager.get("api.nextpublishing.base_url")'
                    if re.search(old_pattern, content):
                        print(f"📝 可能な修正を発見: {file_path}")
                        print(f"   置換前: {old_pattern}")
                        print(f"   置換後: {new_pattern}")
                        modified = True
                        
            return modified
            
        except Exception as e:
            print(f"❌ ファイル修正エラー {file_path}: {e}")
            return False
    
    def run_analysis(self):
        """優先修正分析を実行"""
        print("🔧 重要ハードコーディング修正分析開始")
        print("=" * 60)
        
        # スキャン実行
        print("1️⃣ 重要ファイルスキャン中...")
        scan_results = self.scan_priority_files()
        
        total_detections = sum(
            len(detections) for file_results in scan_results.values()
            for detections in file_results.values()
        )
        print(f"   検出: {total_detections}個のハードコーディング")
        
        # 修正推奨事項生成
        print("\n2️⃣ 修正推奨事項を生成中...")
        recommendations = self.generate_fix_recommendations(scan_results)
        
        high_priority_fixes = sum(
            len(rec['fixes']) for rec in recommendations
        )
        print(f"   高優先度修正: {high_priority_fixes}個")
        
        # 修正推奨の表示
        print("\n3️⃣ 修正推奨事項:")
        print("-" * 40)
        
        for rec in recommendations:
            print(f"\n📄 ファイル: {rec['file']}")
            for fix in rec['fixes']:
                print(f"   🔧 [{fix['priority']}] {fix['pattern']}")
                print(f"      現在: {fix['original']}")
                print(f"      推奨: {fix['suggested_fix']}")
        
        # 修正方針の提示
        print("\n4️⃣ 修正方針:")
        print("-" * 40)
        print("✅ ConfigManagerを各クラスのコンストラクタに追加")
        print("✅ ハードコーディング値をconfig_manager.get()に置換")
        print("✅ デフォルト値を第2引数で指定")
        print("✅ 設定ファイル(techzip_config.yaml)で値を管理")
        
        print("\n5️⃣ 実装例:")
        print("-" * 40)
        print("""
# 修正前:
class NextPublishingService:
    def __init__(self):
        self.base_url = "http://trial.nextpublishing.jp/upload_46tate/"
        self.username = "ep_user"
        self.password = "Nn7eUTX5"

# 修正後:
class NextPublishingService:
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or ConfigManager()
        self.base_url = self.config_manager.get("api.nextpublishing.base_url")
        self.username = self.config_manager.get("api.nextpublishing.username")
        self.password = self.config_manager.get("api.nextpublishing.password")
        """)
        
        print("\n" + "=" * 60)
        print("🎯 重要ハードコーディング修正分析完了")
        print(f"📊 総計: {total_detections}個検出, {high_priority_fixes}個要修正")
        
        return recommendations


def main():
    """メイン実行"""
    fixer = PriorityHardcodingFixer()
    recommendations = fixer.run_analysis()
    
    if recommendations:
        print("\n💡 次のステップ:")
        print("  1. 各クラスにConfigManagerパラメータを追加")
        print("  2. ハードコーディング値をconfig_manager.get()に置換")
        print("  3. テストして動作確認")
        print("  4. 残りのハードコーディングも段階的に修正")
    else:
        print("🎉 重要なハードコーディングは検出されませんでした！")


if __name__ == "__main__":
    main()