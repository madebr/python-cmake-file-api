from pathlib import Path
import subprocess
from typing import Dict, List, Optional

from .kinds.kind import ObjectKind
from .reply.api import REPLY_API


class CMakeProject(object):
    __slots__ = ("_source_path", "_build_path", "_api_version", "_cmake")

    def __init__(self, source_path: Optional[Path], build_path: Path, api_version: Optional[int]=None, cmake: Optional[str]=None):
        if not build_path:
            raise ValueError("Need a build folder")
        self._source_path = Path(source_path)
        self._build_path = Path(build_path)
        self._api_version = api_version if api_version is not None else self.most_recent_api_version()
        self._cmake = cmake or "cmake"

    @property
    def source_path(self) -> Optional[Path]:
        return self._source_path

    @property
    def build_path(self) -> Path:
        return self._build_path

    @staticmethod
    def most_recent_api_version() -> int:
        return max(list(REPLY_API.keys()))

    def configure(self, args: Optional[List[str]]=None, quiet=False):
        if self._source_path is None:
            raise ValueError("Cannot configure with no source path")
        stdout = subprocess.DEVNULL if quiet else None
        args = [str(self._cmake), str(self._source_path)] + (args if args else [])
        subprocess.check_call(args, cwd=str(self._build_path), stdout=stdout)

    def reconfigure(self, quiet=False):
        stdout = subprocess.DEVNULL if quiet else None
        args = [str(self._cmake)]
        if self._source_path:
            args.append(str(self._source_path))
        subprocess.check_call(args, cwd=str(self._build_path), stdout=stdout)

    @property
    def cmake_file_api(self):
        return REPLY_API[self._api_version](self._build_path)
