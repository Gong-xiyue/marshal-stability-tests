"""Hypothesis strategies for fuzzing marshal-supported objects."""

from __future__ import annotations

from typing import Any

from hypothesis import strategies as st


def marshal_supported_values(max_depth: int = 4) -> st.SearchStrategy[Any]:
    """Generate values supported by marshal.

    The strategy avoids unsupported objects and keeps recursion bounded.
    """
    scalar = st.one_of(
        st.none(),
        st.booleans(),
        st.integers(min_value=-(2**80), max_value=2**80),
        st.floats(allow_nan=True, allow_infinity=True, width=64),
        st.binary(max_size=64),
        st.text(max_size=64),
    )

    return st.recursive(
        scalar,
        lambda children: st.one_of(
            st.lists(children, max_size=8),
            st.tuples(children, children),
            st.dictionaries(
                st.one_of(st.text(max_size=32), st.integers()),
                children,
                max_size=8,
            ),
            st.sets(
                st.one_of(st.text(max_size=32), st.integers()),
                max_size=8,
            ),
            st.frozensets(
                st.one_of(st.text(max_size=32), st.integers()),
                max_size=8,
            ),
        ),
        max_leaves=max_depth * 10,
    )
