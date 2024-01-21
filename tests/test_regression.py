import collections
import functools
import re
import subprocess
import textwrap

import pytest

from cmake_file_api.cmake import CMakeProject
from cmake_file_api.kinds.kind import ObjectKind
from cmake_file_api.kinds.codemodel.api import CODEMODEL_API


@functools.lru_cache(1)  # FIXME: CPython 3.9 provides `functools.cache`
def cmake_version():
    cmake_version_raw = subprocess.check_output(["cmake", "--version"]).decode()
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
        cmake_minimum_required(VERSION 3.0...3.5)
        project(demoproject)
        add_library(alib alib.cpp)
        """))
    (build_tree.source / "alib.cpp").write_text(textwrap.dedent(r"""\
        #include <iostream>
        #include <string>
        void lib1_hello(const std::string &s) {
            std::cout << "A string:" << s << "\n";
        }"""))
    return build_tree


@pytest.fixture
def complex_cxx_project(build_tree):
    (build_tree.source / "CMakeLists.txt").write_text(textwrap.dedent("""\
        if(NOT CMAKE_HOST_SYSTEM_NAME STREQUAL "Darwin")
            set(CMAKE_SYSROOT "/usr/opt/toolchain")
        endif()
        cmake_minimum_required(VERSION 3.0...3.5)
        project(demoproject C)
        enable_language(CXX)

        add_library(lib_interface INTERFACE)
        target_include_directories(lib_interface INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}")
        target_sources(lib_interface
            PUBLIC
                "${CMAKE_CURRENT_SOURCE_DIR}/interface.c"
                "${CMAKE_CURRENT_SOURCE_DIR}/interface.h"
        )
        target_compile_definitions(lib_interface INTERFACE INTERFACE_HELLO)
        source_group("Source files" CMakeLists.txt)
        source_group(lib_interface FILES
            # "${CMAKE_CURRENT_SOURCE_DIR}/interface.c"
            "${CMAKE_CURRENT_SOURCE_DIR}/interface.h"
        )
        set_target_properties(lib_interface PROPERTIES FOLDER "${CMAKE_CURRENT_SOURCE_DIR}")

        add_library(lib1_noinstall lib1.cpp)

        add_library(lib1_install lib1.cpp)
        install(TARGETS lib1_install)

        add_library(lib2_noinstall STATIC lib2.cpp)
        target_link_libraries(lib2_noinstall PRIVATE lib1_noinstall)

        add_library(lib2_install lib2.cpp)
        target_link_libraries(lib2_install PRIVATE lib1_install)
        install(TARGETS lib2_install)

        add_executable(exe1_noinstall exe1.cpp)

        add_executable(exe1_install exe1.cpp)
        install(TARGETS exe1_install)

        add_executable(exe2dep_noinstall exe2.cpp)
        target_link_libraries(exe2dep_noinstall PRIVATE lib1_noinstall)

        add_executable(exe2dep_install exe2.cpp)
        target_link_libraries(exe2dep_install lib1_install)
        install(TARGETS exe2dep_install)

        add_executable(exe3dep_noinstall exe3.cpp)
        target_link_libraries(exe3dep_noinstall PRIVATE lib2_noinstall lib_interface)

        add_executable(exe3dep_install exe3.cpp)
        target_link_libraries(exe3dep_install PRIVATE lib2_install lib_interface)
        install(TARGETS exe3dep_install)
        """))
    (build_tree.source / "interface.h").write_text(textwrap.dedent(r"""\
        #include <stdio.h>
        #ifdef __cplusplus
        extern "C" {
        #endif
        extern void interface_hello(const char *s);
        #ifdef __cplusplus
        }
        #endif
        """))
    (build_tree.source / "interface.c").write_text(textwrap.dedent(r"""\
        #include "interface.h"
        void interface_hello(const char* s) {
            printf("Hello from interface: %s\n", s);
        }
        """))
    (build_tree.source / "lib1.cpp").write_text(textwrap.dedent(r"""\
        #include <iostream>
        #include <string>
        void lib1_hello(const std::string &s) {
            std::cout << "A string:" << s << "\n";
        }
        """))
    (build_tree.source / "lib2.cpp").write_text(textwrap.dedent(r"""\
        #include <iostream>
        #include <string>
        void lib1_hello(const std::string &s);
        void lib2_hello(const std::string &s) {
            lib1_hello(s + " " + s);
        }
        """))
    (build_tree.source / "exe1.cpp").write_text(textwrap.dedent(r"""\
        #include <iostream>
        int main() {
            std::cout << "Hello world\n";
            return 0;
        }
        """))
    (build_tree.source / "exe2.cpp").write_text(textwrap.dedent(r"""\
        #include <string>
        void lib1_hello(const std::string &s);
        int main() {
            lib1_hello("Hello from main");
            return 0;
        }
        """))
    (build_tree.source / "exe3.cpp").write_text(textwrap.dedent(r"""\
        #include <string>
        #include <interface.h>
        void lib2_hello(const std::string &s);
        int main() {
            lib2_hello("Hello from main!");
            interface_hello("main");
            return 0;
        }
        """))
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

    # Check if project also works without specifying the source directory
    project2 = CMakeProject(complex_cxx_project.build, api_version=1)
    project2.cmake_file_api.instrument_all()
    project2.reconfigure(quiet=True)
    data2 = project2.cmake_file_api.inspect_all()
    assert data2 is not None


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
