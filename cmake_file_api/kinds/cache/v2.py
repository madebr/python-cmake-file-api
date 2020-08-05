from enum import Enum
import json
from pathlib import Path
from typing import Dict, List

from cmake_file_api.kinds.common import VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind


class CacheEntryType(Enum):
    TYPE_BOOL = "BOOL"
    TYPE_FILEPATH = "FILEPATH"
    TYPE_PATH = "PATH"
    TYPE_STRING = "STRING"
    TYPE_INTERNAL = "INTERNAL"
    TYPE_STATIC = "STATIC"


class CacheEntryProperty(object):
    __slots__ = ("name", "value")

    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CacheEntryProperty":
        name = dikt["name"]
        value = dikt["value"]
        return cls(name, value)

    def __repr__(self) -> str:
        return "{}(name='{}', value='{}')".format(
            type(self).__name__,
            self.name,
            self.value,
        )


class CacheEntry(object):
    __slots__ = ("name", "value", "type", "properties")

    def __init__(self, name: str, value: str, type: CacheEntryType, properties: List[CacheEntryProperty]):
        self.name = name
        self.value = value
        self.type = type
        self.properties = properties

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CacheEntry":
        name = dikt["name"]
        value = dikt["value"]
        type = CacheEntryType(dikt["type"])
        properties = list(CacheEntryProperty.from_dict(cep) for cep in dikt["properties"])
        return cls(name, value, type, properties)

    def __repr__(self) -> str:
        return "{}(name='{}', value='{}', type={}, properties={})".format(
            type(self).__name__,
            self.name,
            self.value,
            self.type.name,
            repr(self.properties),
        )


class CacheV2(object):
    KIND = ObjectKind.CACHE

    __slots__ = ("version", "entries")

    def __init__(self, version: VersionMajorMinor, entries: List[CacheEntry]):
        self.version = version
        self.entries = entries

    @classmethod
    def from_dict(cls, dikt: Dict, reply_path) -> "CacheModelV2":
        if dikt["kind"] != cls.KIND.value:
            raise ValueError
        version = VersionMajorMinor.from_dict(dikt["version"])
        entries = list(CacheEntry.from_dict(ce) for ce in dikt["entries"])
        return cls(version, entries)

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> "CacheModelV2":
        dikt = json.load(path.open())
        return cls.from_dict(dikt, reply_path)

    def __repr__(self) -> str:
        return "{}(version={}, entries={})".format(
            type(self).__name__,
            repr(self.version),
            repr(self.entries),
        )
