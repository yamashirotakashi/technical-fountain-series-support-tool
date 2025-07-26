# Windows PowerShell Pre-flight実働テストランナー
# 技術の泉シリーズ制作支援ツール - Phase 4.3
# 実行方法: .\scripts\windows_test_runner.ps1

param(
    [string]$TestType = "full",  # full, quick, specific
    [string]$SpecificTest = "",  # 特定のテストを指定
    [switch]$Verbose = $false,   # 詳細出力
    [switch]$SaveLogs = $true    # ログ保存
)

# スクリプトの場所を基準にプロジェクトルートを設定
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Windows PowerShell Pre-flight実働テスト" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "プロジェクトルート: $ProjectRoot" -ForegroundColor Green
Write-Host "テストタイプ: $TestType" -ForegroundColor Green
Write-Host ""

# 環境チェック
Write-Host "=== 環境チェック ===" -ForegroundColor Yellow

# Python環境確認
try {
    $PythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python環境: $PythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "✗ Python環境が見つかりません" -ForegroundColor Red
    Write-Host "  Python 3.8以上をインストールしてPATHに追加してください" -ForegroundColor Red
    exit 1
}

# 仮想環境の確認・作成
$VenvPath = Join-Path $ProjectRoot "venv"
if (-not (Test-Path $VenvPath)) {
    Write-Host "⚙ 仮想環境を作成しています..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ 仮想環境の作成に失敗しました" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ 仮想環境を作成しました" -ForegroundColor Green
} else {
    Write-Host "✓ 仮想環境が存在します" -ForegroundColor Green
}

# 仮想環境の有効化
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    Write-Host "⚙ 仮想環境を有効化しています..." -ForegroundColor Yellow
    & $ActivateScript
    Write-Host "✓ 仮想環境を有効化しました" -ForegroundColor Green
} else {
    Write-Host "✗ 仮想環境の有効化スクリプトが見つかりません" -ForegroundColor Red
    exit 1
}

# 依存関係のインストール
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
if (Test-Path $RequirementsFile) {
    Write-Host "⚙ 依存関係をインストールしています..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 依存関係のインストール完了" -ForegroundColor Green
    } else {
        Write-Host "⚠ 依存関係のインストールで警告が発生しました" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ requirements.txtが見つかりません。手動で依存関係を確認してください" -ForegroundColor Yellow
}

# 環境変数の確認
Write-Host ""
Write-Host "=== 環境変数チェック ===" -ForegroundColor Yellow

$EnvFile = Join-Path $ProjectRoot ".env"
if (Test-Path $EnvFile) {
    Write-Host "✓ .envファイルが存在します" -ForegroundColor Green
    
    # .envファイルを読み込み
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            $name = $matches[1]
            $value = $matches[2]
            [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
} else {
    Write-Host "⚠ .envファイルが見つかりません" -ForegroundColor Yellow
    Write-Host "  Gmail認証を使用する場合は.envファイルを作成してください:" -ForegroundColor Yellow
    Write-Host "  GMAIL_ADDRESS=your-email@gmail.com" -ForegroundColor Yellow
    Write-Host "  GMAIL_APP_PASSWORD=your-app-password" -ForegroundColor Yellow
}

# Gmail設定確認
$GmailAddress = [System.Environment]::GetEnvironmentVariable("GMAIL_ADDRESS")
$GmailPassword = [System.Environment]::GetEnvironmentVariable("GMAIL_APP_PASSWORD")

if ($GmailAddress -and $GmailPassword) {
    Write-Host "✓ Gmail認証設定が確認されました" -ForegroundColor Green
    Write-Host "  メールアドレス: $($GmailAddress.Substring(0,3))***" -ForegroundColor Green
} else {
    Write-Host "⚠ Gmail認証設定が未設定です（テスト用ダミー設定を使用）" -ForegroundColor Yellow
}

# ログディレクトリの準備
$LogDir = Join-Path $ProjectRoot "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    Write-Host "✓ ログディレクトリを作成しました: $LogDir" -ForegroundColor Green
}

# テスト実行
Write-Host ""
Write-Host "=== テスト実行 ===" -ForegroundColor Yellow

$TestScript = Join-Path $ProjectRoot "tests\test_windows_powershell.py"
$LogFile = Join-Path $LogDir "windows_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

