# Windows仮想環境修復スクリプト

Write-Host "🔧 Windows仮想環境の修復を開始します..." -ForegroundColor Yellow

# 現在の仮想環境を無効化
if ($env:VIRTUAL_ENV) {
    Write-Host "現在の仮想環境を無効化中..." -ForegroundColor Gray
    deactivate
}

# 古い仮想環境をバックアップ
if (Test-Path "venv") {
    Write-Host "既存の仮想環境をバックアップ中..." -ForegroundColor Gray
    if (Test-Path "venv_backup") {
        Remove-Item "venv_backup" -Recurse -Force
    }
    Rename-Item "venv" "venv_backup"
}

# 新しい仮想環境を作成
Write-Host "新しい仮想環境を作成中..." -ForegroundColor Green
python -m venv venv

# 仮想環境をアクティベート
Write-Host "仮想環境をアクティベート中..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# 必要なライブラリをインストール
Write-Host "必要なライブラリをインストール中..." -ForegroundColor Green
python -m pip install --upgrade pip
pip install google-auth-oauthlib google-api-python-client
pip install requests python-dotenv

# PyQt6とその他の既存ライブラリも再インストール
Write-Host "プロジェクト依存関係をインストール中..." -ForegroundColor Green
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
}

# テスト実行
Write-Host "Gmail API テストを実行中..." -ForegroundColor Green
python test_gmail_oauth_simple.py

Write-Host "✅ 仮想環境の修復が完了しました!" -ForegroundColor Green