from __future__ import annotations
"""定数定義モジュール"""

# メール送信者アドレス
EMAIL_SENDERS = {
    'REVIEW_CONVERSION': 'kanazawa@nextpublishing.jp',  # ReVIEW変換サービス
    'WORD2XHTML5': 'support-np@impress.co.jp',         # Word2XHTML5エラーチェックサービス
}

# メール件名パターン
EMAIL_SUBJECTS = {
    'REVIEW_CONVERSION': 'Re:VIEW to 超原稿用紙',
    'WORD2XHTML5': 'ダウンロード用URLのご案内',
}

# タイムアウト設定（秒）
EMAIL_TIMEOUTS = {
    'REVIEW_CONVERSION': 600,  # 10分
    'WORD2XHTML5': 300,       # 5分（Word2XHTML5は通常3-5分）
}