#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM TEST - GOD MODE 10000
Test toàn bộ chương trình crypto AI prediction
"""

import sys
import os
import traceback
from datetime import datetime

# Add parent directory to path to allow package imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# Test results storage
test_results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def print_header(text):
    """Print test section header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_test(name, status, details=""):
    """Print test result"""
    symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")

def test_imports():
    """Test 1: Kiểm tra tất cả imports"""
    print_header("TEST 1: IMPORTS & DEPENDENCIES")

    # Core Python libraries
    tests = [
        ("Python Standard Library", ["os", "sys", "time", "datetime", "json", "logging"]),
        ("Data Processing", ["pandas", "numpy"]),
        ("AI/ML", ["sklearn", "xgboost", "lightgbm"]),
        ("Async/Threading", ["asyncio", "threading", "concurrent.futures"]),
        ("Network", ["requests", "aiohttp"]),
        ("Exchange", ["ccxt"]),
    ]

    for category, modules in tests:
        try:
            for module in modules:
                __import__(module)
            print_test(f"{category}", "PASS", f"All modules: {', '.join(modules)}")
            test_results['passed'].append(f"Import: {category}")
        except ImportError as e:
            print_test(f"{category}", "FAIL", str(e))
            test_results['failed'].append(f"Import: {category} - {e}")

def test_custom_modules():
    """Test 2: Kiểm tra custom modules"""
    print_header("TEST 2: CUSTOM MODULES")

    # Change to script directory for proper imports
    os.chdir(SCRIPT_DIR)

    modules_to_test = [
        "unified_logging_manager",
        "unified_config",
        "unified_data_structures",
        "intelligent_resource_manager",
        "parallel_executor",
        "real_market_data_fetcher",
        "unified_technical_indicators",
        "ai_training_engine",
        "enhanced_prediction_system",
        "market_constants",
    ]

    for module_name in modules_to_test:
        try:
            # Try importing as crypto.module_name first
            try:
                module = __import__(f'crypto.{module_name}', fromlist=[module_name])
            except (ImportError, ModuleNotFoundError) as e1:
                # Fallback to direct import
                try:
                    module = __import__(module_name)
                except Exception as e2:
                    # If both fail, raise the second error
                    raise e2 from e1
            print_test(f"Module: {module_name}", "PASS", f"Loaded successfully")
            test_results['passed'].append(f"Module: {module_name}")
        except Exception as e:
            # Get just the error message without full traceback for cleaner output
            error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
            print_test(f"Module: {module_name}", "FAIL", error_msg)
            test_results['failed'].append(f"Module: {module_name} - {error_msg}")

def test_resource_manager():
    """Test 3: Resource Management"""
    print_header("TEST 3: RESOURCE MANAGEMENT")

    try:
        try:
            from crypto.intelligent_resource_manager import intelligent_resource_manager
        except ImportError:
            from intelligent_resource_manager import intelligent_resource_manager

        # Test system info
        resources = intelligent_resource_manager.get_current_resources()
        print_test("Get Current Resources", "PASS",
                  f"CPU: {resources.cpu_percent:.1f}%, RAM: {resources.ram_percent:.1f}%")

        # Test optimal workers calculation
        optimal = intelligent_resource_manager.calculate_optimal_workers()
        print_test("Calculate Optimal Workers", "PASS",
                  f"Threads: {optimal['thread_workers']}, Processes: {optimal['process_workers']}")

        test_results['passed'].append("Resource Manager")

    except Exception as e:
        print_test("Resource Manager", "FAIL", str(e))
        test_results['failed'].append(f"Resource Manager - {e}")

def test_parallel_executor():
    """Test 4: Parallel Executor"""
    print_header("TEST 4: PARALLEL EXECUTOR")

    try:
        try:
            from crypto.parallel_executor import parallel_executor
        except ImportError:
            from parallel_executor import parallel_executor

        # Test system info
        info = parallel_executor.get_system_info()
        print_test("Parallel Executor Info", "PASS",
                  f"CPU: {info['cpu_count']}, Thread Workers: {info['max_thread_workers']}")

        # Test simple parallel execution
        def sample_task(x):
            return x * 2

        tasks = [('task1', sample_task, 5), ('task2', sample_task, 10)]
        results = parallel_executor.execute_parallel_threads(tasks, max_workers=2)

        if len(results) == 2:
            print_test("Parallel Execution", "PASS", f"Executed {len(results)} tasks")
            test_results['passed'].append("Parallel Executor")
        else:
            print_test("Parallel Execution", "FAIL", f"Expected 2 results, got {len(results)}")
            test_results['failed'].append("Parallel Executor - Wrong result count")

    except Exception as e:
        print_test("Parallel Executor", "FAIL", str(e))
        test_results['failed'].append(f"Parallel Executor - {e}")

