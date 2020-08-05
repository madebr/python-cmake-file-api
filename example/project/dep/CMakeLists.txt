add_library(dep dep.cpp)
target_include_directories(dep PUBLIC
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
    "$<INSTALL_INTERFACE:include>"
)
target_link_libraries(dep PRIVATE base)

install(FILES "include/dep.hpp" DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
