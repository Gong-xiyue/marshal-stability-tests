import pytest
import marshal
import types
from datetime import datetime

class TestUnsupportedTypes:
    def test_custom_class_instance(self):
        class MyClass:
            def __init__(self, value):
                self.value = value
        obj = MyClass(42)
        with pytest.raises(ValueError, match="unmarshallable"):
            marshal.dumps(obj)
    
    def test_custom_class_with_slots(self):
        class SlotsClass:
            __slots__ = ["x", "y"]
            def __init__(self, x, y):
                self.x = x
                self.y = y
        obj = SlotsClass(1, 2)
        with pytest.raises(ValueError, match="unmarshallable"):
            marshal.dumps(obj)
    
    def test_module_object(self):
        import sys
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(sys)
    
    def test_function_object(self):
        def my_func():
            return 42
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(my_func)
    
    def test_method_object(self):
        class MyClass:
            def method(self):
                pass
        obj = MyClass()
        bound_method = obj.method
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(bound_method)
    
    def test_type_object(self):
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(list)
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(dict)

    def test_file_object(self):
        import tempfile
        with tempfile.NamedTemporaryFile() as f:
            with pytest.raises((ValueError, TypeError)):
                marshal.dumps(f)
    
    def test_generator_object(self):
        def my_gen():
            yield 1
            yield 2
        gen = my_gen()
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(gen)
    
    def test_iterator_object(self):
        it = iter([1, 2, 3])
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(it)
    
    def test_exception_object(self):
        exc = ValueError("test error")
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(exc)
    
    def test_datetime_object(self):
        dt = datetime.now()
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(dt)
    
    def test_lambda_function(self):
        lam = lambda x: x * 2
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(lam)
    
    def test_property_object(self):
        class MyClass:
            @property
            def prop(self):
                return 42
        prop = MyClass.prop
        with pytest.raises((ValueError, TypeError)):
            marshal.dumps(prop)
    
    def test_none_is_supported(self):
        data = marshal.dumps(None)
        assert marshal.loads(data) is None
    
    def test_bool_is_supported(self):
        data_true = marshal.dumps(True)
        data_false = marshal.dumps(False)
        assert marshal.loads(data_true) is True
        assert marshal.loads(data_false) is False
    
    def test_number_is_supported(self):
        data = marshal.dumps(3.14159)
        assert marshal.loads(data) == 3.14159
    
    def test_string_is_supported(self):
        data = marshal.dumps("hello")
        assert marshal.loads(data) == "hello"

class TestUnsupportedTypesDeterministic:
    def test_deterministic_custom_class_error(self):
        class MyClass:
            pass
        obj = MyClass()
        errors = []
        for _ in range(10):
            try:
                marshal.dumps(obj)
                errors.append("NO_ERROR")
            except ValueError as e:
                errors.append(str(e))
        unique_errors = set(errors)
        assert len(unique_errors) == 1
        assert "NO_ERROR" not in unique_errors
        assert "unmarshallable" in list(unique_errors)[0]
    
    def test_deterministic_module_error(self):
        import sys
        errors = []
        for _ in range(10):
            try:
                marshal.dumps(sys)
                errors.append("NO_ERROR")
            except (ValueError, TypeError) as e:
                errors.append(type(e).__name__)
        unique_errors = set(errors)
        assert len(unique_errors) == 1
        assert "NO_ERROR" not in unique_errors

class TestUnsupportedTypesSummary:
    def test_summary_of_unsupported_types(self):
        unsupported_cases = []
        class Dummy:
            pass
        test_cases = [
            ("自定义类实例", Dummy()),
            ("模块对象", __import__("sys")),
            ("函数对象", lambda x: x),
            ("生成器", (x for x in range(5))),
            ("文件对象", open(__file__, "r")),
        ]
        print("\n" + "="*60)
        print("不支持类型测试汇总")
        print("="*60)
        for name, obj in test_cases:
            try:
                marshal.dumps(obj)
                print(f"❌ {name}: 意外成功序列化")
            except (ValueError, TypeError) as e:
                print(f"✅ {name}: {type(e).__name__} - {str(e)[:50]}")
            finally:
                if name == "文件对象":
                    obj.close()  
        print("="*60)