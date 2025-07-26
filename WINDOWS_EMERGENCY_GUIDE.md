# 🚨 Windows環境 緊急対応ガイド

## 問題の概要

WSL環境で作成された仮想環境がWindows PowerShellと競合し、以下のエラーが発生：
```
did not find executable at '/usr/bin\python.exe'
```

## 🛠️ 緊急対応手順（3つの選択肢）

### 選択肢1：完全修復（推奨）

WSL環境を完全にクリーンアップしてWindows専用環境を構築：

```powershell
# 1. 完全修復実行
.\fix_windows_environment.ps1

# 2. 修復後GUI起動
.\run_gui_clean.ps1
```

### 選択肢2：システムPython使用（最も簡単）

仮想環境を使わずシステムPythonで直接実行：

```powershell
# システムPython専用起動
.\run_gui_system_only.ps1
```

### 選択肢3：手動修復

手動で環境をクリーンアップ：

```powershell
# 1. 既存仮想環境削除
Remove-Item -Recurse -Force venv

# 2. 依存関係インストール
pip install --user requests psutil python-dotenv beautifulsoup4

# 3. GUI起動
python main_gui.py
```

## 📋 実行前チェックリスト

### 必須要件確認
```powershell
# Python確認
python --version

# tkinter確認
python -c "import tkinter; print('OK')"

# プロジェクトディレクトリ確認
Get-Location
Get-ChildItem main_gui.py
```

### PowerShell設定確認
```powershell
# 実行ポリシー確認
Get-ExecutionPolicy

# 必要に応じて設定
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🔧 トラブルシューティング

### エラーコード103
- **原因**: 仮想環境の混在
- **解決**: `.\fix_windows_environment.ps1` を実行

### tkinter不足エラー
- **原因**: Python不完全インストール
- **解決**: [Python.org](https://python.org)から完全版を再インストール

### 依存関係エラー
- **解決**: 
  ```powershell
  pip install --user requests psutil python-dotenv beautifulsoup4
  ```

### 実行ポリシーエラー
- **解決**:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## 📁 利用可能なスクリプト一覧

| スクリプト | 用途 | 推奨度 |
|-----------|------|--------|
| `fix_windows_environment.ps1` | 完全修復 | ⭐⭐⭐ |
| `run_gui_clean.ps1` | 修復後起動 | ⭐⭐⭐ |
| `run_gui_system_only.ps1` | システムPython専用 | ⭐⭐ |
| `quickstart.ps1` | 初期セットアップ | ⭐⭐ |
| `install_deps_system.ps1` | 依存関係インストール | ⭐ |

## 🎯 成功の確認

以下が表示されれば成功：
```
🎉 すべてのインポートが成功しました！
✅ 準備完了！GUIアプリケーションを起動できます。
```

## 📞 サポート情報

### 環境情報収集スクリプト
```powershell
Write-Host "=== 環境情報 ==="
Write-Host "Python: $(python --version 2>&1)"
Write-Host "PowerShell: $($PSVersionTable.PSVersion)"
Write-Host "作業ディレクトリ: $(Get-Location)"
Write-Host "仮想環境: $(if(Test-Path 'venv'){'あり'}else{'なし'})"
Write-Host "main_gui.py: $(if(Test-Path 'main_gui.py'){'あり'}else{'なし'})"
```

### よくある質問

**Q: 仮想環境は必要ですか？**
A: 必須ではありません。システムPythonでも動作します。

**Q: どのスクリプトを使えばいいですか？**
A: 迷ったら `fix_windows_environment.ps1` → `run_gui_clean.ps1` の順で実行してください。

**Q: エラーが解決しません**
A: `run_gui_system_only.ps1` を試してください。それでも動かない場合はPythonの再インストールが必要です。

---

## 📝 更新履歴

- **2025-07-26**: WSL/Windows環境混在問題の緊急対応ガイド作成
- 複数の修復オプション提供
- システムPython専用スクリプト追加