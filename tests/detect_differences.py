import marshal
import subprocess
import hashlib

def test_version_differences():
    """测试不同 marshal 版本是否产生不同输出"""
    test_values = [
        42,
        "hello",
        [1, 2, 3],
        {"a": 1, "b": 2},
        {1, 2, 3},
        (1, 2, 3),
        b"bytes",
        None,
        True,
        3.14,
        float('nan'),
        float('inf'),
        complex(1.0, 2.0),
    ]
    
    print("=== 测试不同 marshal 版本 ===")
    has_differences = False
    for value in test_values:
        outputs = {}
        for version in range(0, marshal.version + 1):
            try:
                outputs[version] = marshal.dumps(value, version)
            except ValueError:
                pass
        
        if len(set(outputs.values())) > 1:
            has_differences = True
            print(f"❌ 发现版本差异: {type(value).__name__}")
            for ver, data in outputs.items():
                print(f"  版本 {ver}: {hashlib.sha256(data).hexdigest()[:16]}")
        else:
            print(f"✅ 版本稳定: {type(value).__name__}")
    
    return has_differences

def test_set_order_across_processes():
    """测试集合顺序在不同进程中的变化"""
    print("\n=== 测试集合顺序跨进程变化 ===")
    script = """
import marshal
s = {"apple", "banana", "cherry", "date", "elderberry", "fig", "grape"}
result = marshal.dumps(s).hex()
print(result)
"""
    
    results = []
    for i in range(10):
        proc = subprocess.Popen(
            ["python", "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, _ = proc.communicate()
        results.append(out.strip().decode())
    
    unique_results = set(results)
    if len(unique_results) > 1:
        print(f"❌ 集合顺序不稳定！发现 {len(unique_results)} 种不同输出")
        for i, r in enumerate(results):
            print(f"  进程 {i+1}: {r[:40]}...")
        return True
    else:
        print("✅ 集合顺序稳定")
        return False

def test_float_precision_variations():
    """测试浮点精度变化"""
    print("\n=== 测试浮点精度 ===")
    float_values = [
        1.0000000000000001,
        1.0000000000000002,
        1.0000000000000003,
        2.0 - 2**-52,
        2.0 + 2**-52,
        float.fromhex('0x1.fffffffffffffp+1023'),
        float.fromhex('0x1.0000000000001p-1022'),
    ]
    
    has_issues = False
    for value in float_values:
        dumps = [marshal.dumps(value) for _ in range(10)]
        if len(set(dumps)) > 1:
            has_issues = True
            print(f"❌ 浮点不稳定: {value}")
        else:
            print(f"✅ 浮点稳定: {value}")
    
    return has_issues

if __name__ == "__main__":
    print("="*60)
    print("Marshal 差异检测工具")
    print("="*60)
    
    issues_found = False
    issues_found |= test_version_differences()
    issues_found |= test_set_order_across_processes()
    issues_found |= test_float_precision_variations()
    
    print("\n" + "="*60)
    if issues_found:
        print("⚠️ 发现不稳定情况！")
    else:
        print("✅ 未发现不稳定情况")
    print("="*60)