from pathlib import Path
from typing import Protocol
from typing_extensions import Self

from .kind import ObjectKind
from .cache.api import CACHE_API
from .cmakeFiles.api import CMAKEFILES_API
from .codemodel.api import CODEMODEL_API
from .configureLog.api import CONFIGURELOG_API
from .toolchains.api import TOOLCHAINS_API


class CMakeApiType(Protocol):
    KIND: ObjectKind

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> Self:
        ...

OBJECT_KINDS_API: dict[ObjectKind, dict[int, CMakeApiType]] = {
    ObjectKind.CACHE: CACHE_API,
    ObjectKind.CMAKEFILES: CMAKEFILES_API,
    ObjectKind.CONFIGURELOG: CONFIGURELOG_API,
    ObjectKind.CODEMODEL: CODEMODEL_API,
    ObjectKind.TOOLCHAINS: TOOLCHAINS_API,
}
