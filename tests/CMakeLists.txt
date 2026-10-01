include(FetchContent)
FetchContent_Declare(unity
  GIT_REPOSITORY https://github.com/ThrowTheSwitch/Unity.git
  GIT_TAG        v2.6.0)
FetchContent_MakeAvailable(unity)

add_executable(test_all test_all.c uart_fake.c)
target_link_libraries(test_all PRIVATE app unity)
target_include_directories(test_all PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
add_test(NAME unit COMMAND test_all)
