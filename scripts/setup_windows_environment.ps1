# Windows環境自動セットアップスクリプト
# 技術の泉シリーズ制作支援ツール - Pre-flight Quality Check
# 実行方法: .\scripts\setup_windows_environment.ps1

param(
    [switch]$SkipPython = $false,        # Python環境のセットアップをスキップ
    [switch]$SkipVenv = $false,          # 仮想環境の作成をスキップ
    [switch]$SkipDependencies = $false,  # 依存関係のインストールをスキップ
    [switch]$CreateEnvTemplate = $true,  # .envテンプレートを作成
    [switch]$RunTests = $false,          # セットアップ後にテストを実行
    [switch]$Verbose = $false            # 詳細出力
)

# カラー出力関数
function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Step { param($Message) Write-Host "▶ $Message" -ForegroundColor Blue }

# スクリプトの場所を基準にプロジェクトルートを設定
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Windows環境自動セットアップ" -ForegroundColor Cyan
Write-Host "技術の泉シリーズ制作支援ツール" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Info "プロジェクトルート: $ProjectRoot"
Write-Host ""

# PowerShell実行ポリシーの確認
Write-Step "PowerShell実行ポリシーの確認"
$ExecutionPolicy = Get-ExecutionPolicy -Scope CurrentUser
if ($ExecutionPolicy -eq "Restricted") {
    Write-Warning "PowerShell実行ポリシーが制限されています"
    Write-Host "実行ポリシーを変更しますか？ (Y/N): " -NoNewline -ForegroundColor Yellow
    $Response = Read-Host
    if ($Response -eq "Y" -or $Response -eq "y") {
        try {
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
            Write-Success "実行ポリシーをRemoteSignedに変更しました"
        } catch {
            Write-Error "実行ポリシーの変更に失敗しました: $_"
            exit 1
        }
    } else {
        Write-Warning "実行ポリシーが制限されているため、一部の機能が動作しない可能性があります"
    }
} else {
    Write-Success "実行ポリシー: $ExecutionPolicy"
}

# Python環境のチェック
if (-not $SkipPython) {
    Write-Host ""
    Write-Step "Python環境の確認"
    
    try {
        $PythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python環境: $PythonVersion"
            
            # バージョンチェック
            if ($PythonVersion -match "Python (\d+)\.(\d+)") {
                $MajorVersion = [int]$matches[1]
                $MinorVersion = [int]$matches[2]
                
                if ($MajorVersion -ge 3 -and $MinorVersion -ge 8) {
                    Write-Success "Pythonバージョンは要件を満たしています"
                } else {
                    Write-Warning "Python 3.8以上を推奨します（現在: $PythonVersion）"
                }
            }
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Error "Python環境が見つかりません"
        Write-Info "Python 3.8以上をインストールしてPATHに追加してください"
        Write-Info "ダウンロード: https://www.python.org/downloads/"
        
        Write-Host "Pythonのインストールを続行しますか？ (Y/N): " -NoNewline -ForegroundColor Yellow
        $Response = Read-Host
        if ($Response -eq "Y" -or $Response -eq "y") {
            Write-Info "Webブラウザでダウンロードページを開いています..."
            Start-Process "https://www.python.org/downloads/"
            Write-Warning "Pythonをインストール後、このスクリプトを再実行してください"
            exit 1
        } else {
            Write-Error "Python環境が必要です。セットアップを中止します。"
            exit 1
        }
    }
    
    # pip の確認
    try {
        $PipVersion = pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "pip: $PipVersion"
        } else {
            throw "pip not found"
        }
    } catch {
        Write-Warning "pipが見つかりません。pipをインストールしています..."
        try {
            python -m ensurepip --upgrade
            Write-Success "pipのインストール完了"
        } catch {
            Write-Error "pipのインストールに失敗しました: $_"
            exit 1
        }
    }
}

