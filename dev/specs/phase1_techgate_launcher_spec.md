# Phase 1: TECHGATEランチャー基本実装仕様

## 概要
TECHGATEランチャーは、技術の泉シリーズ制作支援ツールの各種機能を統合管理するメインアプリケーションです。

## 実装要件

### 1. ランチャー機能
- **アプリケーション一覧表示**
  - TECHZIP（既存の変換処理）
  - TechBook27 Analyzer（新規統合）
  - 将来の拡張用スロット

- **アプリケーション起動**
  - 各アプリをモジュールとして起動
  - 独立したプロセスとして実行
  - 起動状態の管理

### 2. 共通機能
- **設定管理**
  - 統一されたsettings.json
  - アプリケーション間での設定共有
  - ユーザープリファレンス

- **認証管理**
  - Git認証情報の一元管理
  - Google API認証の管理
  - セキュアな資格情報保存

- **ログ管理**
  - 統合ログビューア
  - アプリケーション別ログフィルタ
  - ログレベル設定

### 3. UI設計
```
┌─────────────────────────────────────┐
│  TECHGATE - 技術の泉シリーズ支援    │
├─────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│ │         │ │         │ │         ││
│ │ TECHZIP │ │TechBook │ │  Future ││
│ │         │ │Analyzer │ │   App   ││
│ └─────────┘ └─────────┘ └─────────┘│
├─────────────────────────────────────┤
│ [設定] [ログ] [ヘルプ]              │
└─────────────────────────────────────┘
```

### 4. アーキテクチャ
- **プラグインアーキテクチャ**
  - 各アプリケーションをプラグインとして管理
  - 動的ロード/アンロード
  - バージョン管理

- **IPC（プロセス間通信）**
  - 起動したアプリとの通信
  - ステータス監視
  - エラーハンドリング

## 実装ファイル構造
```
app/
├── launcher/
│   ├── __init__.py
│   ├── main.py              # ランチャーメイン
│   ├── app_manager.py       # アプリケーション管理
│   ├── plugin_loader.py     # プラグインローダー
│   └── ui/
│       ├── launcher_window.py
│       └── app_tile.py      # アプリタイル表示
├── plugins/
│   ├── __init__.py
│   ├── base_plugin.py       # プラグイン基底クラス
│   ├── techzip_plugin.py    # TECHZIP統合
│   └── analyzer_plugin.py   # TechBook27 Analyzer統合
└── shared/
    ├── config_manager.py    # 設定管理
    ├── auth_manager.py      # 認証管理
    └── log_manager.py       # ログ管理
```

## 実装段階

### Phase 1-1: 基本ランチャーUI
- ランチャーウィンドウの実装
- アプリケーションタイルの表示
- 基本的な起動機能

### Phase 1-2: プラグインシステム
- プラグイン基底クラスの実装
- 既存アプリのプラグイン化
- 動的ロード機能

### Phase 1-3: 共通機能統合
- 設定管理システム
- 認証情報の共有
- 統合ログシステム

## Windows EXE化対応
- ランチャー自体をEXE化
- 各プラグインは個別のモジュール
- リソースのバンドル方法を検討

## 成功基準
1. ランチャーから各アプリケーションを起動できる
2. 設定・認証情報が共有される
3. 統一されたユーザー体験
4. 将来の拡張が容易な設計