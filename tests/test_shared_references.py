import pytest
import marshal

class TestSharedReferences:
    def test_shared_list_reference(self):
        inner = [1, 2, 3]
        outer = [inner, inner, inner] 
        assert outer[0] is outer[1]
        assert outer[1] is outer[2]
        data = marshal.dumps(outer)
        restored = marshal.loads(data)
        if restored[0] is restored[1]:
            print("✅ marshal 保留了共享引用")
        else:
            print("⚠️ marshal 未保留共享引用（各自独立）")
        assert restored[0] == [1, 2, 3]
        assert restored[1] == [1, 2, 3]
        assert restored[2] == [1, 2, 3]
    
    def test_shared_dict_reference(self):
        inner = {"a": 1, "b": 2}
        outer = [inner, inner, inner]
        
        data = marshal.dumps(outer)
        restored = marshal.loads(data)
        if restored[0] is restored[1]:
            print("✅ 字典共享引用被保留")
        else:
            print("⚠️ 字典共享引用未保留")
        
        assert restored[0] == {"a": 1, "b": 2}
    
    def test_shared_nested_structure(self):
        shared = [1, 2]
        container = [shared, {"key": shared}]
        data = marshal.dumps(container)
        restored = marshal.loads(data)
        if restored[0] is restored[1]["key"]:
            print("✅ 跨容器共享引用被保留")
        else:
            print("⚠️ 跨容器共享引用未保留")
        
        assert restored[0] == [1, 2]
        assert restored[1]["key"] == [1, 2]
    
    def test_shared_string_reference(self):
        s = "hello_world_shared_string"
        outer = [s, s, s]
        assert outer[0] is outer[1]
        data = marshal.dumps(outer)
        restored = marshal.loads(data)
        assert restored[0] == s
        assert restored[1] == s
        assert restored[2] == s
        if restored[0] is restored[1]:
            print("✅ 字符串共享引用被保留")
        else:
            print("⚠️ 字符串共享引用未保留（但值相同）")
    
    def test_shared_int_reference(self):
        n = 999999
        outer = [n, n, n]
        data = marshal.dumps(outer)
        restored = marshal.loads(data)
        assert restored[0] == n
        assert restored[1] == n
    
    def test_complex_shared_graph(self):
        shared = [1, 2]
        a = [shared, shared]
        b = {"data": shared}
        root = [a, b, shared]
        data = marshal.dumps(root)
        restored = marshal.loads(data)
        assert restored[0][0] == [1, 2]
        assert restored[0][1] == [1, 2]
        assert restored[1]["data"] == [1, 2]
        assert restored[2] == [1, 2]
        ref1 = restored[0][0]
        ref2 = restored[0][1]
        ref3 = restored[1]["data"]
        ref4 = restored[2]
        unique_refs = len({id(ref1), id(ref2), id(ref3), id(ref4)})
        print(f"  原始共享：4 个引用指向 1 个对象")
        print(f" marshal 后：{unique_refs} 个不同的对象")
        if unique_refs == 1:
            print("✅ 完全保留了共享引用")
        elif unique_refs == 4:
            print("⚠️ 完全展开了共享引用（每个引用独立）")
        else:
            print(f"🔍 部分保留：{unique_refs} 个对象")
    
    def test_deterministic_shared_behavior(self):
        inner = [1, 2, 3]
        outer = [inner, inner, inner]
        results = []
        for _ in range(10):
            results.append(marshal.dumps(outer))
        for i in range(1, len(results)):
            assert results[0] == results[i], f"第 {i} 次结果不同"
        print("✅ 共享引用处理是确定性的")


class TestSharedReferenceEdgeCases:
    def test_empty_shared_list(self):
        empty = []
        container = [empty, empty, empty]
        data = marshal.dumps(container)
        restored = marshal.loads(data)
        assert restored[0] == []
        assert restored[1] == []
    
    def test_shared_self_referential(self):
        shared = []
        shared.append(shared)  # 自引用
        container = [shared, shared]
        data = marshal.dumps(container)
        restored = marshal.loads(data)
        assert restored[0] is restored[0][0]
        if restored[0] is restored[1]:
            print("✅ 共享 + 自引用组合被正确处理")