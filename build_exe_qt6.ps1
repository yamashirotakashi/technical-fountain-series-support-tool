# Qt6版 exe化スクリプト
# Windows PowerShell用

Write-Host "技術の泉シリーズ制作支援ツール Qt6版 exe化スクリプト" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Python実行可能ファイルの確認
# 複数の一般的なPythonパスを試す
$pythonPaths = @(
    "python",  # PATH環境変数に設定されている場合
    "py",      # Python Launcher
    "C:\Python313\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    "C:\Users\tky99\AppData\Local\Programs\Python\Python313\python.exe",
    "C:\Users\tky99\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Users\tky99\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Users\tky99\AppData\Local\Programs\Python\Python310\python.exe",
    "C:\Program Files\Python313\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python310\python.exe"
)

$pythonPath = $null
foreach ($path in $pythonPaths) {
    try {
        $testPath = if ($path -match "^[A-Z]:") { $path } else { (Get-Command $path -ErrorAction SilentlyContinue).Path }
        if ($testPath -and (Test-Path $testPath)) {
            # Pythonバージョンを確認
            $version = & $testPath --version 2>&1
            if ($version -match "Python 3\.(1[0-3]|[89])") {
                $pythonPath = $testPath
                Write-Host "Pythonを検出: $pythonPath ($version)" -ForegroundColor Green
                break
            }
        }
    } catch {
        # エラーは無視して次を試す
    }
}

if (-not $pythonPath) {
    Write-Host "エラー: Python 3.8以上が見つかりません" -ForegroundColor Red
    Write-Host "Pythonをインストールしてください" -ForegroundColor Yellow
    pause
    exit 1
}

# PyInstallerのインストール確認
Write-Host "PyInstallerの確認..." -ForegroundColor Yellow
& $pythonPath -m pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstallerをインストールしています..." -ForegroundColor Yellow
    & $pythonPath -m pip install pyinstaller
}

# PyQt6の確認
Write-Host "PyQt6の確認..." -ForegroundColor Yellow
& $pythonPath -c "import PyQt6.QtCore; print(f'PyQt6 version: {PyQt6.QtCore.QT_VERSION_STR}')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "エラー: PyQt6がインストールされていません" -ForegroundColor Red
    Write-Host "先にrun_qt6_windows.ps1を実行してください" -ForegroundColor Yellow
    pause
    exit 1
}

# クリーンビルドの確認
$cleanBuild = Read-Host "クリーンビルドを実行しますか? (Y/n)"
if ($cleanBuild -ne 'n') {
    Write-Host "ビルドディレクトリをクリーンアップしています..." -ForegroundColor Yellow
    Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "*.spec" -Force -ErrorAction SilentlyContinue  < /dev/null |  Where-Object { $_.Name -ne "techzip_qt6.spec" }
}

# exe化の実行
Write-Host ""
Write-Host "exe化を開始します..." -ForegroundColor Green

# specファイルが存在する場合はそれを使用
if (Test-Path "techzip_qt6.spec") {
    Write-Host "techzip_qt6.specを使用してビルドします" -ForegroundColor Cyan
    & $pythonPath -m PyInstaller techzip_qt6.spec
} else {
    Write-Host "新規にexeを作成します" -ForegroundColor Cyan
    & $pythonPath -m PyInstaller --onefile --windowed --name TechZip_Qt6 `
        --add-data "config;config" `
        --add-data "logs;logs" `
        --add-data "templates;templates" `
        --hidden-import PyQt6.QtCore `
        --hidden-import PyQt6.QtGui `
        --hidden-import PyQt6.QtWidgets `
        --exclude-module PyQt5 `
        --exclude-module matplotlib `
        --exclude-module numpy `
        --exclude-module pandas `
        main_qt6.py
}

# ビルド結果の確認
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "ビルドが成功しました！" -ForegroundColor Green
    
    if (Test-Path "dist\TechZip_Qt6.exe") {
        $exeInfo = Get-Item "dist\TechZip_Qt6.exe"
        Write-Host "作成されたexe: $($exeInfo.FullName)" -ForegroundColor Cyan
        Write-Host "ファイルサイズ: $([math]::Round($exeInfo.Length / 1MB, 2)) MB" -ForegroundColor Cyan
        
        # 必要なファイルのコピー
        Write-Host ""
        Write-Host "必要なファイルをコピーしています..." -ForegroundColor Yellow
        
        # configフォルダのコピー
        if (Test-Path "config") {
            Copy-Item -Path "config" -Destination "dist\config" -Recurse -Force
            Write-Host "✓ configフォルダをコピーしました" -ForegroundColor Green
        }
        
        # .envファイルのサンプル作成
        if (Test-Path ".env") {
            $envContent = @"
# Gmail設定
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here

# GitHub設定（オプション）
GITHUB_TOKEN=your_github_token_here
"@
            $envContent | Out-File -FilePath "dist\.env.sample" -Encoding UTF8
            Write-Host "✓ .env.sampleを作成しました" -ForegroundColor Green
        }
        
        # READMEの作成
        $readmeContent = @"
# 技術の泉シリーズ制作支援ツール (Qt6版)

## 実行方法
1. TechZip_Qt6.exe をダブルクリックして起動
2. 初回起動時は .env.sample を .env にリネームして設定を入力

## 必要なファイル
- TechZip_Qt6.exe (本体)
- config/ (設定ファイル)
- .env (認証情報)

## トラブルシューティング
- Windows Defenderで警告が出る場合は「詳細情報」→「実行」を選択
- 起動しない場合はlogsフォルダのログを確認
"@
        $readmeContent | Out-File -FilePath "dist\README.txt" -Encoding UTF8
        Write-Host "✓ README.txtを作成しました" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "配布の準備が完了しました！" -ForegroundColor Green
        Write-Host "distフォルダ内のファイルを配布してください。" -ForegroundColor Cyan
        
        # エクスプローラーで開く
        $openExplorer = Read-Host "distフォルダを開きますか? (Y/n)"
        if ($openExplorer -ne 'n') {
            explorer.exe dist
        }
    }
} else {
    Write-Host ""
    Write-Host "ビルドに失敗しました。" -ForegroundColor Red
    Write-Host "エラーログを確認してください。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Enterキーを押して終了..."
Read-Host
