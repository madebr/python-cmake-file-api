add_library(base base.cpp)
target_include_directories(base PUBLIC
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
    "$<INSTALL_INTERFACE:include>"
)

install(FILES "include/base.hpp" DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
