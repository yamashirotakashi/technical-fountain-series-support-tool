# 🚀 TechZip ホットキー設定ガイド

## 問題が発生している場合の解決方法

### 方法1: デスクトップショートカット（最も簡単）
1. `create_shortcut.vbs` をダブルクリック
2. デスクトップに「TechZip」ショートカットが作成される
3. ショートカットをダブルクリックでアプリ起動
4. デスクトップがアクティブな時は Ctrl+Shift+I でも起動可能

### 方法2: 直接起動バッチファイル
```batch
run_techzip.bat
```
これをダブルクリックするだけでアプリが起動します。

### 方法3: PowerShell 7がある場合
```batch
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool
pwsh -NoExit -Command "& .\run_windows.ps1"
```

### 方法4: 通常のPowerShellの場合
```batch
cd C:\Users\tky99\DEV\technical-fountain-series-support-tool
powershell -NoExit -ExecutionPolicy Bypass -File .\run_windows.ps1
```

## AutoHotkeyの問題解決

### AutoHotkeyが動作しない場合
1. AutoHotkeyを再インストール
2. Windows Defenderの除外設定に追加
3. 管理者権限で実行

### 代替案: タスクスケジューラ
1. Win+R → `taskschd.msc`
2. 「基本タスクの作成」
3. トリガー: ログオン時
4. 操作: `run_techzip.bat` を起動

## トラブルシューティング

### "run_windows.ps1 not found" エラー
- ファイル名を確認（大文字小文字に注意）
- パスが正しいか確認

### PowerShellエラー
- 実行ポリシーを確認: `Get-ExecutionPolicy`
- 必要に応じて: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Python not found
- Python がインストールされているか確認
- 環境変数 PATH に Python が含まれているか確認