from __future__ import annotations
import typing

from .v2 import CacheV2

if typing.TYPE_CHECKING:
    from ..api import CMakeApiType

CACHE_API: dict[int, type[CMakeApiType]] = {
    2: CacheV2,
}
