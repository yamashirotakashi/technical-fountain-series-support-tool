#!/usr/bin/env python3
"""
NextPublishing API 400エラー調査スクリプト
/api/uploadエンドポイントの詳細なエラー分析とリクエスト形式の特定
"""
import logging
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path
import json
import tempfile
from src.slack_pdf_poster import ConfigManager

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_400_investigation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_api_endpoints_detailed():
    """APIエンドポイントの詳細分析"""
    logger.info("=== NextPublishing API 400エラー詳細調査開始 ===")
    
    # ConfigManager初期化
    logger.info("ConfigManager初期化")
    config_manager = ConfigManager()
    
    # 設定値取得
    base_url = "http://sd001.nextpublishing.jp/rapture"
    username = config_manager.get("api.nextpublishing.username", "ep_user")
    password = config_manager.get("api.nextpublishing.password", "Nn7eUTX5")
    
    logger.info(f"Base URL: {base_url}")
    logger.info(f"Username: {username}")
    logger.info(f"Password: {'*' * len(password)}")
    
    # セッション設定
    session = requests.Session()
    session.auth = HTTPBasicAuth(username, password)
    
    # テスト用Wordファイルの準備
    test_file_path = None
    try:
        # 既存のdocxテンプレートを探す
        template_paths = [
            Path("venv/Lib/site-packages/docx/templates/default.docx"),
            Path("venv\\Lib\\site-packages\\docx\\templates\\default.docx"),
            Path("./venv/Scripts/../Lib/site-packages/docx/templates/default.docx")
        ]
        
        for template_path in template_paths:
            if template_path.exists():
                test_file_path = template_path
                logger.info(f"テストファイル発見: {test_file_path}")
                break
        
        if not test_file_path:
            logger.error("テスト用Wordファイルが見つかりません")
            return
        
        logger.info(f"ファイルサイズ: {test_file_path.stat().st_size} bytes")
        
        # /api/upload エンドポイントの詳細テスト
        api_endpoint = f"{base_url}/api/upload"
        logger.info(f"\n=== API エンドポイント詳細テスト: {api_endpoint} ===")
        
        # テストパターン1: ZIP mimetype
        logger.info("テスト1: application/zip mimetype")
        test_zip_mimetype(session, api_endpoint, test_file_path)
        
        # テストパターン2: Word mimetype
        logger.info("\nテスト2: Word document mimetype")
        test_word_mimetype(session, api_endpoint, test_file_path)
        
        # テストパターン3: form-data形式
        logger.info("\nテスト3: form-data形式")
        test_form_data_format(session, api_endpoint, test_file_path)
        
        # テストパターン4: JSONベースのAPI
        logger.info("\nテスト4: JSONベースのAPI")
        test_json_api_format(session, api_endpoint, test_file_path)
        
        # テストパターン5: 参考実装から学習
        logger.info("\nテスト5: 参考実装形式")
        test_reference_implementation(session, api_endpoint, test_file_path)
        
    except Exception as e:
        logger.error(f"テスト実行エラー: {e}")
        import traceback
        logger.error(f"スタックトレース: {traceback.format_exc()}")

