import enum
import json
from pathlib import Path
from typing import Any, Optional

from cmake_file_api.kinds.common import CMakeSourceBuildPaths


class TargetType(enum.Enum):
    EXECUTABLE = "EXECUTABLE"
    STATIC = "STATIC_LIBRARY"
    SHARED = "SHARED_LIBRARY"
    MODULE = "MODULE_LIBRARY"
    OBJECT = "OBJECT_LIBRARY"
    INTERFACE_LIBRARY = "INTERFACE_LIBRARY"
    UTILITY = "UTILITY"


class LinkFragmentRole(enum.Enum):
    LINK_FLAGS = "flags"
    LINK_LIBRARIES = "libraries"
    LIBRARY_PATHS = "libraryPath"
    MACOS_FRAMEWORK_PATH = "frameworkPath"


class ArchiveFragmentRole(enum.Enum):
    ARCHIVER_FLAGS = "flags"


class BacktraceNode:
    __slots__ = ("file", "line", "command", "parent")

    def __init__(self, file: Path, line: Optional[int], command: Optional[str]):
        self.file = file
        self.line = line
        self.command = command
        self.parent = None

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], commands: list[str], files: list[Path]) -> "BacktraceNode":
        file = files[dikt["file"]]
        line = dikt.get("line")
        command = None
        if "command" in dikt:
            command = commands[dikt["command"]]
        return cls(file, line, command)

    def update_from_dict(self, dikt: dict[str, Any], nodes: list["BacktraceNode"]) -> None:
        if "parent" in dikt:
            self.parent = nodes[dikt["parent"]]

    def __repr__(self) -> str:
        return "{}(file='{}', line={}, command={}".format(
            type(self).__name__,
            self.file,
            self.line,
            self.command,
        )


class BacktraceGraph:
    __slots__ = ("nodes", )

    def __init__(self, nodes: list[BacktraceNode]):
        self.nodes = nodes

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "BacktraceGraph":
        commands = dikt["commands"]
        files = list(Path(f) for f in dikt["files"])
        nodes = list(BacktraceNode.from_dict(btn, commands, files) for btn in dikt["nodes"])
        for node, dikt_node in zip(nodes, dikt["nodes"]):
            node.update_from_dict(dikt_node, nodes)
        return cls(nodes)

    def __repr__(self) -> str:
        return "{}(nodes={})".format(
            type(self).__name__,
            self.nodes,
        )


class TargetDestination:
    __slots__ = ("path", "backtrace")

    def __init__(self, path: Path, backtrace: BacktraceNode):
        self.path = path
        self.backtrace = backtrace

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], backtraceGraph: BacktraceGraph) -> "TargetDestination":
        path = Path(dikt["path"])
        backtrace = backtraceGraph.nodes[dikt["backtrace"]]
        return cls(path, backtrace)

    def __repr__(self) -> str:
        return "{}(path='{}', backtrace={}".format(
            type(self).__name__,
            self.path,
            self.backtrace,
        )


class TargetInstall:
    __slots__ = ("prefix", "destinations")

    def __init__(self, prefix: Path, destinations: list[TargetDestination]):
        self.prefix = prefix
        self.destinations = destinations

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], backtraceGraph: BacktraceGraph) -> "TargetInstall":
        prefix = Path(dikt["prefix"]["path"])
        destinations = list(TargetDestination.from_dict(td, backtraceGraph) for td in dikt["destinations"])
        return cls(prefix, destinations)

    def __repr__(self) -> str:
        return "{}(prefix='{}', destinations={}".format(
            type(self).__name__,
            self.prefix,
            self.destinations,
        )


class TargetLinkFragment:
    __slots__ = ("fragment", "role")

    def __init__(self, fragment: str, role: LinkFragmentRole):
        self.fragment = fragment
        self.role = role

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "TargetLinkFragment":
        fragment = dikt["fragment"]
        role = LinkFragmentRole(dikt["role"])
        return cls(fragment, role)

    def __repr__(self) -> str:
        return "{}(fragment='{}', role={})".format(
            type(self).__name__,
            self.fragment,
            self.role.name,
        )


