from collections import defaultdict
from copy import deepcopy
from typing import (
    Any, Optional, Union, DefaultDict, Tuple, List, FrozenSet, Dict, Set, Callable, Iterable,
    Sequence)

import attrs
import numpy as np
import pytest
from attr import define

from typedattr import definenumpy, attrs_from_dict
from typedattr.objutils import flatten_dict


@define
class CfgWithOpt:
    f1: int = 12
    f2: Optional[int] = None


@define
class CfgWithOptAtt:
    f1: int = 12
    f2: Optional[int] = None


@define()
class CfgWithOptAttBrackets:
    f1: int = 12
    f2: Optional[int] = None


@define
class CfgWithUnion:
    f1: int = 12
    f2: Union[str, int] = None


@define
class CfgWithFixedTuple:
    f1: int = 12
    f2: Tuple[int, str] = [12, "a"]


@define
class CfgWithVarTuple:
    f1: int = 12
    f2: Tuple[int, ...] = [12, 13, -1]


@define
class CfgWithList:
    f1: int = 12
    f2: List[int] = [12]


@define
class CfgWithCallable:
    f1: int = 12
    f2: Callable = None


@define
class CfgNestInner:
    f1: int = None
    f2: Tuple[str, ...] = ["12"]


@define
class CfgNestOuter:
    nest1: CfgNestInner = None
    nest2: CfgNestInner = CfgNestInner(f1=12, f2=["12"])


@define
class CfgNestOuterFail:
    nest4: CfgNestInner = CfgNestInner(f1=b"12", f2=["12", "13"])


@define
class CfgWithSet:
    f1: int = 12
    f2: Set[int] = {12}
    f3: FrozenSet[int] = frozenset({12})


@define
class CfgWithAbstracts:
    f1: int = 12
    f2: Sequence[int] = {12}
    f3: Iterable[int] = frozenset({12})
    f4: Set[int] = {12}


@define
class CfgWithDict:
    f1: Dict[str, str] = {"a": "b", "c": "d"}
    f2: Dict[str, int] = {"a": 1, "c": 2}
    f3: Dict[str, Dict[str, int]] = {"a": {"b": 1}, "c": {"d": 2}}
    f4: Dict[Tuple[bool, bool], int] = {(True, False): 1, (False, True): 2}


_ref_cfg_with_dict = {'f1': {'a': 'b', 'c': 'd'}, 'f2': {'a': 1, 'c': 2},
                      'f3': {'a': {'b': 1}, 'c': {'d': 2}},
                      'f4': {(True, False): 1, (False, True): 2}}


@define
class CfgWithAny:
    f1: int = 12
    f2: Any = None


@define
class CfgWithDefaultDict:
    f1: int = 12
    f2: DefaultDict = defaultdict(list)


@define
class CfgWithDefaultDictNested:
    f1: int = 12
    f3: CfgWithDefaultDict = CfgWithDefaultDict()


@define
class CfgWithDefaultDictDoubleNested:
    f1: int = 12
    f3: CfgWithDefaultDictNested = CfgWithDefaultDictNested()


@define
class CfgWithDefaultDictNestedUntyped:
    f1: int = 12
    f3: Any = CfgWithDefaultDict()


@definenumpy
class CfgWithNumpy:
    f1: np.ndarray = np.array([1, 7])
    f2: np.ndarray = np.array([[2, 4]])
    f3: List[np.ndarray] = [np.array([1, 2]), np.array([3, 4])]


@define
class CfgIntFloat:
    f1: int = 7
    f2: float = 100


@define
class CfgUntyped:
    f1: tuple = (1, 2, 3)


@define
class CfgPositional:
    f1: int
    f2: int = 7


_ref_cfg_with_numpy = {'f1': np.array([1, 7]), 'f2': np.array([[2, 4]]),
                       'f3': [np.array([1, 2]), np.array([3, 4])]}

_REMOVE_KEY = f"__{__name__}_REMOVE_KEY__"


