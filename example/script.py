from pathlib import Path
import shutil

from cmake_file_api import CMakeProject, ObjectKind

script_path = Path(__file__).resolve().parent
source_path = script_path / "project"
build_path = script_path / "build"

try:
    shutil.rmtree(str(build_path))
except FileNotFoundError:
    pass
build_path.mkdir(exist_ok=True)

cmake_project = CMakeProject(build_path, source_path, api_version=1)
cmake_project.cmake_file_api.instrument_all()
cmake_project.configure(quiet=True)

results = cmake_project.cmake_file_api.inspect_all()
print("cmake path:", cmake_project.cmake_file_api.index().cmake.paths.cmake)
print("version:", cmake_project.cmake_file_api.index().cmake.version.string)

codemodel_v2 = results[ObjectKind.CODEMODEL][2]
print("projects:", list(project.name for project in codemodel_v2.configurations[0].projects))
print("targets:", list(target.name for target in codemodel_v2.configurations[0].targets))
print("target dependencies:", {target.name: list(dependency.target.name for dependency in target.target.dependencies) for target in codemodel_v2.configurations[0].targets})


codemodel_v2 = results[ObjectKind.CODEMODEL][2]
