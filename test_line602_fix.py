#!/usr/bin/env python3
"""
Line 602 AttributeError修正の直接テスト

元の問題:
- container.get(ApiProcessor) → AttributeError: 'ServiceContainer' object has no attribute 'get'

修正:
- container.get_service(ApiProcessor) → 正常動作
"""

def test_line_602_fix():
    """Line 602の修正を直接テスト"""
    print("=" * 60)
    print("Line 602 DI Container AttributeError修正テスト")
    print("=" * 60)
    
    try:
        # Step 1: DI Container取得
        print("\n1. DI Container取得...")
        from core.di_container import get_container, configure_services
        container = configure_services()
        print(f"✓ DI Container: {type(container)}")
        
        # Step 2: ApiProcessor import
        print("\n2. ApiProcessor import...")
        from core.api_processor import ApiProcessor
        print(f"✓ ApiProcessor: {ApiProcessor}")
        
        # Step 3: 旧方式（修正前）の問題を確認
        print("\n3. 旧方式（container.get）の問題確認...")
        try:
            # これは失敗するはず
            api_old = container.get(ApiProcessor)
            print("✗ 想定外: container.get()が動作してしまいました")
            return False
        except AttributeError as ae:
            print(f"✓ 期待通りのエラー: {ae}")
        except Exception as e:
            print(f"✓ container.get()は存在しません: {type(e).__name__}")
        
        # Step 4: 新方式（修正後）の動作確認
        print("\n4. 新方式（container.get_service）の動作確認...")
        try:
            api_new = container.get_service(ApiProcessor)
            print(f"✓ container.get_service()成功: {type(api_new)}")
            
            # インスタンスの妥当性確認
            if hasattr(api_new, 'process_zip_file'):
                print("✓ ApiProcessor機能確認: process_zip_file メソッド存在")
            
        except Exception as e:
            print(f"✗ container.get_service()エラー: {e}")
            return False
        
        # Step 5: 修正コードの実際の動作をシミュレート
        print("\n5. 実際の修正コード（line 602）のシミュレーション...")
        
        def simulate_api_processor_property():
            """line 602周辺の修正されたコードをシミュレート"""
            _api_processor = None
            
            try:
                if _api_processor is None:
                    from core.api_processor import ApiProcessor
                    from core.di_container import get_container
                    
                    # DI Containerから適切にインスタンス化（Enhanced Error Handling）
                    try:
                        container = get_container()
                        print(f"    [SIM] DI Container obtained: {type(container)}")
                        
                        # 修正箇所: get_service()メソッドを使用（line 602）
                        _api_processor = container.get_service(ApiProcessor)
                        print(f"    [SIM] ApiProcessor instance created via DI: {type(_api_processor)}")
                        
                        # DI統合の成功を記録
                        print("    [SIM] DI Container integration successful")
                        
                    except Exception as di_error:
                        print(f"    [SIM] DI Container integration error: {di_error}")
                        raise AttributeError(f"Failed to initialize ApiProcessor: {di_error}") from di_error
                
                return _api_processor
                
            except Exception as prop_error:
                print(f"    [SIM] Property access error: {prop_error}")
                raise AttributeError(f"api_processor property failed: {prop_error}") from prop_error
        
        # シミュレーション実行
        simulated_api = simulate_api_processor_property()
        print(f"✓ シミュレーション成功: {type(simulated_api)}")
        
        print("\n" + "=" * 60)
        print("🎉 Line 602修正完了確認!")
        print("✅ container.get(ApiProcessor) → AttributeError解決")
        print("✅ container.get_service(ApiProcessor) → 正常動作")
        print("✅ DI Container統合エラー修正完了")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ テストエラー: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_line_602_fix()
    if success:
        print("\n🚀 修正検証完了: Line 602のAttributeErrorは解決されました!")
    else:
        print("\n❌ 修正検証失敗: 追加の対応が必要です")
    
    exit(0 if success else 1)