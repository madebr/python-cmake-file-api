import dataclasses
import json
from pathlib import Path
from typing import Any, Optional

from cmake_file_api.kinds.common import VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind


@dataclasses.dataclass(frozen=True, slots=True, repr=False)
class CMakeToolchainCompilerImplicit:
    includeDirectories: list[Path] = dataclasses.field()
    linkDirectories: list[Path] = dataclasses.field()
    linkFrameworkDirectories: list[Path] = dataclasses.field()
    linkLibraries: list[str] = dataclasses.field()

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "CMakeToolchainCompilerImplicit":
        return cls(
            includeDirectories=[Path(p) for p in dikt["includeDirectories"]] if "includeDirectories" in dikt else [],
            linkDirectories=[Path(p) for p in dikt["linkDirectories"]] if "linkDirectories" in dikt else [],
            linkFrameworkDirectories=[Path(p) for p in dikt["linkFrameworkDirectories"]] if "linkFrameworkDirectories" in dikt else [],
            linkLibraries=dikt["linkLibraries"] if "linkLibraries" in dikt else [],
        )

@dataclasses.dataclass(frozen=True, slots=True)
class CMakeToolchainCompiler:
    id: Optional[str]
    path: Optional[Path]
    target: Optional[str]
    version: Optional[str]
    implicit: CMakeToolchainCompilerImplicit = dataclasses.field(repr=False)

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "CMakeToolchainCompiler":
        return cls(
            id=dikt.get("id"),
            path=Path(dikt["path"]) if "path" in dikt else None,
            target=dikt.get("target"),
            version=dikt.get("version"),
            implicit=CMakeToolchainCompilerImplicit.from_dict(dikt.get("implicit", {})),
        )

@dataclasses.dataclass(frozen=True, slots=True)
class CMakeToolchain:
    language: str
    compiler: CMakeToolchainCompiler
    sourceFileExtensions: Optional[list[str]] = dataclasses.field(repr=False)

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "CMakeToolchain":
        return cls(
            language=dikt["language"],
            compiler=CMakeToolchainCompiler.from_dict(dikt["compiler"]),
            sourceFileExtensions=dikt.get("sourceFileExtensions"),
        )

@dataclasses.dataclass(frozen=True, slots=True)
class ToolchainsV1:
    version: VersionMajorMinor
    toolchains: list[CMakeToolchain]

    @staticmethod
    def kind() -> ObjectKind:
        return ObjectKind.TOOLCHAINS

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], reply_path: Path) -> "ToolchainsV1":
        return cls(
            version=VersionMajorMinor.from_dict(dikt["version"]),
            toolchains=list(CMakeToolchain.from_dict(cmi) for cmi in dikt["toolchains"]),
        )

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> "ToolchainsV1":
        with path.open() as file:
            dikt = json.load(file)
        return cls.from_dict(dikt, reply_path)
