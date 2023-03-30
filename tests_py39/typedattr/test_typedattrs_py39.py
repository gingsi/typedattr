"""
Test using builtins and collections.abc for the type definitions.
"""
from collections import defaultdict
from collections.abc import Callable
from typing import Optional

import attrs
from attr import define

from typedattr import attrs_from_dict


@define
class Cfg:
    f1: int = 12
    f2: Optional[int] = None
    f3: tuple[int, str] = [12, "a"]
    f4: tuple[int, ...] = [12, 13, -1]
    f5: list[int] = [12]
    f6: Callable = print
    f7: set[int] = {12}
    f8: frozenset[int] = frozenset({12})
    f9: dict[str, str] = {"a": "b", "c": "d"}
    f10: defaultdict = defaultdict(list)


def test_typedattr_py39():
    c = attrs_from_dict(Cfg, {}, strict=True)
    assert attrs.asdict(c) == {
        'f1': 12, 'f2': None, 'f3': (12, 'a'), 'f4': (12, 13, -1), 'f5': [12],
        'f6': print, 'f7': {12}, 'f8': frozenset({12}), 'f9': {'a': 'b', 'c': 'd'}, 'f10': {}}
