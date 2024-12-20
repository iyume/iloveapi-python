from typing import Any, Callable, Mapping, Sequence, TypeVar

from typing_extensions import Concatenate, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")
TK = TypeVar("TK")
TR = TypeVar("TR")
TM_co = TypeVar("TM_co", bound=Mapping, covariant=True)


def cast_omit_self(
    func: Callable[Concatenate[Any, P], TR]
) -> Callable[Concatenate[P], TR]: ...


def to_dict(obj: Sequence[TM_co], key: TK) -> dict[TK, TM_co]:
    """ToDictionary implementation for Python.

    Considering performance, this function do not use a lambda-based keyselector.
    """
    return {item[key]: item for item in obj}
