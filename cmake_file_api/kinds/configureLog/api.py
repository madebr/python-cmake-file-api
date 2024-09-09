from __future__ import annotations
import typing

from .v1 import ConfigureLogV1

if typing.TYPE_CHECKING:
    from ..api import CMakeApiType

CONFIGURELOG_API: dict[int, CMakeApiType]  = {
    1: ConfigureLogV1,
}
