@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo   TechZip Pre-flight Checker - EXE Build Script
echo ================================================================
echo.

:: 管理者権限チェック
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 【警告】管理者権限で実行することを推奨します
    echo.
)

:: Pythonインストール確認
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 【エラー】Pythonがインストールされていません
    echo Python 3.8以降をインストールしてください
    pause
    exit /b 1
)

echo ✓ Python環境確認済み
for /f "tokens=*" %%a in ('python --version') do set PYTHON_VERSION=%%a
echo   %PYTHON_VERSION%
echo.

:: 作業ディレクトリの確認
if not exist "main.py" (
    echo 【エラー】main.pyが見つかりません
    echo プロジェクトルートディレクトリで実行してください
    pause
    exit /b 1
)

echo ✓ プロジェクトルート確認済み
echo.

:: 仮想環境の作成と有効化
echo [1/6] 仮想環境のセットアップ...
if exist "build_env" (
    echo   既存の仮想環境を削除中...
    rmdir /s /q build_env
)

python -m venv build_env
if %errorLevel% neq 0 (
    echo 【エラー】仮想環境の作成に失敗しました
    pause
    exit /b 1
)

call build_env\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo 【エラー】仮想環境の有効化に失敗しました
    pause
    exit /b 1
)

echo   ✓ 仮想環境作成完了
echo.

:: 依存関係のインストール
echo [2/6] 依存関係のインストール...
python -m pip install --upgrade pip
if %errorLevel% neq 0 (
    echo 【警告】pipのアップグレードに失敗しました
)

python -m pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo 【エラー】依存関係のインストールに失敗しました
    goto cleanup
)

:: PyInstallerのインストール
python -m pip install pyinstaller
if %errorLevel% neq 0 (
    echo 【エラー】PyInstallerのインストールに失敗しました
    goto cleanup
)

echo   ✓ 依存関係インストール完了
echo.

:: 古いビルド成果物の削除
echo [3/6] 古いビルド成果物の削除...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "__pycache__" rmdir /s /q __pycache__
echo   ✓ クリーンアップ完了
echo.

:: テストの実行（オプション）
echo [4/6] 事前テストの実行...
set /p run_test="事前テストを実行しますか？ (y/N): "
if /i "%run_test%"=="y" (
    echo   テスト実行中...
    python tests/test_windows_powershell.py
    if %errorLevel% neq 0 (
        echo 【警告】テストが失敗しました。続行しますか？
        pause
    ) else (
        echo   ✓ テスト完了
    )
) else (
    echo   テストをスキップしました
)
echo.

:: EXEファイルのビルド
echo [5/6] EXEファイルのビルド中...
echo   これには数分かかる場合があります...
pyinstaller build_exe.spec --clean --noconfirm
if %errorLevel% neq 0 (
    echo 【エラー】EXEビルドに失敗しました
    goto cleanup
)

echo   ✓ EXEビルド完了
echo.

:: ビルド結果の確認
echo [6/6] ビルド結果の確認...
if exist "dist\TechZipPreflightCheckerGUI.exe" (
    echo   ✓ EXEファイル作成成功: dist\TechZipPreflightCheckerGUI.exe
    
    :: ファイルサイズの表示
    for %%A in ("dist\TechZipPreflightCheckerGUI.exe") do (
        set /a size=%%~zA/1024/1024
        echo   ファイルサイズ: !size! MB
    )
    
    :: テスト実行の提案
    echo.
    set /p test_exe="作成されたGUIアプリケーションをテストしますか？ (y/N): "
    if /i "%test_exe%"=="y" (
        echo   GUIアプリケーション起動中...
        cd dist
        start TechZipPreflightCheckerGUI.exe
        echo   ✓ GUI起動を開始しました
        timeout /t 3 /nobreak >nul
        cd ..
    )
) else (
    echo 【エラー】EXEファイルが作成されませんでした
    goto cleanup
)

echo.
echo ================================================================
echo   ビルド完了！
echo ================================================================
echo.
echo 生成されたファイル:
echo   - dist\TechZipPreflightCheckerGUI.exe  (統合テストGUIアプリケーション)
echo.
echo 配布時に必要なファイル:
echo   - TechZipPreflightCheckerGUI.exe
echo   - .env ファイル（メール設定用）
echo.
echo 使用方法:
echo   1. TechZipPreflightCheckerGUI.exe を任意の場所にコピー
echo   2. 同じ場所に .env ファイルを配置
echo   3. EXEファイルをダブルクリックしてGUIアプリケーションを起動
echo   4. 環境チェック → ファイル選択 → テスト実行の順で操作
echo.

goto end

:cleanup
echo.
echo ビルドプロセスを中断しています...
call build_env\Scripts\deactivate.bat 2>nul
if exist "build_env" rmdir /s /q build_env
echo 仮想環境をクリーンアップしました
pause
exit /b 1

:end
:: 仮想環境の非活性化と削除
call build_env\Scripts\deactivate.bat 2>nul
echo.
echo 仮想環境をクリーンアップ中...
rmdir /s /q build_env
echo ✓ クリーンアップ完了

pause