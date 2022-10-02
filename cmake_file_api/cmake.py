from pathlib import Path
import subprocess
from typing import List, Optional, Union

from .reply.api import REPLY_API

PathLike = Union[Path, str]


class CMakeProject(object):
    __slots__ = ("_source_path", "_build_path", "_api_version", "_cmake")

    def __init__(self, build_path: PathLike, source_path: Optional[PathLike]=None, api_version: Optional[int]=None, cmake: Optional[str]=None):
        if not build_path:
            raise ValueError("Need a build folder")
        if isinstance(build_path, str):
            build_path = Path(build_path).resolve()
        self._build_path = build_path

        cache = self.build_path / "CMakeCache.txt"

        if source_path is None and cache.exists():
            source_path = self._cache_lookup("CMAKE_HOME_DIRECTORY", cache)
        if isinstance(source_path, str):
            source_path = Path(source_path).resolve()
        self._source_path = source_path.resolve() if source_path else None

        self._api_version = api_version if api_version is not None else self.most_recent_api_version()

        if cmake is None and cache.exists():
            cmake = self._cache_lookup("CMAKE_COMMAND", cache)

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

    @staticmethod
    def _cache_lookup(name: str, cache: PathLike) -> str:
        # Cache entries are formatted like:
        # <variable>:<type>=<value>
        with open(cache) as f:
            line = next(
                line
                for line in f.read().splitlines()
                if line.startswith(name + ":")
            )
        _, value = line.split("=", 1)
        return value

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
        else:
            args.append(".")
        subprocess.check_call(args, cwd=str(self._build_path), stdout=stdout)

    @property
    def cmake_file_api(self):
        return REPLY_API[self._api_version](self._build_path)