class TargetLink:
    __slots__ = ("language", "commandFragments", "lto", "sysroot")

    def __init__(self, language: str, commandFragments: list[TargetLinkFragment], lto: Optional[bool], sysroot: Optional[Path]):
        self.language = language
        self.commandFragments = commandFragments
        self.lto = lto
        self.sysroot = sysroot

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "TargetLink":
        language = dikt["language"]
        commandFragments = []
        if "commandFragments" in dikt:
            commandFragments = list(TargetLinkFragment.from_dict(tlf) for tlf in dikt["commandFragments"])
        lto = dikt.get("lto")
        sysroot = None
        if "sysroot" in dikt:
            sysroot = Path(dikt["sysroot"]["path"])
        return cls(language, commandFragments, lto, sysroot)

    def __repr__(self) -> str:
        return "{}(language='{}', commandFragments={}, lto={}, sysroot={}".format(
            type(self).__name__,
            self.language,
            self.commandFragments,
            self.lto,
            f"'{self.sysroot}'" if self.sysroot else None,
        )


class TargetArchiveFragment:
    __slots__ = ("fragment", "role")

    def __init__(self, fragment: str, role: ArchiveFragmentRole):
        self.fragment = fragment
        self.role = role

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "TargetArchiveFragment":
        fragment = dikt["fragment"]
        role = ArchiveFragmentRole(dikt["role"])
        return cls(fragment, role)

    def __repr__(self) -> str:
        return "{}(fragment='{}', role={})".format(
            type(self).__name__,
            self.fragment,
            self.role.name,
        )


class TargetArchive:
    __slots__ = ("commandFragments", "lto")

    def __init__(self, commandFragments: list[TargetArchiveFragment], lto: Optional[bool]):
        self.commandFragments = commandFragments
        self.lto = lto

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "TargetArchive":
        commandFragments = []
        if "commandFragments" in dikt:
            commandFragments = list(TargetArchiveFragment.from_dict(tlf) for tlf in dikt["commandFragments"])
        lto = dikt.get("lto")
        return cls(commandFragments, lto)

    def __repr__(self) -> str:
        return "{}(commandFragments={}, lto={})".format(
            type(self).__name__,
            self.commandFragments,
            self.lto,
        )


class TargetSourceGroup:
    __slots__ = ("name", "sources")

    def __init__(self, name: str, sources: list["TargetSource"]):
        self.name = name
        self.sources: list[TargetSource] = []

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], target_sources: list["TargetSource"]) -> "TargetSourceGroup":
        name = dikt["name"]
        sources = list(target_sources[tsi] for tsi in dikt["sourceIndexes"])
        return cls(name, sources)

    def __repr__(self) -> str:
        return "{}(name='{}', sources={})".format(
            type(self).__name__, self.name, self.sources,
        )


class TargetCompileFragment:
    __slots__ = ("fragment", )

    def __init__(self, fragment: str):
        self.fragment = fragment

    @classmethod
    def from_dict(cls, dikt: dict[str, Any]) -> "TargetCompileFragment":
        fragment = dikt["fragment"]
        return cls(fragment)

    def __repr__(self) -> str:
        return "{}(fragment={})".format(
            type(self).__name__,
            self.fragment,
        )


class TargetCompileGroupInclude:
    __slots__ = ("path", "isSystem", "backtrace")

    def __init__(self, path: Path, isSystem: Optional[bool], backtrace: Optional[BacktraceNode]):
        self.path = path
        self.isSystem = isSystem
        self.backtrace = backtrace

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], backtraceGraph: BacktraceGraph) -> "TargetCompileGroupInclude":
        path = Path(dikt["path"])
        isSystem = dikt.get("isSystem")
        backtrace = None
        if "backtrace" in dikt:
            backtrace = backtraceGraph.nodes[dikt["backtrace"]]
        return cls(path, isSystem, backtrace)

    def __repr__(self) -> str:
        return "{}(path={}, system={}, backtrace={})".format(
            type(self).__name__,
            f"'{self.path}'" if self.path else None,
            self.isSystem,
            self.backtrace,
        )


class TargetCompileGroupPCH:
    __slots__ = ("header", "backtrace")

    def __init__(self, header: Path, backtrace: Optional[BacktraceNode]):
        self.header = header
        self.backtrace = backtrace

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], backtraceGraph: BacktraceGraph) -> "TargetCompileGroupPCH":
        header = Path(dikt["header"])
        backtrace = None
        if "backtrace" in dikt:
            backtrace = backtraceGraph.nodes[dikt["backtrace"]]
        return cls(header, backtrace)

    def __repr__(self) -> str:
        return "{}(header='{}', backtrace={})".format(
            type(self).__name__,
            self.header,
            self.backtrace,
        )


