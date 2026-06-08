import marshal
import hashlib
import sys
import os
import json
import subprocess
import time


def get_python_info():
    """获取当前Python环境信息"""
    return {
        "python_version": sys.version.split()[0],
        "implementation": sys.implementation.name,
        "marshal_version": marshal.version,
        "os": os.name,
        "platform": sys.platform,
        "hash_seed": os.environ.get("PYTHONHASHSEED", "random"),
        "machine": os.environ.get("PROCESSOR_ARCHITECTURE", "unknown")
    }


def test_basic_types():
    """测试基础类型 - 通常在各平台一致"""
    test_cases = [
        ("int_small", 42),
        ("int_large", 2**100),
        ("float_normal", 3.14),
        ("str_short", "hello"),
        ("str_long", "a" * 1000),
        ("bytes", b"test data"),
        ("list_int", [1, 2, 3, 4, 5]),
        ("dict_int_keys", {1: "a", 2: "b", 3: "c"}),
        ("tuple", (1, "a", True, None)),
        ("bool", True),
        ("none", None),
    ]

    results = {}
    for name, value in test_cases:
        try:
            dumps = [marshal.dumps(value) for _ in range(3)]
            all_same = all(d == dumps[0] for d in dumps)
            results[name] = {
                "stable": all_same,
                "hash": hashlib.sha256(dumps[0]).hexdigest() if all_same else None,
                "length": len(dumps[0]) if all_same else None
            }
        except Exception as e:
            results[name] = {"stable": False, "error": str(e)}
    return results


def test_float_specials():
    """测试浮点特殊值 - 可能有平台差异"""
    test_cases = [
        ("float_nan", float('nan')),
        ("float_inf", float('inf')),
        ("float_neg_inf", float('-inf')),
        ("float_neg_zero", -0.0),
        ("float_very_small", 1e-308),
        ("float_very_large", 1e308),
    ]

    results = {}
    for name, value in test_cases:
        try:
            dumps = [marshal.dumps(value) for _ in range(3)]
            all_same = all(d == dumps[0] for d in dumps)
            results[name] = {
                "stable": all_same,
                "hash": hashlib.sha256(dumps[0]).hexdigest() if all_same else None,
                "length": len(dumps[0]) if all_same else None
            }
        except Exception as e:
            results[name] = {"stable": False, "error": str(e)}
    return results


def test_set_ordering():
    """测试集合顺序 - 受PYTHONHASHSEED影响，跨进程可能不同"""
    # 使用字符串元素，字符串的哈希值受PYTHONHASHSEED影响
    test_values = [
        {"apple", "banana", "cherry", "date", "elderberry"},
        frozenset({"x", "y", "z", "w", "v", "u"}),
        {"one", "two", "three", "four", "five", "six", "seven"},
    ]

    results = {}
    for i, s in enumerate(test_values):
        try:
            # 在当前进程内多次序列化，应该一致
            dumps = [marshal.dumps(s) for _ in range(5)]
            in_process_stable = all(d == dumps[0] for d in dumps)
            results[f"set_strings_{i+1}"] = {
                "in_process_stable": in_process_stable,
                "hash": hashlib.sha256(dumps[0]).hexdigest() if in_process_stable else None,
                "length": len(dumps[0]) if in_process_stable else None,
                "note": "跨进程可能不同(依赖PYTHONHASHSEED)"
            }
        except Exception as e:
            results[f"set_strings_{i+1}"] = {"stable": False, "error": str(e)}
    return results


def test_code_objects():
    """测试代码对象 - 不同平台/版本通常不同"""
    test_cases = [
        ("simple_func", compile("def f(x): return x + 1", "<string>", "exec")),
        ("complex_func", compile("def g(x, y, z): return (x + y) * z if x > y else x - y", "<string>", "exec")),
        ("lambda_func", compile("lambda x: x**2", "<string>", "eval")),
    ]

    results = {}
    for name, code in test_cases:
        try:
            dumps = [marshal.dumps(code) for _ in range(3)]
            all_same = all(d == dumps[0] for d in dumps)
            results[name] = {
                "stable": all_same,
                "hash": hashlib.sha256(dumps[0]).hexdigest() if all_same else None,
                "length": len(dumps[0]) if all_same else None,
                "note": "不同平台/版本通常不同"
            }
        except Exception as e:
            results[name] = {"stable": False, "error": str(e)}
    return results


def test_complex_nested():
    """测试复杂嵌套结构 - 包含集合时可能有跨平台差异"""
    test_cases = [
        ("nested_with_set", {"data": [1, 2, 3], "tags": {"a", "b", "c"}, "config": {"x": 1.5}}),
        ("nested_with_frozenset", {"set": frozenset(["x", "y", "z"]), "list": [{1}, {2}, {3}]}),
        ("deep_nested", [[[[1, 2], [3, 4]], [[5, 6], [7, 8]]], [[[9, 10], [11, 12]], [[13, 14], [15, 16]]]]),
    ]

    results = {}
    for name, value in test_cases:
        try:
            dumps = [marshal.dumps(value) for _ in range(3)]
            all_same = all(d == dumps[0] for d in dumps)
            results[name] = {
                "stable": all_same,
                "hash": hashlib.sha256(dumps[0]).hexdigest() if all_same else None,
                "length": len(dumps[0]) if all_same else None
            }
        except Exception as e:
            results[name] = {"stable": False, "error": str(e)}
    return results


