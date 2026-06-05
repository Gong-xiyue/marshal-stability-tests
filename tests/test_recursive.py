import pytest
import marshal
import sys

class TestRecursiveStructures:
    def test_self_referential_list(self):
        recursive_list = []
        recursive_list.append(recursive_list)
        for i in range(3):
            with pytest.raises(ValueError) as exc_info:
                marshal.dumps(recursive_list)
            assert "recursive" in str(exc_info.value).lower()
            
    def test_self_referential_dict(self):
        recursive_dict = {}
        recursive_dict["self"] = recursive_dict
        with pytest.raises(ValueError) as exc_info:
            marshal.dumps(recursive_dict)
        assert "recursive" in str(exc_info.value).lower()
    
    def test_deeply_nested_list(self):
        deep_list = None
        for _ in range(2000):
            deep_list = [deep_list]
        with pytest.raises(RecursionError):
            marshal.dumps(deep_list)
    
    def test_circular_reference_between_objects(self):
        class Node:
            def __init__(self, value):
                self.value = value
                self.next = None
        a = Node(1)
        b = Node(2)
        a.next = b
        b.next = a
        with pytest.raises((TypeError, ValueError)):
            marshal.dumps(a)
            
    def test_tuple_indirect_self_reference(self):
        inner = []
        t = (inner,)
        inner.append(t)
        with pytest.raises(ValueError) as exc_info:
            marshal.dumps(t)
        assert "recursive" in str(exc_info.value).lower()
    
    def test_non_recursive_deep_tuple(self):
        def build_deep_tuple(depth):
            if depth <= 0:
                return 1
            return (build_deep_tuple(depth - 1),)
        deep_tuple = build_deep_tuple(500)
        data = marshal.dumps(deep_tuple)
        restored = marshal.loads(data)
        assert restored == deep_tuple
    
    def test_deterministic_error_behavior(self):
        recursive_list = []
        recursive_list.append(recursive_list)
        errors = []
        for _ in range(10):
            try:
                marshal.dumps(recursive_list)
                errors.append("NO_ERROR")
            except ValueError as e:
                errors.append(str(e))
        unique_errors = set(errors)
        assert len(unique_errors) == 1
        assert "NO_ERROR" not in unique_errors
        assert "recursive" in list(unique_errors)[0].lower()


class TestBoundaryBehavior:
    def test_empty_structures(self):
        empty_list = []
        empty_dict = {}
        empty_tuple = ()
        data1 = marshal.dumps(empty_list)
        data2 = marshal.dumps(empty_dict)
        data3 = marshal.dumps(empty_tuple)
        assert marshal.loads(data1) == empty_list
        assert marshal.loads(data2) == empty_dict
        assert marshal.loads(data3) == empty_tuple
    
    def test_large_non_recursive_list(self):
        large_list = list(range(10000))
        data1 = marshal.dumps(large_list)
        data2 = marshal.dumps(large_list)
        assert data1 == data2
        restored = marshal.loads(data1)
        assert restored == large_list
