# PowerShell script to build Windows EXE
# Encoding: UTF-8 with BOM

param(
    [switch]$Clean,
    [switch]$OneFile,
    [switch]$DebugMode
)

# カラー出力用関数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "  TechZip Windows EXE ビルドスクリプト  " "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput ""

# 現在のディレクトリを保存
$originalLocation = Get-Location

try {
    # プロジェクトルートに移動
    $projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $projectRoot
    Write-ColorOutput "プロジェクトディレクトリ: $projectRoot" "Green"

    # クリーンビルドの場合
    if ($Clean) {
        Write-ColorOutput "`nクリーンビルドを実行します..." "Yellow"
        if (Test-Path "build") {
            Remove-Item -Path "build" -Recurse -Force
            Write-ColorOutput "  - buildディレクトリを削除しました" "Gray"
        }
        if (Test-Path "dist") {
            Remove-Item -Path "dist" -Recurse -Force
            Write-ColorOutput "  - distディレクトリを削除しました" "Gray"
        }
    }

    # Python仮想環境の確認
    Write-ColorOutput "`nPython環境を確認中..." "Yellow"
    
    # venv_windowsが存在する場合は使用
    $venvPath = "venv_windows"
    if (-not (Test-Path $venvPath)) {
        $venvPath = "venv"
    }
    
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        Write-ColorOutput "  - 仮想環境を有効化: $venvPath" "Green"
        & $activateScript
    } else {
        Write-ColorOutput "  - 警告: 仮想環境が見つかりません" "Red"
        Write-ColorOutput "  - システムのPython環境を使用します" "Yellow"
    }

    # Pythonバージョンの確認
    $pythonVersion = python --version 2>&1
    Write-ColorOutput "  - Python バージョン: $pythonVersion" "Gray"

    # PyInstallerのインストール確認
    Write-ColorOutput "`nPyInstallerを確認中..." "Yellow"
    $pyinstallerVersion = pip show pyinstaller 2>&1 | Select-String "Version"
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "  - PyInstallerがインストールされていません" "Red"
        Write-ColorOutput "  - PyInstallerをインストールします..." "Yellow"
        pip install pyinstaller
        if ($LASTEXITCODE -ne 0) {
            throw "PyInstallerのインストールに失敗しました"
        }
    } else {
        Write-ColorOutput "  - PyInstaller $pyinstallerVersion" "Green"
    }

    # 依存関係の確認
    Write-ColorOutput "`n依存関係を確認中..." "Yellow"
    pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "  - すべての依存関係がインストールされています" "Green"
    } else {
        Write-ColorOutput "  - 警告: 一部の依存関係のインストールに失敗しました" "Yellow"
    }

    # PyInstallerオプションの設定
    $pyinstallerArgs = @()
    
    if ($OneFile) {
        Write-ColorOutput "`n単一ファイルEXEをビルドします..." "Cyan"
        $pyinstallerArgs += "--onefile"
        $outputName = "TechZip_portable.exe"
    } else {
        Write-ColorOutput "`nフォルダ形式のEXEをビルドします..." "Cyan"
        $outputName = "TechZip.exe"
    }

    if ($DebugMode) {
        $pyinstallerArgs += "--debug", "all"
        Write-ColorOutput "  - デバッグモードが有効です" "Yellow"
    }

    # Gmail OAuth関連の警告
    Write-ColorOutput "`n注意事項:" "Yellow"
    Write-ColorOutput "  - Gmail OAuth認証ファイルは含まれません" "Yellow"
    Write-ColorOutput "  - 初回実行時に認証が必要です" "Yellow"
    Write-ColorOutput "  - config/settings.jsonは含まれます（編集可能）" "Gray"

    # ビルド実行
    Write-ColorOutput "`nビルドを開始します..." "Cyan"
    $buildCommand = "pyinstaller techzip_windows.spec $($pyinstallerArgs -join ' ')"
    Write-ColorOutput "  実行コマンド: $buildCommand" "Gray"
    
    Invoke-Expression $buildCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "`nビルドが成功しました！" "Green"
        
        # 出力ファイルの確認
        if ($OneFile) {
            $outputPath = Join-Path "dist" $outputName
        } else {
            $outputPath = Join-Path "dist\TechZip1.0" "TechZip1.0.exe"
        }
        
        if (Test-Path $outputPath) {
            $fileInfo = Get-Item $outputPath
            Write-ColorOutput "  - 出力ファイル: $outputPath" "Green"
            Write-ColorOutput "  - ファイルサイズ: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" "Gray"
            
            # 追加ファイルのコピー（フォルダ形式の場合）
            if (-not $OneFile) {
                $distFolder = "dist\TechZip1.0"
                
                # README.mdのコピー
                if (Test-Path "README.md") {
                    Copy-Item "README.md" $distFolder -Force
                    Write-ColorOutput "  - README.mdをコピーしました" "Gray"
                }
                
                # 実行用バッチファイルの作成
                $batchContent = @"
@echo off
echo TechZip - Technical Fountain Series Production Support Tool
echo.
start "" "%~dp0TechZip1.0.exe"
"@
                $batchPath = Join-Path $distFolder "TechZip_起動.bat"
                [System.IO.File]::WriteAllText($batchPath, $batchContent, [System.Text.Encoding]::GetEncoding("shift_jis"))
                Write-ColorOutput "  - 起動用バッチファイルを作成しました" "Gray"
            }
            
            Write-ColorOutput "`n実行方法:" "Cyan"
            if ($OneFile) {
                Write-ColorOutput "  $outputPath" "White"
            } else {
                Write-ColorOutput "  $outputPath" "White"
                Write-ColorOutput "  または" "Gray"
                Write-ColorOutput "  dist\TechZip1.0\TechZip_起動.bat" "White"
            }
            
        } else {
            Write-ColorOutput "  - エラー: 出力ファイルが見つかりません" "Red"
        }
    } else {
        throw "ビルドに失敗しました"
    }

} catch {
    Write-ColorOutput "`nエラーが発生しました:" "Red"
    Write-ColorOutput $_.Exception.Message "Red"
    exit 1
} finally {
    # 元のディレクトリに戻る
    Set-Location $originalLocation
}

Write-ColorOutput "`n処理が完了しました" "Green"