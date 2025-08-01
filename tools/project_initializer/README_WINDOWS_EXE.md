# Windows EXE生成手順

## ❌ 現在の問題
WSL環境で生成されたファイルはLinux ELF実行ファイルであり、WindowsのEXEファイルではありません。

## ✅ 解決方法

### 1. Windows環境での実行が必要
Windows用EXEを生成するには、**Windows環境**で以下を実行してください：

```cmd
# コマンドプロンプトで実行
cd C:\Users\tky99\DEV\techbridge\app\mini_apps\project_initializer
build_windows_exe.bat
```

### 2. PowerShellでの実行
```powershell
# PowerShellで実行
cd "C:\Users\tky99\DEV\techbridge\app\mini_apps\project_initializer"
.\build_windows_exe.bat
```

### 3. 手動セットアップ（必要に応じて）
```cmd
# 仮想環境が存在しない場合
python -m venv venv_exe
venv_exe\Scripts\activate
pip install -r requirements_exe.txt

# EXE生成
pyinstaller build_exe.spec --clean
```

## 📁 生成されるファイル構造
```
dist/
└── TechBridge_ProjectInitializer/
    ├── TechBridge_ProjectInitializer.exe  ← Windows実行ファイル
    └── _internal/                         ← 依存ライブラリ
        ├── PyQt6/
        ├── config/
        ├── .env
        └── ...
```

## 🚀 実行方法
```cmd
cd dist\TechBridge_ProjectInitializer
TechBridge_ProjectInitializer.exe
```

## 📋 必要環境
- Windows 10/11 (64bit)
- .NET Framework (PyQt6用)
- Visual C++ Redistributable (必要に応じて)

## ⚠️ 重要事項
- WSL環境では**Linux実行ファイル**しか生成できません
- **Windows環境**でのビルドが必須です
- 全ての依存関係は`_internal`フォルダに含まれます
- フォルダ全体をコピーして配布してください