import subprocess
from typing import Dict

# 需要测试的 conda 环境列表
ENVIRONMENTS = [
    "marshal-py38",
    "marshal-py39",
    "marshal-py310",
    "marshal-py311",
    "marshal-py312",
]

def run_test_in_env(env_name: str) -> Dict[str, str]:
    """在指定的 conda 环境中执行测试脚本，并返回解析后的结果字典。"""
    try:
        # 使用 conda activate 然后运行 python（Windows 下用 && 连接命令）
        # 注意：需要确保 conda 命令在 PATH 中（通常在 base 环境下是有的）
        cmd = f'conda activate {env_name} && python marshal_cross_version_test.py'
        result = subprocess.run(
            cmd,
            shell=True,                      # 允许使用 shell 语法（&&）
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )
        parsed_results = {}
        for line in result.stdout.splitlines():
            if line.startswith("VERSION:"):
                parsed_results["version"] = line.split(":", 1)[1]
            elif line.startswith("RESULT:"):
                _, name, value = line.split(":", 2)
                parsed_results[name] = value
        return parsed_results
    except subprocess.CalledProcessError as e:
        print(f"Error running test in {env_name}: {e}")
        print(f"stderr: {e.stderr}")
        return {}

def main():
    all_results = {}
    for env in ENVIRONMENTS:
        print(f"--- Testing in environment: {env} ---")
        results = run_test_in_env(env)
        all_results[env] = results

    print("\n" + "="*50)
    print("CROSS-VERSION MARSHAL TEST REPORT")
    print("="*50)

    reference_env = ENVIRONMENTS[0]
    ref_results = all_results.get(reference_env, {})
    print(f"\nReference Environment: {reference_env} (Python {ref_results.get('version', 'N/A')})")

    for test_env, test_results in all_results.items():
        if test_env == reference_env:
            continue
        print(f"\nComparing {test_env} (Python {test_results.get('version', 'N/A')}) with {reference_env}:")
        diff_count = 0
        for name in ref_results:
            if name == "version":
                continue
            ref_val = ref_results.get(name)
            test_val = test_results.get(name)
            if ref_val != test_val:
                diff_count += 1
                print(f"  [DIFF] {name}: {test_val} vs {ref_val}")
        if diff_count == 0:
            print("  ✔ All results are byte-identical.")
        else:
            print(f"  ✘ Found {diff_count} differences.")

if __name__ == "__main__":
    main()