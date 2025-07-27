# Windows環境でのTECHZIP1.5.exe ビルドガイド

## 問題の概要
WSLとWindows PowerShellの環境が混在しており、PyInstallerが間違ったPythonパスを参照している。

## 解決手順

### 1. 現在の問題
```
did not find executable at '/usr/bin\python.exe': ????????????????
```
PyInstallerがWSLパス（/usr/bin）を探しているが、Windows PowerShellで実行している。

### 2. 修正方法

#### オプション A: fix_python_env.bat 実行（推奨）
```powershell
# Windows PowerShellで実行
.\fix_python_env.bat
```

#### オプション B: 手動実行
```powershell
# 1. 仮想環境を確実にアクティベート
venv\Scripts\Activate.ps1

# 2. PyInstallerが正しくインストールされているか確認
pip show pyinstaller

# 3. インストールされていない場合
pip install pyinstaller

# 4. ビルド実行
pyinstaller techzip_windows.spec --clean --noconfirm
```

### 3. 環境変数の確認と修正

もしPATH環境変数にWSLパスが含まれている場合：

```powershell
# 現在のPATHを確認
$env:PATH -split ';'

# WSLパス要素を一時的に除去（セッション内のみ）
$env:PATH = ($env:PATH -split ';' | Where-Object { $_ -notlike '*wsl*' -and $_ -notlike '*/usr/*' }) -join ';'
```

### 4. 完全にクリーンな環境での実行

```powershell
# PowerShellを管理者として再起動
# プロジェクトディレクトリに移動
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool

# 仮想環境をアクティベート
venv\Scripts\Activate.ps1

# PyInstallerを再インストール
pip uninstall pyinstaller -y
pip install pyinstaller

# ビルド実行
pyinstaller techzip_windows.spec --clean --noconfirm
```

### 5. 確認事項

ビルド成功時の出力場所：
```
dist\TECHZIP1.5\TECHZIP1.5.exe
```

## トラブルシューティング

### Q: まだWSLパスエラーが出る場合
A: PowerShellのプロファイルや環境変数にWSLパスが設定されている可能性があります。

```powershell
# PowerShellプロファイルの確認
$PROFILE
Get-Content $PROFILE
```

### Q: venv\Scripts\Activate.ps1が実行できない場合
A: 実行ポリシーを一時的に変更：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
venv\Scripts\Activate.ps1
```

### Q: PyInstallerでC++エラーが出る場合
A: Visual Studio Build Toolsが必要：

```powershell
# Visual Studio Build Tools 2019+ をインストール
# または
pip install --upgrade setuptools wheel
```

## 最終確認

ビルド成功後：
1. `dist\TECHZIP1.5\TECHZIP1.5.exe` が存在することを確認
2. EXEファイルをダブルクリックして起動テスト
3. Slack PDF投稿機能の動作確認