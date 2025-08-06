#!/usr/bin/env python3
"""Phase 4: DI Container Performance Benchmark Test

パフォーマンス最適化効果を検証するベンチマークテスト
- サービス解決時間測定（目標: <1ms）
- キャッシュ効果検証
- LRU最適化の効果測定
"""

import sys
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_test_services(container):
    """テスト用サービス群を作成"""
    
    # 依存関係のないサービス
    class SimpleService:
        def __init__(self):
            self.value = "simple"
    
    # 単一依存関係サービス
    class SingleDependencyService:
        def __init__(self, simple: SimpleService):
            self.simple = simple
            
    # 複数依存関係サービス
    class MultipleDependencyService:
        def __init__(self, simple: SimpleService, single: SingleDependencyService):
            self.simple = simple
            self.single = single
    
    # 深い依存関係チェーン
    class Level1Service:
        def __init__(self, multiple: MultipleDependencyService):
            self.multiple = multiple
            
    class Level2Service:
        def __init__(self, level1: Level1Service):
            self.level1 = level1
    
    # コンテナに登録
    container.register_singleton(SimpleService, SimpleService)
    container.register_transient(SingleDependencyService, SingleDependencyService)
    container.register_scoped(MultipleDependencyService, MultipleDependencyService)
    container.register_transient(Level1Service, Level1Service)
    container.register_transient(Level2Service, Level2Service)
    
    return {
        'SimpleService': SimpleService,
        'SingleDependencyService': SingleDependencyService,
        'MultipleDependencyService': MultipleDependencyService,
        'Level1Service': Level1Service,
        'Level2Service': Level2Service
    }

def benchmark_service_resolution(container, service_type, iterations: int = 1000) -> Dict[str, float]:
    """サービス解決のベンチマーク"""
    
    print(f"🏃‍♂️ {service_type.__name__} ベンチマーク ({iterations}回)")
    
    times = []
    
    # ウォームアップ（キャッシュを準備）
    for _ in range(10):
        container.get_service(service_type)
    
    # 実際の測定
    for i in range(iterations):
        start_time = time.perf_counter()
        service = container.get_service(service_type)
        end_time = time.perf_counter()
        
        duration_ms = (end_time - start_time) * 1000
        times.append(duration_ms)
        
        # サービスが正しく取得できたことを確認
        assert service is not None, f"サービス取得失敗: {service_type.__name__}"
    
    # 統計計算
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    median_time = statistics.median(times)
    std_dev = statistics.stdev(times) if len(times) > 1 else 0
    
    # 目標達成確認
    target_met = avg_time < 1.0
    performance_grade = "🟢 EXCELLENT" if avg_time < 0.5 else "🟡 GOOD" if target_met else "🔴 NEEDS IMPROVEMENT"
    
    print(f"  平均: {avg_time:.3f}ms | 中央値: {median_time:.3f}ms | 最小: {min_time:.3f}ms | 最大: {max_time:.3f}ms")
    print(f"  標準偏差: {std_dev:.3f}ms | {performance_grade} | 目標達成: {target_met}")
    
    return {
        'service_name': service_type.__name__,
        'average_ms': avg_time,
        'median_ms': median_time,
        'min_ms': min_time,
        'max_ms': max_time,
        'std_dev_ms': std_dev,
        'target_met': target_met,
        'iterations': iterations
    }

def benchmark_cache_effectiveness(container, service_types: List[type]) -> Dict[str, Any]:
    """キャッシュ効果測定"""
    
    print("\n🧠 キャッシュ効果ベンチマーク")
    
    # メトリクスをリセット
    container._metrics = container._metrics.__class__()
    
    # 複数回のサービス解決でキャッシュ効果を測定
    total_resolutions = 0
    for service_type in service_types:
        for _ in range(50):  # 各サービスを50回解決
            container.get_service(service_type)
            total_resolutions += 1
    
    # パフォーマンスメトリクス取得
    metrics = container.get_performance_metrics()
    
    print(f"  総解決回数: {total_resolutions}")
    print(f"  平均解決時間: {metrics.get('overall_avg_resolution_ms', 'N/A')}ms")
    print(f"  キャッシュヒット率: {metrics.get('cache_hit_rate_percent', 'N/A')}%")
    print(f"  パフォーマンス状態: {metrics.get('status', 'N/A')}")
    
    return metrics

