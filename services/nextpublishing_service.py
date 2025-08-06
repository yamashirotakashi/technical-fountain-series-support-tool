"""NextPublishing Word2XHTML5サービスモジュール"""
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import time
from dataclasses import dataclass
from core.configuration_provider import get_unified_config, ConfigurationProvider


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
    
    def __init__(self, settings: Optional[UploadSettings] = None, config_provider: Optional[ConfigurationProvider] = None, process_mode: str = "api"):
        """
        サービスを初期化
        
        Args:
            settings: アップロード設定（省略時はデフォルト値）
            config_provider: 統一設定プロバイダー（省略時は統一設定サービス）
            process_mode: 処理方式 ("api", "traditional", "gmail_api")
        """
        self.settings = settings or UploadSettings()
        self.config_provider = config_provider or get_unified_config()
        self.process_mode = process_mode
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # 処理方式に基づいて適切なベースURLを選択
        self.base_url = self._get_base_url_for_mode(process_mode)
        
        # 設定キーの不整合対応：複数のキーパターンをチェック
        username_source = "default"
        password_source = "default"
        
        # ユーザー名の取得（優先順位順）
        if self.config_provider.get("api.nextpublishing.username"):
            username = self.config_provider.get("api.nextpublishing.username")
            username_source = "api.nextpublishing.username"
        elif self.config_provider.get("web.username"):
            username = self.config_provider.get("web.username")
            username_source = "web.username"
        else:
            username = "ep_user"
            username_source = "default"
        
        # パスワードの取得（優先順位順）
        if self.config_provider.get("api.nextpublishing.password"):
            password = self.config_provider.get("api.nextpublishing.password")
            password_source = "api.nextpublishing.password"
        elif self.config_provider.get("web.password"):
            password = self.config_provider.get("web.password")
            password_source = "web.password"
        else:
            password = "Nn7eUTX5"
            password_source = "default"
        
        # Basic認証を設定
        self.session.auth = HTTPBasicAuth(username, password)
        self.logger.info(f"===== NextPublishingService 初期化情報 =====")
        self.logger.info(f"処理方式: {process_mode}")
        self.logger.info(f"ベースURL: {self.base_url}")
        self.logger.info(f"Basic認証ユーザー名: {username} (取得元: {username_source})")
        self.logger.info(f"Basic認証パスワード: {'*' * len(password)} (取得元: {password_source})")
        self.logger.info(f"プロジェクト名: {self.settings.project_name}")
        self.logger.info(f"メールアドレス: {self.settings.email}")
        
        # 設定値詳細ダンプ（デバッグ用）
        self.logger.debug("===== 詳細設定値ダンプ =====")
        debug_config_keys = [
            "api.nextpublishing.gmail_base_url",
            "api.nextpublishing.api_base_url",
            "api.nextpublishing.base_url",
            "api.nextpublishing.username",
            "api.nextpublishing.password",
            "web.username",
            "web.password"
        ]
        for key in debug_config_keys:
            value = self.config_provider.get(key, "[未設定]")
            if 'password' in key.lower() and value != "[未設定]":
                value = "*" * len(str(value))
            self.logger.debug(f"  {key}: {value}")
        self.logger.info(f"===== 初期化完了 =====")
        
        # デフォルトヘッダーを設定
        self.session.headers.update({
            'User-Agent': 'TechnicalFountainTool/1.0'
        })
        
    def _get_base_url_for_mode(self, process_mode: str) -> str:
        """
        処理方式に基づいて適切なベースURLを取得
        
        Args:
            process_mode: 処理方式 ("api", "traditional", "gmail_api")
            
        Returns:
            適切なベースURL
        """
        # Gmail API方式とTraditional方式はtrial.nextpublishing.jpを使用
        if process_mode in ["gmail_api", "traditional"]:
            # Gmail/Traditional用の専用設定キーを最初にチェック
            base_url = self.config_provider.get("api.nextpublishing.gmail_base_url", None)
            if base_url is None:
                # 専用設定がない場合は、既存のbase_urlをチェック（trial URLが設定されている可能性）
                configured_url = self.config_provider.get("api.nextpublishing.base_url", "")
                if "trial.nextpublishing.jp" in configured_url:
                    base_url = configured_url
                else:
                    # デフォルトのtrial URLを使用
                    base_url = "http://trial.nextpublishing.jp/rapture"
            
        else:
            # API方式はsd001.nextpublishing.jpを使用
            # API専用の設定キーを最初にチェック
            base_url = self.config_provider.get("api.nextpublishing.api_base_url", None)
            if base_url is None:
                # 専用設定がない場合は、既存のbase_urlをチェック（sd001 URLが設定されている可能性）
                configured_url = self.config_provider.get("api.nextpublishing.base_url", "")
                if "sd001.nextpublishing.jp" in configured_url:
                    base_url = configured_url
                else:
                    # デフォルトのsd001 URLを使用
                    base_url = "http://sd001.nextpublishing.jp/rapture"
        
        base_url = base_url.rstrip('/')
        self.logger.info(f"===== ベースURL選択プロセス =====")
        self.logger.info(f"処理方式: {process_mode}")
        self.logger.info(f"選択されたベースURL: {base_url}")
        
        if process_mode in ["gmail_api", "traditional"]:
            gmail_url = self.config_provider.get("api.nextpublishing.gmail_base_url", None)
            generic_url = self.config_provider.get("api.nextpublishing.base_url", "")
            self.logger.info(f"Gmail専用URL設定: {gmail_url if gmail_url else '[未設定]'}")
            self.logger.info(f"汎用URL設定: {generic_url if generic_url else '[未設定]'}")
            if "trial.nextpublishing.jp" in generic_url:
                self.logger.info("汎用URL設定にtrial URLが含まれています")
        else:
            api_url = self.config_provider.get("api.nextpublishing.api_base_url", None)
            generic_url = self.config_provider.get("api.nextpublishing.base_url", "")
            self.logger.info(f"API専用URL設定: {api_url if api_url else '[未設定]'}")
            self.logger.info(f"汎用URL設定: {generic_url if generic_url else '[未設定]'}")
            if "sd001.nextpublishing.jp" in generic_url:
                self.logger.info("汎用URL設定にsd001 URLが含まれています")
        
        self.logger.info(f"===== ベースURL選択完了: {base_url} =====")
        return base_url
        
    def upload_single_file(self, file_path: Path) -> Tuple[bool, str, Optional[str]]:
        """
        単一ファイルをアップロード
        
        Args:
            file_path: アップロードするWordファイルのパス
            
        Returns:
            Tuple[成功フラグ, メッセージ, 管理番号]
        """
        try:
            # 重要: WebフォームはWordファイルを直接送信するため、ZIP化は不要
            self.logger.info(f"アップロード開始: {file_path.name}")
            self.logger.info("ブラウザ互換のWebフォーム形式でWordファイルを直接送信します")
            
            # アップロード時は必ずtrial.nextpublishing.jpを使用
            upload_endpoint = "http://trial.nextpublishing.jp/rapture"
            self.logger.info(f"アップロード用URLを使用: {upload_endpoint}")
            
            timeout = self.config_provider.get("api.nextpublishing.timeout", 300)
            
            # ステップ1: まずページにアクセスしてCookieやセッション情報を取得
            self.logger.info(f"事前アクセス: {upload_endpoint} でセッション確立")
            
            # ブラウザ同等のヘッダーでページアクセス
            browser_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            }
            
            # 事前にページにアクセス（セッション・Cookie確立）
            pre_response = self.session.get(
                upload_endpoint, 
                headers=browser_headers, 
                timeout=30,
                auth=self.session.auth
            )
            
            self.logger.info(f"事前アクセス結果: HTTP {pre_response.status_code}")
            self.logger.info(f"取得Cookie数: {len(self.session.cookies)}")
            
            # ステップ2: フォーム送信用のヘッダーを準備
            form_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Origin': f"http://{upload_endpoint.split('//')[1].split('/')[0]}",
                'Referer': upload_endpoint,
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1'
            }
            
            # multipart/form-data形式のリクエストデータ（スクリーンショットのフォームと同じ構造）
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
            
            # ファイルデータの読み込み
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # ファイル拡張子に基づいてMIMEタイプを決定
            if file_path.suffix.lower() == '.zip':
                mime_type = 'application/zip'
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            else:
                mime_type = 'application/octet-stream'
            
            self.logger.info(f"MIMEタイプ: {mime_type}")
            
            files = {
                'userfile': (file_path.name, file_data, mime_type)
            }
            
            # ステップ3: 詳細ログ出力とフォーム送信
            self.logger.info(f"===== ブラウザ互換アップロード詳細 =====")
            self.logger.info(f"送信URL: {upload_endpoint}")
            self.logger.info(f"Origin: {form_headers['Origin']}")
            self.logger.info(f"Referer: {form_headers['Referer']}")
            self.logger.info(f"ファイル名: {file_path.name}")
            self.logger.info(f"ファイルサイズ: {len(file_data)} bytes")
            self.logger.info(f"フィールド名: userfile")
            self.logger.info(f"プロジェクト設定: {form_data['project_name']}")
            self.logger.info(f"メール設定: {form_data['mail']}")
            
            # フォーム送信
            response = self.session.post(
                upload_endpoint,
                data=form_data,
                files=files,
                headers=form_headers,
                auth=self.session.auth,
                timeout=timeout,
                allow_redirects=True  # リダイレクトを追従
            )
            
            self.logger.info(f"multipart/form-data - HTTPステータス: {response.status_code}")
            self.logger.info(f"multipart/form-data - Content-Type: {response.headers.get('Content-Type', 'なし')}")
            self.logger.info(f"最終URL: {response.url}")
            
            if response.status_code == 200:
                # 成功時のレスポンス処理
                # ISO-8859-1として誤認識されている場合の対処
                if response.encoding == 'ISO-8859-1':
                    self.logger.info("レスポンスがISO-8859-1として認識されました。UTF-8として再デコードします。")
                    # バイトデータをUTF-8として再デコード
                    try:
                        response_text = response.content.decode('utf-8')
                    except UnicodeDecodeError:
                        # UTF-8で失敗した場合は元のテキストを使用
                        response_text = response.text
                else:
                    response_text = response.text
                
                self.logger.info(f"レスポンス長: {len(response_text)} 文字")
                self.logger.info(f"レスポンス最初の500文字: {response_text[:500]}")
                
                # 完全なレスポンス内容をログに記録（デバッグ用）
                self.logger.debug(f"===== 完全レスポンス内容 =====")
                self.logger.debug(response_text)
                self.logger.debug(f"===== レスポンス内容終了 =====")
                
                # HTMLレスポンスの詳細分析（BOM付きUTF-8も考慮）
                # BOMを除去（複数パターンに対応）
                if response_text.startswith('\ufeff'):
                    response_text = response_text[1:]
                    self.logger.debug("BOM (\\ufeff) を除去しました")
                elif response_text.startswith('ï»¿'):
                    response_text = response_text[3:]
                    self.logger.debug("BOM (ï»¿) を除去しました")
                elif response_text[:3] == '\xef\xbb\xbf':
                    response_text = response_text[3:]
                    self.logger.debug("BOM (\\xef\\xbb\\xbf) を除去しました")
                
                if response_text.strip().startswith('<!DOCTYPE html') or response_text.strip().startswith('<html'):
                    self.logger.info("HTMLページが返されました - フォーム送信結果をHTMLで確認")
                    
                    # HTML内のbody要素のテキスト部分を抽出してチェック
                    import re
                    body_match = re.search(r'<body[^>]*>(.*?)</body>', response_text, re.DOTALL | re.IGNORECASE)
                    if body_match:
                        body_text = body_match.group(1)
                        # HTMLタグを除去してテキストのみ抽出
                        text_only = re.sub(r'<[^>]+>', '', body_text)
                        text_only = re.sub(r'\s+', ' ', text_only).strip()
                        
                        self.logger.info(f"HTMLページのテキスト内容: {text_only[:800]}")
                        
                        # 成功・失敗の判定
                        # 文字化けパターンは複数の方法で検索
                        mojibake_patterns = [
                            'ã¢ããã­ã¼ããå®äºãã¾ããã',  # 標準的な文字化けパターン
                            'アップロードが完了しました',  # 正しくデコードされた場合
                            'アップロード完了'
                        ]
                        
                        # 文字列での検索
                        for pattern in mojibake_patterns:
                            if pattern in text_only:
                                self.logger.info(f"成功メッセージを発見: {pattern[:20]}...")
                                return True, f"アップロード成功: {file_path.name}", None
                        
                        # レスポンス全体での検索（BOMの影響を受けていない場合）
                        for pattern in mojibake_patterns:
                            if pattern in response_text:
                                self.logger.info(f"レスポンス全体で成功メッセージを発見: {pattern[:20]}...")
                                return True, f"アップロード成功: {file_path.name}", None
                        
                        # バイトレベルでの検索も試みる
                        try:
                            response_bytes = response.content
                            # UTF-8でエンコードした文字化けパターンのバイト列
                            mojibake_bytes = 'ã¢ããã­ã¼ããå®äºãã¾ããã'.encode('utf-8')
                            if mojibake_bytes in response_bytes:
                                self.logger.info("バイトレベルで文字化けした成功メッセージを発見")
                                return True, f"アップロード成功: {file_path.name}", None
                            
                            # ISO-8859-1としてデコードしてみる
                            try:
                                iso_text = response_bytes.decode('iso-8859-1')
                                if 'ã¢ããã­ã¼ããå®äºãã¾ããã' in iso_text:
                                    self.logger.info("ISO-8859-1デコードで文字化けした成功メッセージを発見")
                                    return True, f"アップロード成功: {file_path.name}", None
                            except:
                                pass
                                
                        except Exception as e:
                            self.logger.debug(f"バイトレベル検索でエラー: {e}")
                        
                        success_patterns = [
                            r'ファイルのアップロードに成功',
                            r'アップロードが完了',
                            r'受付番号[:：]\s*(\d+)',
                            r'管理番号[:：]\s*(\d+)',
                            r'ジョブ[:：]\s*(\d+)',
                            r'job[:：]\s*(\d+)',
                            r'処理が開始されました',
                            r'正常に受信されました'
                        ]
                        
                        error_patterns = [
                            r'エラーが発生しました',
                            r'アップロードに失敗',
                            r'ファイルが不正',
                            r'サイズが大きすぎます',
                            r'形式が対応していません',
                            r'認証に失敗'
                        ]
                        
                        # 成功パターンのチェック
                        for pattern in success_patterns:
                            match = re.search(pattern, text_only, re.IGNORECASE)
                            if match:
                                if match.groups():
                                    control_number = match.group(1)
                                    self.logger.info(f"HTML内で管理番号を発見: {control_number}")
                                    return True, f"アップロード成功: {file_path.name}", control_number
                                else:
                                    self.logger.info(f"HTML内で成功メッセージを発見: {pattern}")
                                    return True, f"アップロード成功: {file_path.name}", None
                        
                        # エラーパターンのチェック
                        for pattern in error_patterns:
                            if re.search(pattern, text_only, re.IGNORECASE):
                                self.logger.error(f"HTML内でエラーパターンを発見: {pattern}")
                                return False, f"アップロードエラー: {pattern}", None
                        
                        # パターンマッチしない場合、HTMLページの内容を詳しく解析
                        self.logger.warning("HTMLページで明確な成功・失敗パターンが見つかりません")
                        
                        # フォーム送信ページかログインページかを判定
                        if any(keyword in text_only.lower() for keyword in ['login', 'ログイン', 'password', 'パスワード', 'username', 'ユーザー名']):
                            self.logger.error("ログインページが返されました - 認証に問題があります")
                            return False, "認証エラー: ログインページが返されました", None
                        elif any(keyword in text_only.lower() for keyword in ['form', 'フォーム', 'upload', 'アップロード']):
                            self.logger.warning("アップロードフォームページが返されました - フォーム送信が処理されていない可能性")
                            return False, "フォーム送信エラー: フォームページが再表示されました", None
                        else:
                            self.logger.warning("不明なHTMLページが返されました")
                            return False, f"不明なレスポンス: {text_only[:200]}", None
                    else:
                        self.logger.error("HTMLページのbody要素が見つかりません")
                        return False, "HTMLレスポンス解析エラー", None
                
                else:
                    # テキストレスポンスの場合
                    # 成功レスポンスから管理番号を抽出
                    if "ファイルのアップロードに成功しました" in response_text or "アップロードに成功" in response_text:
                        # 管理番号を抽出（正規表現で8桁の数字を探す）
                        import re
                        match = re.search(r'管理番号\s*[:：]\s*(\d{8})', response_text)
                        control_number = match.group(1) if match else None
                        
                        self.logger.info(f"アップロード成功: {file_path.name} (管理番号: {control_number})")
                        return True, f"アップロード成功: {file_path.name}", control_number
                    else:
                        self.logger.warning(f"アップロード結果不明: 予期しないレスポンス")
                        # 成功の可能性があるキーワードをチェック
                        success_indicators = ["success", "成功", "completed", "uploaded"]
                        error_indicators = ["error", "エラー", "failed", "失敗"]
                        
                        has_success = any(indicator in response_text.lower() for indicator in success_indicators)
                        has_error = any(indicator in response_text.lower() for indicator in error_indicators)
                        
                        if has_success and not has_error:
                            return True, "アップロード成功（推定）", None
                        elif has_error:
                            return False, f"アップロードエラー: {response_text[:200]}", None
                        else:
                            return False, f"アップロード結果不明: {response_text[:200]}", None
                        
            elif response.status_code == 400:
                # 400エラーの詳細分析
                response_text = response.text[:500]
                self.logger.error(f"400エラー: {response_text}")
                
                # 一般的なエラーパターンを確認
                if "ファイル" in response_text and ("サイズ" in response_text or "大きい" in response_text):
                    return False, "ファイルサイズエラー", None
                elif "形式" in response_text or "format" in response_text.lower():
                    return False, "ファイル形式エラー", None
                else:
                    return False, f"リクエストエラー: {response_text}", None
            
            elif response.status_code == 404:
                # 404エラーの詳細分析
                self.logger.error(f"===== 404エラー詳細分析 =====")
                self.logger.error(f"送信先URL: {upload_endpoint}")
                self.logger.error(f"処理方式: {self.process_mode}")
                self.logger.error(f"ベースURL: {self.base_url}")
                self.logger.error(f"使用認証: {self.session.auth.username} / {'*' * len(self.session.auth.password)}")
                
                # レスポンス内容の確認
                if response.text:
                    response_preview = response.text[:500]
                    self.logger.error(f"404レスポンスボディ: {response_preview}")
                    
                    # HTMLエラーページの場合、タイトルを抽出
                    if '<title>' in response_preview.lower():
                        import re
                        title_match = re.search(r'<title>(.*?)</title>', response_preview, re.IGNORECASE | re.DOTALL)
                        if title_match:
                            page_title = title_match.group(1).strip()
                            self.logger.error(f"エラーページタイトル: {page_title}")
                
                return False, f"404エラー: URL={upload_endpoint}", None
            
            else:
                # その他のHTTPエラー
                self.logger.error(f"HTTPエラー {response.status_code}: URL={upload_endpoint}")
                response_text = response.text[:300] if response.text else "レスポンスなし"
                self.logger.error(f"エラーレスポンス: {response_text}")
                return False, f"HTTPエラー {response.status_code}: {response_text}", None
                
        except Exception as e:
            self.logger.error(f"アップロード処理エラー: {str(e)}")
            import traceback
            self.logger.error(f"スタックトレース: {traceback.format_exc()}")
            return False, f"アップロード処理エラー: {str(e)}", None
    
    
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
                batch_timeout = self.config_provider.get("api.nextpublishing.batch_timeout", 600)
                response = self.session.post(
                    self.base_url,
                    data=form_data,
                    files=files,
                    timeout=batch_timeout
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
            pdf_timeout = self.config_provider.get("api.nextpublishing.pdf_timeout", 30)
            response = self.session.get(pdf_url, timeout=pdf_timeout, allow_redirects=True, headers=headers)
            
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