#!/usr/bin/env python3
"""
手動招待用のチャネルリスト生成
"""

def main():
    print("=== 技術の泉シリーズ Bot招待リスト ===\n")
    print("以下のチャネルにBotを招待してください：\n")
    
    # 既知のチャネルパターン（Nコードに基づく）
    print("【推定されるチャネル名】")
    print("※実際のチャネル名と異なる場合があります")
    print("-" * 50)
    
    # サンプルチャネル（実際のNコードに基づいて追加）
    sample_channels = [
        "n1234-example-book",
        "n5678-another-book",
        "n9012-tech-book",
        # 実際のプロジェクトに合わせて追加
    ]
    
    print("📝 手動招待手順：")
    print("1. Slackで各チャネルを開く")
    print("2. チャネル名をクリック")
    print("3. 「メンバーを追加」または「Add people」")
    print("4. @techzip_pdf_bot を検索")
    print("5. 「追加」をクリック")
    print("\n" + "-" * 50)
    
    print("\n💡 ヒント：")
    print("- プライベートチャネルは 'n' または 'N' で始まることが多い")
    print("- 技術の泉シリーズのチャネルは通常 'nXXXX-' の形式")
    print("- 招待後、以下のコマンドで確認：")
    print("  python check_all_channels_detailed.py")
    
    print("\n📊 現在の参加状況：")
    print("- n9999-bottest ✅（テスト用）")
    print("- その他のチャネル：未参加")
    
    # CSV形式で出力（コピペ用）
    print("\n【管理者への依頼テンプレート】")
    print("-" * 50)
    print("技術の泉シリーズのSlack Botを以下のチャネルに招待お願いします：")
    print("")
    print("Bot名: @techzip_pdf_bot")
    print("表示名: 技術の泉シリーズ")
    print("")
    print("対象チャネル：")
    print("- すべての 'n' で始まるプライベートチャネル")
    print("- 特に書籍制作用のチャネル（nXXXX-書籍名）")
    print("")
    print("招待方法：")
    print("1. 各チャネルで /invite @techzip_pdf_bot")
    print("2. またはチャネル設定から「メンバーを追加」")
    print("-" * 50)

if __name__ == "__main__":
    main()