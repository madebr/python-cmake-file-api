from __future__ import annotations
import typing

from .v1 import ToolchainsV1

if typing.TYPE_CHECKING:
    from ..api import CMakeApiType

TOOLCHAINS_API: dict[int, CMakeApiType]  = {
    1: ToolchainsV1,
}
