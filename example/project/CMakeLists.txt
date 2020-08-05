cmake_minimum_required(VERSION 3.14)
# The file-based api of cmake required CMake 3.14+
project(test_project)

include(GNUInstallDirs)

add_subdirectory(base)
add_subdirectory(dep)
add_subdirectory(exe)

install(TARGETS base dep exe EXPORT Example
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
)
install(EXPORT Example
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}"
    FILE ExampleTargets.cmake
    NAMESPACE "TestProject::"
)
