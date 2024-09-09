from __future__ import annotations
import typing

from .v1 import CMakeFilesV1

if typing.TYPE_CHECKING:
    from ..api import CMakeApiType

CMAKEFILES_API: dict[int, CMakeApiType]  = {
    1: CMakeFilesV1,
}