if (-not (Test-Path $TestScript)) {
    Write-Host "✗ テストスクリプトが見つかりません: $TestScript" -ForegroundColor Red
    exit 1
}

# テスト実行コマンドを構築
$TestCommand = "python `"$TestScript`""

Write-Host "テストスクリプト: $TestScript" -ForegroundColor Cyan
Write-Host "実行コマンド: $TestCommand" -ForegroundColor Cyan

if ($SaveLogs) {
    Write-Host "ログファイル: $LogFile" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "テストを開始しています..." -ForegroundColor Green
Write-Host ""

# テスト実行
try {
    $StartTime = Get-Date
    
    if ($SaveLogs) {
        # ログ保存有り
        if ($Verbose) {
            # 標準出力とログ両方に出力
            Invoke-Expression $TestCommand | Tee-Object -FilePath $LogFile
        } else {
            # ログのみに出力、重要な情報は標準出力
            Invoke-Expression $TestCommand | Out-File -FilePath $LogFile -Encoding UTF8
            Write-Host "テスト実行中... (詳細はログファイルを参照)" -ForegroundColor Yellow
        }
    } else {
        # ログ保存なし
        Invoke-Expression $TestCommand
    }
    
    $EndTime = Get-Date
    $Duration = $EndTime - $StartTime
    
    Write-Host ""
    Write-Host "=== テスト完了 ===" -ForegroundColor Yellow
    Write-Host "実行時間: $($Duration.ToString('mm\:ss\.fff'))" -ForegroundColor Green
    
    if ($SaveLogs) {
        Write-Host "ログファイル: $LogFile" -ForegroundColor Green
    }
    
    # テスト結果ファイルの確認
    $ResultsFile = Join-Path $ProjectRoot "windows_powershell_test_results.json"
    if (Test-Path $ResultsFile) {
        Write-Host "結果ファイル: $ResultsFile" -ForegroundColor Green
        
        # 結果の概要を表示
        try {
            $Results = Get-Content $ResultsFile -Encoding UTF8 | ConvertFrom-Json
            $Summary = $Results.test_summary
            
            Write-Host ""
            Write-Host "=== テスト結果概要 ===" -ForegroundColor Cyan
            Write-Host "総テスト数: $($Summary.total_tests)" -ForegroundColor White
            Write-Host "成功: $($Summary.passed)" -ForegroundColor Green
            Write-Host "失敗: $($Summary.failed)" -ForegroundColor $(if ($Summary.failed -eq 0) { "Green" } else { "Red" })
            Write-Host "成功率: $($Summary.success_rate)%" -ForegroundColor $(if ($Summary.success_rate -eq 100) { "Green" } else { "Yellow" })
            
            if ($Summary.failed -eq 0) {
                Write-Host ""
                Write-Host "🎉 すべてのテストが成功しました！" -ForegroundColor Green
                $ExitCode = 0
            } else {
                Write-Host ""
                Write-Host "⚠️ 一部のテストが失敗しました。" -ForegroundColor Yellow
                Write-Host "詳細はログファイルと結果ファイルを確認してください。" -ForegroundColor Yellow
                $ExitCode = 1
            }
        } catch {
            Write-Host "結果ファイルの解析に失敗しました: $_" -ForegroundColor Red
            $ExitCode = 1
        }
    } else {
        Write-Host "⚠ 結果ファイルが生成されませんでした" -ForegroundColor Yellow
        $ExitCode = 1
    }
    
} catch {
    Write-Host ""
    Write-Host "✗ テスト実行中にエラーが発生しました:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    $ExitCode = 1
}

# 最終メッセージ
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Windows PowerShell実働テスト完了" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

if ($ExitCode -eq 0) {
    Write-Host "✅ テストが正常に完了しました" -ForegroundColor Green
} else {
    Write-Host "❌ テストで問題が発生しました" -ForegroundColor Red
}

Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Yellow
Write-Host "1. ログファイルで詳細を確認: $LogFile" -ForegroundColor White
Write-Host "2. 結果ファイルで統計を確認: windows_powershell_test_results.json" -ForegroundColor White
Write-Host "3. 必要に応じて環境設定を調整" -ForegroundColor White
Write-Host "4. 実際のWordファイルでテスト実行" -ForegroundColor White

exit $ExitCode