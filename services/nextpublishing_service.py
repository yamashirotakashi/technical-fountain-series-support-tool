"""NextPublishing Word2XHTML5サービスモジュール"""
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import time
from dataclasses import dataclass
from utils.config import get_config


@dataclass
class UploadSettings:
    """アップロード設定"""
    project_name: str = "山城技術の泉"
    orientation: int = -10  # 横（B5技術書）
    has_cover: int = 0     # 扉なし
    has_tombo: int = 0     # トンボなし
    style_vertical: int = 1  # 縦書きスタイル：本文
    style_horizontal: int = 7  # 横書きスタイル：本文（ソースコード）
    has_index: int = 0     # 索引なし
    email: str = "yamashiro.takashi@gmail.com"


class NextPublishingService:
    """Word2XHTML5アップロードサービス"""
    
    BASE_URL = "http://trial.nextpublishing.jp/upload_46tate/"
    
    def __init__(self, settings: Optional[UploadSettings] = None):
        """
        サービスを初期化
        
        Args:
            settings: アップロード設定（省略時はデフォルト値）
        """
        self.settings = settings or UploadSettings()
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # 設定から認証情報を取得
        config = get_config()
        web_config = config.get_web_config()
        username = web_config.get('username', 'ep_user')
        password = web_config.get('password', 'Nn7eUTX5')
        
        # Basic認証を設定
        self.session.auth = HTTPBasicAuth(username, password)
        self.logger.info(f"Basic認証を設定しました: {username}")
        
        # デフォルトヘッダーを設定
        self.session.headers.update({
            'User-Agent': 'TechnicalFountainTool/1.0'
        })
        
    def upload_single_file(self, file_path: Path) -> Tuple[bool, str, Optional[str]]:
        """
        単一ファイルをアップロード
        
        Args:
            file_path: アップロードするWordファイルのパス
            
        Returns:
            Tuple[成功フラグ, メッセージ, 管理番号]
        """
        try:
            # フォームデータを準備
            form_data = {
                'project_name': self.settings.project_name,
                'orientation': str(self.settings.orientation),
                'has_cover': str(self.settings.has_cover),
                'has_tombo': str(self.settings.has_tombo),
                'style_vertical': str(self.settings.style_vertical),
                'style_horizontal': str(self.settings.style_horizontal),
                'has_index': str(self.settings.has_index),
                'mail': self.settings.email,
                'mailconf': self.settings.email
            }
            
            # ファイルを準備
            with open(file_path, 'rb') as f:
                files = {
                    'file1': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                # アップロード実行
                self.logger.info(f"アップロード開始: {file_path.name}")
                response = self.session.post(
                    self.BASE_URL,
                    data=form_data,
                    files=files,
                    timeout=300  # 5分のタイムアウト
                )
                
            # レスポンスを確認
            if response.status_code == 200:
                # 成功レスポンスから管理番号を抽出
                if "ファイルのアップロードに成功しました" in response.text:
                    # 管理番号を抽出（正規表現で8桁の数字を探す）
                    import re
                    match = re.search(r'管理番号\s*[:：]\s*(\d{8})', response.text)
                    control_number = match.group(1) if match else None
                    
                    self.logger.info(f"アップロード成功: {file_path.name} (管理番号: {control_number})")
                    return True, f"アップロード成功: {file_path.name}", control_number
                else:
                    self.logger.error(f"アップロード失敗: 予期しないレスポンス")
                    return False, f"アップロード失敗: 予期しないレスポンス", None
            else:
                self.logger.error(f"アップロード失敗: HTTPステータス {response.status_code}")
                return False, f"アップロード失敗: HTTPステータス {response.status_code}", None
                
        except requests.RequestException as e:
            self.logger.error(f"ネットワークエラー: {e}")
            return False, f"ネットワークエラー: {str(e)}", None
        except Exception as e:
            self.logger.error(f"予期しないエラー: {e}")
            return False, f"予期しないエラー: {str(e)}", None
    
    def upload_multiple_files(self, file_paths: List[Path], batch_size: int = 10) -> List[Dict[str, any]]:
        """
        複数ファイルをアップロード（バッチ処理）
        
        Args:
            file_paths: アップロードするWordファイルのパスリスト
            batch_size: 一度にアップロードするファイル数（デフォルト10）
            
        Returns:
            各ファイルのアップロード結果のリスト
        """
        results = []
        
        # バッチに分割
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            self.logger.info(f"バッチ {i//batch_size + 1}: {len(batch)}ファイル")
            
            try:
                # フォームデータを準備
                form_data = {
                    'project_name': self.settings.project_name,
                    'orientation': str(self.settings.orientation),
                    'has_cover': str(self.settings.has_cover),
                    'has_tombo': str(self.settings.has_tombo),
                    'style_vertical': str(self.settings.style_vertical),
                    'style_horizontal': str(self.settings.style_horizontal),
                    'has_index': str(self.settings.has_index),
                    'mail': self.settings.email,
                    'mailconf': self.settings.email
                }
                
                # ファイルを準備（複数ファイル対応）
                files = []
                for j, file_path in enumerate(batch):
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    files.append((
                        f'file{j+1}',
                        (file_path.name, file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    ))
                
                # アップロード実行
                self.logger.info(f"バッチアップロード開始")
                response = self.session.post(
                    self.BASE_URL,
                    data=form_data,
                    files=files,
                    timeout=600  # 10分のタイムアウト
                )
                
                # レスポンスを確認
                if response.status_code == 200:
                    # 各ファイルの結果を記録
                    for file_path in batch:
                        results.append({
                            'file_path': file_path,
                            'success': True,
                            'message': f"アップロード成功",
                            'batch_number': i//batch_size + 1
                        })
                    self.logger.info(f"バッチアップロード成功")
                else:
                    # エラーの場合
                    for file_path in batch:
                        results.append({
                            'file_path': file_path,
                            'success': False,
                            'message': f"HTTPステータス {response.status_code}",
                            'batch_number': i//batch_size + 1
                        })
                    self.logger.error(f"バッチアップロード失敗: HTTPステータス {response.status_code}")
                    
            except Exception as e:
                self.logger.error(f"バッチアップロードエラー: {e}")
                for file_path in batch:
                    results.append({
                        'file_path': file_path,
                        'success': False,
                        'message': str(e),
                        'batch_number': i//batch_size + 1
                    })
            
            # バッチ間の待機（サーバー負荷軽減）
            if i + batch_size < len(file_paths):
                time.sleep(5)
        
        return results
    
    def check_pdf_downloadable(self, pdf_url: str) -> Tuple[bool, str]:
        """
        PDFダウンロード可否をチェック
        
        Args:
            pdf_url: PDFダウンロードURL
            
        Returns:
            Tuple[ダウンロード可能フラグ, エラーメッセージ]
        """
        try:
            self.logger.info(f"PDFダウンロード可否チェック: {pdf_url}")
            
            # ブラウザのようなヘッダーを設定
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            # GETリクエストでアクセス（リダイレクトに追従）
            response = self.session.get(pdf_url, timeout=30, allow_redirects=True, headers=headers)
            
            self.logger.info(f"レスポンスステータス: {response.status_code}")
            self.logger.info(f"最終URL: {response.url}")
            self.logger.info(f"Content-Type: {response.headers.get('Content-Type', 'なし')}")
            
            # 401エラーの場合、認証情報が正しく送信されていない可能性がある
            if response.status_code == 401:
                self.logger.error("401エラー: 認証に失敗しました")
                self.logger.error(f"使用中の認証情報: username={self.session.auth.username}")
                return False, "認証エラー（401）"
            
            if response.status_code == 200:
                # まずContent-Typeとファイル内容を確認
                content_type = response.headers.get('Content-Type', '')
                content_start = response.content[:10] if response.content else b''
                
                # PDFファイルのマジックナンバーをチェック
                if content_start.startswith(b'%PDF'):
                    return True, "PDFダウンロード可能"
                elif 'application/pdf' in content_type:
                    # Content-TypeがPDFの場合
                    return True, "PDFダウンロード可能"
                
                # PDFではない場合、エラーページかどうか確認
                final_url = str(response.url)
                if 'do_download_pdf' in final_url:
                    # HTMLコンテンツの場合のみエラーメッセージを確認
                    if b'<html' in content_start.lower() or b'<!doctype' in content_start.lower():
                        self.logger.info("HTMLエラーページを検出")
                        # エラー内容を確認
                        content = response.content.decode('utf-8', errors='ignore')
                        if 'ファイルの作成に失敗しました' in content:
                            return False, "PDF生成エラー（超原稿用紙に不備）"
                        else:
                            return False, "PDF生成エラー"
                elif 'application/x-zip' in content_type or 'application/zip' in content_type:
                    # ZIPファイルが返される場合（PDF URLでZIPが返されることは異常）
                    if content_start.startswith(b'PK'):  # ZIPファイルのマジックナンバー
                        self.logger.warning("PDF URLでZIPファイルが返されました - 異常な状態")
                        return False, "PDF生成エラー（PDF URLでZIPファイルが返された）"
                    else:
                        # ZIP形式ではない何か
                        self.logger.warning(f"予期しないZIPコンテンツ: {content_start}")
                        return False, "不正なZIPファイル"
                else:
                    # HTMLレスポンスの場合
                    if b'<html' in content_start.lower() or b'<!doctype' in content_start.lower():
                        # HTMLの内容を確認
                        content_text = response.content[:1000].decode('utf-8', errors='ignore').lower()
                        if 'ファイルの作成に失敗' in content_text or 'エラー' in content_text:
                            return False, "PDF生成エラー"
                        else:
                            return False, "HTMLレスポンス（PDF生成失敗）"
                    else:
                        return False, f"不明なコンテンツ（Content-Type: {content_type}）"
            else:
                return False, f"HTTPステータス {response.status_code}"
                
        except requests.RequestException as e:
            self.logger.error(f"PDFチェックエラー: {e}")
            return False, f"ネットワークエラー: {str(e)}"
    
    def _analyze_zip_content(self, zip_data: bytes) -> Tuple[bool, str]:
        """
        ZIPファイルの内容を分析してエラーページかPDFかを判定
        
        Args:
            zip_data: ZIPファイルのバイナリデータ
            
        Returns:
            Tuple[ダウンロード可能フラグ, 判定メッセージ]
        """
        try:
            import zipfile
            import io
            
            self.logger.info("ZIP内容分析を開始")
            
            # ZIPファイルとして読み込み
            zip_buffer = io.BytesIO(zip_data)
            
            with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                file_list = zip_file.namelist()
                self.logger.info(f"ZIP内ファイル数: {len(file_list)}")
                
                pdf_files = []
                error_indicators = []
                
                # 各ファイルを検査
                for file_name in file_list:
                    self.logger.debug(f"ZIP内ファイル確認: {file_name}")
                    
                    # PDFファイルの検出
                    if file_name.lower().endswith('.pdf'):
                        pdf_files.append(file_name)
                        self.logger.info(f"PDFファイル発見: {file_name}")
                    
                    # HTMLファイル（エラーページの可能性）の検出
                    elif file_name.lower().endswith('.html') or file_name.lower().endswith('.htm'):
                        try:
                            with zip_file.open(file_name) as html_file:
                                # HTMLファイルの先頭1000文字を読み取り
                                html_content = html_file.read(1000).decode('utf-8', errors='ignore')
                                self.logger.debug(f"HTML内容サンプル: {html_content[:200]}")
                                
                                # エラーページのキーワードを検索
                                error_keywords = [
                                    'ファイルの作成に失敗',
                                    'エラーが発生',
                                    'PDF生成エラー',
                                    'エラー',
                                    'failed',
                                    'error'
                                ]
                                
                                for keyword in error_keywords:
                                    if keyword.lower() in html_content.lower():
                                        error_indicators.append(f"{file_name}: {keyword}")
                                        self.logger.warning(f"エラーページ検出: {file_name} - {keyword}")
                                        break
                        
                        except Exception as e:
                            self.logger.warning(f"HTMLファイル読み取りエラー: {file_name} - {e}")
                            error_indicators.append(f"{file_name}: 読み取りエラー")
                
                # 判定ロジック
                if error_indicators:
                    # エラーページが見つかった場合
                    error_summary = ", ".join(error_indicators[:3])  # 最大3つのエラーを表示
                    self.logger.error(f"ZIP内にエラーページを検出: {error_summary}")
                    return False, f"ZIP内にエラーページを検出: {error_summary}"
                
                elif pdf_files:
                    # 正常なPDFファイルが見つかった場合
                    self.logger.info(f"ZIP内に{len(pdf_files)}個の正常なPDFファイルを検出")
                    return True, f"PDFダウンロード可能（ZIP内に{len(pdf_files)}個のPDF）"
                
                else:
                    # PDFもエラーページも見つからない場合
                    self.logger.warning("ZIP内にPDFファイルもエラーページも見つからない")
                    # ファイル一覧をログに記録
                    file_types = [f.split('.')[-1].lower() if '.' in f else 'no_ext' for f in file_list]
                    type_summary = ", ".join(set(file_types))
                    return False, f"ZIP内にPDFなし（含まれるファイル: {type_summary}）"
                    
        except zipfile.BadZipFile:
            self.logger.error("不正なZIPファイル")
            return False, "不正なZIPファイル"
        except Exception as e:
            self.logger.error(f"ZIP分析エラー: {e}")
            return False, f"ZIP分析エラー: {str(e)}"
    
    def close(self):
        """セッションを閉じる"""
        self.session.close()