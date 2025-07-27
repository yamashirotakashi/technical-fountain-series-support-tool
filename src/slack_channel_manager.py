#!/usr/bin/env python3
"""
Slackチャネル管理支援ツール

Botの参加状況確認と招待支援機能を提供
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackChannelManager:
    """Slackチャネル管理クラス"""
    
    def __init__(self, bot_token: str):
        self.client = WebClient(token=bot_token)
        self.cache_file = Path("config/slack_channel_cache.json")
        self.pending_invites_file = Path("config/pending_invites.json")
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """必要なディレクトリを作成"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.pending_invites_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_bot_channels(self) -> Dict[str, Dict]:
        """Bot参加チャネル一覧を取得"""
        try:
            response = self.client.conversations_list(
                types="private_channel",
                limit=1000
            )
            
            channels = {}
            for channel in response.get('channels', []):
                if channel.get('is_member', False):
                    channels[channel['name']] = {
                        'id': channel['id'],
                        'name': channel['name'],
                        'is_private': True,
                        'last_checked': datetime.now().isoformat()
                    }
            
            # キャッシュを更新
            self._update_cache(channels)
            return channels
            
        except SlackApiError as e:
            logger.error(f"Failed to get channels: {e}")
            return self._load_cache()
    
    def _update_cache(self, channels: Dict):
        """チャネルキャッシュを更新"""
        cache_data = {
            'channels': channels,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    def _load_cache(self) -> Dict:
        """キャッシュからチャネル情報を読み込み"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('channels', {})
        return {}
    
    def check_channel_membership(self, channel_name: str) -> Dict[str, any]:
        """特定チャネルへの参加状況を確認"""
        channels = self.get_bot_channels()
        
        if channel_name in channels:
            return {
                'is_member': True,
                'channel_id': channels[channel_name]['id'],
                'message': f"✅ Bot is already in #{channel_name}"
            }
        else:
            # 招待待ちリストに追加
            self._add_pending_invite(channel_name)
            
            return {
                'is_member': False,
                'channel_id': None,
                'message': f"❌ Bot is not in #{channel_name}",
                'action_required': "Manual invitation needed",
                'instruction': self._get_invite_instruction(channel_name)
            }
    
    def _add_pending_invite(self, channel_name: str):
        """招待待ちリストに追加"""
        pending = self._load_pending_invites()
        
        if channel_name not in pending:
            pending[channel_name] = {
                'requested_at': datetime.now().isoformat(),
                'attempts': 1,
                'status': 'pending'
            }
        else:
            pending[channel_name]['attempts'] += 1
            pending[channel_name]['last_attempt'] = datetime.now().isoformat()
        
        with open(self.pending_invites_file, 'w', encoding='utf-8') as f:
            json.dump(pending, f, indent=2, ensure_ascii=False)
    
    def _load_pending_invites(self) -> Dict:
        """招待待ちリストを読み込み"""
        if self.pending_invites_file.exists():
            with open(self.pending_invites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _get_invite_instruction(self, channel_name: str) -> str:
        """招待手順を返す"""
        return f"""
Botを招待する手順:
1. Slackで #{channel_name} チャネルを開く
2. チャネル名をクリック → 「メンバーを追加」
3. @techzip_pdf_bot を検索して追加
4. 追加完了後、もう一度PDF生成を実行
"""
    
    def get_missing_channels(self, target_channels: List[str]) -> List[str]:
        """未参加のチャネル一覧を取得"""
        current_channels = set(self.get_bot_channels().keys())
        target_set = set(target_channels)
        return list(target_set - current_channels)
    
    def generate_invite_report(self) -> str:
        """招待レポートを生成"""
        current_channels = self.get_bot_channels()
        pending_invites = self._load_pending_invites()
        
        report = []
        report.append("# Slack Bot 参加状況レポート")
        report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 参加済みチャネル
        report.append(f"## 参加済みチャネル ({len(current_channels)}個)")
        tech_channels = [ch for ch in current_channels.keys() if ch.startswith(('n', 'N'))]
        other_channels = [ch for ch in current_channels.keys() if not ch.startswith(('n', 'N'))]
        
        if tech_channels:
            report.append("\n### 技術の泉シリーズ")
            for ch in sorted(tech_channels):
                report.append(f"- {ch}")
        
        if other_channels:
            report.append("\n### その他")
            for ch in sorted(other_channels):
                report.append(f"- {ch}")
        
        # 招待待ち
        if pending_invites:
            report.append(f"\n## 招待待ちチャネル ({len(pending_invites)}個)")
            for ch, info in sorted(pending_invites.items()):
                if info['status'] == 'pending':
                    report.append(f"- {ch} (試行回数: {info['attempts']})")
        
        return "\n".join(report)


# CLIツール
if __name__ == "__main__":
    import os
    import sys
    
    bot_token = os.environ.get('SLACK_BOT_TOKEN')
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN環境変数が設定されていません")
        sys.exit(1)
    
    manager = SlackChannelManager(bot_token)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            channels = manager.get_bot_channels()
            print(f"📊 Bot参加チャネル: {len(channels)}個")
            for name in sorted(channels.keys()):
                print(f"  - {name}")
        
        elif command == "check" and len(sys.argv) > 2:
            channel_name = sys.argv[2]
            result = manager.check_channel_membership(channel_name)
            print(result['message'])
            if not result['is_member']:
                print(result['instruction'])
        
        elif command == "report":
            report = manager.generate_invite_report()
            print(report)
            
            # ファイルにも保存
            report_file = Path("slack_bot_status_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n📄 レポートを保存: {report_file}")
        
        else:
            print("使い方:")
            print("  python slack_channel_manager.py list     # 参加チャネル一覧")
            print("  python slack_channel_manager.py check <channel>  # 特定チャネルの確認")
            print("  python slack_channel_manager.py report   # 詳細レポート生成")
    else:
        # デフォルト: レポート生成
        report = manager.generate_invite_report()
        print(report)