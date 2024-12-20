from pathlib import Path
from typing import Any, Callable, Mapping, Sequence, TypeVar
from urllib.parse import urlparse

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


def get_filename_from_url(url: str) -> str:
    url_parsed = urlparse(url)
    return Path(url_parsed.path).name