@pytest.fixture(params=[
    ({"f1": 0, "f2": 23, "f3": b"6", }, CfgWithOptAtt, TypeError, {"f2": 23, "f3": _REMOVE_KEY}),
    ({"f1": 1, }, CfgWithOptAtt, None, {"f2": None}),
    ({"f1": 2, }, CfgWithOptAttBrackets, None, {"f2": None}),
    ({"f1": 3, }, CfgWithOpt, None, {"f2": None}),
    ({"f1": 4, "f2": 123}, CfgWithUnion, None, {}),
    ({"f1": 5, "f2": "123"}, CfgWithUnion, None, {}),
    # note: isinstance(True, int) evaluates to True
    ({"f1": 6, "f2": True}, CfgWithUnion, None, {}),
    ({"f1": 7, "f2": b"77"}, CfgWithUnion, TypeError, {"f2": b"77"}),
    ({"f1": 8}, CfgWithList, None, {"f2": [12]}),
    ({"f1": 9, "f2": "str"}, CfgWithVarTuple, TypeError, {}),
    ({"f1": 10}, CfgWithVarTuple, None, {"f2": (12, 13, -1)}),
    ({"f1": 11, "f2": [23, 4, "str"]}, CfgWithVarTuple, TypeError, {}),
    ({"f1": 12}, CfgWithFixedTuple, None, {"f2": (12, "a")}),
    ({"f1": 13, "f2": [12]}, CfgWithFixedTuple, TypeError, {}),
    ({"f1": 14, "f2": [12, b"6", "hi"]}, CfgWithFixedTuple, TypeError, {}),
    ({"f1": 15, "f2": 12}, CfgWithFixedTuple, TypeError, {}),
    ({"f1": 16, "f2": lambda x: 12}, CfgWithCallable, None, {}),
    ({"f1": 17, "f2": 12}, CfgWithCallable, TypeError, {}),
    ({'f1': 18}, CfgWithCallable, TypeError, {'f2': None}),
    ({"f1": 19, "f2": "12"}, CfgWithCallable, TypeError, {}),
    # note: conversion to tuple does not happen with strict=False, so the output stays a list
    ({}, CfgNestOuter, TypeError, {"nest1": None, "nest2": {"f1": 12, "f2": ["12"]}}),
    ({"nest1": {"f1": 21, "f2": ("12", "13")}}, CfgNestOuter, None,
     {"nest2": {"f1": 12, "f2": ("12",)}}),
    ({"nest1": {"f1": 22, "f2": ("12", "13")}}, CfgNestOuter, None,
     {"nest2": {"f1": 12, "f2": ("12",)}}),
    ({}, CfgNestOuterFail, TypeError, {'nest4': {'f1': b'12', 'f2': ['12', '13']}}),
    ({"nest4": {"f1": 24, "f2": ("13", "14")}}, CfgNestOuterFail, None, {}),
    ({"f1": 25, "f2": {25}}, CfgWithSet, None, {"f3": frozenset({12})}),
    ({"f1": 26, "f2": {12, "no"}}, CfgWithSet, TypeError, {"f3": frozenset({12})}),
    ({}, CfgWithAbstracts, TypeError, {'f1': 12, 'f2': {12}, 'f3': frozenset({12}), 'f4': {12}}),
    ({}, CfgWithDict, None, _ref_cfg_with_dict),
    ({"f1": 28}, CfgWithDict, TypeError, {**_ref_cfg_with_dict, "f1": 28}),
    ({"f4": {(True, 8): 12}}, CfgWithDict, TypeError,
     {**_ref_cfg_with_dict, "f4": {(True, 8): 12}}),
    ({"f1": 30, "f2": np.array([1, 6])}, CfgWithNumpy, TypeError, {
        "f3": _ref_cfg_with_numpy["f3"]}),
    ({}, CfgWithNumpy, None, _ref_cfg_with_numpy),
    ({}, CfgWithAny, None, {"f1": 12, "f2": None}),
    ({"f2": [7, 8, 9]}, CfgWithAny, None, {"f1": 12, "f2": [7, 8, 9]}),
    # note: the attrs.as_dict() removes the defaultdict
    ({"f1": 35}, CfgWithDefaultDict, None, {"f2": {}}),
    ({"f1": 36}, CfgWithDefaultDictNested, None, {"f3": {"f1": 12, "f2": {}}}),
    ({"f1": 36}, CfgWithDefaultDictDoubleNested, None,
     {'f3': {'f1': 12, 'f3': {'f1': 12, 'f2': {}}}}),
    ({"f1": b"6"}, CfgWithDefaultDictNested, TypeError, {"f3": {"f1": 12, "f2": {}}}),
    ({"f1": 36}, CfgWithDefaultDictNestedUntyped, None, {"f3": {"f1": 12, "f2": {}}}),
    ({"f1": 38}, CfgIntFloat, None, {"f2": 100}),
    ({"f1": (1, 3)}, CfgUntyped, None, {}),
    ({"f1": 8}, CfgPositional, None, {"f2": 7}),
])
def fixture_test_cases(request):
    yield request.param


