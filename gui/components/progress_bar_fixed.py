"""プログレスバーパネルモジュール（修正版）"""

        if is_indeterminate:
            self.progress_bar.setMaximum(0)
            self.progress_bar.setMinimum(0)
        else:
            self.progress_bar.setMaximum(100)
            self.progress_bar.setMinimum(0)