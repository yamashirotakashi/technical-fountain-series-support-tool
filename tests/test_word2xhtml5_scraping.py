"""Word2XHTML5サイトのスクレイピング調査スクリプト"""
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path


def analyze_upload_page():
    """アップロードページのフォーム構造を解析"""
    url = "http://trial.nextpublishing.jp/upload_46tate/"
    
    try:
        # ページを取得
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # 日本語対応
        
        # BeautifulSoupで解析
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # フォームを探す
        forms = soup.find_all('form')
        print(f"フォーム数: {len(forms)}")
        
        for i, form in enumerate(forms):
            print(f"\n--- フォーム {i+1} ---")
            print(f"Action: {form.get('action', 'なし')}")
            print(f"Method: {form.get('method', 'なし')}")
            print(f"Enctype: {form.get('enctype', 'なし')}")
            
            # input要素を解析
            inputs = form.find_all(['input', 'select', 'textarea'])
            print(f"\n入力要素数: {len(inputs)}")
            
            for inp in inputs:
                tag_name = inp.name
                inp_type = inp.get('type', 'text')
                inp_name = inp.get('name', 'なし')
                inp_value = inp.get('value', '')
                
                print(f"\n  タグ: {tag_name}")
                print(f"  Type: {inp_type}")
                print(f"  Name: {inp_name}")
                print(f"  Value: {inp_value}")
                
                # selectタグの場合はオプションも表示
                if tag_name == 'select':
                    options = inp.find_all('option')
                    print(f"  オプション:")
                    for opt in options:
                        opt_value = opt.get('value', '')
                        opt_text = opt.text.strip()
                        selected = 'selected' in opt.attrs
                        print(f"    - {opt_value}: {opt_text} {'(選択済み)' if selected else ''}")
                
                # ファイルアップロードフィールドの特定
                if inp_type == 'file':
                    multiple = inp.get('multiple')
                    accept = inp.get('accept')
                    print(f"  複数ファイル: {'可' if multiple is not None else '不可'}")
                    print(f"  受け入れ形式: {accept if accept else 'すべて'}")
        
        # ファイルアップロードフィールドの詳細確認
        file_inputs = soup.find_all('input', {'type': 'file'})
        print(f"\n\n=== ファイルアップロードフィールド詳細 ===")
        print(f"ファイルフィールド数: {len(file_inputs)}")
        
        for i, file_input in enumerate(file_inputs):
            print(f"\nファイルフィールド {i+1}:")
            print(f"  Name: {file_input.get('name', 'なし')}")
            print(f"  ID: {file_input.get('id', 'なし')}")
            print(f"  Multiple: {file_input.get('multiple') is not None}")
            print(f"  クラス: {file_input.get('class', [])}")
            
            # ラベルを探す
            label = soup.find('label', {'for': file_input.get('id')})
            if label:
                print(f"  ラベル: {label.text.strip()}")
        
        # フォーム構造をJSONとして保存
        form_structure = {
            'url': url,
            'forms': []
        }
        
        for form in forms:
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', ''),
                'enctype': form.get('enctype', ''),
                'fields': []
            }
            
            for inp in form.find_all(['input', 'select', 'textarea']):
                field = {
                    'tag': inp.name,
                    'type': inp.get('type', 'text'),
                    'name': inp.get('name', ''),
                    'value': inp.get('value', ''),
                    'multiple': inp.get('multiple') is not None
                }
                
                if inp.name == 'select':
                    field['options'] = [
                        {
                            'value': opt.get('value', ''),
                            'text': opt.text.strip(),
                            'selected': 'selected' in opt.attrs
                        }
                        for opt in inp.find_all('option')
                    ]
                
                form_data['fields'].append(field)
            
            form_structure['forms'].append(form_data)
        
        # 構造を保存
        output_path = Path('tests/word2xhtml5_form_structure.json')
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(form_structure, f, ensure_ascii=False, indent=2)
        
        print(f"\n\nフォーム構造を保存: {output_path}")
        
        return form_structure
        
    except requests.RequestException as e:
        print(f"エラー: {e}")
        return None


def test_single_file_upload():
    """単一ファイルアップロードのテスト（実際には送信しない）"""
    print("\n\n=== 単一ファイルアップロードのテストデータ ===")
    
    # フォームデータの構造
    form_data = {
        'project_name': '山城技術の泉',
        'orientation': '-10',  # 横（B5技術書）
        'has_cover': '0',      # 扉なし
        'has_tombo': '0',      # トンボなし
        'style_vertical': '1',  # 縦書きスタイル（本文）
        'style_horizontal': '7', # 横書きスタイル（本文ソースコード）
        'has_index': '0',      # 索引なし
        'mail': 'yamashiro.takashi@gmail.com',
        'mailconf': 'yamashiro.takashi@gmail.com'
    }
    
    print("フォームデータ:")
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    
    print("\nファイル:")
    print("  Wordファイル1: test_document.docx")
    
    return form_data


if __name__ == "__main__":
    print("Word2XHTML5サイト構造解析")
    print("=" * 50)
    
    # ページ構造を解析
    structure = analyze_upload_page()
    
    # テストデータを表示
    test_single_file_upload()