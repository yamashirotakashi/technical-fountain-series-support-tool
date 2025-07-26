# 技術の泉シリーズ制作支援ツール EXEビルドスクリプト
# Windows PowerShell

Write-Host "技術の泉シリーズ制作支援ツール EXEビルドスクリプト" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# スクリプトのディレクトリに移動
Set-Location $PSScriptRoot

# 仮想環境を使用
if (Test-Path ".\venv_windows") {
    Write-Host "仮想環境を有効化しています..." -ForegroundColor Yellow
    & ".\venv_windows\Scripts\Activate.ps1"
} else {
    Write-Host "エラー: 仮想環境が見つかりません" -ForegroundColor Red
    Write-Host "setup_windows.ps1を先に実行してください" -ForegroundColor Yellow
    pause
    exit 1
}

# PyInstallerがインストールされているか確認
Write-Host "PyInstallerを確認しています..." -ForegroundColor Yellow
python -m pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstallerをインストールしています..." -ForegroundColor Yellow
    python -m pip install pyinstaller
}

# PyQt6の確認
Write-Host "PyQt6を確認しています..." -ForegroundColor Yellow
python -c "import PyQt6.QtCore; print(f'PyQt6 version: {PyQt6.QtCore.QT_VERSION_STR}')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "エラー: PyQt6がインストールされていません" -ForegroundColor Red
    Write-Host "setup_windows.ps1を先に実行してください" -ForegroundColor Yellow
    pause
    exit 1
}

# クリーンビルドの確認
$cleanBuild = Read-Host "クリーンビルドを実行しますか？ (Y/n)"
if ($cleanBuild -ne 'n') {
    Write-Host "ビルドディレクトリをクリーンアップしています..." -ForegroundColor Yellow
    Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path "*.spec" | Where-Object { $_.Name -ne "techzip.spec" } | Remove-Item -Force -ErrorAction SilentlyContinue
}

# EXEのビルド実行
Write-Host ""
Write-Host "EXEビルドを開始しています..." -ForegroundColor Green

# specファイルを使用してビルド
if (Test-Path "techzip.spec") {
    Write-Host "techzip.specを使用してビルドしています" -ForegroundColor Cyan
    python -m PyInstaller techzip.spec
} else {
    Write-Host "新規EXEを作成しています" -ForegroundColor Cyan
    python -m PyInstaller --onefile --windowed --name TechZip `
        --add-data "config;config" `
        --hidden-import PyQt6.QtCore `
        --hidden-import PyQt6.QtGui `
        --hidden-import PyQt6.QtWidgets `
        --exclude-module PyQt5 `
        --exclude-module matplotlib `
        --exclude-module numpy `
        --exclude-module pandas `
        main.py
}

# ビルド結果の確認
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "ビルドが成功しました！" -ForegroundColor Green
    
    if (Test-Path "dist\TechZip.exe") {
        $exeInfo = Get-Item "dist\TechZip.exe"
        Write-Host "作成されたEXE: $($exeInfo.FullName)" -ForegroundColor Cyan
        Write-Host "ファイルサイズ: $([math]::Round($exeInfo.Length / 1MB, 2)) MB" -ForegroundColor Cyan
        
        # 必要なファイルをコピー
        Write-Host ""
        Write-Host "必要なファイルをコピーしています..." -ForegroundColor Yellow
        
        # configフォルダのコピー
        if (Test-Path "config") {
            Copy-Item -Path "config" -Destination "dist\config" -Recurse -Force
            Write-Host "✓ configフォルダをコピーしました" -ForegroundColor Green
        }
        
        # .envサンプルファイルの作成
        if (Test-Path ".env") {
            $envContent = "# Gmail設定`nGMAIL_ADDRESS=your_email@gmail.com`nGMAIL_APP_PASSWORD=your_app_password_here`n`n# GitHub設定（オプション）`nGITHUB_TOKEN=your_github_token_here"
            $envContent | Out-File -FilePath "dist\.env.sample" -Encoding UTF8
            Write-Host "✓ .env.sampleを作成しました" -ForegroundColor Green
        }
        
        # READMEの作成
        $readmeContent = @"
# 技術の泉シリーズ制作支援ツール

## 実行方法
1. TechZip.exeをダブルクリックして起動
2. 初回起動時は.env.sampleを.envにリネームして設定を入力

## 必要なファイル
- TechZip.exe（メインアプリケーション）
- config/（設定ファイル）
- .env（認証情報）

## トラブルシューティング
- Windows Defenderに警告される場合は「詳細情報」→「実行」を選択
- 起動しない場合はlogsフォルダのエラーログを確認

## 使い方
1. Nコードを入力（複数可、カンマ・タブ・改行区切り）
2. 処理開始ボタンをクリック
3. API方式（推奨）またはメール方式を選択
4. 処理完了後、ファイルの配置先を確認

## 設定
- ツール→リポジトリ設定でGitHub連携を設定可能
- デフォルトはAPI方式（高速・詳細な警告表示）
"@
        $readmeContent | Out-File -FilePath "dist\README.txt" -Encoding UTF8
        Write-Host "✓ README.txtを作成しました" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "配布準備が完了しました！" -ForegroundColor Green
        Write-Host "distフォルダ内のファイルを配布してください。" -ForegroundColor Cyan
        
        # エクスプローラーで開く
        $openExplorer = Read-Host "distフォルダを開きますか？ (Y/n)"
        if ($openExplorer -ne 'n') {
            explorer.exe dist
        }
    }
} else {
    Write-Host ""
    Write-Host "ビルドが失敗しました。" -ForegroundColor Red
    Write-Host "エラーログを確認してください。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Enterキーを押して終了..."
$null = Read-Host