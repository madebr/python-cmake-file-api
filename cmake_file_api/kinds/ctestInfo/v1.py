from enum import Enum
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from cmake_file_api.kinds.common import VersionMajorMinor
from cmake_file_api.kinds.common.backtraceGraph import BacktraceNode, BacktraceGraph
from cmake_file_api.kinds.kind import ObjectKind


class CTestTest(object):
    __slots__ = ("name", "command", "properties", "backtrace")

    def __init__(self, name: str, command: List[str], properties: Dict[str, Any], backtrace: BacktraceNode):
        self.name = name
        self.command = command
        self.properties = properties
        self.backtrace = backtrace

    @classmethod
    def from_dict(cls, dikt: Dict, backtraceGraph: BacktraceGraph) -> "CTestTest":
        name = dikt["name"]
        command = dikt.get("command")
        properties = {d["name"]: d["value"] for d in dikt["properties"]}
        backtrace = backtraceGraph.nodes[dikt["backtrace"]]
        return cls(name, command, properties, backtrace)

    def __repr__(self) -> str:
        return "{}(name='{}', command={}, properties={}, backtrace={})".format(
            type(self).__name__,
            self.name,
            self.command,
            self.properties,
            self.backtrace,
        )


class CTestInfoV1(object):
    KIND = ObjectKind.CTESTINFO

    __slots__ = ("version", "tests")

    def __init__(self, version: VersionMajorMinor, tests: List[CTestTest]):
        self.version = version
        self.tests = tests

    @classmethod
    def from_dict(cls, dikt: Dict, reply_path) -> "CTestInfoV1":
        if dikt["kind"] != cls.KIND.value:
            raise ValueError
        version = VersionMajorMinor.from_dict(dikt["version"])
        backtraceGraph = BacktraceGraph.from_dict(dikt["backtraceGraph"])
        tests = list(CTestTest.from_dict(t, backtraceGraph) for t in dikt["tests"])
        return cls(version, tests)

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> "CTestInfoV1":
        with path.open() as f:
            return cls.from_text(f.read(), reply_path)

    @classmethod
    def from_text(cls, text: str, reply_path: Path) -> "CTestInfoV1":
        return cls.from_dict(json.loads(text), reply_path)

    def __repr__(self) -> str:
        return "{}(version={}, tests={})".format(
            type(self).__name__,
            repr(self.version),
            self.tests,
        )