# 仮想環境のセットアップ
if (-not $SkipVenv) {
    Write-Host ""
    Write-Step "仮想環境のセットアップ"
    
    $VenvPath = Join-Path $ProjectRoot "venv"
    
    if (Test-Path $VenvPath) {
        Write-Info "仮想環境が既に存在します"
        Write-Host "既存の仮想環境を削除して再作成しますか？ (Y/N): " -NoNewline -ForegroundColor Yellow
        $Response = Read-Host
        if ($Response -eq "Y" -or $Response -eq "y") {
            Write-Step "既存の仮想環境を削除しています..."
            Remove-Item -Recurse -Force $VenvPath
            Write-Success "既存の仮想環境を削除しました"
        } else {
            Write-Info "既存の仮想環境を使用します"
        }
    }
    
    if (-not (Test-Path $VenvPath)) {
        Write-Step "仮想環境を作成しています..."
        try {
            python -m venv venv
            if ($LASTEXITCODE -eq 0) {
                Write-Success "仮想環境を作成しました: $VenvPath"
            } else {
                throw "venv creation failed"
            }
        } catch {
            Write-Error "仮想環境の作成に失敗しました: $_"
            exit 1
        }
    }
    
    # 仮想環境の有効化
    $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (Test-Path $ActivateScript) {
        Write-Step "仮想環境を有効化しています..."
        try {
            & $ActivateScript
            Write-Success "仮想環境を有効化しました"
        } catch {
            Write-Error "仮想環境の有効化に失敗しました: $_"
            Write-Info "手動で有効化してください: .\venv\Scripts\Activate.ps1"
        }
    } else {
        Write-Error "仮想環境の有効化スクリプトが見つかりません"
        exit 1
    }
}

# 依存関係のインストール
if (-not $SkipDependencies) {
    Write-Host ""
    Write-Step "依存関係のインストール"
    
    # pip のアップグレード
    Write-Step "pipをアップグレードしています..."
    try {
        python -m pip install --upgrade pip
        Write-Success "pipのアップグレード完了"
    } catch {
        Write-Warning "pipのアップグレードに失敗しました: $_"
    }
    
    # requirements.txtからのインストール
    $RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
    if (Test-Path $RequirementsFile) {
        Write-Step "requirements.txtから依存関係をインストールしています..."
        try {
            pip install -r requirements.txt
            Write-Success "依存関係のインストール完了"
        } catch {
            Write-Warning "requirements.txtからのインストールで警告が発生しました"
            Write-Info "個別パッケージのインストールを試行します..."
        }
    } else {
        Write-Warning "requirements.txtが見つかりません"
    }
    
    # 重要なパッケージの個別インストール
    $EssentialPackages = @("requests", "psutil", "python-dotenv")
    Write-Step "重要なパッケージの確認とインストール..."
    
    foreach ($Package in $EssentialPackages) {
        try {
            python -c "import $($Package.Replace('-', '_'))" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$Package は既にインストールされています"
            } else {
                throw "Package not found"
            }
        } catch {
            Write-Step "$Package をインストールしています..."
            try {
                pip install $Package
                Write-Success "$Package のインストール完了"
            } catch {
                Write-Error "$Package のインストールに失敗しました: $_"
            }
        }
    }
}

# ディレクトリ構造の作成
Write-Host ""
Write-Step "必要なディレクトリの作成"

$RequiredDirs = @("logs", "temp", "backup", "config")
foreach ($Dir in $RequiredDirs) {
    $DirPath = Join-Path $ProjectRoot $Dir
    if (-not (Test-Path $DirPath)) {
        New-Item -ItemType Directory -Path $DirPath -Force | Out-Null
        Write-Success "ディレクトリを作成しました: $Dir"
    } else {
        Write-Info "ディレクトリが既に存在します: $Dir"
    }
}

