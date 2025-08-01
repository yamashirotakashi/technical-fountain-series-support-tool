# Project Initializer Tool

## 概要
技術の泉シリーズプロジェクト初期化ツール（PJinit）
TechBridgeプロジェクトから移管されたスタンドアロンツール

## 場所
- 開発: `/technical-fountain-series-support-tool/tools/project_initializer/`
- 配布: `/technical-fountain-series-support-tool/dist/tools/PJinit/`

## 特徴
- techzipのメインアプリケーションとは独立
- 独自の仮想環境とビルドプロセス
- Google Sheets、Slack、GitHub APIとの連携

## ビルド方法
```powershell
cd tools\project_initializer
.\build.ps1
```

## 配布
ビルド成果物は `dist/tools/PJinit/` に配置され、独立したツールとして配布可能。