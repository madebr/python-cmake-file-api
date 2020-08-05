from pathlib import Path
from typing import Dict

from cmake_file_api.kinds.kind import ObjectKind
from cmake_file_api.kinds.common import VersionMajorMinor


class CMakeReplyFileReferenceV1(object):
    def __init__(self, kind: ObjectKind, version: VersionMajorMinor, jsonFile: Path):
        self.kind = kind
        self.version = version
        self.jsonFile = jsonFile

    @classmethod
    def from_dict(cls, dikt: Dict) -> "CMakeReplyFileReferenceV1":
        kind = ObjectKind(dikt["kind"])
        version = VersionMajorMinor.from_dict(dikt["version"])
        jsonFile = Path(dikt["jsonFile"])
        return cls(kind, version, jsonFile)
