"""
GitHub API連携モジュール
リポジトリ作成とコラボレーター管理
"""

import os
from typing import Dict, List, Optional, Any
import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubClient:
    """GitHub API クライアント"""
    
    BASE_URL = "https://api.github.com"
    ORG_NAME = "irdtechbook"  # 技術の泉シリーズの組織
    
    def __init__(self, token: str):
        """
        Args:
            token: GitHub Personal Access Token
        """
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def create_repository(
        self, 
        repo_name: str,
        description: str = None,
        private: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        組織内にリポジトリを作成
        
        Args:
            repo_name: リポジトリ名（例: zn9999）
            description: リポジトリの説明
            private: プライベートリポジトリとして作成（デフォルト: True）
            
        Returns:
            作成されたリポジトリの情報、失敗時はNone
        """
        # 組織アカウントの場合は/user/reposを使用
        url = f"{self.BASE_URL}/user/repos"
        
        data = {
            "name": repo_name,
            "private": private,
            "auto_init": True,  # READMEを自動生成
            "has_issues": True,
            "has_projects": False,
            "has_wiki": False
        }
        
        if description:
            data["description"] = description
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=self.headers) as response:
                    if response.status == 201:
                        repo_data = await response.json()
                        logger.info(f"Created repository: {repo_name}")
                        return repo_data
                    elif response.status == 422:
                        error_data = await response.json()
                        if any(e.get("field") == "name" and "already exists" in e.get("message", "") 
                               for e in error_data.get("errors", [])):
                            logger.warning(f"Repository {repo_name} already exists")
                            # 既存のリポジトリ情報を取得
                            return await self.get_repository(repo_name)
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create repository: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error creating repository: {e}")
            
        return None
    
    async def get_repository(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        リポジトリ情報を取得
        
        Args:
            repo_name: リポジトリ名
            
        Returns:
            リポジトリ情報、見つからない場合はNone
        """
        url = f"{self.BASE_URL}/repos/{self.ORG_NAME}/{repo_name}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.info(f"Repository {repo_name} not found")
                    else:
                        logger.error(f"Failed to get repository: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting repository: {e}")
            
        return None
    
    async def add_collaborator(
        self, 
        repo_name: str,
        username: str,
        permission: str = "push"
    ) -> bool:
        """
        リポジトリにコラボレーターを追加
        
        Args:
            repo_name: リポジトリ名
            username: GitHubユーザー名
            permission: 権限（"pull", "push", "admin", "maintain", "triage"）
            
        Returns:
            成功時True
        """
        url = f"{self.BASE_URL}/repos/{self.ORG_NAME}/{repo_name}/collaborators/{username}"
        
        data = {"permission": permission}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=data, headers=self.headers) as response:
                    if response.status in [201, 204]:
                        logger.info(f"Added collaborator {username} to {repo_name}")
                        return True
                    elif response.status == 404:
                        logger.error(f"Repository or user not found: {repo_name}/{username}")
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to add collaborator: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error adding collaborator: {e}")
            
        return False
    
    async def check_user_exists(self, username: str) -> bool:
        """
        GitHubユーザーの存在を確認
        
        Args:
            username: GitHubユーザー名
            
        Returns:
            存在する場合True
        """
        url = f"{self.BASE_URL}/users/{username}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error checking user: {e}")
            
        return False
    
    async def create_initial_files(
        self, 
        repo_name: str,
        n_code: str,
        book_title: Optional[str] = None
    ) -> bool:
        """
        初期ファイルを作成（README.md、.gitignore）
        
        Args:
            repo_name: リポジトリ名
            n_code: Nコード
            book_title: 書籍タイトル
            
        Returns:
            成功時True
        """
        # README.mdの内容（添削版に基づく）
        if book_title:
            title_line = f"# {book_title}"
        else:
            title_line = ""  # 書籍名がない場合は存在しない
        
        if title_line:
            readme_content = f"""{title_line}

## 概要
技術の泉シリーズの入稿作業用リポジトリです。

※校了後、半年目処でこのリポジトリは削除される可能性があります。今後の改修等のために、お手元に最終版のデータは保存を御願いします。

## フォルダ構成(推奨形式、ルートを「ReVIEW」フォルダとしてください)
```
ReVIEW/
├── README.md          # このファイル
├── .gitignore         # Git除外設定
├── config.yml         # Re:VIEW設定ファイル
├── catalog.yml        # 章構成ファイル
├── chap01.re          # 第1章原稿
├── chap02.re          # 第2章原稿
├── ...
└── images/            # 画像ファイル
    ├── chap01/        # 第1章の画像
    ├── chap02/        # 第2章の画像
    └── ...
```

## 原稿作成ガイドライン（抜粋）

### このセクションの全文は以下に共有しています。
https://docs.google.com/document/d/1WptR3TC-HRDoGf6brCTVLllj4WshzuzNC01f_xVPeQo/edit?usp=sharing

### Re:VIEW形式での執筆
- 原稿はRe:VIEW形式（.reファイル）で作成してください
- ファイル名は `chap01.re`, `chap02.re` のように連番で命名
- 一つの章は必ず一つの.reファイルと対応させてください
- 見出しは第3レベル（===）まで使用可能、第4レベルは原則不可

### 設定ファイル
- `config.yml`で`chapterlink: null`を必ず設定してください
- `catalog.yml`で章構成を定義してください

### 画像について
- 画像は `images/chap01/`, `images/chap02/` のように章ごとにフォルダ分け推奨
- 画像形式はJPG（RGB）で入稿してください
- 画像サイズは長辺2000px以下、総合計400万ピクセル未満
- 画像指定は必ず採番してください（//image[ID][キャプション]）

### リスト表現
- リスト表現は必ず行番号付き（//listnum）を使用
- 連番は必ず採番してください

### 表現の制約
- 句読点は「、。」を使用
- 和文と英単語の間に空白を入れないでください
- ハイパーリンクのURLに「#」「%」を含めないでください
- 絵文字（環境依存文字）は使用できません

### コード・リスト表現
- シンタックスハイライトは使用できません
- 見出しにタグや装飾（@<b>、@<i>など）、ハイパーリンクは使用できません
- リスト内での装飾（@<b>、@<i>など）は使用できません
- リスト内、見出しからの注釈@<fn>は設定できません

## 入稿チェックリスト
- [ ] config.ymlで`chapterlink: null`設定済み
- [ ] 画像はすべてJPG形式（RGB）
- [ ] URLに「#」「%」が含まれていない
- [ ] 絵文字を使用していない
- [ ] リストは//listnumで採番済み
- [ ] HTMLビルドが正常に通る

## サンプルコードリポジトリ
読者向けのサンプルコード公開リポジトリを準備することを推奨します。
正誤表もリポジトリのREADME.mdに記載可能です。
"""
        else:
            readme_content = """## 概要
技術の泉シリーズの入稿作業用リポジトリです。

※校了後、半年目処でこのリポジトリは削除される可能性があります。今後の改修等のために、お手元に最終版のデータは保存を御願いします。

## フォルダ構成(推奨形式、ルートを「ReVIEW」フォルダとしてください)
```
ReVIEW/
├── README.md          # このファイル
├── .gitignore         # Git除外設定
├── config.yml         # Re:VIEW設定ファイル
├── catalog.yml        # 章構成ファイル
├── chap01.re          # 第1章原稿
├── chap02.re          # 第2章原稿
├── ...
└── images/            # 画像ファイル
    ├── chap01/        # 第1章の画像
    ├── chap02/        # 第2章の画像
    └── ...
```

## 原稿作成ガイドライン（抜粋）

### このセクションの全文は以下に共有しています。
https://docs.google.com/document/d/1WptR3TC-HRDoGf6brCTVLllj4WshzuzNC01f_xVPeQo/edit?usp=sharing

### Re:VIEW形式での執筆
- 原稿はRe:VIEW形式（.reファイル）で作成してください
- ファイル名は `chap01.re`, `chap02.re` のように連番で命名
- 一つの章は必ず一つの.reファイルと対応させてください
- 見出しは第3レベル（===）まで使用可能、第4レベルは原則不可

### 設定ファイル
- `config.yml`で`chapterlink: null`を必ず設定してください
- `catalog.yml`で章構成を定義してください

### 画像について
- 画像は `images/chap01/`, `images/chap02/` のように章ごとにフォルダ分け推奨
- 画像形式はJPG（RGB）で入稿してください
- 画像サイズは長辺2000px以下、総合計400万ピクセル未満
- 画像指定は必ず採番してください（//image[ID][キャプション]）

### リスト表現
- リスト表現は必ず行番号付き（//listnum）を使用
- 連番は必ず採番してください

### 表現の制約
- 句読点は「、。」を使用
- 和文と英単語の間に空白を入れないでください
- ハイパーリンクのURLに「#」「%」を含めないでください
- 絵文字（環境依存文字）は使用できません

### コード・リスト表現
- シンタックスハイライトは使用できません
- 見出しにタグや装飾（@<b>、@<i>など）、ハイパーリンクは使用できません
- リスト内での装飾（@<b>、@<i>など）は使用できません
- リスト内、見出しからの注釈@<fn>は設定できません

## 入稿チェックリスト
- [ ] config.ymlで`chapterlink: null`設定済み
- [ ] 画像はすべてJPG形式（RGB）
- [ ] URLに「#」「%」が含まれていない
- [ ] 絵文字を使用していない
- [ ] リストは//listnumで採番済み
- [ ] HTMLビルドが正常に通る

## サンプルコードリポジトリ
読者向けのサンプルコード公開リポジトリを準備することを推奨します。
正誤表もリポジトリのREADME.mdに記載可能です。
"""
        
        # .gitignoreの内容
        gitignore_content = """# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Editor files
*.swp
*.swo
*~
.idea/
.vscode/

# Build files
*.pdf
*.epub
*.mobi
*.docx
*.html

# Temporary files
*.tmp
*.bak
*.log

# Re:VIEW build files
book-pdf/
book-epub/
webroot/
"""
        
        try:
            # README.mdを作成
            await self._create_file(
                repo_name,
                "README.md",
                readme_content,
                f"Initial commit: Add README for {n_code}"
            )
            
            # .gitignoreを作成
            await self._create_file(
                repo_name,
                ".gitignore",
                gitignore_content,
                "Add .gitignore"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating initial files: {e}")
            return False
    
    async def _create_file(
        self,
        repo_name: str,
        file_path: str,
        content: str,
        message: str
    ) -> bool:
        """
        ファイルを作成または更新
        
        Args:
            repo_name: リポジトリ名
            file_path: ファイルパス
            content: ファイル内容
            message: コミットメッセージ
            
        Returns:
            成功時True
        """
        import base64
        
        url = f"{self.BASE_URL}/repos/{self.ORG_NAME}/{repo_name}/contents/{file_path}"
        
        # 既存ファイルのSHAを取得
        existing_sha = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        existing_file = await response.json()
                        existing_sha = existing_file.get("sha")
                        logger.info(f"Found existing file {file_path}, SHA: {existing_sha}")
        except Exception:
            # ファイルが存在しない場合は無視
            pass
        
        data = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode()
        }
        
        # 既存ファイルがある場合はSHAを含める
        if existing_sha:
            data["sha"] = existing_sha
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=data, headers=self.headers) as response:
                    if response.status in [201, 200]:
                        action = "Updated" if existing_sha else "Created"
                        logger.info(f"{action} file: {file_path} in {repo_name}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create/update file: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Error creating/updating file: {e}")
            
        return False
    
    async def setup_repository(
        self,
        n_code: str,
        repo_name: str,
        github_username: Optional[str] = None,
        description: Optional[str] = None,
        book_title: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        リポジトリの完全セットアップ
        
        Args:
            n_code: Nコード
            repo_name: リポジトリ名
            github_username: 著者のGitHubユーザー名
            description: リポジトリの説明
            book_title: 書籍タイトル（README.md作成用）
            
        Returns:
            作成されたリポジトリ情報、失敗時はNone
        """
        # リポジトリを作成
        repo_info = await self.create_repository(repo_name, description)
        if not repo_info:
            return None
        
        # 初期ファイルを作成（書籍タイトル付きREADME.md含む）
        await self.create_initial_files(repo_name, n_code, book_title)
        
        # yamashirotakashi（編集者）をコラボレーターとして追加
        yamashiro_username = "yamashirotakashi"
        yamashiro_success = await self.add_collaborator(repo_name, yamashiro_username, "admin")
        if not yamashiro_success:
            logger.warning(f"Failed to add {yamashiro_username} as collaborator")
        
        # 著者をコラボレーターとして追加
        invitation_failed = False
        failed_github_username = None
        
        if github_username:
            if await self.check_user_exists(github_username):
                success = await self.add_collaborator(repo_name, github_username)
                if not success:
                    invitation_failed = True
                    failed_github_username = github_username
            else:
                logger.warning(f"GitHub user {github_username} not found, skipping collaborator addition")
                invitation_failed = True
                failed_github_username = github_username
        
        # 招待失敗情報をリポジトリ情報に追加
        if invitation_failed:
            repo_info["invitation_failed"] = True
            repo_info["failed_github_username"] = failed_github_username
        
        return repo_info