# 📋 TechBridge ProjectInitializer - バージョン管理ガイド

## 🎯 バージョン管理ポリシー

- **初回リリース**: v1.0
- **マイナー更新**: 0.1ずつ増加 (1.0 → 1.1 → 1.2)
- **メジャー更新**: 1.0ずつ増加 (1.9 → 2.0)

## 🔧 バージョン管理コマンド

### 現在のバージョン確認
```powershell
python version_manager.py
```

### マイナーバージョンアップ（0.1増加）
```powershell
python version_manager.py minor
```

### メジャーバージョンアップ（1.0増加）
```powershell
python version_manager.py major
```

## 🚀 本番版EXE作成（バージョン管理付き）

### 通常のビルド（現在のバージョン）
```powershell
.\create_production_exe.ps1
```

### バージョンアップしてビルド（マイナー）
```powershell
.\create_production_exe.ps1 -IncrementVersion -VersionType minor
```

### バージョンアップしてビルド（メジャー）
```powershell
.\create_production_exe.ps1 -IncrementVersion -VersionType major
```

## 📝 バージョン履歴の例

```
v1.0   - 初回リリース（本番版）
v1.1   - 機能追加・改善
v1.2   - バグ修正
v1.3   - UI改善
...
v2.0   - 大幅アップデート
```

## 🎯 使用例

### 日常的な更新作業
```powershell
# 1. 機能追加・修正作業
# 2. マイナーバージョンアップしてEXE生成
.\create_production_exe.ps1 -IncrementVersion -VersionType minor

# 結果: v1.0 → v1.1 でEXE生成
```

### 大幅アップデート時
```powershell
# 1. 大幅な機能追加・変更作業
# 2. メジャーバージョンアップしてEXE生成
.\create_production_exe.ps1 -IncrementVersion -VersionType major

# 結果: v1.9 → v2.0 でEXE生成
```

## 📦 配布ファイル命名規則

生成されるファイルは以下の命名規則に従います：

- **EXEフォルダ**: `TechBridge_ProjectInitializer`
- **EXE本体**: `TechBridge_ProjectInitializer.exe`  
- **配布ZIP**: `TechBridge_ProjectInitializer_v{バージョン}.zip`

例：
- `TechBridge_ProjectInitializer_v1.0.zip`
- `TechBridge_ProjectInitializer_v1.1.zip`
- `TechBridge_ProjectInitializer_v2.0.zip`

## 🔍 バージョン情報の確認場所

バージョン情報は以下の場所で確認できます：

1. **ソースコード**: `main_exe.py` の `__version__` 変数
2. **アプリケーション起動時**: コンソール出力
3. **バージョン管理スクリプト**: `python version_manager.py`

## ⚠️ 注意事項

- バージョンアップは自動でコミットされません
- 手動でGitコミットを行ってください
- リリース前にはデバッグ版でのテストを推奨します