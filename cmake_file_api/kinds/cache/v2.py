import dataclasses
from enum import Enum
import json
from pathlib import Path
from typing import Any

from cmake_file_api.kinds.common import VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind


class CacheEntryType(Enum):
    TYPE_BOOL = "BOOL"
    TYPE_FILEPATH = "FILEPATH"
    TYPE_PATH = "PATH"
    TYPE_STRING = "STRING"
    TYPE_INTERNAL = "INTERNAL"
    TYPE_STATIC = "STATIC"
    TYPE_UNINITIALIZED = "UNINITIALIZED"

@dataclasses.dataclass(slots=True, frozen=True, repr=True)
class CacheEntryProperty:
    name: str
    value: str

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "CacheEntryProperty":
        name = dikt["name"]
        value = dikt["value"]
        return cls(name, value)

@dataclasses.dataclass(frozen = True, slots = True)
class CacheEntry:
    name : str
    value : str
    type : CacheEntryType
    properties : list[CacheEntryProperty]

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "CacheEntry":
        name = dikt["name"]
        value = dikt["value"]
        type = CacheEntryType(dikt["type"])
        properties = list(CacheEntryProperty.from_dict(cep) for cep in dikt["properties"])
        return cls(name, value, type, properties)

@dataclasses.dataclass(frozen=True, slots=True)
class CacheV2:
    version: VersionMajorMinor
    entries: list[CacheEntry]

    @staticmethod
    def kind() -> ObjectKind:
        return ObjectKind.CACHE

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], reply_path: Path) -> "CacheV2":
        if dikt["kind"] != cls.kind():
            raise ValueError
        version = VersionMajorMinor.from_dict(dikt["version"])
        entries = list(CacheEntry.from_dict(ce) for ce in dikt["entries"])
        return cls(version, entries)

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> "CacheV2":
        with path.open() as file:
            dikt = json.load(file)
        return cls.from_dict(dikt, reply_path)
