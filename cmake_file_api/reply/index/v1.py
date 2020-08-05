import json
from pathlib import Path
from typing import Dict, List, Tuple


from cmake_file_api.kinds.kind import ObjectKind
from .file.v1 import CMakeReplyFileReferenceV1


class CMakeGenerator(object):
    __slots__ = ("name", "multiConfig")

    def __init__(self, name: str, multiConfig: bool):
        self.name = name
        self.multiConfig = multiConfig

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakeGenerator":
        name = dikt["name"]
        multiConfig = dikt["multiConfig"]
        return cls(name, multiConfig)

    def __repr__(self) -> str:
        return "{}(name='{}', multiConfig={})".format(
            type(self).__name__,
            self.name,
            self.multiConfig,
        )


class CMakeVersion(object):
    def __init__(self, major: int, minor: int, patch: int, string: str, suffix: str, isDirty: bool):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.string = string
        self.suffix = suffix
        self.isDirty = isDirty

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakeVersion":
        major = dikt["major"]
        minor = dikt["minor"]
        patch = dikt["patch"]
        string = dikt["string"]
        suffix = dikt["suffix"]
        isDirty = dikt["isDirty"]
        return cls(major, minor, patch, string, suffix, isDirty)

    def __repr__(self) -> str:
        return "{}(major={}, minor={}, patch={}, string='{}', suffix='{}', isDirty={})".format(
            type(self).__name__,
            self.major,
            self.minor,
            self.patch,
            self.string,
            self.suffix,
            self.isDirty,
        )


class CMakePaths(object):
    __slots__ = ("cmake", "cpack", "ctest", "root")

    def __init__(self, cmake: Path, cpack: Path, ctest: Path, root: Path):
        self.cmake = cmake
        self.cpack = cpack
        self.ctest = ctest
        self.root = root

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakePaths":
        cmake = Path(dikt["cmake"])
        cpack = Path(dikt["cpack"])
        ctest = Path(dikt["ctest"])
        root = Path(dikt["root"])
        return cls(cmake, cpack, ctest, root)

    def __str__(self) -> str:
        return "{}(cmake='{}', cpack='{}', ctest='{}', root='{}')".format(
            type(self).__name__,
            self.cmake,
            self.cpack,
            self.ctest,
            self.root,
        )


class CMakeInfo(object):
    __slots__ = ("version", "paths", "generator")

    def __init__(self, version: CMakeVersion, paths: CMakePaths, generator: CMakeGenerator):
        self.version = version
        self.paths = paths
        self.generator = generator

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakeInfo":
        version = CMakeVersion.from_dict(dikt["version"])
        paths = CMakePaths.from_dict(dikt["paths"])
        generator = CMakeGenerator.from_dict(dikt["generator"])
        return cls(version, paths, generator)

    def __str__(self) -> str:
        return "{}(version={}, paths={}, generator={})".format(
            type(self).__name__,
            self.version,
            self.paths,
            self.generator,
        )


class CMakeReply(object):
    __slots__ = ("stateless", "stateful", "unknowns")

    def __init__(self, stateless: Dict[Tuple[ObjectKind, int], CMakeReplyFileReferenceV1],
                 stateful: Dict[str, Dict], unknowns: List[str]):
        self.stateless = stateless
        self.stateful = stateful
        self.unknowns = unknowns

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakeReply":
        stateless = {}
        stateful = {}
        unknowns = []
        for k, v in dikt.items():
            import re
            stateless_match = re.match(r"([a-zA-Z0-9]+)-v([0-9]+)", k)
            if stateless_match:
                kind, version = ObjectKind(stateless_match.group(1)), int(stateless_match.group(2))
                stateless[(kind, version)] = CMakeReplyFileReferenceV1.from_dict(v)
            elif re.match(r"client-[a-zA-Z0-9]+", k):
                stateful[k] = v
            else:
                unknowns.append(k)

        return cls(stateless, stateful, unknowns)


class CMakeReplyFileV1(object):
    __slots__ = ("cmake", "objects", "reply")

    def __init__(self, cmake: CMakeInfo, objects: List[CMakeReplyFileReferenceV1], reply: CMakeReply):
        self.cmake = cmake
        self.objects = objects
        self.reply = reply

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakeReplyFileV1":
        cmake = CMakeInfo.from_dict(dikt["cmake"])
        objects = list(CMakeReplyFileReferenceV1.from_dict(do) for do in dikt["objects"])
        reply = CMakeReply.from_dict(dikt["reply"])
        return cls(cmake, objects, reply)

    @classmethod
    def from_path(cls, path: Path) -> "CMakeReplyFileV1":
        dikt = json.load(path.open())
        return cls.from_dict(dikt)