def test_cross_process_set_variation():
    """测试跨进程集合顺序变化 - 这个是检测实际差异的关键"""
    script = '''
import marshal
import hashlib
import sys

# 使用字符串集合 - 受PYTHONHASHSEED影响
s = {"apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "kiwi", "lemon", "mango"}
data = marshal.dumps(s)
print(hashlib.sha256(data).hexdigest())
print(data.hex()[:64])
'''

    results = []
    num_processes = 10

    for i in range(num_processes):
        try:
            proc = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                timeout=10
            )
            if proc.returncode == 0:
                lines = proc.stdout.strip().split('\n')
                if len(lines) >= 2:
                    results.append({
                        "process": i + 1,
                        "hash": lines[0],
                        "bytes_preview": lines[1]
                    })
        except Exception as e:
            results.append({"process": i + 1, "error": str(e)})

    return results


if __name__ == "__main__":
    print("=" * 70)
    print("【增强版】Python Marshal 跨版本/跨平台测试")
    print("=" * 70)

    # 获取环境信息
    env_info = get_python_info()
    print("\n【环境信息】")
    for key, value in env_info.items():
        print(f"  {key}: {value}")

    # 测试1: 基础类型
    print("\n" + "=" * 70)
    print("【测试1: 基础类型】 (通常跨平台一致)")
    print("=" * 70)
    basic_results = test_basic_types()
    for name, result in basic_results.items():
        status = "✅" if result.get("stable") else "❌"
        info = f'hash={result.get("hash", "N/A")[:16]}...' if result.get("stable") else f'error={result.get("error", "N/A")}'
        print(f"  {status} {name}: {'稳定' if result.get('stable') else '不稳定'} ({info})")

    # 测试2: 浮点特殊值
    print("\n" + "=" * 70)
    print("【测试2: 浮点特殊值】 (可能有平台差异)")
    print("=" * 70)
    float_results = test_float_specials()
    for name, result in float_results.items():
        status = "✅" if result.get("stable") else "❌"
        info = f'hash={result.get("hash", "N/A")[:16]}...' if result.get("stable") else f'error={result.get("error", "N/A")}'
        print(f"  {status} {name}: {'稳定' if result.get('stable') else '不稳定'} ({info})")

    # 测试3: 集合顺序
    print("\n" + "=" * 70)
    print("【测试3: 集合顺序】 (当前进程内稳定，跨进程可能不同)")
    print("=" * 70)
    set_results = test_set_ordering()
    for name, result in set_results.items():
        status = "✅" if result.get("in_process_stable") else "❌"
        info = f'hash={result.get("hash", "N/A")[:16]}...' if result.get("in_process_stable") else '不稳定'
        print(f"  {status} {name}: {'进程内稳定' if result.get('in_process_stable') else '进程内也不稳定'} ({info})")
        print(f"     说明: {result.get('note', '')}")

    # 测试4: 代码对象
    print("\n" + "=" * 70)
    print("【测试4: 代码对象】 (不同平台/版本通常不同)")
    print("=" * 70)
    code_results = test_code_objects()
    for name, result in code_results.items():
        status = "✅" if result.get("stable") else "❌"
        info = f'hash={result.get("hash", "N/A")[:16]}...' if result.get("stable") else f'error={result.get("error", "N/A")}'
        print(f"  {status} {name}: {'进程内稳定' if result.get('stable') else '不稳定'} ({info})")
        print(f"     说明: {result.get('note', '')}")

    # 测试5: 复杂嵌套
    print("\n" + "=" * 70)
    print("【测试5: 复杂嵌套结构】")
    print("=" * 70)
    nested_results = test_complex_nested()
    for name, result in nested_results.items():
        status = "✅" if result.get("stable") else "❌"
        info = f'hash={result.get("hash", "N/A")[:16]}...' if result.get("stable") else f'error={result.get("error", "N/A")}'
        print(f"  {status} {name}: {'稳定' if result.get('stable') else '不稳定'} ({info})")

    # 测试6: 跨进程集合变化
    print("\n" + "=" * 70)
    print("【测试6: 跨进程集合顺序变化】")
    print("=" * 70)
    cross_process_results = test_cross_process_set_variation()

    unique_hashes = set()
    for r in cross_process_results:
        if "hash" in r:
            unique_hashes.add(r["hash"])

    if len(unique_hashes) > 1:
        print(f"  ❌ 发现 {len(unique_hashes)} 种不同输出！跨进程集合顺序不稳定！")
        for r in cross_process_results:
            print(f"     进程 {r['process']}: {r.get('hash', 'N/A')[:16]}...")
    else:
        print(f"  ✅ 所有进程输出相同 ({len(unique_hashes)} 种)")
        for r in cross_process_results:
            print(f"     进程 {r['process']}: {r.get('hash', 'N/A')[:16]}...")

    # 保存结果
    output = {
        "environment": env_info,
        "basic_types": basic_results,
        "float_specials": float_results,
        "set_ordering": set_results,
        "code_objects": code_results,
        "complex_nested": nested_results,
        "cross_process_variation": cross_process_results,
    }

    output_file = f"marshal_enhanced_{env_info['python_version']}_{env_info['platform']}_{env_info['hash_seed']}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n【结果已保存】{output_file}")
    print("=" * 70)
    print("\n【关键发现】")
    print("  1. 基础类型在同一平台内稳定，但跨平台可能相同或不同")
    print("  2. 集合顺序受 PYTHONHASHSEED 影响，跨进程可能不同")
    print("  3. 代码对象在不同平台/版本通常不同")
    print("  4. 要验证跨平台差异，请在不同系统运行此脚本后比较结果文件")
    print("=" * 70)