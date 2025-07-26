"""Pre-flight Check状態管理モジュール"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.logger import get_logger


class PreflightStateManager:
    """Pre-flight Checkの状態を管理"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.state_dir = Path.home() / ".techzip" / "preflight_state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.current_state_file = self.state_dir / "current_state.json"
        
    def save_state(self, state: Dict[str, Any]):
        """現在の状態を保存
        
        Args:
            state: 保存する状態データ
        """
        try:
            state['last_updated'] = datetime.now().isoformat()
            
            with open(self.current_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                
            self.logger.info("状態を保存しました")
            
        except Exception as e:
            self.logger.error(f"状態保存エラー: {e}")
            
    def load_state(self) -> Optional[Dict[str, Any]]:
        """保存された状態を読み込み
        
        Returns:
            状態データ（存在しない場合はNone）
        """
        try:
            if not self.current_state_file.exists():
                return None
                
            with open(self.current_state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            self.logger.info(f"状態を読み込みました（最終更新: {state.get('last_updated')}）")
            return state
            
        except Exception as e:
            self.logger.error(f"状態読み込みエラー: {e}")
            return None
            
    def clear_state(self):
        """状態をクリア"""
        try:
            if self.current_state_file.exists():
                self.current_state_file.unlink()
                self.logger.info("状態をクリアしました")
                
        except Exception as e:
            self.logger.error(f"状態クリアエラー: {e}")
            
    def create_checkpoint(self, name: str, state: Dict[str, Any]):
        """チェックポイントを作成
        
        Args:
            name: チェックポイント名
            state: 保存する状態データ
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_file = self.state_dir / f"checkpoint_{name}_{timestamp}.json"
            
            state['checkpoint_name'] = name
            state['checkpoint_time'] = datetime.now().isoformat()
            
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"チェックポイントを作成: {checkpoint_file.name}")
            
        except Exception as e:
            self.logger.error(f"チェックポイント作成エラー: {e}")
            
    def list_checkpoints(self) -> List[Dict[str, str]]:
        """利用可能なチェックポイントをリスト
        
        Returns:
            チェックポイント情報のリスト
        """
        checkpoints = []
        
        try:
            for checkpoint_file in self.state_dir.glob("checkpoint_*.json"):
                try:
                    with open(checkpoint_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    checkpoints.append({
                        'file': checkpoint_file.name,
                        'name': data.get('checkpoint_name', 'Unknown'),
                        'time': data.get('checkpoint_time', 'Unknown'),
                        'path': str(checkpoint_file)
                    })
                except:
                    continue
                    
            # 時間順にソート（新しい順）
            checkpoints.sort(key=lambda x: x['time'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"チェックポイントリスト取得エラー: {e}")
            
        return checkpoints
        
    def restore_checkpoint(self, checkpoint_path: str) -> Optional[Dict[str, Any]]:
        """チェックポイントから復元
        
        Args:
            checkpoint_path: チェックポイントファイルのパス
            
        Returns:
            復元された状態データ
        """
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            # 現在の状態として保存
            self.save_state(state)
            
            self.logger.info(f"チェックポイントから復元: {Path(checkpoint_path).name}")
            return state
            
        except Exception as e:
            self.logger.error(f"チェックポイント復元エラー: {e}")
            return None