# CodeBlock Overflow Checker - Tesseract設定付き起動スクリプト
# 仮想環境をアクティベートし、Tesseractパスを設定してからアプリを起動

# スクリプトのディレクトリに移動
Set-Location $PSScriptRoot

Write-Host "===== CodeBlock Overflow Checker 起動準備 =====`n" -ForegroundColor Cyan

# 1. 仮想環境の確認
if (-not (Test-Path ".\venv")) {
    Write-Host "エラー: 仮想環境が見つかりません。" -ForegroundColor Red
    Write-Host "先に setup_and_run.ps1 を実行してください。" -ForegroundColor Yellow
    exit 1
}

# 2. 仮想環境のアクティベート
Write-Host "仮想環境をアクティベート中..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# 3. Tesseract OCRの検索と設定
Write-Host "`nTesseract OCRを検索中..." -ForegroundColor Yellow

# 複数の可能なパスをチェック
$tesseractPaths = @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "$env:LOCALAPPDATA\Tesseract-OCR\tesseract.exe",
    "$env:LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe"
)

$foundTesseract = $false
$tesseractPath = ""

# 既存の環境変数をチェック
if ($env:TESSERACT_CMD -and (Test-Path $env:TESSERACT_CMD)) {
    $tesseractPath = $env:TESSERACT_CMD
    Write-Host "環境変数TESSERACT_CMDから検出: $tesseractPath" -ForegroundColor Green
    $foundTesseract = $true
} else {
    # パスを探す
    foreach ($path in $tesseractPaths) {
        if (Test-Path $path) {
            $tesseractPath = $path
            Write-Host "Tesseractを検出: $path" -ForegroundColor Green
            $foundTesseract = $true
            break
        }
    }
}

# whereコマンドでも探す
if (-not $foundTesseract) {
    try {
        $whereResult = where.exe tesseract 2>$null | Select-Object -First 1
        if ($whereResult -and (Test-Path $whereResult)) {
            $tesseractPath = $whereResult
            Write-Host "システムPATHから検出: $whereResult" -ForegroundColor Green
            $foundTesseract = $true
        }
    } catch {
        # エラーは無視
    }
}

if ($foundTesseract) {
    # 環境変数を設定
    $env:TESSERACT_CMD = $tesseractPath
    Write-Host "環境変数TESSERACT_CMDを設定しました。" -ForegroundColor Green
    
    # PATHにも追加
    $tesseractDir = Split-Path $tesseractPath -Parent
    if ($env:PATH -notlike "*$tesseractDir*") {
        $env:PATH = "$tesseractDir;$env:PATH"
        Write-Host "PATHに追加: $tesseractDir" -ForegroundColor Green
    }
    
    # 設定のテスト
    Write-Host "`nTesseract設定をテスト中..." -ForegroundColor Yellow
    python test_tesseract.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Tesseractが正常に設定されました！" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️ Tesseractの動作確認に失敗しました。" -ForegroundColor Yellow
        Write-Host "続行しますか？ (Y/N): " -ForegroundColor Cyan -NoNewline
        $response = Read-Host
        if ($response -ne 'Y' -and $response -ne 'y') {
            exit 1
        }
    }
} else {
    Write-Host "`n❌ Tesseract OCRが見つかりません！" -ForegroundColor Red
    Write-Host "インストール方法:" -ForegroundColor Yellow
    Write-Host "1. https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
    Write-Host "2. Windows用インストーラーをダウンロード" -ForegroundColor White
    Write-Host "3. インストール後、このスクリプトを再実行" -ForegroundColor White
    Write-Host "`nOCR機能なしで続行しますか？ (Y/N): " -ForegroundColor Cyan -NoNewline
    $response = Read-Host
    if ($response -ne 'Y' -and $response -ne 'y') {
        exit 1
    }
}

# 4. アプリケーション起動
Write-Host "`n===== アプリケーション起動 =====`n" -ForegroundColor Cyan
Write-Host "起動中..." -ForegroundColor Yellow

# pdfplumberのデバッグログを抑制
$env:PDFPLUMBER_LOGGING = "WARNING"
$env:PYPDF_LOGLEVEL = "WARNING"

python run_ultimate.py

# 終了コードを保持
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "`n⚠️ アプリケーションがエラーで終了しました。" -ForegroundColor Red
    Write-Host "終了コード: $exitCode" -ForegroundColor Red
}

Write-Host "`nEnterキーを押して終了..." -ForegroundColor Gray
Read-Host

exit $exitCode