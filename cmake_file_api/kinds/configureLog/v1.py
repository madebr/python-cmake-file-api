import json
from pathlib import Path
from typing import Dict, List, Optional

from cmake_file_api.kinds.common import CMakeSourceBuildPaths, VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind
from .target.v2 import CodemodelTargetV2


class ConfigureLogV1(object):
    KIND = ObjectKind.CONFIGURELOG

    __slots__ = ("version", "path", "eventKindNames")

    def __init__(self, version: VersionMajorMinor, path: Path, eventKindNames: List[str]):
        self.version = version
        self.path = path
        self.eventKindNames = eventKindNames

    @classmethod
    def from_dict(cls, dikt: dict, reply_path: Path) -> "ConfigureLogV1":
        if dikt["kind"] != cls.KIND.value:
            raise ValueError
        path = Path(dikt["path"])
        version = VersionMajorMinor.from_dict(dikt["version"])
        event_kind_names = dikt["eventKindNames"]
        return cls(version, path, event_kind_names)

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> "ConfigureLogV1":
        dikt = json.load(path.open())
        return cls.from_dict(dikt, reply_path)

    def __repr__(self) -> str:
        return "{}(version={}, paths={}, configurations={})".format(
            type(self).__name__,
            self.version,
            self.paths,
            self.configurations,
        )
