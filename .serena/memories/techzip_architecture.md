# TechZip プロジェクト アーキテクチャ

## プロジェクト概要
- 技術の泉シリーズ制作支援ツール
- Qt6ベースのGUIアプリケーション
- 複数のメール監視実装とAPI統合

## 主要コンポーネント
1. **core/** - ビジネスロジック
   - WorkflowProcessorWithErrorDetection（506行 - 要リファクタリング）
   - 複数のメール監視実装（統合候補）
   - Preflight検証サブシステム

2. **gui/** - Qt6 UI層
   - components/（再利用可能なウィジェット）
   - dialogs/（ダイアログ群）

3. **CodeBlockOverFlowDisposal/** - PDFオーバーフロー検出
   - 独立したサブプロジェクト
   - OCR統合、フィルターチェーン

## リファクタリング推奨事項
- WorkflowProcessorWithErrorDetectionの分解
- メール監視実装の統合
- テストファイルの整理（重複多数）