add_executable(exe exe.cpp)
target_link_libraries(exe PRIVATE dep)

add_test(NAME exe_noargs COMMAND exe)
add_test(NAME exe_1arg COMMAND exe arg1)
add_test(NAME exe_2args COMMAND exe arg1 arg2)

set_tests_properties(exe_noargs exe_1arg exe_2args PROPERTIES
    TIMEOUT 2
    ENVIRONMENT "FOO=BAR;CAFEBABE=DEADBABE"
)
set_tests_properties(exe_2args PROPERTIES
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
)