def _create_ref_dict(input_dict, expected_input_update):
    ref_dict = deepcopy(input_dict)
    ref_dict.update(expected_input_update)
    for k in list(ref_dict.keys()):
        val = ref_dict[k]
        if isinstance(val, str) and val == _REMOVE_KEY:
            del ref_dict[k]
    return ref_dict


def test_typedattr(fixture_test_cases):
    input_dict, cfg_class, expected_error, expected_input_update = fixture_test_cases
    # note: if there is an expected_error, the final comparison will be between
    # output with strict=False, otherwise with strict=True
    ref_dict = _create_ref_dict(input_dict, expected_input_update)

    print(f"===================== test input {input_dict} class {cfg_class}")
    if expected_error is not None:
        print(f"---------- Expected to raise {expected_error}")
        with pytest.raises(expected_error):
            attrs_from_dict(cfg_class, input_dict, strict=True)

        print(f"---------- Expected to work when strict=False")
        c = attrs_from_dict(cfg_class, input_dict, strict=False)
    else:
        print(f"---------- Expected to work when strict=True")
        c = attrs_from_dict(cfg_class, input_dict, strict=True)
    print(f"Got {c}")
    print(f"          asserting output")
    cand_dict = attrs.asdict(c)

    ref_dict_flat = flatten_dict(ref_dict)
    cand_dict_flat = flatten_dict(cand_dict)
    all_values = list(ref_dict_flat.values()) + list(cand_dict_flat.values())
    if any(isinstance(v, np.ndarray) for v in all_values):
        # special case: numpy must be compared with .all()
        assert set(ref_dict_flat.keys()) == set(cand_dict_flat.keys()), (
            f"Mismatch in flat keys. Original dicts: {ref_dict} != {cand_dict}")
        print(f"Ref  flat {ref_dict}")
        print(f"Cand flat {cand_dict}")
        for k, v_ref in ref_dict_flat.items():
            v_cand = cand_dict_flat[k]
            if isinstance(v_ref, np.ndarray):
                assert (v_cand == v_ref).all()
                continue
            assert v_cand == v_ref
    else:
        # in other cases the dict comparison works out
        print(f"Ref  {ref_dict}")
        print(f"Cand {cand_dict}")
        assert cand_dict == ref_dict
    print()


def test_numpy_comparison():
    @definenumpy
    class CfgNumpyLocal:
        f1: np.ndarray = np.array([1, 7])


    c1 = CfgNumpyLocal()
    c2 = CfgNumpyLocal()
    assert c1 == c2
    c3 = CfgNumpyLocal(f1=np.array([1, 7]))
    assert c1 == c3
    c4 = CfgNumpyLocal(f1=np.array([1, 8]))
    assert c1 != c4


def test_readme_content():
    @define
    class Cfg:
        foo: int = 12
        bar: Optional[int] = None


    assert str(attrs_from_dict(Cfg, {"foo": 1, "bar": 2})) == "Cfg(foo=1, bar=2)"


    @define
    class CfgNested:
        sub_cfg: Cfg = None


    assert str(attrs_from_dict(CfgNested, {"sub_cfg": {"foo": 1, "bar": 2}})
               ) == "CfgNested(sub_cfg=Cfg(foo=1, bar=2))"
