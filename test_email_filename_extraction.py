#!/usr/bin/env python3
"""メール本文からのファイル名抽出テスト"""
import re
from pathlib import Path

def test_filename_extraction():
    """ファイル名抽出パターンのテスト"""
    
    # テスト用のメール本文サンプル
    test_cases = [
        {
            "name": "パターン1: ファイル名: xxx.docx",
            "body": """
            いつもご利用ありがとうございます。
            
            ファイル名: 04_powershell_sample_advanced.docx
            
            以下のURLからダウンロードしてください。
            http://trial.nextpublishing.jp/upload_46tate/do_download?n=xxx
            """,
            "expected": "04_powershell_sample_advanced.docx"
        },
        {
            "name": "パターン2: xxx.docx の変換",
            "body": """
            05_appendix.docx の変換が完了しました。
            
            ダウンロードURL:
            http://trial.nextpublishing.jp/upload_46tate/do_download?n=yyy
            """,
            "expected": "05_appendix.docx"
        },
        {
            "name": "パターン3: 「xxx.docx」",
            "body": """
            「chapter_01_introduction.docx」のPDF変換結果
            
            URL: http://trial.nextpublishing.jp/upload_46tate/do_download?n=zzz
            """,
            "expected": "chapter_01_introduction.docx"
        },
        {
            "name": "パターン4: \"xxx.docx\"",
            "body": """
            変換ファイル: "02_setup_guide.docx"
            
            ダウンロードリンク: http://trial.nextpublishing.jp/upload_46tate/do_download?n=aaa
            """,
            "expected": "02_setup_guide.docx"
        },
        {
            "name": "パターン5: 単純なdocxファイル名",
            "body": """
            summary_report.docx
            
            http://trial.nextpublishing.jp/upload_46tate/do_download?n=bbb
            """,
            "expected": "summary_report.docx"
        },
        {
            "name": "パターン6: 複数のdocxファイル（最初のもの）",
            "body": """
            本日のファイル:
            - first_file.docx
            - second_file.docx
            
            最初のファイルのURL:
            http://trial.nextpublishing.jp/upload_46tate/do_download?n=ccc
            """,
            "expected": "first_file.docx"
        }
    ]
    
    # core/email_monitor.pyと同じパターンを使用
    patterns = [
        r'(?:ファイル名|File|file)[\s:：]+([^\s]+\.docx)',  # "ファイル名: xxx.docx"
        r'([^\s/]+\.docx)(?=\s*の変換)',  # "xxx.docx の変換"
        r'「([^」]+\.docx)」',  # 「xxx.docx」
        r'"([^"]+\.docx)"',  # "xxx.docx"
        r'([^\s/<>]+\.docx)',  # 単純にdocxファイル名を探す
    ]
    
    print("=" * 80)
    print("メール本文からのファイル名抽出テスト")
    print("=" * 80)
    
    success_count = 0
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print(f"期待される結果: {test['expected']}")
        
        # ファイル名を抽出
        filename = None
        for pattern in patterns:
            match = re.search(pattern, test['body'])
            if match:
                filename = match.group(1)
                break
        
        if filename == test['expected']:
            print(f"✓ 成功: {filename}")
            success_count += 1
        else:
            print(f"✗ 失敗: {filename or '抽出できませんでした'}")
            
            # どのパターンがマッチしたか詳細を表示
            print("  パターンマッチ詳細:")
            for i, pattern in enumerate(patterns, 1):
                match = re.search(pattern, test['body'])
                if match:
                    print(f"    パターン{i}: マッチ → {match.group(1)}")
                else:
                    print(f"    パターン{i}: マッチなし")
    
    print(f"\n結果: {success_count}/{len(test_cases)} 成功")
    
    # 実際のメール本文サンプルがある場合のテスト
    print("\n" + "=" * 80)
    print("実際のメール本文サンプルテスト")
    print("=" * 80)
    
    # ユーザーが提供したメール本文の一部
    real_email_sample = """
    山城 敬 様

    Word2XHTML5 PDFジェネレータをご利用いただきまして、ありがとうございます。

    アップロードされた超原稿用紙から生成されたファイルを
    以下のURLからダウンロードできます。

    http://trial.nextpublishing.jp/upload_46tate/do_download?n=cOc%2BWtyOaiCygUI0QyVpjOAIr%2F4PR7ifWZbNZzUhpKqukbY3LhsyO3oqOIoMwB47KUGNYXnnw2lMcDoYZMBosQ%3D%3D

    05_appendix.docx

    ※ダウンロード期限は本メール配信後72時間(3日間)です。
    """
    
    print("メール本文サンプル（一部）:")
    print(real_email_sample[:200] + "...")
    
    # ファイル名を探す
    filename = None
    for pattern in patterns:
        match = re.search(pattern, real_email_sample)
        if match:
            filename = match.group(1)
            print(f"\n✓ ファイル名を検出: {filename}")
            break
    
    if not filename:
        print("\n✗ ファイル名を検出できませんでした")

if __name__ == "__main__":
    test_filename_extraction()