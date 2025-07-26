# TechZip Pre-flight Checker - クイックスタート

Write-Host "================================================================" -ForegroundColor Green
Write-Host "  TechZip Pre-flight Checker - クイックスタート" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "実行方法を選択してください:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. システムPythonで実行（簡単・推奨）" -ForegroundColor White
Write-Host "2. 仮想環境をセットアップして実行（上級者向け）" -ForegroundColor White
Write-Host "3. 依存関係のみインストール" -ForegroundColor White
Write-Host "4. 直接GUI起動を試す" -ForegroundColor White
Write-Host ""

$choice = Read-Host "選択してください (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "システムPython用の依存関係をインストールします..." -ForegroundColor Blue
        & ".\install_deps_system.ps1"
        
        Write-Host ""
        Write-Host "依存関係インストール完了後、GUIを起動しますか？" -ForegroundColor Yellow
        $startGui = Read-Host "(y/N)"
        if ($startGui -eq "y" -or $startGui -eq "Y") {
            & ".\run_gui_simple.ps1"
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "仮想環境をセットアップします..." -ForegroundColor Blue
        & ".\setup_windows_venv.ps1"
    }
    
    "3" {
        Write-Host ""
        Write-Host "依存関係のインストールのみ実行します..." -ForegroundColor Blue
        & ".\install_deps_system.ps1"
    }
    
    "4" {
        Write-Host ""
        Write-Host "GUIを直接起動します..." -ForegroundColor Blue
        & ".\run_gui_simple.ps1"
    }
    
    default {
        Write-Host ""
        Write-Host "[エラー] 無効な選択です" -ForegroundColor Red
        Write-Host "1-4の数字を入力してください" -ForegroundColor Red
        Read-Host "Enterキーで終了"
        exit 1
    }
}

Write-Host ""
Write-Host "クイックスタート完了" -ForegroundColor Green
Read-Host "Enterキーで終了"