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
Write-ColorOutput "  TechZip Windows EXE Build Script  " "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput ""

# 現在のディレクトリを保存
$originalLocation = Get-Location

try {
    # プロジェクトルートに移動
    $projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $projectRoot
    Write-ColorOutput "Project Directory: $projectRoot" "Green"

    # クリーンビルドの場合
    if ($Clean) {
        Write-ColorOutput "`nPerforming clean build..." "Yellow"
        if (Test-Path "build") {
            Remove-Item -Path "build" -Recurse -Force
            Write-ColorOutput "  - Removed build directory" "Gray"
        }
        # TechZip関連のみ削除
        if (Test-Path "dist\TechZip1.0") {
            Remove-Item -Path "dist\TechZip1.0" -Recurse -Force
            Write-ColorOutput "  - Removed dist\TechZip1.0 directory" "Gray"
        }
        if (Test-Path "dist\TechZip1.0.exe") {
            Remove-Item -Path "dist\TechZip1.0.exe" -Force
            Write-ColorOutput "  - Removed dist\TechZip1.0.exe" "Gray"
        }
        if (Test-Path "dist\TechZip1.0_portable.exe") {
            Remove-Item -Path "dist\TechZip1.0_portable.exe" -Force
            Write-ColorOutput "  - Removed dist\TechZip1.0_portable.exe" "Gray"
        }
    }

    # Python仮想環境の確認
    Write-ColorOutput "`nChecking Python environment..." "Yellow"
    
    # venv_windowsが存在する場合は使用
    $venvPath = "venv_windows"
    if (-not (Test-Path $venvPath)) {
        $venvPath = "venv"
    }
    
    if (-not (Test-Path $venvPath)) {
        Write-ColorOutput "  - Warning: Virtual environment not found" "Red"
        Write-ColorOutput "  - Using system Python" "Yellow"
    } else {
        Write-ColorOutput "  - Found virtual environment: $venvPath" "Green"
    }

    # Pythonバージョンの確認
    $pythonVersion = python --version 2>&1
    Write-ColorOutput "  - Python version: $pythonVersion" "Gray"

    # PyInstallerのインストール確認
    Write-ColorOutput "`nChecking PyInstaller..." "Yellow"
    $pyinstallerCheck = pip show pyinstaller 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "  - PyInstaller not installed" "Red"
        Write-ColorOutput "  - Installing PyInstaller..." "Yellow"
        pip install pyinstaller
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install PyInstaller"
        }
    } else {
        $pyinstallerVersion = $pyinstallerCheck | Select-String "Version" | ForEach-Object { $_.ToString().Split(":")[1].Trim() }
        Write-ColorOutput "  - PyInstaller version: $pyinstallerVersion" "Green"
    }

    # 依存関係の確認
    Write-ColorOutput "`nChecking dependencies..." "Yellow"
    pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "  - All dependencies installed" "Green"
    } else {
        Write-ColorOutput "  - Warning: Some dependencies failed to install" "Yellow"
    }

    # PyInstallerオプションの設定
    $pyinstallerArgs = @()
    
    if ($OneFile) {
        Write-ColorOutput "`nBuilding single file EXE..." "Cyan"
        $pyinstallerArgs += "--onefile"
        $outputName = "TechZip1.0_portable.exe"
    } else {
        Write-ColorOutput "`nBuilding folder EXE..." "Cyan"
        $outputName = "TechZip1.0.exe"
    }

    if ($DebugMode) {
        $pyinstallerArgs += "--debug", "all"
        Write-ColorOutput "  - Debug mode enabled" "Yellow"
    }

    # Gmail OAuth関連の警告
    Write-ColorOutput "`nNotes:" "Yellow"
    Write-ColorOutput "  - Gmail OAuth credentials not included" "Yellow"
    Write-ColorOutput "  - Authentication required on first run" "Yellow"
    Write-ColorOutput "  - config/settings.json included (editable)" "Gray"

    # ビルド実行
    Write-ColorOutput "`nStarting build..." "Cyan"
    $buildCommand = "pyinstaller techzip_windows.spec $($pyinstallerArgs -join ' ')"
    Write-ColorOutput "  Command: $buildCommand" "Gray"
    
    Invoke-Expression $buildCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "`nBuild successful!" "Green"
        
        # 出力ファイルの確認
        if ($OneFile) {
            $outputPath = Join-Path "dist" $outputName
        } else {
            $outputPath = Join-Path "dist\TechZip1.0" "TechZip1.0.exe"
        }
        
        if (Test-Path $outputPath) {
            $fileInfo = Get-Item $outputPath
            Write-ColorOutput "  - Output file: $outputPath" "Green"
            Write-ColorOutput "  - File size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" "Gray"
            
            # 追加ファイルのコピー（フォルダ形式の場合）
            if (-not $OneFile) {
                $distFolder = "dist\TechZip1.0"
                
                # README.mdのコピー
                if (Test-Path "README.md") {
                    Copy-Item "README.md" $distFolder -Force
                    Write-ColorOutput "  - Copied README.md" "Gray"
                }
                
                # 実行用バッチファイルの作成
                $batchContent = @"
@echo off
echo TechZip - Technical Fountain Series Production Support Tool
echo.
start "" "%~dp0TechZip1.0.exe"
"@
                $batchPath = Join-Path $distFolder "TechZip_Start.bat"
                [System.IO.File]::WriteAllText($batchPath, $batchContent, [System.Text.Encoding]::GetEncoding("shift_jis"))
                Write-ColorOutput "  - Created startup batch file" "Gray"
            }
            
            Write-ColorOutput "`nHow to run:" "Cyan"
            if ($OneFile) {
                Write-ColorOutput "  $outputPath" "White"
            } else {
                Write-ColorOutput "  $outputPath" "White"
                Write-ColorOutput "  or" "Gray"
                Write-ColorOutput "  dist\TechZip1.0\TechZip_Start.bat" "White"
            }
            
        } else {
            Write-ColorOutput "  - Error: Output file not found" "Red"
        }
    } else {
        throw "Build failed"
    }

} catch {
    Write-ColorOutput "`nError occurred:" "Red"
    Write-ColorOutput $_.Exception.Message "Red"
    exit 1
} finally {
    # 元のディレクトリに戻る
    Set-Location $originalLocation
}

Write-ColorOutput "`nProcess complete" "Green"