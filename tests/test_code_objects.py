import pytest
import marshal
import hashlib
import sys
from textwrap import dedent

class TestBasicCodeObjects:
    def test_normal_function_code_object(self):
        def sample_function(x, y):
            result = x + y + 1
            return result
        code_obj = sample_function.__code__
        serialized_results = []
        for _ in range(5):
            data = marshal.dumps(code_obj)
            serialized_results.append(data)
        for i in range(1, len(serialized_results)):
            assert serialized_results[0] == serialized_results[i], \
                f"第 {i} 次序列化结果与第一次不同"
        first_hash = hashlib.sha256(serialized_results[0]).hexdigest()
        for data in serialized_results[1:]:
            assert hashlib.sha256(data).hexdigest() == first_hash
    
    def test_lambda_code_object(self):
        lam = lambda a, b: a * b + 1
        code_obj = lam.__code__
        data1 = marshal.dumps(code_obj)
        data2 = marshal.dumps(code_obj)
        assert data1 == data2
        restored_code = marshal.loads(data1)
        assert restored_code.co_argcount == code_obj.co_argcount
        assert restored_code.co_name == code_obj.co_name
    
    def test_code_object_from_exec(self):
        source = dedent("""
        def dynamic_function(x):
            '''动态创建的函数'''
            return x ** 2 + x
        """)
        namespace = {}
        exec(source, namespace)
        code_obj = namespace["dynamic_function"].__code__
        data1 = marshal.dumps(code_obj)
        data2 = marshal.dumps(code_obj)
        assert data1 == data2
    
    def test_builtin_function_no_code_attribute(self):
        with pytest.raises(AttributeError):
            _ = sum.__code__
        with pytest.raises(AttributeError):
            _ = max.__code__
        with pytest.raises(AttributeError):
            _ = len.__code__
    data = marshal.dumps(None)
    assert marshal.loads(data) is None
    
    def test_method_code_object(self):
        class MyClass:
            def my_method(self, value):
                return value * 2
        code_obj = MyClass.my_method.__code__
        data1 = marshal.dumps(code_obj)
        data2 = marshal.dumps(code_obj)
        assert data1 == data2

class TestComplexCodeObjects:
    def test_code_object_with_constants(self):
        source = dedent("""
        def constant_function():
            return (
                42,                    # 整数
                "hello world",         # 字符串
                3.14159,               # 浮点数
                None,                  # None
                True,                  # 布尔 True
                False,                 # 布尔 False
                b"binary data",        # 字节串
                (1, 2, 3),             # 元组
                [1, 2, 3],             # 列表
                {"a": 1, "b": 2}       # 字典
            )
        """)      
        namespace = {}
        exec(source, namespace)
        code_obj = namespace["constant_function"].__code__
        results = []
        for _ in range(10):
            results.append(marshal.dumps(code_obj))
        for result in results[1:]:
            assert results[0] == result
    
    def test_code_object_with_closure(self):
        def outer_function(x):
            def inner_function(y):
                return x + y 
            return inner_function
        closure_func = outer_function(10)
        code_obj = closure_func.__code__
        assert len(code_obj.co_freevars) > 0
        data1 = marshal.dumps(code_obj)
        data2 = marshal.dumps(code_obj)
        assert data1 == data2
        restored = marshal.loads(data1)
        assert restored.co_freevars == code_obj.co_freevars
    
    def test_code_object_with_complex_bytecode(self):
        source = dedent("""
        def complex_logic(numbers):
            total = 0
            for i, n in enumerate(numbers):
                if n % 2 == 0:
                    total += n * i
                else:
                    total -= n
            return total
        """)
        namespace = {}
        exec(source, namespace)
        code_obj = namespace["complex_logic"].__code__
        data1 = marshal.dumps(code_obj)
        data2 = marshal.dumps(code_obj)
        assert data1 == data2

class TestStabilityAcrossRuns:
    def test_hash_seed_independence_demo(self):
        def test_function():
            return {"key": "value"}
        code_obj = test_function.__code__
        data = marshal.dumps(code_obj)
        digest = hashlib.sha256(data).hexdigest()
        print(f"\n[INFO] Code object SHA-256: {digest}")
        print(f"[INFO] Python version: {sys.version}")
        assert data == marshal.dumps(code_obj)
    
    def test_byte_identical_after_multiple_imports(self):
        def multiply(a, b):
            return a * b
        code_obj = multiply.__code__
        import time
        results = []
        for _ in range(10):
            results.append(marshal.dumps(code_obj))
            time.sleep(0.01)
        for i, result in enumerate(results[1:], 1):
            assert results[0] == result, f"第 {i} 次结果不同"
