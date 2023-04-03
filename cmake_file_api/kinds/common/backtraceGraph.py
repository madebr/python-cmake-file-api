from pathlib import Path
from typing import Dict, List, Optional


class BacktraceNode(object):
    __slots__ = ("file", "line", "command", "parent")

    def __init__(self, file: Path, line: Optional[int], command: Optional[str]):
        self.file = file
        self.line = line
        self.command = command
        self.parent = None

    @classmethod
    def from_dict(cls, dikt: Dict, commands: List[str], files: List[Path]) -> "BacktraceNode":
        file = files[dikt["file"]]
        line = dikt.get("line")
        command = None
        if "command" in dikt:
            command = commands[dikt["command"]]
        return cls(file, line, command)

    def update_from_dict(self, dikt: Dict, nodes: List["BacktraceNode"]) -> None:
        if "parent" in dikt:
            self.parent = nodes[dikt["parent"]]

    def __repr__(self) -> str:
        return "{}(file='{}', line={}, command={}".format(
            type(self).__name__,
            self.file,
            self.line,
            self.command,
        )


class BacktraceGraph(object):
    __slots__ = ("nodes", )

    def __init__(self, nodes: List[BacktraceNode]):
        self.nodes = nodes

    @classmethod
    def from_dict(cls, dikt: Dict) -> "BacktraceGraph":
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
