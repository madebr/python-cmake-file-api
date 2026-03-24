import dataclasses
import json
from pathlib import Path
from typing import Any

from cmake_file_api.kinds.common import VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind


@dataclasses.dataclass(frozen=True, slots=True)
class ConfigureLogV1:
    version: VersionMajorMinor
    path: Path
    eventKindNames: list[str]

    @staticmethod
    def kind() -> ObjectKind:
        return ObjectKind.CONFIGURELOG

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], reply_path: Path) -> "ConfigureLogV1":
        if dikt["kind"] != cls.kind():
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
