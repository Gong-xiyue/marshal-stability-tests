import json
import glob
import sys


def compare_cross_platform():
    """比较跨平台测试结果"""

    print("=" * 70)
    print("【跨平台结果详细对比】")
    print("=" * 70)

    # 查找所有增强版结果文件
    result_files = glob.glob("marshal_enhanced_*.json")

    if len(result_files) < 1:
        print("❌ 没有找到增强版测试结果文件！")
        print("   请先在 Windows 和 macOS 上运行:")
        print("   python test_cross_version_enhanced.py")
        return

    print(f"\n找到 {len(result_files)} 个结果文件:")
    for f in result_files:
        print(f"  - {f}")

    # 加载所有结果
    results = {}
    for file in result_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            key = f"{data['environment']['python_version']}_{data['environment']['platform']}"
            results[key] = data

    if len(results) < 1:
        print("\n❌ 没有有效的结果数据")
        return

    # 显示每个平台的环境信息
    print("\n" + "=" * 70)
    print("【各平台环境信息】")
    print("=" * 70)
    for platform, data in results.items():
        env = data['environment']
        print(f"\n  📋 {platform}:")
        print(f"     Python: {env['python_version']} ({env['implementation']})")
        print(f"     Marshal版本: {env['marshal_version']}")
        print(f"     平台: {env['platform']}")
        print(f"     Hash Seed: {env['hash_seed']}")

    # 对比1: 基础类型的hash
    print("\n" + "=" * 70)
    print("【对比1: 基础类型 Hash 对比】 (跨平台应该一致)")
    print("=" * 70)

    first_platform = list(results.keys())[0]
    test_names = list(results[first_platform]['basic_types'].keys())

    for name in test_names:
        hashes = {}
        all_same = True
        first_hash = None

        for platform, data in results.items():
            result = data['basic_types'].get(name, {})
            h = result.get('hash', 'N/A')
            hashes[platform] = h[:20] if h != 'N/A' else 'N/A'
            if first_hash is None:
                first_hash = h
            elif h != first_hash:
                all_same = False

        if all_same:
            print(f"  ✅ {name}: 一致")
            for p, h in hashes.items():
                print(f"     {p}: {h}...")
        else:
            print(f"  ❌ {name}: 不一致！")
            for p, h in hashes.items():
                print(f"     {p}: {h}...")

    # 对比2: 集合顺序的hash
    print("\n" + "=" * 70)
    print("【对比2: 字符串集合 Hash 对比】 (跨平台通常不同！)")
    print("=" * 70)

    test_names = list(results[first_platform]['set_ordering'].keys())

    for name in test_names:
        hashes = {}
        all_same = True
        first_hash = None

        for platform, data in results.items():
            result = data['set_ordering'].get(name, {})
            h = result.get('hash', 'N/A')
            hashes[platform] = h[:20] if h != 'N/A' else 'N/A'
            if first_hash is None:
                first_hash = h
            elif h != first_hash:
                all_same = False

        if all_same:
            print(f"  ✅ {name}: 一致 (巧合)")
            for p, h in hashes.items():
                print(f"     {p}: {h}...")
        else:
            print(f"  ❌ {name}: 不一致！(这是预期的，受PYTHONHASHSEED影响)")
            for p, h in hashes.items():
                print(f"     {p}: {h}...")

    # 对比3: 代码对象的hash
    print("\n" + "=" * 70)
    print("【对比3: 代码对象 Hash 对比】 (跨平台/版本通常不同！)")
    print("=" * 70)

    test_names = list(results[first_platform]['code_objects'].keys())

    for name in test_names:
        hashes = {}
        all_same = True
        first_hash = None

        for platform, data in results.items():
            result = data['code_objects'].get(name, {})
            h = result.get('hash', 'N/A')
            hashes[platform] = h[:20] if h != 'N/A' else 'N/A'
            if first_hash is None:
                first_hash = h
            elif h != first_hash:
                all_same = False

        if all_same:
            print(f"  ✅ {name}: 一致 (相同Python版本/平台)")
            for p, h in hashes.items():
                print(f"     {p}: {h}...")
        else:
            print(f"  ❌ {name}: 不一致！(这是预期的，代码对象依赖平台/版本)")
            for p, h in hashes.items():
                print(f"     {p}: {h}...")

    # 对比4: 跨进程集合变化
    print("\n" + "=" * 70)
    print("【对比4: 跨进程集合变化】")
    print("=" * 70)

    for platform, data in results.items():
        if 'cross_process_variation' in data:
            cross_proc = data['cross_process_variation']
            unique_hashes = set()
            for r in cross_proc:
                if 'hash' in r:
                    unique_hashes.add(r['hash'])

            print(f"\n  🖥 {platform}:")
            if len(unique_hashes) > 1:
                print(f"     ❌ 发现 {len(unique_hashes)} 种不同输出！集合顺序不稳定！")
                for r in cross_proc:
                    if 'hash' in r:
                        print(f"        进程{r['process']}: {r['hash'][:16]}...")
            else:
                print(f"     ✅ 所有进程输出相同 ({len(unique_hashes)} 种)")

    # 结论
    print("\n" + "=" * 70)
    print("【结论总结】")
    print("=" * 70)
    print("\n  ✅ 基础类型: 跨平台一致 (marshal设计目标)")
    print("  ❌ 字符串集合: 跨平台/跨进程可能不同 (受PYTHONHASHSEED影响)")
    print("  ❌ 代码对象: 跨平台/版本通常不同 (依赖编译环境)")
    print("\n  💡 关键发现:")
    print("     1. 同一操作系统内，相同输入 = 相同输出 (稳定)")
    print("     2. 但集合的序列化顺序受 PYTHONHASHSEED 影响")
    print("     3. 不同Python进程可能有不同的 PYTHONHASHSEED")
    print("     4. 因此跨进程/跨平台的集合输出可能不同！")
    print("\n  🎯 这就是你作业要找的『相同输入产生不同输出』的情况！")
    print("=" * 70)


if __name__ == "__main__":
    compare_cross_platform()
