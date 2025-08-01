# 🖥️ Windows EXE生成手順書

## 🚨 現在の状況
WSL環境で生成されたファイルは**Linux ELF実行ファイル**です。
Windows用EXEを生成するには、**Windows環境**での実行が必要です。

## ✅ Windows環境での確実なEXE生成手順

### 方法1: PowerShellスクリプト実行（推奨）

**1. PowerShellを管理者権限で起動**

**2. 実行ポリシーを一時的に変更**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**3. プロジェクトディレクトリに移動**
```powershell
cd "C:\Users\tky99\DEV\techbridge\app\mini_apps\project_initializer"
```

**4. EXE生成スクリプトを実行**
```powershell
.\windows_exe_setup.ps1 -Clean
```

### 方法2: 手動実行

**1. コマンドプロンプトを起動**

**2. プロジェクトディレクトリに移動**
```cmd
cd C:\Users\tky99\DEV\techbridge\app\mini_apps\project_initializer
```

**3. 仮想環境が存在しない場合は作成**
```cmd
python -m venv venv_exe
```

**4. 仮想環境をアクティベート**
```cmd
venv_exe\Scripts\activate
```

**5. 依存関係をインストール**
```cmd
pip install -r requirements_exe.txt
```

**6. 古いビルドをクリア**
```cmd
rmdir /s /q dist
rmdir /s /q build
```

**7. Windows EXE生成**
```cmd
pyinstaller build_exe.spec --clean --noconfirm
```

## 🎯 成功時の結果

生成される構造：
```
dist/
└── TechBridge_ProjectInitializer/
    ├── TechBridge_ProjectInitializer.exe  ← Windows実行ファイル
    └── _internal/                         ← 依存ライブラリ
        ├── PyQt6/
        ├── config/
        │   └── service_account.json
        ├── .env
        └── [その他の依存関係]
```

## 🚀 EXE実行方法

**コマンドラインから：**
```cmd
cd dist\TechBridge_ProjectInitializer
TechBridge_ProjectInitializer.exe
```

**エクスプローラーから：**
`TechBridge_ProjectInitializer.exe`をダブルクリック

## 📋 必要な環境

- Windows 10/11 (64bit)
- Python 3.8以上
- .NET Framework (PyQt6用)
- Visual C++ Redistributable (必要に応じて)

## 🛠️ トラブルシューティング

### エラー1: "pyinstaller コマンドが見つかりません"
```cmd
venv_exe\Scripts\pip install pyinstaller
```

### エラー2: "モジュールが見つかりません"
```cmd
venv_exe\Scripts\pip install -r requirements_exe.txt
```

### エラー3: "実行ポリシーエラー"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## ⚠️ 重要な注意事項

1. **WSL環境では Windows EXE を生成できません**
2. **Windows環境での実行が必須です**
3. **フォルダ全体（TechBridge_ProjectInitializer）を配布してください**
4. **_internal フォルダは実行に必要です**

## 📦 配布用パッケージング

EXE生成後、配布用にZIPファイルを作成：
```powershell
Compress-Archive -Path "dist\TechBridge_ProjectInitializer" -DestinationPath "TechBridge_ProjectInitializer_v1.0.0.zip"
```

これで完全なWindows用配布パッケージが作成されます。