# .envテンプレートの作成
if ($CreateEnvTemplate) {
    Write-Host ""
    Write-Step ".envテンプレートの作成"
    
    $EnvFile = Join-Path $ProjectRoot ".env"
    $EnvTemplateFile = Join-Path $ProjectRoot ".env.template"
    
    $EnvTemplate = @"
# Gmail設定（必須）
# Google アカウントで2段階認証を有効にし、アプリパスワードを生成してください
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# ログレベル（オプション）
LOG_LEVEL=INFO

# Word2XHTML5サービス設定（通常は変更不要）
WORD2XHTML_URL=http://trial.nextpublishing.jp/upload_46tate/
WORD2XHTML_USER=ep_user
WORD2XHTML_PASSWORD=Nn7eUTX5

# パフォーマンス監視設定（オプション）
PERFORMANCE_MONITORING_INTERVAL=30
PERFORMANCE_ALERT_CPU_THRESHOLD=80
PERFORMANCE_ALERT_MEMORY_THRESHOLD=90
"@
    
    # .env.templateを作成
    try {
        $EnvTemplate | Out-File -FilePath $EnvTemplateFile -Encoding UTF8
        Write-Success ".envテンプレートを作成しました: .env.template"
    } catch {
        Write-Error ".envテンプレートの作成に失敗しました: $_"
    }
    
    # .envファイルが存在しない場合は作成
    if (-not (Test-Path $EnvFile)) {
        try {
            $EnvTemplate | Out-File -FilePath $EnvFile -Encoding UTF8
            Write-Success ".envファイルを作成しました"
            Write-Warning "Gmail認証情報を設定してください: $EnvFile"
        } catch {
            Write-Error ".envファイルの作成に失敗しました: $_"
        }
    } else {
        Write-Info ".envファイルが既に存在します"
    }
}

# 設定ファイルの初期化
Write-Host ""
Write-Step "設定ファイルの初期化"

try {
    python -c "
from core.preflight.config_manager import get_config_manager
config_manager = get_config_manager()
issues = config_manager.validate_config()
print(f'設定検証完了: {len(issues)}件の問題')
for issue in issues:
    print(f'  - {issue}')
"
    Write-Success "設定ファイルの初期化完了"
} catch {
    Write-Warning "設定ファイルの初期化で問題が発生しました: $_"
    Write-Info "アプリケーション初回実行時に自動作成されます"
}

# テスト実行（オプション）
if ($RunTests) {
    Write-Host ""
    Write-Step "セットアップ後のテスト実行"
    
    $TestScript = Join-Path $ProjectRoot "scripts\windows_test_runner.ps1"
    if (Test-Path $TestScript) {
        Write-Info "テストランナーを実行しています..."
        try {
            & $TestScript -Verbose:$Verbose
            Write-Success "テスト実行完了"
        } catch {
            Write-Warning "テスト実行で問題が発生しました: $_"
        }
    } else {
        Write-Warning "テストランナーが見つかりません: $TestScript"
    }
}

# セットアップ完了メッセージ
Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "Windows環境セットアップ完了！" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Yellow
Write-Host "1. .envファイルでGmail認証情報を設定" -ForegroundColor White
Write-Host "   編集: $ProjectRoot\.env" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Gmail設定の確認" -ForegroundColor White
Write-Host "   - 2段階認証の有効化" -ForegroundColor Gray
Write-Host "   - アプリパスワードの生成" -ForegroundColor Gray
Write-Host "   - IMAP設定の有効化" -ForegroundColor Gray
Write-Host ""
Write-Host "3. テストの実行" -ForegroundColor White
Write-Host "   .\scripts\windows_test_runner.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "4. アプリケーションの実行" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor Gray

Write-Host ""
Write-Host "ドキュメント:" -ForegroundColor Yellow
Write-Host "- セットアップガイド: docs\WINDOWS_SETUP_GUIDE.md" -ForegroundColor Gray
Write-Host "- プロジェクト概要: CLAUDE.md" -ForegroundColor Gray

Write-Host ""
Write-Success "セットアップが正常に完了しました！"