# 🌐 TechZip グローバルホットキー設定

PowerShellが起動していない状態でも、**Ctrl+Shift+I** でPowerShell 7を起動してTechZipアプリを実行できます。

## 📋 前提条件

### AutoHotkeyのインストール
1. [AutoHotkey公式サイト](https://www.autohotkey.com/)からダウンロード
2. インストーラーを実行（v1.1またはv2どちらでもOK）

### PowerShell 7（推奨）
- インストールされていない場合は通常のPowerShellが使用されます
- [PowerShell 7のダウンロード](https://github.com/PowerShell/PowerShell/releases)

## 🚀 セットアップ

### 1. グローバルホットキーの設定
管理者権限は不要です：

```batch
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool
setup_global_hotkey.bat
```

これにより：
- スタートアップフォルダにショートカットが作成されます
- AutoHotkeyスクリプトが自動起動します
- Windows起動時に自動的に有効になります

### 2. 設定の削除
```batch
remove_global_hotkey.bat
```

## 🎯 使い方

どのアプリケーションからでも使用可能：
1. **Ctrl+Shift+I** を押す
2. PowerShell 7（またはPowerShell）が起動
3. TechZipアプリが自動的に実行される

## 🔧 カスタマイズ

### ホットキーの変更
`TechZip_Hotkey_v1.ahk`を編集：
```autohotkey
^+i::  ; Ctrl+Shift+I
```

他の例：
- `#t::` - Win+T
- `!^t::` - Alt+Ctrl+T
- `F9::` - F9キー

### PowerShellのオプション変更
```autohotkey
runCommand := pwsh7Path . " -NoExit -WorkingDirectory """ . appPath . """ -Command ""& .\run_windows.ps1"""
```

## 📌 トラブルシューティング

### AutoHotkeyが見つからない
- AutoHotkeyをインストールしてください
- インストール後、PCを再起動

### ホットキーが動作しない
1. タスクトレイでAutoHotkeyアイコンを確認
2. 他のアプリケーションとキーが競合していないか確認
3. `TechZip_Hotkey_v1.ahk`をダブルクリックして手動実行

### セキュリティ警告が表示される
- AutoHotkeyスクリプトは安全です
- Windows Defenderで許可してください

## 🔐 セキュリティ

このスクリプトは：
- システムファイルを変更しません
- 管理者権限を必要としません
- TechZipアプリの起動のみを行います