def run_comprehensive_benchmark():
    """包括的ベンチマークテスト"""
    
    print("📊 Phase 4: DI Container Performance Benchmark")
    print("=" * 60)
    
    from core.di_container import ServiceContainer
    
    # 新しいコンテナインスタンス作成（クリーンな状態で測定）
    container = ServiceContainer()
    
    # テストサービス群作成
    service_types = create_test_services(container)
    
    print(f"\n🔧 テスト対象サービス: {len(service_types)}種類")
    for name in service_types.keys():
        print(f"  - {name}")
    
    # 個別サービスベンチマーク
    print(f"\n🏁 個別サービス解決ベンチマーク")
    print("-" * 40)
    
    benchmark_results = []
    for service_type in service_types.values():
        result = benchmark_service_resolution(container, service_type, iterations=500)
        benchmark_results.append(result)
    
    # キャッシュ効果測定
    cache_metrics = benchmark_cache_effectiveness(container, list(service_types.values()))
    
    # 総合評価
    print(f"\n📈 ベンチマーク結果サマリー")
    print("=" * 60)
    
    # 全サービスの平均パフォーマンス
    all_averages = [r['average_ms'] for r in benchmark_results]
    overall_average = statistics.mean(all_averages)
    target_achievement_rate = sum(1 for r in benchmark_results if r['target_met']) / len(benchmark_results) * 100
    
    print(f"全体平均解決時間: {overall_average:.3f}ms")
    print(f"目標達成率: {target_achievement_rate:.1f}% ({sum(1 for r in benchmark_results if r['target_met'])}/{len(benchmark_results)}サービス)")
    
    # パフォーマンス最適化効果評価
    if overall_average < 1.0:
        if overall_average < 0.5:
            grade = "🌟 OUTSTANDING"
            message = "LRU最適化が期待以上の効果を発揮しています"
        else:
            grade = "✅ SUCCESS"
            message = "目標パフォーマンス(<1ms)を達成しました"
    else:
        grade = "❌ OPTIMIZATION NEEDED"
        message = "追加の最適化が必要です"
    
    print(f"最適化評価: {grade}")
    print(f"総評: {message}")
    
    # 詳細レポート
    print(f"\n📋 詳細パフォーマンスレポート")
    print("-" * 60)
    
    print("サービス別パフォーマンス:")
    for result in sorted(benchmark_results, key=lambda x: x['average_ms']):
        status_icon = "🟢" if result['target_met'] else "🔴"
        print(f"  {status_icon} {result['service_name']:<25} {result['average_ms']:>6.3f}ms")
    
    print(f"\nキャッシュ効果:")
    print(f"  ヒット率: {cache_metrics.get('cache_hit_rate_percent', 'N/A')}%")
    print(f"  総解決数: {cache_metrics.get('total_resolutions', 'N/A')}")
    print(f"  健全性: {cache_metrics.get('status', 'N/A')}")
    
    # Phase 4完了判定
    phase4_success = (
        overall_average < 1.0 and 
        target_achievement_rate >= 80 and
        cache_metrics.get('status') == 'healthy'
    )
    
    print(f"\n🎯 Phase 4完了判定")
    print("=" * 60)
    
    if phase4_success:
        print("🎉 Phase 4: Testing and validation 完了成功!")
        print("✅ パフォーマンス目標達成 (<1ms)")
        print("✅ 最適化効果確認完了")
        print("✅ アーキテクチャ検証完了")
        print("\n🚀 技術の泉シリーズ制作支援ツール")
        print("   Phase 3-2 → Phase 4 アーキテクチャ刷新完了!")
    else:
        print("⚠️  Phase 4: 一部改善が必要")
        if overall_average >= 1.0:
            print("❌ パフォーマンス目標未達成")
        if target_achievement_rate < 80:
            print("❌ 目標達成率が不十分")
        if cache_metrics.get('status') != 'healthy':
            print("❌ キャッシュ最適化が不十分")
    
    return phase4_success, {
        'overall_average_ms': overall_average,
        'target_achievement_rate': target_achievement_rate,
        'benchmark_results': benchmark_results,
        'cache_metrics': cache_metrics
    }

def main():
    """メインベンチマーク実行"""
    try:
        success, metrics = run_comprehensive_benchmark()
        
        if success:
            print(f"\n🏆 ベンチマーク完了: Phase 4 SUCCESS")
            sys.exit(0)
        else:
            print(f"\n⚠️  ベンチマーク完了: Phase 4 要改善")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ベンチマークエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()