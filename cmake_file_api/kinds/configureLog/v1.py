import json
from pathlib import Path
from typing import Any

from cmake_file_api.kinds.common import VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind


class ConfigureLogV1:
    KIND = ObjectKind.CONFIGURELOG

    __slots__ = ("version", "path", "eventKindNames")

    def __init__(self, version: VersionMajorMinor, path: Path, eventKindNames: list[str]):
        self.version = version
        self.path = path
        self.eventKindNames = eventKindNames

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], reply_path: Path) -> "ConfigureLogV1":
        if dikt["kind"] != cls.KIND.value:
            raise ValueError
        path = Path(dikt["path"])
        version = VersionMajorMinor.from_dict(dikt["version"])
        event_kind_names = dikt["eventKindNames"]
        return cls(version, path, event_kind_names)

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> "ConfigureLogV1":
        with path.open() as file:
            dikt = json.load(file)
        return cls.from_dict(dikt, reply_path)

    def __repr__(self) -> str:
        return "{}(version={}, paths={}, configurations={})".format(
            type(self).__name__,
            self.version,
            self.path,
            self.eventKindNames,
        )
