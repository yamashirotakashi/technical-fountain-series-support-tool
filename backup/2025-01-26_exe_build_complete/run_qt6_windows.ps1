# Qt6版 技術の泉シリーズ制作支援ツール起動スクリプト
# Windows PowerShell用

# カレントディレクトリを保存
$originalLocation = Get-Location

try {
    # スクリプトのディレクトリに移動
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $scriptPath
    
    Write-Host "技術の泉シリーズ制作支援ツール (Qt6版) を起動します..." -ForegroundColor Green
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
        Write-Host "以下のいずれかの方法でPythonをインストールしてください：" -ForegroundColor Yellow
        Write-Host "1. Python公式サイト: https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "2. Microsoft Store: 'Python 3.12'を検索" -ForegroundColor Yellow
        Write-Host "" -ForegroundColor Yellow
        Write-Host "現在のPATH:" -ForegroundColor Cyan
        Write-Host $env:PATH -ForegroundColor Gray
        pause
        exit 1
    }
    
    # PyQt6のインストール確認
    Write-Host "PyQt6のインストールを確認しています..." -ForegroundColor Yellow
    & $pythonPath -c "import PyQt6.QtCore; print(f'PyQt6 version: {PyQt6.QtCore.QT_VERSION_STR}')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyQt6がインストールされていません。インストールします..." -ForegroundColor Yellow
        & $pythonPath -m pip install PyQt6
        if ($LASTEXITCODE -ne 0) {
            Write-Host "エラー: PyQt6のインストールに失敗しました" -ForegroundColor Red
            pause
            exit 1
        }
    }
    
    # 他の依存関係の確認
    Write-Host "依存関係を確認しています..." -ForegroundColor Yellow
    $requiredPackages = @(
        "python-dotenv",
        "google-api-python-client",
        "google-auth",
        "requests",
        "colorama"
    )
    
    foreach ($package in $requiredPackages) {
        & $pythonPath -c "import importlib; importlib.import_module('$($package.Replace('-', '_'))')" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "$package をインストールしています..." -ForegroundColor Yellow
            & $pythonPath -m pip install $package
        }
    }
    
    # メインアプリケーションを起動
    Write-Host ""
    Write-Host "アプリケーションを起動しています..." -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
    # main_qt6.pyを実行
    & $pythonPath main_qt6.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "エラーが発生しました。エラーコード: $LASTEXITCODE" -ForegroundColor Red
        
        # エラーログの確認
        if (Test-Path "logs") {
            $latestLog = Get-ChildItem "logs\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($latestLog) {
                Write-Host "最新のログファイル: $($latestLog.FullName)" -ForegroundColor Yellow
                Write-Host "ログの最後の10行:" -ForegroundColor Yellow
                Get-Content $latestLog.FullName -Tail 10
            }
        }
    }
}
finally {
    # 元のディレクトリに戻る
    Set-Location $originalLocation
    
    Write-Host ""
    Write-Host "Enterキーを押して終了してください..." -ForegroundColor Gray
    Read-Host
}