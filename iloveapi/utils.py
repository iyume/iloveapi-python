from typing import Any, Callable, TypeVar

from typing_extensions import Concatenate, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")
TR = TypeVar("TR")


def cast_omit_self(
    func: Callable[Concatenate[Any, P], TR]
) -> Callable[Concatenate[P], TR]: ...
