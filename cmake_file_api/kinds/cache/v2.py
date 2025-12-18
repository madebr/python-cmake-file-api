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


class CacheEntryProperty:
    __slots__ = ("name", "value")

    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "CacheEntryProperty":
        name = dikt["name"]
        value = dikt["value"]
        return cls(name, value)

    def __repr__(self) -> str:
        return "{}(name='{}', value='{}')".format(
            type(self).__name__,
            self.name,
            self.value,
        )

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

class CacheV2:
    KIND = ObjectKind.CACHE

    __slots__ = ("version", "entries")

    def __init__(self, version: VersionMajorMinor, entries: list[CacheEntry]):
        self.version = version
        self.entries = entries

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], reply_path: Path) -> "CacheV2":
        if dikt["kind"] != cls.KIND.value:
            raise ValueError
        version = VersionMajorMinor.from_dict(dikt["version"])
        entries = list(CacheEntry.from_dict(ce) for ce in dikt["entries"])
        return cls(version, entries)

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> "CacheV2":
        with path.open() as file:
            dikt = json.load(file)
        return cls.from_dict(dikt, reply_path)

    def __repr__(self) -> str:
        return "{}(version={}, entries={})".format(
            type(self).__name__,
            repr(self.version),
            repr(self.entries),
        )