class TargetCompileGroupDefine:
    __slots__ = ("define", "backtrace")

    def __init__(self, define: str, backtrace: Optional[BacktraceNode]):
        self.define = define
        self.backtrace = backtrace

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], backtraceGraph: BacktraceGraph) -> "TargetCompileGroupDefine":
        define = dikt["define"]
        backtrace = None
        if "backtrace" in dikt:
            backtrace = backtraceGraph.nodes[dikt["backtrace"]]
        return cls(define, backtrace)

    def __repr__(self) -> str:
        return "{}(define='{}', backtrace={})".format(
            type(self).__name__,
            self.define,
            self.backtrace,
        )


class TargetCompileGroup:
    __slots__ = ("sources", "language", "compileCommandFragments", "includes", "precompileHeaders", "defines", "sysroot")

    def __init__(self, sources: list["TargetSource"], language: str,
                 compileCommandFragments: list[TargetCompileFragment], includes: list[TargetCompileGroupInclude],
                 precompileHeaders: list[TargetCompileGroupPCH], defines: list[TargetCompileGroupDefine],
                 sysroot: Optional[Path]):
        self.sources = sources
        self.language = language
        self.compileCommandFragments = compileCommandFragments
        self.includes = includes
        self.precompileHeaders = precompileHeaders
        self.defines = defines
        self.sysroot = sysroot

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], target_sources: list["TargetSource"], backtraceGraph: BacktraceGraph) -> "TargetCompileGroup":
        language = dikt["language"]
        compileCommandFragments = list(TargetCompileFragment.from_dict(tcf) for tcf in dikt.get("compileCommandFragments", ()))
        includes = list(TargetCompileGroupInclude.from_dict(tci, backtraceGraph) for tci in dikt.get("includes", ()))
        precompileHeaders = list(TargetCompileGroupPCH.from_dict(tcpch, backtraceGraph) for tcpch in dikt.get("precompileHeaders", ()))
        defines = list(TargetCompileGroupDefine.from_dict(tcdef, backtraceGraph) for tcdef in dikt.get("defines", ()))
        sysroot = Path(dikt["sysroot"]["path"]) if "sysroot" in dikt and "path" in dikt["sysroot"] else None
        sources = list(target_sources[tsi] for tsi in dikt["sourceIndexes"])
        return cls(sources, language, compileCommandFragments, includes, precompileHeaders, defines, sysroot)

    def __repr__(self) -> str:
        return "{}(sources={}, language='{}', compileCommandFragments={}, #includes={}, #precompileHeaders={}, #defines={}, sysroot={})".format(
            type(self).__name__,
            self.sources,
            self.language,
            self.compileCommandFragments,
            len(self.includes),
            len(self.precompileHeaders),
            len(self.defines),
            f"'{self.sysroot}'" if self.sysroot else None,
        )


class TargetDependency:
    __slots__ = ("id", "target", "backtrace")

    def __init__(self, id: str, backtrace: Optional[BacktraceNode]):
        self.id = id
        self.target: Optional[CodemodelTargetV2] = None
        self.backtrace = backtrace

    def update_dependency(self, lut_id_target: dict[str, "CodemodelTargetV2"]) -> None:
        self.target = lut_id_target[self.id]

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], backtraceGraph: BacktraceGraph) -> "TargetDependency":
        id = dikt["id"]
        backtrace = None
        if "backtrace" in dikt:
            backtrace = backtraceGraph.nodes[dikt["backtrace"]]
        return cls(id, backtrace)

    def __repr__(self) -> str:
        return "{}(id='{}', target='{}', backtrace={})".format(
            type(self).__name__,
            self.id,
            self.target.name if self.target else None,
            self.backtrace,
        )


class TargetSource:
    __slots__ = ("path", "isGenerated", "backtrace", "compileGroup", "sourceGroup")

    def __init__(self, path: Path, isGenerated: Optional[bool], backtrace: Optional[BacktraceNode]):
        self.path = path
        self.isGenerated = isGenerated
        self.backtrace = backtrace
        self.compileGroup: Optional[TargetCompileGroup] = None
        self.sourceGroup: Optional[TargetSourceGroup] = None

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], backtraceGraph: BacktraceGraph) -> "TargetSource":
        path = Path(dikt["path"])
        isGenerated = dikt.get("isGenerated")
        backtrace = None
        if "backtrace" in dikt:
            backtrace = backtraceGraph.nodes[dikt["backtrace"]]
        return cls(path, isGenerated, backtrace)

    def update_from_dict(self, dikt: dict[str, Any], modelTarget: "CodemodelTargetV2") -> None:
        if "compileGroupIndex" in dikt:
            self.compileGroup = modelTarget.compileGroups[dikt["compileGroupIndex"]]
        if "sourceGroupIndex" in dikt:
            self.sourceGroup = modelTarget.sourceGroups[dikt["sourceGroupIndex"]]

    def __repr__(self) -> str:
        return "{}(path='{}', isGenerated={}, backtrace={}, compileGroup={}, sourceGroup={})".format(
            type(self).__name__,
            self.path,
            self.isGenerated,
            self.backtrace,
            self.compileGroup,
            self.sourceGroup,
        )


