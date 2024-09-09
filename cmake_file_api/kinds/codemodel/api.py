from __future__ import annotations
import typing

from .v2 import CodemodelV2


if typing.TYPE_CHECKING:
    from ..api import CMakeApiType

CODEMODEL_API: dict[int, CMakeApiType]  = {
    2: CodemodelV2,
}
