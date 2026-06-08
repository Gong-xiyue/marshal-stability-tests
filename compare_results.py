import json
import glob

def compare_results():
    """比较多个平台的测试结果"""
    result_files = glob.glob("marshal_test_result_*.json")
    
    if len(result_files) < 2:
        print("需要至少2个结果文件进行比较")
        print(f"当前找到 {len(result_files)} 个文件: {result_files}")
        return
    
    print("=" * 60)
    print("跨平台/跨版本结果比较")
    print("=" * 60)
    
    # 加载所有结果
    results = {}
    for file in result_files:
        with open(file, 'r') as f:
            data = json.load(f)
            key = f"{data['environment']['python_version']}_{data['environment']['platform']}"
            results[key] = data
            print(f"\n加载文件: {file}")
            print(f"  平台: {key}")
    
    # 比较稳定性结果
    print("\n【稳定性结果比较】")
    first_key = list(results.keys())[0]
    test_names = list(results[first_key]['stability_results'].keys())
    
    for name in test_names:
        statuses = []
        for platform, data in results.items():
            status = data['stability_results'][name]['stable']
            statuses.append((platform, status))
        
        all_same = all(s[1] == statuses[0][1] for s in statuses)
        if not all_same:
            print(f"  ❌ {name}: 不同平台结果不一致")
            for platform, status in statuses:
                print(f"    {platform}: {'稳定' if status else '不稳定'}")
        else:
            print(f"  ✅ {name}: 所有平台结果一致")
    
    # 比较hash值
    print("\n【Hash值比较】")
    for name in test_names:
        hashes = {}
        for platform, data in results.items():
            result = data['stability_results'][name]
            if result['stable']:
                hashes[platform] = result['hash'][:16]
        
        if len(hashes) > 0:
            if len(set(hashes.values())) > 1:
                print(f"  ❌ {name}: 不同平台hash值不同")
                for platform, h in hashes.items():
                    print(f"    {platform}: {h}...")
            else:
                print(f"  ✅ {name}: 所有平台hash值相同")
        else:
            print(f"  ⚠️ {name}: 所有平台都不稳定")

if __name__ == "__main__":
    compare_results()