class CodemodelTargetV2:
    __slots__ = ("name", "id", "type", "backtrace", "folder", "paths", "nameOnDisk", "artifacts",
                 "isGeneratorProvided", "install", "link", "archive", "dependencies", "sources",
                 "sourceGroups", "compileGroups")

    def __init__(self, name: str, id: str, type: TargetType, backtrace: Optional[BacktraceNode], folder: Optional[Path],
                 paths: CMakeSourceBuildPaths, nameOnDisk: str, artifacts: list[Path],
                 isGeneratorProvided: Optional[bool], install: Optional[TargetInstall],
                 link: Optional[TargetLink], archive: Optional[TargetArchive],
                 dependencies: list[TargetDependency], sources: list[TargetSource],
                 sourceGroups: list[TargetSourceGroup], compileGroups: list[TargetCompileGroup]):
        self.name = name
        self.id = id
        self.type = type
        self.backtrace = backtrace
        self.folder = folder
        self.paths = paths
        self.nameOnDisk = nameOnDisk
        self.artifacts = artifacts
        self.isGeneratorProvided = isGeneratorProvided
        self.install = install
        self.link = link
        self.archive = archive
        self.dependencies = dependencies
        self.sources = sources
        self.sourceGroups = sourceGroups
        self.compileGroups = compileGroups

    def update_dependencies(self, lut_id_target: dict[str, "CodemodelTargetV2"]) -> None:
        for dependency in self.dependencies:
            dependency.update_dependency(lut_id_target)

    @classmethod
    def from_dict(cls, dikt: dict[str, Any], reply_path: Path) -> "CodemodelTargetV2":
        name = dikt["name"]
        id = dikt["id"]
        type = TargetType(dikt["type"])
        backtraceGraph = BacktraceGraph.from_dict(dikt["backtraceGraph"])
        backtrace = None
        if "backtrace" in dikt:
            backtrace = backtraceGraph.nodes[dikt["backtrace"]]
        folder = None
        if "folder" in dikt:
            folder = Path(dikt["folder"]["name"])
        paths = CMakeSourceBuildPaths.from_dict(dikt["paths"])
        nameOnDisk = dikt.get("nameOnDisk", "")
        artifacts = list(Path(p["path"]) for p in dikt.get("artifacts", ()))
        isGeneratorProvided = dikt.get("isGeneratorProvided")
        install = None
        if "install" in dikt:
            install = TargetInstall.from_dict(dikt["install"], backtraceGraph)
        link = None
        if "link" in dikt:
            link = TargetLink.from_dict(dikt["link"])
        archive = None
        if "archive" in dikt:
            archive = TargetArchive.from_dict(dikt["archive"])
        dependencies = []
        if "dependencies" in dikt:
            dependencies = list(TargetDependency.from_dict(td, backtraceGraph) for td in dikt["dependencies"])
        sources = list(TargetSource.from_dict(ts, backtraceGraph) for ts in dikt["sources"])
        sourceGroups = list(TargetSourceGroup.from_dict(tsg, sources) for tsg in dikt.get("sourceGroups", ()))
        compileGroups = list(TargetCompileGroup.from_dict(tsg, sources, backtraceGraph) for tsg in dikt.get("compileGroups", ()))

        return cls(name, id, type, backtrace, folder, paths, nameOnDisk, artifacts,
                   isGeneratorProvided, install, link, archive, dependencies, sources, sourceGroups, compileGroups)

    @classmethod
    def from_path(cls, file: Path, reply_path: Path) -> "CodemodelTargetV2":
        dikt = json.load(file.open())
        return cls.from_dict(dikt, reply_path)

    def __repr__(self) -> str:
        return "{}(name='{}', type={}, backtrace={})".format(
            type(self).__name__,
            self.name,
            self.type.name,
            self.backtrace,
        )