def test_zip_mimetype(session, endpoint, file_path):
    """ZIPファイル形式でのテスト"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/zip')}
            headers = {'User-Agent': 'TechnicalFountainTool/1.0'}
            
            response = session.post(
                endpoint,
                files=files,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"ZIP形式 - Status: {response.status_code}")
            logger.info(f"ZIP形式 - Content-Type: {response.headers.get('Content-Type', 'なし')}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    logger.info(f"ZIP形式 - JSON エラー: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    logger.info(f"ZIP形式 - テキストエラー: {response.text[:500]}")
            else:
                logger.info(f"ZIP形式 - レスポンス: {response.text[:200]}")
                
    except Exception as e:
        logger.error(f"ZIP形式テストエラー: {e}")

def test_word_mimetype(session, endpoint, file_path):
    """Word文書形式でのテスト"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            headers = {'User-Agent': 'TechnicalFountainTool/1.0'}
            
            response = session.post(
                endpoint,
                files=files,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Word形式 - Status: {response.status_code}")
            logger.info(f"Word形式 - Content-Type: {response.headers.get('Content-Type', 'なし')}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    logger.info(f"Word形式 - JSON エラー: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    logger.info(f"Word形式 - テキストエラー: {response.text[:500]}")
            else:
                logger.info(f"Word形式 - レスポンス: {response.text[:200]}")
                
    except Exception as e:
        logger.error(f"Word形式テストエラー: {e}")

def test_form_data_format(session, endpoint, file_path):
    """フォームデータ形式でのテスト"""
    try:
        # フォームデータを準備
        form_data = {
            'project_name': '山城技術の泉',
            'orientation': '-10',
            'has_cover': '0',
            'has_tombo': '0',
            'style_vertical': '1',
            'style_horizontal': '7',
            'has_index': '0',
            'mail': 'yamashiro.takashi@gmail.com',
            'mailconf': 'yamashiro.takashi@gmail.com'
        }
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            
            response = session.post(
                endpoint,
                data=form_data,
                files=files,
                timeout=30
            )
            
            logger.info(f"フォーム形式 - Status: {response.status_code}")
            logger.info(f"フォーム形式 - Content-Type: {response.headers.get('Content-Type', 'なし')}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    logger.info(f"フォーム形式 - JSON エラー: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    logger.info(f"フォーム形式 - テキストエラー: {response.text[:500]}")
            else:
                logger.info(f"フォーム形式 - レスポンス: {response.text[:200]}")
                
    except Exception as e:
        logger.error(f"フォーム形式テストエラー: {e}")

def test_json_api_format(session, endpoint, file_path):
    """JSON API形式でのテスト"""
    try:
        # Base64エンコードでファイル送信を試行
        import base64
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        json_data = {
            'file': {
                'name': file_path.name,
                'content': file_b64,
                'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            },
            'settings': {
                'project_name': '山城技術の泉',
                'orientation': -10,
                'has_cover': 0,
                'has_tombo': 0,
                'style_vertical': 1,
                'style_horizontal': 7,
                'has_index': 0,
                'email': 'yamashiro.takashi@gmail.com'
            }
        }
        
        response = session.post(
            endpoint,
            json=json_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        logger.info(f"JSON形式 - Status: {response.status_code}")
        logger.info(f"JSON形式 - Content-Type: {response.headers.get('Content-Type', 'なし')}")
        
        if response.status_code == 400:
            try:
                error_data = response.json()
                logger.info(f"JSON形式 - JSON エラー: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                logger.info(f"JSON形式 - テキストエラー: {response.text[:500]}")
        else:
            logger.info(f"JSON形式 - レスポンス: {response.text[:200]}")
            
    except Exception as e:
        logger.error(f"JSON形式テストエラー: {e}")

def test_reference_implementation(session, endpoint, file_path):
    """参考実装（backup/2025-01-26）からの学習テスト"""
    try:
        logger.info("参考実装: backup/2025-01-26のapi_processor.pyパターンを参考")
        
        # api_processor.pyと同様の形式でテスト
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/zip')}
            
            # api_processor.pyと同様のヘッダー
            headers = {
                'User-Agent': 'TechnicalFountainTool/1.0'
            }
            
            response = session.post(
                endpoint,
                files=files,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"参考実装形式 - Status: {response.status_code}")
            logger.info(f"参考実装形式 - Content-Type: {response.headers.get('Content-Type', 'なし')}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    logger.info(f"参考実装形式 - JSON エラー: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                    
                    # エラーメッセージから期待される形式を推測
                    if 'error' in error_data:
                        error_msg = error_data.get('error', '')
                        logger.info(f"エラー分析: {error_msg}")
                        
                        if 'invalid' in error_msg.lower():
                            logger.info("→ リクエスト形式が無効")
                        if 'missing' in error_msg.lower():
                            logger.info("→ 必須パラメータが不足")
                        if 'format' in error_msg.lower():
                            logger.info("→ データ形式エラー")
                            
                except Exception as json_error:
                    logger.warning(f"JSON解析エラー: {json_error}")
                    logger.info(f"参考実装形式 - テキストエラー: {response.text[:500]}")
            else:
                logger.info(f"参考実装形式 - レスポンス: {response.text[:200]}")
                
    except Exception as e:
        logger.error(f"参考実装形式テストエラー: {e}")

if __name__ == "__main__":
    test_api_endpoints_detailed()
    
    logger.info("=== API 400エラー調査完了 ===")
    logger.info("詳細ログは api_400_investigation.log を確認してください")