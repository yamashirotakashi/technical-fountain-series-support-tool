# 🖥️ Windows EXE生成完全ガイド v2.0

## 🚨 重要な注意事項

- **WSL環境では Windows EXE を生成できません**
- **Windows環境での実行が必須です**
- Linux ELFファイルが生成されている場合は、このガイドに従ってください

## ✅ 確実なWindows EXE生成手順

### 方法1: PowerShellスクリプト実行（推奨）

**1. PowerShellを管理者権限で起動**

**2. 実行ポリシーを設定**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**3. プロジェクトディレクトリに移動**
```powershell
cd "C:\Users\tky99\DEV\techbridge\app\mini_apps\project_initializer"
```

**4. 新しいWindows EXE生成スクリプトを実行**
```powershell
.\create_windows_exe.ps1
```

### 方法2: バッチファイル実行

**1. コマンドプロンプトを起動**

**2. プロジェクトディレクトリに移動**
```cmd
cd C:\Users\tky99\DEV\techbridge\app\mini_apps\project_initializer
```

**3. Windows EXE生成バッチファイルを実行**
```cmd
create_windows_exe.bat
```

### 方法3: 手動実行（トラブルシューティング用）

```cmd
# 1. プロジェクトディレクトリに移動
cd C:\Users\tky99\DEV\techbridge\app\mini_apps\project_initializer

# 2. Windows用仮想環境を作成（初回のみ）
python -m venv venv_windows

# 3. 仮想環境をアクティベート
venv_windows\Scripts\activate

# 4. 依存関係をインストール
pip install --upgrade pip
pip install -r requirements_exe.txt

# 5. 古いビルドをクリア
rmdir /s /q dist
rmdir /s /q build

# 6. Windows EXE生成
pyinstaller build_windows_exe.spec --clean --noconfirm
```

## 🎯 成功時の期待結果

生成される構造：
```
C:\Users\tky99\DEV\techbridge\app\mini_apps\project_initializer\
└── dist\
    └── TechBridge_ProjectInitializer\
        ├── TechBridge_ProjectInitializer.exe  ← Windows実行ファイル
        └── _internal\                         ← 依存ライブラリ
            ├── PyQt6\
            ├── config\
            │   └── service_account.json
            ├── base_library.zip
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

## 📋 前提条件

- Windows 10/11 (64bit)
- Python 3.8以上がインストール済み
- .NET Framework (PyQt6用)
- Visual C++ Redistributable (必要に応じて)

## 🛠️ トラブルシューティング

### エラー1: "pyinstaller コマンドが見つかりません"
```cmd
venv_windows\Scripts\pip install pyinstaller
```

### エラー2: "モジュールが見つかりません"
```cmd
venv_windows\Scripts\pip install -r requirements_exe.txt
```

### エラー3: "実行ポリシーエラー"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### エラー4: "Python環境が見つかりません"
Python公式サイトから最新版をダウンロード・インストールしてください

## ✅ 成功確認方法

1. **ファイル存在確認**
   ```cmd
   dir dist\TechBridge_ProjectInitializer\TechBridge_ProjectInitializer.exe
   ```

2. **実行テスト**
   ```cmd
   cd dist\TechBridge_ProjectInitializer
   TechBridge_ProjectInitializer.exe --help
   ```

3. **ファイル形式確認**
   - ファイル拡張子が `.exe` であること
   - ファイルサイズが数MB以上であること
   - Windowsのプロパティで「種類: アプリケーション」と表示されること

## 📦 配布用パッケージング

EXE生成後、配布用にZIPファイルを作成：
```powershell
Compress-Archive -Path "dist\TechBridge_ProjectInitializer" -DestinationPath "TechBridge_ProjectInitializer_Windows_v2.0.zip"
```

## ⚠️ 重要な制限事項

1. **WSL環境制限**: WSLでは絶対にWindows EXEは生成できません
2. **フォルダ配布**: `_internal`フォルダも含めて配布が必要
3. **依存関係**: Pythonランタイムが内包されているため、配布先にPythonは不要
4. **ウイルス対策**: 初回実行時にウイルス対策ソフトの警告が出る可能性があります

## 📄 変更履歴

- **v2.0**: WSL制限を明確化し、Windows専用ビルドスクリプトに刷新
- **v1.0**: 初期版（WSL互換性問題あり）

---

**注意**: このガイドに従ってもEXE生成に失敗する場合は、WSL環境で実行していないか確認してください。