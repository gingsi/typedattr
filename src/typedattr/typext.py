"""Type extensions"""
from io import IOBase
from pathlib import Path
from typing import Union, Any, Type, List

from attrs import AttrsInstance, fields
from importlib_resources.abc import Traversable

TensorType = Any
AttrsClass = Type[AttrsInstance]
PathType = Union[str, Path, Traversable]
PathOrIO = Union[PathType, IOBase]

# Subscripted generics cannot be used with class and instance check
# i.e. to use isinstance(obj, the_type) they need to be defined as a tuple
PathTypeCls = (str, Path, Traversable)
PathOrIOCls = (str, Path, Traversable, IOBase)


def get_attr_names(cls: AttrsClass) -> List[str]:
    """Get all attribute names of an attrs class."""
    return [att.name for att in fields(cls)]  # noqa
