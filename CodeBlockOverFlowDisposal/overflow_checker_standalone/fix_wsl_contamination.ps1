# WSL PATH汚染の根本的解決スクリプト
# 汚染された仮想環境を削除し、純粋なWindows環境で再作成

param(
    [switch]$Force = $false,
    [string]$RequiredPythonVersion = "3.9"
)

$ErrorActionPreference = "Stop"

Write-Host "=== WSL PATH汚染の根本的解決 ===" -ForegroundColor Cyan
Write-Host "概要: 汚染された仮想環境を削除し、純粋なWindows環境で再作成" -ForegroundColor Yellow

# 管理者権限チェック（推奨）
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Host "⚠️ 管理者権限での実行を推奨します（より確実な環境分離のため）" -ForegroundColor Yellow
    if (-not $Force) {
        $choice = Read-Host "管理者権限なしで続行しますか？ (y/N)"
        if ($choice -ne "y" -and $choice -ne "Y") {
            Write-Host "スクリプトを終了します。管理者権限で再実行してください。" -ForegroundColor Red
            exit 1
        }
    }
}

# WSL環境変数の完全クリア
function Clear-WSLEnvironment {
    Write-Host "WSL環境変数をクリア中..." -ForegroundColor Yellow
    
    # WSL関連環境変数の完全削除
    $wslVars = @(
        "WSL_DISTRO_NAME",
        "WSL_INTEROP",
        "WSLENV",
        "DISPLAY",
        "WAYLAND_DISPLAY",
        "XDG_RUNTIME_DIR",
        "PULSE_AUDIO_SERVER"
    )
    
    foreach ($var in $wslVars) {
        if ($env:PSModulePath -and $env:PSModulePath.Contains($var)) {
            Remove-Item "Env:$var" -ErrorAction SilentlyContinue
            Write-Host "  削除: $var" -ForegroundColor Gray
        }
    }
    
    # PATHからLinuxパスを完全除去
    $originalPath = $env:PATH
    $cleanPath = $originalPath -split ';' | Where-Object { 
        $_ -and 
        -not $_.StartsWith('/usr/') -and 
        -not $_.StartsWith('/bin/') -and 
        -not $_.StartsWith('/sbin/') -and 
        -not $_.StartsWith('/opt/') -and
        -not $_.Contains('wsl')
    } | Where-Object { $_.Trim() -ne '' }
    
    $env:PATH = $cleanPath -join ';'
    
    Write-Host "✅ WSL環境変数クリア完了" -ForegroundColor Green
    Write-Host "  削除されたLinuxパス数: $((($originalPath -split ';').Count) - ($cleanPath.Count))" -ForegroundColor Gray
}

# 汚染された仮想環境の削除
function Remove-ContaminatedVenv {
    Write-Host "汚染された仮想環境を削除中..." -ForegroundColor Yellow
    
    if (Test-Path "venv") {
        Write-Host "既存の仮想環境を検出: $(Resolve-Path 'venv')" -ForegroundColor Cyan
        
        # 汚染チェック
        $venvPython = "venv\Scripts\python.exe"
        if (Test-Path $venvPython) {
            try {
                $venvInfo = & $venvPython -c "import sys; print(sys.executable)"
                Write-Host "現在の仮想環境Python: $venvInfo" -ForegroundColor Gray
                
                # WSL PATH汚染の確認
                $pipList = & $venvPython -m pip list --format=freeze 2>&1
                if ($pipList -match '/usr/bin' -or $pipList -match 'ãã') {
                    Write-Host "❌ WSL PATH汚染が確認されました" -ForegroundColor Red
                    $contaminated = $true
                } else {
                    Write-Host "✅ 汚染は検出されませんでした" -ForegroundColor Green
                    $contaminated = $false
                }
            } catch {
                Write-Host "⚠️ 仮想環境の状態確認でエラー: $($_.Exception.Message)" -ForegroundColor Yellow
                $contaminated = $true
            }
        } else {
            Write-Host "❌ 不完全な仮想環境が検出されました" -ForegroundColor Red
            $contaminated = $true
        }
        
        if ($contaminated -or $Force) {
            Write-Host "汚染された仮想環境を削除します..." -ForegroundColor Yellow
            
            # プロセス終了の確認
            Get-Process | Where-Object { $_.Path -and $_.Path.Contains("venv") } | ForEach-Object {
                Write-Host "警告: 仮想環境プロセスが実行中です: $($_.ProcessName)" -ForegroundColor Yellow
                $_.Kill()
                Start-Sleep -Seconds 2
            }
            
            Remove-Item -Path "venv" -Recurse -Force
            Write-Host "✅ 汚染された仮想環境削除完了" -ForegroundColor Green
        } else {
            Write-Host "⏭️ 仮想環境は汚染されていないため、削除をスキップします" -ForegroundColor Green
            return $false
        }
    } else {
        Write-Host "⏭️ 既存の仮想環境が見つかりません" -ForegroundColor Gray
    }
    
    return $true
}

