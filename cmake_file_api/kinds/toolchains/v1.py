import json
from pathlib import Path
from typing import Any, Optional

from cmake_file_api.kinds.common import VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind


class CMakeToolchainCompilerImplicit:
    __slots__ = ("includeDirectories", "linkDirectories", "linkFrameworkDirectories", "linkLibraries")

    def __init__(self) -> None:
        self.includeDirectories: list[Path] = []
        self.linkDirectories: list[Path] = []
        self.linkFrameworkDirectories: list[Path] = []
        self.linkLibraries: list[str] = []

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "CMakeToolchainCompilerImplicit":
        res = cls()
        if "includeDirectories" in dikt:
            res.includeDirectories.extend(Path(p) for p in dikt["includeDirectories"])
        if "linkDirectories" in dikt:
            res.linkDirectories.extend(Path(p) for p in dikt["linkDirectories"])
        if "linkFrameworkDirectories" in dikt:
            res.linkFrameworkDirectories.extend(Path(p) for p in dikt["linkFrameworkDirectories"])
        if "linkLibraries" in dikt:
            res.linkFrameworkDirectories.extend(dikt["linkLibraries"])
        return res


class CMakeToolchainCompiler:
    __slots__ = ("id", "path", "target", "version", "implicit")

    def __init__(self, id: Optional[str], path: Optional[Path], target: Optional[str], version: Optional[str], implicit: CMakeToolchainCompilerImplicit):
        self.id = id
        self.path = path
        self.target = target
        self.version = version
        self.implicit = implicit

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "CMakeToolchainCompiler":
        id = dikt.get("id")
        path = Path(dikt["path"]) if "path" in dikt else None
        target = dikt.get("target")
        version = dikt.get("version")
        implicit = CMakeToolchainCompilerImplicit.from_dict(dikt.get("implicit", {}))
        return cls(id, path, target, version, implicit)

    def __repr__(self) -> str:
        return "{}(id='{}', path='{}', target='{}', version='{}')".format(
            type(self).__name__,
            self.id,
            self.path,
            self.target,
            self.version
        )


class CMakeToolchain:
    __slots__ = ("language", "compiler", "sourceFileExtensions")

    def __init__(self, language: str, compiler: CMakeToolchainCompiler, sourceFileExtensions: Optional[list[str]]):
        self.language = language
        self.compiler = compiler
        self.sourceFileExtensions = sourceFileExtensions

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "CMakeToolchain":
        language = dikt["language"]
        compiler = CMakeToolchainCompiler.from_dict(dikt["compiler"])
        sourceFileExtensions = dikt.get("sourceFileExtensions")

        return cls(language, compiler, sourceFileExtensions)

    def __repr__(self) -> str:
        return "{}(language='{}', compiler='{}')".format(
            type(self).__name__,
            self.language,
            self.compiler
        )


class ToolchainsV1:
    KIND = ObjectKind.TOOLCHAINS

    __slots__ = ("version", "toolchains")

    def __init__(self, version: VersionMajorMinor, toolchains: list[CMakeToolchain]):
        self.version = version
        self.toolchains = toolchains

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], reply_path: Path) -> "ToolchainsV1":
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
