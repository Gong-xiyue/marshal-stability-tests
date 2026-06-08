import marshal
import hashlib
import sys

# 定义要测试的用例
TEST_CASES = [
    ("None", None),
    ("Int", 123456),
    ("String", "Hello, marshal!"),
    ("List", [1, 2, 3, "a", "b"]),
    ("Set", {1, 2, 3, 4}),  # 特别关注：无序集合可能导致差异
    ("Dict", {"a": 1, "b": 2, "c": 3}),
]

def main():
    version_info = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"VERSION:{version_info}")
    for name, data in TEST_CASES:
        try:
            serialized = marshal.dumps(data)
            # 使用 sha256 哈希来比较内容是否一致
            hash_val = hashlib.sha256(serialized).hexdigest()
            print(f"RESULT:{name}:{hash_val}")
        except Exception as e:
            print(f"RESULT:{name}:ERROR_{type(e).__name__}")

if __name__ == "__main__":
    main()