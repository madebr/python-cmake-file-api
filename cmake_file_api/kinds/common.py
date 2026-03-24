import dataclasses
from pathlib import Path
from typing import Any


@dataclasses.dataclass(frozen=True, slots=True)
class VersionMajorMinor:
    major: int
    minor: int

    @classmethod
    def from_dict(cls, d: dict[str, int]) -> "VersionMajorMinor":
        return cls(d["major"], d["minor"])


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
