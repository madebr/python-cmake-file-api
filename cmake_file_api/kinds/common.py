from pathlib import Path
from typing import Any


class VersionMajorMinor:
    __slots__ = ("major", "minor")

    def __init__(self, major: int, minor: int):
        self.major = major
        self.minor = minor

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> "VersionMajorMinor":
        return cls(int(d["major"]), int(d["minor"]))

    def __repr__(self) -> str:
        return "Version({}.{})".format(
            self.major,
            self.minor,
        )


class CMakeSourceBuildPaths:
    __slots__ = ("source", "build")

    def __init__(self, source: Path, build: Path):
        self.source = source
        self.build = build

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CMakeSourceBuildPaths":
        return cls(Path(d["source"]), Path(d["build"]))

    def __repr__(self) -> str:
        return "CMakePaths(source='{}', build='{}')".format(
            self.source,
            self.build,
        )
