# TechZip クイックスタート

## 🚀 簡単起動

```powershell
.\run.ps1
```

## 📋 機能

- **自動仮想環境作成/確認**
- **依存関係自動インストール**
- **GUI起動**
- **終了後自動クリーンアップ**

## 🔧 オプション

```powershell
.\run.ps1 -Reset    # 仮想環境を再作成
```

## 📁 ファイル整理

- `run.ps1` - **メイン起動スクリプト**
- `_deprecated/` - 古いスクリプト（使用しない）
  - `run_gui.ps1`
  - `run_windows.ps1`
  - `setup_and_run_techwf.ps1`
  - その他の古いスクリプト

## ⚡ 実行例

```powershell
# 通常起動
PS> .\run.ps1

# 環境リセット起動
PS> .\run.ps1 -Reset
```

## 📝 動作フロー

1. Python環境チェック
2. 仮想環境作成/確認
3. 依存関係インストール
4. GUI起動（main_gui.py）
5. GUI終了待機
6. 仮想環境から退出
7. 完了

## 🛠️ トラブルシューティング

### Python未インストール
```
[エラー] Pythonをインストールしてください
```
→ Python 3.8以降をインストール

### 仮想環境エラー
```powershell
.\run.ps1 -Reset
```
→ 仮想環境を再作成

### 依存関係エラー
- `requirements.txt` を確認
- インターネット接続を確認