import json
from pathlib import Path
from typing import Any, Optional

from cmake_file_api.kinds.common import CMakeSourceBuildPaths, VersionMajorMinor
from cmake_file_api.kinds.kind import ObjectKind
from .target.v2 import CodemodelTargetV2


class CMakeProject:
    __slots__ = ("name", "parentProject", "childProjects", "directories", "targets")

    def __init__(self, name: str):
        self.name = name
        self.parentProject: Optional[CMakeProject] = None
        self.childProjects: list[CMakeProject] = []
        self.directories: list[CMakeDirectory] = []
        self.targets: list[CMakeTarget] = []

    @classmethod
    def from_dict(cls, dikt: dict[str, str]) -> "CMakeProject":
        name = dikt["name"]
        return cls(name)

    def update_from_dict(self, dikt: dict[str, Any], configuration: "CMakeConfiguration") -> None:
        if "parentIndex" in dikt:
            self.parentProject = configuration.projects[dikt["parentIndex"]]
        self.childProjects = list(configuration.projects[ti] for ti in dikt.get("childIndexes", ()))
        self.directories = list(configuration.directories[di] for di in dikt["directoryIndexes"])
        self.targets = list(configuration.targets[ti] for ti in dikt.get("targetIndexes", ()))

    def __repr__(self) -> str:
        return "{}(name='{}', parentProject={}, #childProjects={}, #directories={}, #targets={})".format(
            type(self).__name__,
            self.name,
            repr(self.parentProject.name) if self.parentProject else None,
            len(self.childProjects),
            len(self.directories),
            len(self.targets),
        )


class CMakeDirectory:
    __slots__ = ("source", "build", "parentDirectory", "childDirectories", "project", "targets", "minimumCMakeVersion", "hasInstallRule")

    def __init__(self, source: Path, build: Path, minimumCMakeVersion: Optional[str], hasInstallRule: bool):
        self.source = source
        self.build = build
        self.parentDirectory: Optional[CMakeDirectory] = None
        self.childDirectories: list[CMakeDirectory] = []
        self.project: Optional[CMakeProject] = None
        self.targets: list[CMakeTarget] = []
        self.minimumCMakeVersion = minimumCMakeVersion
        self.hasInstallRule = hasInstallRule

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "CMakeDirectory":
        source = Path(dikt["source"])
        build = Path(dikt["build"])
        minimumCMakeVersion = dikt.get("minimumCMakeVersion", None)
        hasInstallRule = dikt.get("hasInstallRule", False)
        return cls(source, build, minimumCMakeVersion, hasInstallRule)

    def update_from_dict(self, dikt: dict[str, Any], configuration: "CMakeConfiguration") -> None:
        if "parentIndex" in dikt:
            self.parentDirectory = configuration.directories[dikt["parentIndex"]]
        self.childDirectories = list(configuration.directories[di] for di in dikt.get("childIndexes", ()))
        self.project = configuration.projects[dikt["projectIndex"]]
        self.targets = list(configuration.targets[ti] for ti in dikt.get("targetIndexes", ()))

    def __repr__(self) -> str:
        return "{}(source='{}', build='{}', parentDirectory={}, #childDirectories={}, project={}, #targets={}, minimumCMakeVersion={}, hasInstallRule={})".format(
            type(self).__name__,
            self.source,
            self.build,
            f'{self.parentDirectory}' if self.parentDirectory else None,
            len(self.childDirectories),
            self.project.name if self.project else "",
            len(self.targets),
            self.minimumCMakeVersion,
            self.hasInstallRule,
        )


class CMakeTarget:
    __slots__ = ("name", "directory", "project", "jsonFile", "target")

    def __init__(self, name: str, directory: CMakeDirectory, project: CMakeProject, jsonFile: Path, target: CodemodelTargetV2):
        self.name = name
        self.directory = directory
        self.project = project
        self.jsonFile = jsonFile
        self.target = target

    def update_dependencies(self, lut_id_target: dict[str, "CMakeTarget"]) -> None:
        lut = {k: v.target for k, v in lut_id_target.items()}
        self.target.update_dependencies(lut)

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], directories: list[CMakeDirectory], projects: list[CMakeProject], reply_path: Path) -> "CMakeTarget":
        name = dikt["name"]
        directory = directories[dikt["directoryIndex"]]
        project = projects[dikt["projectIndex"]]
        jsonFile = reply_path / dikt["jsonFile"]
        target = CodemodelTargetV2.from_path(jsonFile, reply_path)
        return cls(name, directory, project, jsonFile, target)

    def __repr__(self) -> str:
        return "{}(name='{}', directory={}, project={}, jsonFile='{}', target={})".format(
            type(self).__name__,
            self.name,
            repr(self.directory),
            repr(self.project),
            self.jsonFile,
            self.target,
        )


class CMakeConfiguration:
    __slots__ = ("name", "directories", "projects", "targets")

    def __init__(self, name: str, directories: list[CMakeDirectory], projects: list[CMakeProject], targets: list[CMakeTarget]):
        self.name = name
        self.directories = directories
        self.projects = projects
        self.targets = targets

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], reply_path: Path) -> "CMakeConfiguration":
        name = dikt["name"]
        directories = list(CMakeDirectory.from_dict(d) for d in dikt["directories"])
        projects = list(CMakeProject.from_dict(d) for d in dikt["projects"])
        targets = list(CMakeTarget.from_dict(td, directories, projects, reply_path) for td in dikt["targets"])
        lut_id_target = {target.target.id: target for target in targets}
        for target in targets:
            target.update_dependencies(lut_id_target)

        obj = cls(name, directories, projects, targets)
        for d, project in zip(dikt["projects"], projects):
            project.update_from_dict(d, obj)
        for d, directory in zip(dikt["directories"], directories):
            directory.update_from_dict(d, obj)

        return obj

    def __repr__(self) -> str:
        return "{}(name='{}', #directories={}, #projects={}, #targets={})".format(
            type(self).__name__,
            self.name,
            len(self.directories),
            len(self.projects),
            len(self.targets),
        )


class CodemodelV2:
    KIND = ObjectKind.CODEMODEL

    __slots__ = ("version", "paths", "configurations")

    def __init__(self, version: VersionMajorMinor, paths: CMakeSourceBuildPaths, configurations: list[CMakeConfiguration]):
        self.version = version
        self.paths = paths
        self.configurations = configurations

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], reply_path: Path) -> "CodemodelV2":
        if dikt["kind"] != cls.KIND.value:
            raise ValueError
        paths = CMakeSourceBuildPaths.from_dict(dikt["paths"])
        version = VersionMajorMinor.from_dict(dikt["version"])
        configurations = [CMakeConfiguration.from_dict(c_dikt, reply_path) for c_dikt in dikt["configurations"]]
        return cls(version, paths, configurations)

    @classmethod
    def from_path(cls, path: Path, reply_path: Path) -> "CodemodelV2":
        dikt = json.load(path.open())
        return cls.from_dict(dikt, reply_path)

    def get_configuration(self, name: str) -> CMakeConfiguration:
        try:
            return next(c for c in self.configurations if c.name == name)
        except StopIteration:
            raise KeyError("Unknown configuration")

    def __repr__(self) -> str:
        return "{}(version={}, paths={}, configurations={})".format(
            type(self).__name__,
            self.version,
            self.paths,
            self.configurations,
        )
