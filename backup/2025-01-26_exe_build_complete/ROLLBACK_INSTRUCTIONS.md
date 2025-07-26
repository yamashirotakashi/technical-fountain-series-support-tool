# ロールバック手順

## バックアップ情報
- 日時: 2025-01-26
- コミットハッシュ: e0a2f61
- 状態: Windows EXEビルド機能実装完了

## 含まれる主要な変更
1. 完全な日本語化
2. カスタムボタンラベル（配置/一部ファイルを選択/キャンセル）
3. APIモードがデフォルト
4. Windows EXEビルド機能

## ロールバック方法

### 方法1: Gitを使用
```bash
git reset --hard e0a2f61
```

### 方法2: バックアップから復元
```bash
# 現在のファイルをバックアップ
mkdir -p backup/current_backup
cp -r *.py gui/ core/ utils/ backup/current_backup/

# バックアップから復元
cp -r backup/2025-01-26_exe_build_complete/* .
```

## 重要なファイル
- main.py (エントリーポイント)
- gui/main_window.py (APIモードデフォルト設定)
- gui/components/*.py (日本語化済み)
- gui/dialogs/simple_warning_dialog.py (文字化け修正済み)
- build_exe.ps1 (EXEビルドスクリプト)
- techzip.spec (PyInstaller設定)

## 動作確認済みの機能
- Windows ネイティブ実行
- Qt6完全移行
- 日本語GUI
- カスタムダイアログボタン
- APIモード/従来モード切り替え
- ファイル選択機能
- EXEビルド