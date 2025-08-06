"""
Configuration Migration Utility
Phase 2: Configuration Hell Resolution
設定システム移行ユーティリティ

Purpose:
- Legacy Config から新しいConfigManager への移行を支援
- 設定値の整合性チェックとマッピング
- 安全な段階的移行の実現
"""
from __future__ import annotations

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from utils.logger import get_logger


class ConfigurationMigration:
    """設定システム移行ユーティリティ"""
    
    # Legacy Config から新しいConfigManager へのキーマッピング
    KEY_MAPPING = {
        # Web設定 -> API設定への移行
        "web.upload_url": "api.nextpublishing.base_url",
        "web.username": "api.nextpublishing.username", 
        "web.password": "api.nextpublishing.password",
        
        # パス設定の移行
        "paths.git_base": "paths.base_repository_path",
        "paths.output_base": "paths.output_directory",
        
        # Google Sheet設定の保持（そのまま）
        "google_sheet.sheet_id": "google_sheet.sheet_id",
        "google_sheet.credentials_path": "google_sheet.credentials_path",
        
        # メール設定の移行（新しい構造）
        "email.gmail_address": "email.gmail_address",
        "email.gmail_app_password": "email.gmail_app_password",
        "email.gmail_credentials_path": "email.gmail_credentials_path"
    }
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def analyze_current_config(self) -> Dict[str, Any]:
        """現在の設定状況を分析"""
        analysis = {
            "legacy_config_exists": False,
            "new_config_exists": False,
            "legacy_config_path": None,
            "new_config_path": None,
            "migration_needed": False,
            "conflicts": [],
            "recommendations": []
        }
        
        # Legacy設定の存在チェック
        legacy_paths = [
            Path("config/settings.json"),
            Path("config/techgate_settings.json")
        ]
        
        for path in legacy_paths:
            if path.exists():
                analysis["legacy_config_exists"] = True
                analysis["legacy_config_path"] = str(path)
                break
        
        # 新しい設定の存在チェック
        new_config_path = Path("config/techzip_config.yaml")
        if new_config_path.exists():
            analysis["new_config_exists"] = True
            analysis["new_config_path"] = str(new_config_path)
        
        # 移行が必要かどうかの判定
        if analysis["legacy_config_exists"] and not analysis["new_config_exists"]:
            analysis["migration_needed"] = True
            analysis["recommendations"].append("Legacy設定が検出されました。新しい統一設定への移行を推奨します。")
        
        elif analysis["legacy_config_exists"] and analysis["new_config_exists"]:
            analysis["recommendations"].append("両方の設定が存在します。整合性をチェックしてください。")
            
        elif not analysis["legacy_config_exists"] and not analysis["new_config_exists"]:
            analysis["recommendations"].append("設定ファイルが見つかりません。初期セットアップが必要です。")
        
        return analysis
    
    def migrate_legacy_to_new(self, dry_run: bool = True) -> Dict[str, Any]:
        """Legacy設定から新しい統一設定への移行"""
        result = {
            "success": False,
            "dry_run": dry_run,
            "migrated_keys": [],
            "skipped_keys": [],
            "errors": [],
            "new_config_preview": {}
        }
        
        try:
            # Legacy設定を読み込み
            legacy_config = self._load_legacy_config()
            if not legacy_config:
                result["errors"].append("Legacy設定ファイルが読み込めません")
                return result
            
            # 新しい設定構造を構築
            new_config = self._create_new_config_structure()
            
            # キーマッピングに従って移行
            for legacy_key, new_key in self.KEY_MAPPING.items():
                legacy_value = self._get_nested_value(legacy_config, legacy_key)
                
                if legacy_value is not None:
                    self._set_nested_value(new_config, new_key, legacy_value)
                    result["migrated_keys"].append(f"{legacy_key} -> {new_key}")
                    self.logger.info(f"設定移行: {legacy_key} -> {new_key}")
                else:
                    result["skipped_keys"].append(legacy_key)
            
            # 環境変数との統合
            self._integrate_environment_variables(new_config)
            
            result["new_config_preview"] = new_config
            
            if not dry_run:
                # 実際に新しい設定ファイルを保存
                self._save_new_config(new_config)
                result["success"] = True
                self.logger.info("設定移行が完了しました")
            else:
                result["success"] = True
                self.logger.info("設定移行のドライランが完了しました（実際の保存は行われていません）")
            
        except Exception as e:
            result["errors"].append(f"移行エラー: {str(e)}")
            self.logger.error(f"設定移行エラー: {e}")
        
        return result
    
    def validate_configuration_consistency(self) -> Dict[str, Any]:
        """Legacy設定と新設定の整合性チェック"""
        validation = {
            "consistent": True,
            "differences": [],
            "warnings": [],
            "critical_issues": []
        }
        
        try:
            # 両方の設定を読み込み
            legacy_config = self._load_legacy_config()
            new_config = self._load_new_config()
            
            if not legacy_config or not new_config:
                validation["critical_issues"].append("いずれかの設定が読み込めません")
                validation["consistent"] = False
                return validation
            
            # キーマッピングに基づく整合性チェック
            for legacy_key, new_key in self.KEY_MAPPING.items():
                legacy_value = self._get_nested_value(legacy_config, legacy_key)
                new_value = self._get_nested_value(new_config, new_key)
                
                if legacy_value != new_value:
                    validation["consistent"] = False
                    validation["differences"].append({
                        "key": f"{legacy_key} vs {new_key}",
                        "legacy_value": legacy_value,
                        "new_value": new_value
                    })
            
            # 重要な設定の検証
            critical_keys = [
                ("api.nextpublishing.username", "認証情報"),
                ("api.nextpublishing.base_url", "APIエンドポイント"),
                ("paths.base_repository_path", "ベースパス")
            ]
            
            for key, description in critical_keys:
                value = self._get_nested_value(new_config, key)
                if not value:
                    validation["critical_issues"].append(f"{description}が設定されていません: {key}")
                    validation["consistent"] = False
        
        except Exception as e:
            validation["critical_issues"].append(f"整合性チェックエラー: {str(e)}")
            validation["consistent"] = False
        
        return validation
    
    def _load_legacy_config(self) -> Optional[Dict[str, Any]]:
        """Legacy設定を読み込み"""
        legacy_paths = [
            Path("config/settings.json"),
            Path("config/techgate_settings.json")
        ]
        
        for path in legacy_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    self.logger.error(f"Legacy設定読み込みエラー: {path} - {e}")
        
        return None
    
    def _load_new_config(self) -> Optional[Dict[str, Any]]:
        """新しい設定を読み込み"""
        config_path = Path("config/techzip_config.yaml")
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self.logger.error(f"新設定読み込みエラー: {config_path} - {e}")
        
        return None
    
    def _create_new_config_structure(self) -> Dict[str, Any]:
        """新しい設定構造のテンプレートを作成"""
        from core.config_manager import ConfigManager
        temp_manager = ConfigManager()
        return temp_manager._create_default_config()
    
    def _get_nested_value(self, config: Dict[str, Any], key_path: str) -> Any:
        """ネストされた設定値を取得"""
        try:
            keys = key_path.split('.')
            value = config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
                    
            return value
        except Exception:
            return None
    
    def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: Any) -> None:
        """ネストされた設定値を設定"""
        try:
            keys = key_path.split('.')
            current = config
            
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            current[keys[-1]] = value
        except Exception as e:
            self.logger.error(f"設定値設定エラー: {key_path} - {e}")
    
    def _integrate_environment_variables(self, config: Dict[str, Any]) -> None:
        """環境変数を統合"""
        import os
        
        env_mappings = [
            ("NEXTPUB_USERNAME", "api.nextpublishing.username"),
            ("NEXTPUB_PASSWORD", "api.nextpublishing.password"), 
            ("NEXTPUB_BASE_URL", "api.nextpublishing.base_url"),
            ("SLACK_BOT_TOKEN", "api.slack.bot_token"),
            ("TECHZIP_BASE_PATH", "paths.base_repository_path"),
            ("TECHZIP_LOG_LEVEL", "logging.level")
        ]
        
        for env_var, config_key in env_mappings:
            env_value = os.getenv(env_var)
            if env_value:
                self._set_nested_value(config, config_key, env_value)
                self.logger.info(f"環境変数統合: {env_var} -> {config_key}")
    
    def _save_new_config(self, config: Dict[str, Any]) -> None:
        """新しい設定をファイルに保存"""
        config_path = Path("config/techzip_config.yaml")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        self.logger.info(f"新しい設定を保存しました: {config_path}")


def migrate_configuration(dry_run: bool = True) -> Dict[str, Any]:
    """設定移行のエントリーポイント"""
    migration = ConfigurationMigration()
    return migration.migrate_legacy_to_new(dry_run)


def analyze_configuration() -> Dict[str, Any]:
    """設定分析のエントリーポイント"""
    migration = ConfigurationMigration()
    return migration.analyze_current_config()


def validate_configuration() -> Dict[str, Any]:
    """設定検証のエントリーポイント"""
    migration = ConfigurationMigration()
    return migration.validate_configuration_consistency()