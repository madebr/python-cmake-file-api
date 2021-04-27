import collections
import functools
import re
import subprocess
import textwrap

import pytest

from cmake_file_api.cmake import CMakeProject
from cmake_file_api.kinds.kind import ObjectKind
from cmake_file_api.kinds.codemodel.api import CODEMODEL_API


@functools.cache
def cmake_version():
    cmake_version_raw = subprocess.check_output(["cmake", "--version"], text=True)
    cmake_version_match = next(re.finditer(r"cmake version ((?:[0-9.]+.)[0-9.]+)", cmake_version_raw, flags=re.I))
    version_list = cmake_version_match.group(1).split(".")
    version_tuple = tuple(int(v) for v in version_list)
    return version_tuple

CMAKE_SUPPORTS_TOOLCHAINS_V1 = cmake_version() >= (3, 20)

@pytest.fixture
def build_tree(tmp_path_factory):
    SrcBuild = collections.namedtuple("SrcBuild", ("source", "build"))
    src = tmp_path_factory.getbasetemp()
    build = tmp_path_factory.mktemp("build")
    return SrcBuild(src, build)


@pytest.fixture
def simple_cxx_project(build_tree):
    (build_tree.source / "CMakeLists.txt").write_text(textwrap.dedent("""\
        cmake_minimum_required(VERSION 3.0)
        project(demoproject)
        add_library(alib alib.cpp)
        """))
    (build_tree.source / "alib.cpp").write_text(textwrap.dedent(r"""\
        #include <iostream>
        #include <string>
        void print_something(const std::string &s) {
            std::cout << "A string:" << s << "\n";
        }"""))
    return build_tree


@pytest.fixture
def complex_cxx_project(build_tree):
    (build_tree.source / "CMakeLists.txt").write_text(textwrap.dedent("""\
        cmake_minimum_required(VERSION 3.0)
        project(demoproject)
        add_library(lib_noinstall lib1.cpp)
        add_library(lib_install lib1.cpp)
        install(TARGETS lib_install)
        add_library(libdep_noinstall lib2.cpp)
        add_library(libdep_install lib2.cpp)
        install(TARGETS libdep_install)
        add_executable(exe_noinstall exe1.cpp)
        add_executable(exe_install exe1.cpp)
        install(TARGETS exe_install)
        add_executable(exedep_noinstall exe2.cpp)
        target_link_libraries(exedep_noinstall lib_noinstall)
        add_executable(exedep_install exe2.cpp)
        target_link_libraries(exedep_install lib_install)
        install(TARGETS exedep_install)
        add_executable(exedep2_noinstall exe3.cpp)
        target_link_libraries(exedep2_noinstall libdep_noinstall)
        add_executable(exedep2_install exe3.cpp)
        target_link_libraries(exedep2_install libdep_install)
        install(TARGETS exedep2_install)
        """))
    (build_tree.source / "lib1.cpp").write_text(textwrap.dedent(r"""\
        #include <iostream>
        #include <string>
        void print_something(const std::string &s) {
            std::cout << "A string:" << s << "\n";
        }"""))
    (build_tree.source / "lib2.cpp").write_text(textwrap.dedent(r"""\
        #include <iostream>
        #include <string>
        void print_something(const std::string &s);
        void print_extra(const std::string &s) {
            print_something(s + " " + s);
        }"""))
    (build_tree.source / "exe1.cpp").write_text(textwrap.dedent(r"""\
        #include <iostream>
        int main() {
            std::cout << "Hello world\n";
            return 0;
        }"""))
    (build_tree.source / "exe2.cpp").write_text(textwrap.dedent(r"""\
        #include <string>
        void print_something(const std::string &s);
        int main() {
            print_something("Hello from main");
            return 0;
        }"""))
    (build_tree.source / "exe3.cpp").write_text(textwrap.dedent(r"""\
        #include <string>
        void print_extra(const std::string &s);
        int main() {
            print_extra("Hello from main!");
            return 0;
        }"""))
    return build_tree


def test_codemodelV2(simple_cxx_project, capsys):
    project = CMakeProject(simple_cxx_project.build, simple_cxx_project.source, api_version=1)
    object_kind = ObjectKind.CODEMODEL
    kind_version = 2
    project.cmake_file_api.instrument(object_kind, kind_version)
    project.reconfigure(quiet=True)
    data = project.cmake_file_api.inspect(object_kind, kind_version)
    assert data is not None
    assert isinstance(data, CODEMODEL_API[kind_version])


def test_complete_project(complex_cxx_project, capsys):
    project = CMakeProject(complex_cxx_project.build, complex_cxx_project.source, api_version=1)
    project.cmake_file_api.instrument_all()
    project.reconfigure(quiet=True)
    data = project.cmake_file_api.inspect_all()
    assert data is not None


@pytest.mark.skipif(not CMAKE_SUPPORTS_TOOLCHAINS_V1, reason="CMake does not support toolchains V1 kind")
def test_toolchain_kind_cxx(complex_cxx_project, capsys):
    project = CMakeProject(complex_cxx_project.build, complex_cxx_project.source, api_version=1)
    project.cmake_file_api.instrument(ObjectKind.TOOLCHAINS, 1)
    project.reconfigure(quiet=True)
    kind_obj = project.cmake_file_api.inspect(ObjectKind.TOOLCHAINS, 1)

    from cmake_file_api.kinds.toolchains.v1 import ToolchainsV1
    from cmake_file_api.kinds.common import VersionMajorMinor

    assert isinstance(kind_obj, ToolchainsV1)
    assert isinstance(kind_obj.version, VersionMajorMinor)
    assert kind_obj.version.major == 1
    assert "CXX" in tuple(toolchain.language for toolchain in kind_obj.toolchains)
