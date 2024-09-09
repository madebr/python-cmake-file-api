from pathlib import Path
from typing import Any, Optional

from cmake_file_api.errors import CMakeException
from cmake_file_api.kinds.api import CMakeApiType, OBJECT_KINDS_API
from cmake_file_api.kinds.cmakeFiles.v1 import CMakeFilesV1
from cmake_file_api.reply.index.api import INDEX_API
from cmake_file_api.kinds.kind import ObjectKind
from cmake_file_api.reply.index.v1 import CMakeReplyFileV1


class CMakeFileApiV1:
    __slots__ = ("_build_path", )

    def __init__(self, build_path: Path):
        self._build_path = build_path

    def _create_query_path(self) -> Path:
        result = self._build_path / ".cmake" / "api" / "v1" / "query"
        result.mkdir(parents=True, exist_ok=True)
        if not result.is_dir():
            raise NotADirectoryError(f"Query path '{result}' is not a directory")
        return result

    def _create_reply_path(self) -> Path:
        result = self._build_path / ".cmake" / "api" / "v1" / "reply"
        result.mkdir(parents=True, exist_ok=True)
        if not result.is_dir():
            raise NotADirectoryError(f"Reply path '{result}' is not a directory")
        return result

    @staticmethod
    def _instrument_query_path(query_path: Path, kind: ObjectKind, kind_version: int) -> None:
        (query_path / f"{kind.value}-v{kind_version}").touch()

    @staticmethod
    def _find_index_path(reply_path: Path) -> Optional[Path]:
        try:
            return next(reply_path.glob("index-*.json"))
        except StopIteration:
            return None

    def find_index_path(self) -> Optional[Path]:
        reply_path = self._create_reply_path()
        return self._find_index_path(reply_path)

    def instrument(self, kind: ObjectKind, kind_version: int) -> None:
        query_path = self._create_query_path()
        self._instrument_query_path(query_path, kind, kind_version)

    def instrument_all(self) -> None:
        query_path = self._create_query_path()
        for kind, kind_api in OBJECT_KINDS_API.items():
            for kind_version in kind_api.keys():
                self._instrument_query_path(query_path, kind, kind_version)

    def _index(self, reply_path: Path) -> CMakeReplyFileV1:
        index_path = self._find_index_path(reply_path)
        if index_path is None:
            raise CMakeException("CMake did not generate index file. Maybe your cmake version is too old?")

        index_api = INDEX_API.get(1)
        if not index_api:
            raise CMakeException("Unknown api version")
        return index_api.from_path(index_path)

    def index(self) -> CMakeReplyFileV1:
        reply_path = self._create_reply_path()
        return self._index(reply_path)

    def inspect(self, kind: ObjectKind, kind_version: int) -> Optional[CMakeApiType]:
        reply_path = self._create_reply_path()
        index = self._index(reply_path)

        data_path = index.reply.stateless.get((kind, kind_version), None)
        if data_path is None:
            return None
        api: Optional[CMakeApiType] = OBJECT_KINDS_API.get(kind, {}).get(kind_version, None)
        if api is None:
            return None
        return api.from_path(reply_path / str(data_path.jsonFile), reply_path)

    def inspect_all(self) -> dict[ObjectKind, dict[int, object]]:
        reply_path = self._create_reply_path()
        index = self._index(reply_path)

        result: dict[ObjectKind, dict[int, Any]] = {}
        for (kind, kind_version), reply_file_ref in index.reply.stateless.items():
            api = OBJECT_KINDS_API.get(kind, {}).get(kind_version, None)
            if api is None:
                continue
            kind_data = api.from_path(reply_path / str(reply_file_ref.jsonFile), reply_path)
            result.setdefault(kind, {})[kind_version] = kind_data
        return result