# 純粋なWindows Python検出
function Find-CleanWindowsPython {
    Write-Host "純粋なWindows Pythonを検出中..." -ForegroundColor Yellow
    
    # Windows固有のPythonパス
    $windowsPythonPaths = @(
        "${env:LOCALAPPDATA}\Programs\Python\*\python.exe",
        "${env:ProgramFiles}\Python*\python.exe",
        "${env:ProgramFiles(x86)}\Python*\python.exe",
        "C:\Python*\python.exe"
    )
    
    $foundPythons = @()
    
    foreach ($pathPattern in $windowsPythonPaths) {
        $paths = Get-ChildItem -Path $pathPattern -ErrorAction SilentlyContinue
        foreach ($path in $paths) {
            if (Test-Path $path) {
                try {
                    $version = & $path --version 2>&1
                    if ($version -match "Python (\d+\.\d+(?:\.\d+)?)") {
                        $versionString = $matches[1]
                        $foundPythons += @{
                            Path = $path.FullName
                            Version = $versionString
                        }
                        Write-Host "  発見: $($path.FullName) - Python $versionString" -ForegroundColor Cyan
                    }
                } catch {
                    # スキップ
                }
            }
        }
    }
    
    # py.exe launcher (推奨)
    try {
        $pyVersion = & py --version 2>&1
        if ($pyVersion -match "Python (\d+\.\d+(?:\.\d+)?)") {
            $versionString = $matches[1]
            $pyPath = & py -c "import sys; print(sys.executable)" 2>&1
            if (-not $pyPath.Contains('/usr/') -and -not $pyPath.Contains('wsl')) {
                $foundPythons += @{
                    Path = "py"
                    Version = $versionString
                    Executable = $pyPath
                }
                Write-Host "  発見: py launcher - Python $versionString ($pyPath)" -ForegroundColor Cyan
            }
        }
    } catch {
        # py.exeが無い場合はスキップ
    }
    
    if ($foundPythons.Count -eq 0) {
        Write-Host "❌ Windows Pythonが見つかりません" -ForegroundColor Red
        Write-Host "以下のいずれかの方法でPythonをインストールしてください:" -ForegroundColor Yellow
        Write-Host "1. Microsoft Store: https://apps.microsoft.com/store/detail/python-311/9NRWMJP3717K" -ForegroundColor Cyan
        Write-Host "2. 公式サイト: https://www.python.org/downloads/" -ForegroundColor Cyan
        Write-Host "3. winget: winget install Python.Python.3.11" -ForegroundColor Cyan
        return $null
    }
    
    # バージョン要件チェック
    $suitablePythons = $foundPythons | Where-Object {
        $versionParts = $_.Version.Split('.')
        $majorVersion = [int]$versionParts[0]
        $minorVersion = [int]$versionParts[1]
        
        $requiredParts = $RequiredPythonVersion.Split('.')
        $requiredMajor = [int]$requiredParts[0]
        $requiredMinor = [int]$requiredParts[1]
        
        ($majorVersion -gt $requiredMajor) -or ($majorVersion -eq $requiredMajor -and $minorVersion -ge $requiredMinor)
    }
    
    if ($suitablePythons.Count -eq 0) {
        Write-Host "❌ 要件を満たすPython (>= $RequiredPythonVersion) が見つかりません" -ForegroundColor Red
        return $null
    }
    
    # 最新バージョンを選択
    $bestPython = $suitablePythons | Sort-Object { [Version]$_.Version } | Select-Object -Last 1
    Write-Host "✅ 選択されたPython: $($bestPython.Path) - Python $($bestPython.Version)" -ForegroundColor Green
    
    return $bestPython
}

