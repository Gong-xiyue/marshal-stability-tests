import marshal
import hashlib
import sys
import os
import json

def get_python_info():
    """获取当前Python环境信息"""
    return {
        "python_version": sys.version.split()[0],
        "implementation": sys.implementation.name,
        "marshal_version": marshal.version,
        "os": os.name,
        "platform": sys.platform
    }

def test_marshal_stability():
    """测试marshal稳定性"""
    test_cases = [
        ("int_small", 42),
        ("int_large", 2**100),
        ("float_normal", 3.14),
        ("float_nan", float('nan')),
        ("float_inf", float('inf')),
        ("str_short", "hello"),
        ("str_long", "a" * 1000),
        ("bytes", b"test data"),
        ("list", [1, 2, 3, "a", None]),
        ("dict", {"a": 1, "b": 2, "c": 3}),
        ("set", {1, 2, 3, 4, 5}),
        ("tuple", (1, "a", True, None)),
        ("bool", True),
        ("none", None),
    ]
    
    results = {}
    for name, value in test_cases:
        try:
            # 多次序列化确保稳定性
            dumps = [marshal.dumps(value) for _ in range(5)]
            all_same = all(d == dumps[0] for d in dumps)
            
            if all_same:
                results[name] = {
                    "stable": True,
                    "hash": hashlib.sha256(dumps[0]).hexdigest(),
                    "length": len(dumps[0]),
                    "error": None
                }
            else:
                results[name] = {
                    "stable": False,
                    "hash": None,
                    "length": None,
                    "error": "Inconsistent serialization"
                }
        except Exception as e:
            results[name] = {
                "stable": False,
                "hash": None,
                "length": None,
                "error": str(e)
            }
    
    return results

def test_version_differences():
    """测试不同marshal版本的输出差异"""
    results = {}
    test_value = {"test": "data", "number": 42, "list": [1, 2, 3]}
    
    for version in range(0, marshal.version + 1):
        try:
            data = marshal.dumps(test_value, version)
            results[version] = hashlib.sha256(data).hexdigest()
        except ValueError as e:
            results[version] = f"Error: {e}"
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("Python Marshal Cross-Version/Cross-Platform Test")
    print("=" * 60)
    
    # 获取环境信息
    env_info = get_python_info()
    print("\n【环境信息】")
    for key, value in env_info.items():
        print(f"  {key}: {value}")
    
    # 测试基础稳定性
    print("\n【基础稳定性测试】")
    stability_results = test_marshal_stability()
    for name, result in stability_results.items():
        status = "✅" if result["stable"] else "❌"
        print(f"  {status} {name}: {'稳定' if result['stable'] else result['error']}")
    
    # 测试版本差异
    print("\n【版本差异测试】")
    version_results = test_version_differences()
    unique_hashes = set(v for v in version_results.values() if isinstance(v, str) and len(v) == 64)
    
    if len(unique_hashes) > 1:
        print("  ❌ 不同版本产生不同输出！")
        for version, hash_val in version_results.items():
            print(f"    版本 {version}: {hash_val[:16]}...")
    else:
        print("  ✅ 所有版本输出相同")
    
    # 保存结果到文件
    output = {
        "environment": env_info,
        "stability_results": stability_results,
        "version_results": version_results
    }
    
    output_file = f"marshal_test_result_{env_info['python_version']}_{env_info['platform']}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n【结果已保存】{output_file}")
    print("=" * 60)