def test_data_fetcher():
    """Test 5: Real Market Data Fetcher"""
    print_header("TEST 5: REAL MARKET DATA FETCHER")

    try:
        try:
            from crypto.real_market_data_fetcher import real_market_data_fetcher
        except ImportError:
            from real_market_data_fetcher import real_market_data_fetcher

        # Test get market data
        print("   Testing BTC/USDT data fetch...")
        btc_data = real_market_data_fetcher.get_market_data('BTC/USDT')

        if btc_data and 'price' in btc_data:
            price = float(btc_data['price'])
            print_test("Fetch BTC/USDT Price", "PASS", f"Price: ${price:,.2f}")
            test_results['passed'].append("Data Fetcher - Market Data")
        else:
            print_test("Fetch BTC/USDT Price", "WARN", "No price data available")
            test_results['warnings'].append("Data Fetcher - No market data")

        # Test historical data
        print("   Testing historical data fetch...")
        hist_data = real_market_data_fetcher.get_historical_data('BTC/USDT', '1h', 10)

        if hist_data and len(hist_data) > 0:
            print_test("Fetch Historical Data", "PASS", f"Got {len(hist_data)} candles")
            test_results['passed'].append("Data Fetcher - Historical Data")
        else:
            print_test("Fetch Historical Data", "WARN", "No historical data")
            test_results['warnings'].append("Data Fetcher - No historical data")

    except Exception as e:
        print_test("Data Fetcher", "FAIL", str(e))
        test_results['failed'].append(f"Data Fetcher - {e}")

def test_technical_indicators():
    """Test 6: Technical Indicators"""
    print_header("TEST 6: TECHNICAL INDICATORS")

    try:
        try:
            from crypto.unified_technical_indicators import unified_technical_indicators
        except ImportError:
            from unified_technical_indicators import unified_technical_indicators
        import pandas as pd
        import numpy as np

        # Create sample OHLCV data
        sample_data = pd.DataFrame({
            'open': np.random.uniform(40000, 42000, 100),
            'high': np.random.uniform(41000, 43000, 100),
            'low': np.random.uniform(39000, 41000, 100),
            'close': np.random.uniform(40000, 42000, 100),
            'volume': np.random.uniform(1000, 5000, 100)
        })

        # Calculate indicators
        indicators = unified_technical_indicators.calculate_all_indicators(sample_data)

        if indicators and len(indicators) > 0:
            print_test("Calculate Indicators", "PASS", f"Calculated {len(indicators)} indicators")

            # Show some key indicators
            key_indicators = ['SMA_20', 'RSI_14', 'MACD']
            found = [k for k in key_indicators if k in indicators]
            if found:
                print(f"   Key indicators found: {', '.join(found)}")

            test_results['passed'].append("Technical Indicators")
        else:
            print_test("Calculate Indicators", "FAIL", "No indicators calculated")
            test_results['failed'].append("Technical Indicators - No results")

    except Exception as e:
        print_test("Technical Indicators", "FAIL", str(e))
        test_results['failed'].append(f"Technical Indicators - {e}")

def test_market_constants():
    """Test 7: Market Constants"""
    print_header("TEST 7: MARKET CONSTANTS")

    try:
        try:
            from crypto.market_constants import MarketConstants
        except ImportError:
            from market_constants import MarketConstants

        # Test BTC price fetch
        btc_price = MarketConstants.get_btc_price()
        if btc_price and btc_price > 0:
            print_test("Get BTC Price", "PASS", f"${btc_price:,.2f}")
            test_results['passed'].append("Market Constants - BTC Price")
        else:
            print_test("Get BTC Price", "WARN", "Returned 0 (no real data)")
            test_results['warnings'].append("Market Constants - BTC Price is 0")

        # Test dynamic calculations
        position_size = MarketConstants.get_dynamic_default_position_size()
        print_test("Dynamic Position Size", "PASS", f"{position_size}%")

        test_results['passed'].append("Market Constants")

    except Exception as e:
        print_test("Market Constants", "FAIL", str(e))
        test_results['failed'].append(f"Market Constants - {e}")

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")

    total = len(test_results['passed']) + len(test_results['failed']) + len(test_results['warnings'])
    passed = len(test_results['passed'])
    failed = len(test_results['failed'])
    warnings = len(test_results['warnings'])

    print(f"\n📊 Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Warnings: {warnings}")

    if failed > 0:
        print("\n❌ FAILED TESTS:")
        for fail in test_results['failed']:
            print(f"   - {fail}")

    if warnings > 0:
        print("\n⚠️  WARNINGS:")
        for warn in test_results['warnings']:
            print(f"   - {warn}")

    # Overall status
    print("\n" + "="*80)
    if failed == 0:
        print("✅ ALL TESTS PASSED!" if warnings == 0 else "✅ TESTS PASSED WITH WARNINGS")
        print("🚀 System is ready to run!")
    else:
        print("❌ SOME TESTS FAILED")
        print("⚠️  Please fix the issues above before running the system")
    print("="*80)

    return failed == 0

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  CRYPTO AI PREDICTION SYSTEM - COMPREHENSIVE TEST")
    print("  God Mode 10000 - System Validation")
    print("="*80)
    print(f"\n🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Run all tests
        test_imports()
        test_custom_modules()
        test_resource_manager()
        test_parallel_executor()
        test_data_fetcher()
        test_technical_indicators()
        test_market_constants()

        # Print summary
        success = print_summary()

        print(f"\n🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 2
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