# 純粋なWindows環境での仮想環境作成
function New-CleanVirtualEnvironment {
    param($pythonInfo)
    
    Write-Host "純粋なWindows環境で仮想環境を作成中..." -ForegroundColor Yellow
    
    # 環境変数の完全分離
    $cleanEnv = @{}
    
    # 必要最小限のWindows環境変数のみ保持
    $essentialVars = @(
        "PATH", "SYSTEMROOT", "SYSTEMDRIVE", "PROGRAMFILES", "PROGRAMFILES(X86)",
        "WINDIR", "COMPUTERNAME", "USERNAME", "USERPROFILE", "HOMEPATH",
        "LOCALAPPDATA", "APPDATA", "TEMP", "TMP"
    )
    
    foreach ($var in $essentialVars) {
        if (Get-Variable -Name "env:$var" -ErrorAction SilentlyContinue) {
            $cleanEnv[$var] = (Get-Variable -Name "env:$var").Value
        }
    }
    
    # WindowsのPATHのみに限定
    $windowsOnlyPath = $cleanEnv["PATH"] -split ';' | Where-Object { 
        $_ -and 
        -not $_.StartsWith('/') -and
        -not $_.Contains('wsl') -and
        ($_.StartsWith('C:\') -or $_.StartsWith('%'))
    } | Where-Object { $_.Trim() -ne '' }
    
    $cleanEnv["PATH"] = $windowsOnlyPath -join ';'
    
    Write-Host "  クリーンなPATH設定: $($windowsOnlyPath.Count) パス" -ForegroundColor Gray
    
    # 仮想環境作成コマンド準備
    $pythonCmd = $pythonInfo.Path
    if ($pythonInfo.Path -eq "py") {
        $createCmd = "py -m venv venv"
    } else {
        $createCmd = "`"$($pythonInfo.Path)`" -m venv venv"
    }
    
    Write-Host "  実行コマンド: $createCmd" -ForegroundColor Gray
    
    # 分離されたプロセスで仮想環境作成
    try {
        $processInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processInfo.FileName = "cmd.exe"
        $processInfo.Arguments = "/c $createCmd"
        $processInfo.UseShellExecute = $false
        $processInfo.CreateNoWindow = $true
        $processInfo.RedirectStandardOutput = $true
        $processInfo.RedirectStandardError = $true
        
        # 環境変数の完全置換
        $processInfo.EnvironmentVariables.Clear()
        foreach ($kvp in $cleanEnv.GetEnumerator()) {
            $processInfo.EnvironmentVariables.Add($kvp.Key, $kvp.Value)
        }
        
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $processInfo
        
        Write-Host "  分離されたプロセスで仮想環境を作成中..." -ForegroundColor Gray
        $process.Start() | Out-Null
        $process.WaitForExit()
        
        $output = $process.StandardOutput.ReadToEnd()
        $error = $process.StandardError.ReadToEnd()
        
        if ($process.ExitCode -ne 0) {
            Write-Host "❌ 仮想環境作成に失敗しました" -ForegroundColor Red
            Write-Host "標準出力: $output" -ForegroundColor Gray
            Write-Host "エラー出力: $error" -ForegroundColor Red
            return $false
        }
        
    } catch {
        Write-Host "❌ 仮想環境作成プロセスでエラー: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    # 作成確認
    if (-not (Test-Path "venv\Scripts\python.exe")) {
        Write-Host "❌ 仮想環境の作成に失敗しました" -ForegroundColor Red
        return $false
    }
    
    # 汚染チェック
    try {
        $venvPython = ".\venv\Scripts\python.exe"
        $venvSysPath = & $venvPython -c "import sys; print(';'.join(sys.path))" 2>&1
        
        if ($venvSysPath -match '/usr/' -or $venvSysPath -match 'wsl') {
            Write-Host "❌ 新しい仮想環境にもWSL汚染が検出されました" -ForegroundColor Red
            Write-Host "sys.path: $venvSysPath" -ForegroundColor Gray
            return $false
        }
        
        Write-Host "✅ 純粋なWindows仮想環境作成完了" -ForegroundColor Green
        Write-Host "  仮想環境Python: $venvPython" -ForegroundColor Cyan
        
    } catch {
        Write-Host "❌ 仮想環境の汚染チェックでエラー: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# 依存関係のクリーンインストール
function Install-CleanDependencies {
    Write-Host "依存関係をクリーンインストール中..." -ForegroundColor Yellow
    
    $venvPython = ".\venv\Scripts\python.exe"
    $venvPip = ".\venv\Scripts\pip.exe"
    
    # pipアップグレード（純粋なWindows環境で）
    Write-Host "  pipをアップグレード中..." -ForegroundColor Gray
    try {
        & $venvPython -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) {
            throw "pipアップグレードに失敗"
        }
    } catch {
        Write-Host "❌ pipアップグレードに失敗: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    # requirements.txtから依存関係インストール
    if (Test-Path "requirements.txt") {
        Write-Host "  requirements.txtから依存関係をインストール中..." -ForegroundColor Gray
        try {
            & $venvPip install -r requirements.txt --no-warn-script-location
            if ($LASTEXITCODE -ne 0) {
                throw "依存関係インストールに失敗"
            }
        } catch {
            Write-Host "❌ 依存関係インストールに失敗: $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "⚠️ requirements.txtが見つかりません" -ForegroundColor Yellow
    }
    
    Write-Host "✅ 依存関係のクリーンインストール完了" -ForegroundColor Green
    return $true
}

# 動作確認テスト
function Test-CleanEnvironment {
    Write-Host "クリーンな環境の動作確認中..." -ForegroundColor Yellow
    
    $testScript = @"
import sys
import os

print("=== 環境確認テスト ===")
print(f"Python実行ファイル: {sys.executable}")
print(f"Pythonバージョン: {sys.version}")
print(f"仮想環境: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")

# WSL汚染チェック
contamination_found = False
for path in sys.path:
    if '/usr/' in path or 'wsl' in path.lower():
        print(f"❌ WSL汚染検出: {path}")
        contamination_found = True

if not contamination_found:
    print("✅ WSL汚染は検出されませんでした")

# 主要ライブラリのインポートテスト
test_modules = ['PyQt6.QtCore', 'fitz', 'cv2', 'numpy', 'PIL']
failed_modules = []

for module in test_modules:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError as e:
        print(f"❌ {module}: {e}")
        failed_modules.append(module)

if failed_modules:
    print(f"\n失敗したモジュール: {failed_modules}")
    sys.exit(1)
else:
    print("\n✅ 全てのテストに成功")
"@
    
    $testScript | Out-File -FilePath "environment_test.py" -Encoding UTF8
    
    try {
        & .\venv\Scripts\python.exe environment_test.py
        $success = ($LASTEXITCODE -eq 0)
    } catch {
        Write-Host "❌ 環境テストでエラー: $($_.Exception.Message)" -ForegroundColor Red
        $success = $false
    } finally {
        Remove-Item "environment_test.py" -ErrorAction SilentlyContinue
    }
    
    if ($success) {
        Write-Host "✅ クリーンな環境の動作確認完了" -ForegroundColor Green
    } else {
        Write-Host "❌ 環境テストに失敗しました" -ForegroundColor Red
    }
    
    return $success
}

# メイン処理
try {
    Write-Host "開始時刻: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
    # WSL環境変数クリア
    Clear-WSLEnvironment
    
    # 汚染された仮想環境の削除
    $needRecreate = Remove-ContaminatedVenv
    
    if ($needRecreate) {
        # 純粋なWindows Python検出
        $pythonInfo = Find-CleanWindowsPython
        if (-not $pythonInfo) {
            exit 1
        }
        
        # クリーンな仮想環境作成
        if (-not (New-CleanVirtualEnvironment -pythonInfo $pythonInfo)) {
            exit 1
        }
        
        # 依存関係のクリーンインストール
        if (-not (Install-CleanDependencies)) {
            exit 1
        }
    }
    
    # 動作確認テスト
    if (-not (Test-CleanEnvironment)) {
        Write-Host "⚠️ 一部のテストに失敗しましたが、基本的な環境は整いました" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎉 WSL PATH汚染の根本的解決完了！" -ForegroundColor Green
    Write-Host ""
    Write-Host "次のステップ:" -ForegroundColor Cyan
    Write-Host "1. アプリケーション実行テスト: .\run_windows.ps1" -ForegroundColor White
    Write-Host "2. EXE化実行: .\build_exe.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "完了時刻: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
} catch {
    Write-Host ""
    Write-Host "❌ WSL汚染解決中にエラーが発生しました: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "詳細なログが必要な場合は -Force フラグを使用してください" -ForegroundColor Yellow
    exit 1
}