# TechZip Pre-flight Checker - Windows問題解決ガイド

## 🚨 今回発生した問題の解決方法

### 問題：仮想環境の混在エラー
```
did not find executable at '/usr/bin\python.exe'
```

**原因**: WSL環境で作成された仮想環境をWindows PowerShellから使用しようとしたため

**解決方法**: 以下の手順で実行してください

## 🚀 推奨解決手順

### オプション1: システムPythonで実行（最も簡単）

1. **クイックスタート実行**
   ```powershell
   .\quickstart.ps1
   ```
   
2. **「1」を選択してシステムPython環境をセットアップ**

3. **GUI起動**
   ```powershell
   .\run_gui_simple.ps1
   ```

### オプション2: Windows用仮想環境を作成

1. **既存仮想環境を削除**
   ```powershell
   Remove-Item -Recurse -Force venv
   ```

2. **Windows用仮想環境セットアップ**
   ```powershell
   .\setup_windows_venv.ps1
   ```

3. **新しいPowerShellでGUI起動**
   ```powershell
   .\run_gui_simple.ps1
   ```

### オプション3: 依存関係のみインストール

```powershell
.\install_deps_system.ps1
```

## 🛠️ よくある問題と解決方法

### 1. ExecutionPolicy エラー
```
実行ポリシーによりスクリプトの実行が禁止されています
```

**解決方法**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. tkinter不足エラー
```
ModuleNotFoundError: No module named 'tkinter'
```

**解決方法**:
- Pythonを完全版で再インストール
- [Python.org](https://python.org)から「Add to PATH」オプション付きでインストール

### 3. pip認識エラー
```
'pip' is not recognized
```

**解決方法**:
```powershell
python -m pip install --upgrade pip
```

### 4. 依存関係インストールエラー
```
ERROR: Could not install packages
```

**解決方法**:
```powershell
# 管理者権限でPowerShellを開く
python -m pip install --upgrade pip
pip install requests psutil python-dotenv beautifulsoup4
```

## 📋 診断コマンド

### Python環境確認
```powershell
python --version
python -m pip --version
python -c "import tkinter; print('tkinter OK')"
```

### プロジェクト状況確認
```powershell
Get-ChildItem -Name "main_gui.py"
Get-ChildItem -Name "venv" -Directory
```

### 依存関係確認
```powershell
python test_imports_only.py
```

## 🔧 手動実行手順

上記の方法がすべて失敗した場合：

1. **最小限の依存関係インストール**
   ```powershell
   pip install --user requests psutil python-dotenv beautifulsoup4
   ```

2. **GUI直接起動**
   ```powershell
   python main_gui.py
   ```

3. **エラー発生時の対処**
   - エラーメッセージをコピー
   - `python --version`でPythonバージョン確認
   - `pip list`で インストール済みパッケージ確認

## 📞 サポート情報

### 環境情報収集
問題報告時は以下の情報を含めてください：

```powershell
# 環境情報収集
Write-Host "Python Version:"
python --version

Write-Host "Pip Version:"
python -m pip --version

Write-Host "Installed Packages:"
pip list

Write-Host "PowerShell Version:"
$PSVersionTable.PSVersion

Write-Host "Windows Version:"
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion
```

### ログファイル確認
- GUI内の「実行ログ」タブでエラー詳細を確認
- PowerShellでのエラーメッセージをコピー

## 🎯 成功の確認

以下が表示されれば成功：
```
🎉 すべてのインポートが成功しました！
✅ 準備完了！GUIアプリケーションを起動できます。
```

---

## 📝 更新履歴

- **2025-07-26**: Windows環境での仮想環境混在問題解決
- クイックスタートスクリプト追加
- システムPython実行オプション追加