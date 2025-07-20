# 🎯 TechZip ホットキー設定ガイド

## Ctrl+Shift+I でアプリを起動

### 🚀 クイックスタート

#### 1. 永続的な設定（推奨）
PowerShellプロファイルに設定を追加し、常に利用可能にします：

```powershell
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool
.\setup_hotkey.ps1
```

設定後、PowerShellを再起動するか以下を実行：
```powershell
. $PROFILE
```

#### 2. 一時的な設定
現在のPowerShellセッションでのみ有効：

```powershell
.\hotkey_quick_launch.ps1
```

### 📝 使い方

1. PowerShellウィンドウ上で **Ctrl+Shift+I** を押す
2. 新しいPowerShellウィンドウが開き、TechZipアプリが自動起動
3. 元のPowerShellウィンドウはそのまま使用可能

### ⚙️ 設定管理

#### 設定の確認
```powershell
# プロファイルの内容を確認
notepad $PROFILE
```

#### 設定の削除
```powershell
.\remove_hotkey.ps1
```

### 🔧 トラブルシューティング

#### PSReadLineモジュールがない場合
```powershell
Install-Module -Name PSReadLine -Force -SkipPublisherCheck
```

#### プロファイルの実行ポリシーエラー
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 📌 注意事項

- ホットキーはPowerShellウィンドウがアクティブな時のみ動作
- 他のアプリケーションでは動作しません
- Windows Terminalでも動作します