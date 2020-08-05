import collections
import textwrap

import pytest

from cmake_file_api.cmake import CMakeProject
from cmake_file_api.kinds.kind import ObjectKind
from cmake_file_api.kinds.codemodel.api import CODEMODEL_API


@pytest.fixture
def build_tree(tmp_path_factory):
    SrcBuild = collections.namedtuple("SrcBuild", ("source", "build"))
    src = tmp_path_factory.getbasetemp()
    build = tmp_path_factory.mktemp("build")
    return SrcBuild(src, build)


def test_codemodelV2(build_tree, capsys):
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
    project = CMakeProject(build_tree.source, build_tree.build, api_version=1)
    object_kind = ObjectKind.CODEMODEL
    kind_version = 2
    project.cmake_file_api.instrument(object_kind, kind_version)
    project.reconfigure(quiet=True)
    data = project.cmake_file_api.inspect(object_kind, kind_version)
    assert data is not None
    assert isinstance(data, CODEMODEL_API[kind_version])


def test_complete_project(build_tree, capsys):
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
    project = CMakeProject(build_tree.source, build_tree.build, api_version=1)
    project.cmake_file_api.instrument_all()
    project.reconfigure(quiet=True)
    data = project.cmake_file_api.inspect_all()
    assert data is not None
