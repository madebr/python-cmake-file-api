import pathlib
import textwrap

import pytest

from cmake_file_api.cmake import CMakeProject
from cmake_file_api.kinds.ctestInfo.v1 import CTestInfoV1, CTestTest
from cmake_file_api.kinds.common import VersionMajorMinor
from cmake_file_api.kinds.common.backtraceGraph import BacktraceNode


@pytest.fixture
def simple_cxx_project_with_tests(build_tree):
    (build_tree.source / "CMakeLists.txt").write_text(textwrap.dedent(r"""
        cmake_minimum_required(VERSION 3.5)
        project(demoproject CXX)
        enable_testing()
        add_executable(demo_sqrtf main.cpp)
        add_test(NAME Test_needs_arg COMMAND demo_sqrtf)
        set_property(TEST Test_needs_arg PROPERTY WILL_FAIL 1)
        add_test(NAME Test_runs COMMAND demo_sqrtf 4)
        function(add_new_test name argToMagic logExpected)
            add_test(NAME ${name} COMMAND demo_sqrtf ${argToMagic})
            set_property(TEST "${name}" PROPERTY PASS_REGULAR_EXPRESSION "${logExpected}")
        endfunction()
        add_new_test(Test_9_3 "9" "sqrt\\(9\\) = 3\n")
        add_new_test(Test_25_5 "25" "sqrt\\(25\\) = 5\n")
        """))
    (build_tree.source / "main.cpp").write_text(textwrap.dedent(r"""\
        #include <cmath>
        #include <iostream>
        #include <string>
        int main(int argc, char *argv[]) {
            if (argc < 2) {
                std::cout << "Usage: " << argv[0] << " number\n";
                return 1;
            }
            int inputValue = std::stoi(argv[1]);
            std::cout << "sqrt(" << argv[1] << ") = " << (int)std::round(std::sqrt((float)inputValue)) << "\n";
            return 0;
        }"""))
    return build_tree


def test_ctest_info_v1(simple_cxx_project_with_tests, capsys):
    project = CMakeProject(simple_cxx_project_with_tests.build,
                           simple_cxx_project_with_tests.source, api_version=1)
    project.cmake_file_api.instrument_all()
    project.reconfigure(quiet=True)

    kind_obj = project._query_tests(configuration="Release")
    assert isinstance(kind_obj, CTestInfoV1)
    assert isinstance(kind_obj.version, VersionMajorMinor)
    assert kind_obj.version.major == 1
    assert isinstance(kind_obj.tests, list)
    for test in kind_obj.tests:
        assert isinstance(test, CTestTest)
        assert isinstance(test.properties, dict)
        assert isinstance(test.backtrace, BacktraceNode)


def test_ctestinfo_v1(build_tree):
    kind_obj = CTestInfoV1.from_text(pathlib.Path("tests/resources/output-ctestInfo-v1.json").read_text(), build_tree.build)

    assert isinstance(kind_obj, CTestInfoV1)
    assert isinstance(kind_obj.version, VersionMajorMinor)
    assert kind_obj.version.major == 1
    assert len(kind_obj.tests) == 3
    assert kind_obj.tests[0].name == "Test_runs"
    assert len(kind_obj.tests[0].properties) == 1
    assert kind_obj.tests[0].command == [
        "/Foobar/build0/MagicMath",
        "4"
    ]
    assert kind_obj.tests[1].name == "Test_9_3"
    assert len(kind_obj.tests[1].properties) == 2
    assert kind_obj.tests[1].command == [
        "/Foobar/build0/MagicMath",
        "9"
    ]
    assert kind_obj.tests[2].name == "Test_25_5"
    assert len(kind_obj.tests[2].properties) == 2
    assert kind_obj.tests[2].command == [
        "/Foobar/build0/MagicMath",
        "25"
    ]
