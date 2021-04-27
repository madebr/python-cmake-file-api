from enum import Enum
import json
from pathlib import Path
from typing import Dict, List

from cmake_file_api.kinds.common import VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind


class ToolchainLanguageType(Enum):
    """ See https://cmake.org/cmake/help/v3.20/command/project.html#command:project for reference """
    LANGUAGE_C = "C"
    LANGUAGE_CXX = "CXX"
    LANGUAGE_ASM = "ASM"
    LANGUAGE_CUDA = "CUDA"
    LANGUAGE_OBJC = "OBJC"
    LANGUAGE_OBJCXX = "OBJCXX"
    LANGUAGE_Fortran = "Fortran"
    LANGUAGE_ISPC = "ISPC"

class ToolchainCompilerType(Enum):
    """ See https://cmake.org/cmake/help/v3.20/variable/CMAKE_LANG_COMPILER_ID.html#variable:CMAKE_%3CLANG%3E_COMPILER_ID for reference """
    COMPILER_Absoft = "Absoft"
    COMPILER_ADSP = "ADSP"
    COMPILER_AppleClang = "AppleClang"
    COMPILER_ARMClang = "ARMClang"
    COMPILER_ARMCC = "ARMCC"
    COMPILER_Bruce = "Bruce"
    COMPILER_CCur = "CCur"
    COMPILER_Clang = "Clang"
    COMPILER_Cray = "Cray"
    COMPILER_Embarcadero = "Embarcadero"
    COMPILER_Flang = "Flang"
    COMPILER_G95 = "G95"
    COMPILER_GNU = "GNU"
    COMPILER_GHS = "GHS"
    COMPILER_HP = "HP"
    COMPILER_IAR = "IAR"
    COMPILER_Intel = "Intel"
    COMPILER_IntelLLVM = "IntelLLVM"
    COMPILER_MSVC = "MSVC"
    COMPILER_NVHPC = "NVHPC"
    COMPILER_NVIDIA = "NVIDIA"
    COMPILER_OpenWatcom = "OpenWatcom"
    COMPILER_PGI = "PGI"
    COMPILER_PathScale = "PathScale"
    COMPILER_SDCC = "SDCC"
    COMPILER_SunPro = "SunPro"
    COMPILER_TI = "TI"
    COMPILER_TinyCC = "TinyCC"
    COMPILER_XL = "XL"
    COMPILER_XLClang = "XLClang"

class CMakeToolchainCompiler(object):
    __slots__ = ("id", "path", "target", "version")

    def __init__(self, id: "ToolchainCompilerType", path: Path, target: str, version: str):
        self.id = id
        self.path = path
        self.target = target
        self.version = version

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakeToolchain":
        id = ToolchainCompilerType(dikt["id"])
        path = dikt["path"]
        target = dikt["target"]
        version = dikt["version"]
        return cls(id, path, target, version)

    def __repr__(self) -> str:
        return "{}(id='{}', path='{}', target='{}', version='{}')".format(
            type(self).__name__,
            self.id,
            self.path,
            self.target,
            self.version
        ) 

class CMakeToolchain(object):
    __slots__ = ("language", "compiler")

    def __init__(self, language: ToolchainLanguageType, compiler: CMakeToolchainCompiler):
        self.language = language
        self.compiler = compiler

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakeToolchain":
        language = ToolchainLanguageType(dikt["language"])
        compiler = CMakeToolchainCompiler.from_dict(dikt["compiler"])
        return cls(language, compiler)

    def __repr__(self) -> str:
        return "{}(language='{}', compiler='{}')".format(
            type(self).__name__,
            self.language,
            self.compiler
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
