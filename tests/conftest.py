import collections
import pytest


@pytest.fixture
def build_tree(tmp_path_factory):
    SrcBuild = collections.namedtuple("SrcBuild", ("source", "build"))
    src = tmp_path_factory.mktemp("source")
    build = tmp_path_factory.mktemp("build")
    return SrcBuild(src, build)
