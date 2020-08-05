import json
from pathlib import Path
from typing import Dict, List, Optional

from cmake_file_api.kinds.common import CMakeSourceBuildPaths, VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind


class CMakeFilesInput(object):
    __slots__ = ("path", "isGenerator", "isExternal", "isCMake")

    def __init__(self, path: Path, isGenerator: Optional[bool], isExternal: Optional[bool], isCMake: Optional[bool]):
        self.path = path
        self.isGenerator = isGenerator
        self.isExternal = isExternal
        self.isCMake = isCMake

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakeFileInput":
        path = Path(dikt["path"])
        isGenerator = dikt.get("isGenerator")
        isExternal = dikt.get("isExternal")
        isCMake = dikt.get("isExternal")
        return cls(path, isGenerator, isExternal, isCMake)

    def __repr__(self) -> str:
        return "{}(path='{}', generator={}, external={}, cmake={})".format(
            type(self).__name__,
            self.path,
            self.isGenerator,
            self.isExternal,
            self.isCMake,
        )


class CMakeFilesV1(object):
    KIND = ObjectKind.CMAKEFILES

    __slots__ = ("version", "paths", "inputs")

    def __init__(self, version: VersionMajorMinor, paths: CMakeSourceBuildPaths, inputs: List[CMakeFilesInput]):
        self.version = version
        self.paths = paths
        self.inputs = inputs

    @classmethod
    def from_dict(cls, dikt: Dict, reply_path: Path) -> "CmakeFilesV2":
        version = VersionMajorMinor.from_dict(dikt["version"])
        paths = CMakeSourceBuildPaths.from_dict(dikt["paths"])
        inputs = list(CMakeFilesInput.from_dict(cmi) for cmi in dikt["inputs"])
        return cls(version, paths, inputs)

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> "CmakeFilesV2":
        dikt = json.load(path.open())
        return cls.from_dict(dikt, reply_path)

    def __repr__(self) -> str:
        return "{}(version={}, paths={}, inputs={})".format(
            type(self).__name__,
            repr(self.version),
            self.paths,
            repr(self.inputs),
        )
