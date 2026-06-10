"""Tests for bytearray vs bytes differences in marshal.

Key finding: marshal turns bytearray into bytes after round-trip.
"""

import marshal


def test_ba_to_bytes():
    """BUG: bytearray becomes bytes after marshal round-trip (should stay bytearray)."""
    original = bytearray(b"hello")
    restored = marshal.loads(marshal.dumps(original))
    assert type(restored) is bytearray


def test_bytes_stays_bytes():
    """bytes stays bytes after marshal round-trip."""
    original = b"hello"
    restored = marshal.loads(marshal.dumps(original))
    assert type(restored) is bytes


def test_ba_content():
    """The content of a bytearray survives the round-trip."""
    original = bytearray(b"\x00\x01\x02\xff")
    restored = marshal.loads(marshal.dumps(original))
    assert restored == original


def test_bytes_content_survives():
    """The content of bytes survives the round-trip."""
    original = b"\x00\x01\x02\xff"
    restored = marshal.loads(marshal.dumps(original))
    assert restored == original


def test_empty_bytearray():
    """BUG: Empty bytearray becomes empty bytes after round-trip (should stay bytearray)."""
    original = bytearray()
    restored = marshal.loads(marshal.dumps(original))
    assert type(restored) is bytearray
    assert len(restored) == 0


def test_bytearray_boundaries():
    """BUG: bytearray at different sizes should stay bytearray after round-trip."""
    for size in [0, 1, 254, 255, 256, 1000]:
        if size <= 256:
            original = bytearray(range(size))
        else:
            original = bytearray(b"\x00" * size)
        restored = marshal.loads(marshal.dumps(original))
        assert type(restored) is bytearray
        assert restored == bytes(original)


def test_bytes_boundaries():
    """Test bytes at different sizes (boundary values)."""
    for size in [0, 1, 254, 255, 256, 1000]:
        if size <= 256:
            original = bytes(range(size))
        else:
            original = b"\x00" * size
        restored = marshal.loads(marshal.dumps(original))
        assert type(restored) is bytes
        assert restored == original


def test_bytearray_in_list():
    """BUG: bytearray inside a list becomes bytes after round-trip (should stay bytearray)."""
    original = [bytearray(b"a"), bytearray(b"b")]
    restored = marshal.loads(marshal.dumps(original))
    assert type(restored[0]) is bytearray
    assert type(restored[1]) is bytearray
    assert restored == [b"a", b"b"]


def test_ba_bytes_same_type():
    """bytearray and bytes produce the same first byte."""
    b_first = marshal.dumps(b"X")[0]
    ba_first = marshal.dumps(bytearray(b"X"))[0]
    # Remove the reference flag to compare base type
    assert (b_first - (b_first // 128) * 128) == (ba_first - (ba_first // 128) * 128)


def test_unsupported_types_raise_error():
    """Unsupported types should raise ValueError."""
    for val in [object(), lambda: None]:
        try:
            marshal.dumps(val)
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass


def test_garbage_data_raises_error():
    """Random bytes should make marshal.loads raise an error."""
    for bad in [b"\x00", b"\xFF" * 10, b"hello"]:
        try:
            marshal.loads(bad)
            raise AssertionError("Should have raised error")
        except (EOFError, ValueError, TypeError):
            pass


def test_non_ascii():
    """Non-ASCII strings should survive marshal."""
    for t in ["中文测试", "日本語", "Español"]:
        restored = marshal.loads(marshal.dumps(t))
        assert restored == t


def test_string_with_null_bytes():
    """Strings with null bytes should survive."""
    original = "hello\x00world\x00\x00test"
    restored = marshal.loads(marshal.dumps(original))
    assert restored == original
