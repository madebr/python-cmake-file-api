from enum import Enum
import json
from pathlib import Path
from typing import Dict, List

from cmake_file_api.kinds.common import VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind


class ToolchainLanguageType(Enum):
    LANGUAGE_C = "C"
    LANGUAGE_CXX = "CXX"
    LANGUAGE_ASM = "ASM"
    LANGUAGE_CUDA = "CUDA"
    LANGUAGE_OBJC = "OBJC"
    LANGUAGE_OBJCXX = "OBJCXX"
    LANGUAGE_Fortran = "Fortran"
    LANGUAGE_ISPC = "ISPC"


class CMakeToolchain(object):
    __slots__ = ("language")

    def __init__(self, language: ToolchainLanguageType):
        self.language = language

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakeToolchain":
        language = ToolchainLanguageType(dikt["language"])
        return cls(language)

    def __repr__(self) -> str:
        return "{}(language='{}')".format(
            type(self).__name__,
            self.language,
        )


class ToolchainsV1(object):
    KIND = ObjectKind.TOOLCHAINS

    __slots__ = ("version", "toolchains")

    def __init__(self, version: VersionMajorMinor, toolchains: List[CMakeToolchain]):
        self.version = version
        self.toolchains = toolchains

    @classmethod
    def from_dict(cls, dikt: Dict, reply_path: Path) -> "ToolchainsV1":
        version = VersionMajorMinor.from_dict(dikt["version"])
        toolchains = list(CMakeToolchain.from_dict(cmi) for cmi in dikt["toolchains"])
        return cls(version, toolchains)

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> "ToolchainsV1":
        dikt = json.load(path.open())
        return cls.from_dict(dikt, reply_path)

    def __repr__(self) -> str:
        return "{}(version={}, inputs={})".format(
            type(self).__name__,
            repr(self.version),
            repr(self.toolchains),
        )
