cmake_minimum_required(VERSION 3.20)
project(
    line-flash-adapter
    VERSION "0.1.0"
    LANGUAGES C CXX)

option(FLASH_LINE_BUILD_TESTS "Enables library test cases" OFF)

# TODO: how does CPM work when it's included multiple times?
include(tools/cmake/CPM.cmake)
CPMAddPackage("gh:c4deszes/bike-line-protocol#master")

add_library(flash-line-api INTERFACE)
target_include_directories(flash-line-api INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
# TODO: do we leave this here?
target_link_libraries(flash-line-api INTERFACE line-protocol-api)

add_library(flash-line-sources INTERFACE)
target_sources(flash-line-sources INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/flash_line_diag.c
)

if(FLASH_LINE_BUILD_TESTS)
    enable_testing()
    include(FetchContent)
    include(GoogleTest)

    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG        release-1.12.0
    )
    FetchContent_Declare(
        fff
        GIT_REPOSITORY https://github.com/meekrosoft/fff.git
        GIT_TAG        5111c61e1ef7848e3afd3550044a8cf4405f4199
    )

    FetchContent_MakeAvailable(googletest fff)
    add_subdirectory(tests)

    add_custom_target(
        coverage
        COMMAND ${Python_EXECUTABLE} -m gcovr --html-self-contained --html-details ${CMAKE_BINARY_DIR}/coverage.html
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )

    add_custom_target(
        docs
        COMMAND ${Python_EXECUTABLE} -m sphinx -b html -E ${CMAKE_CURRENT_SOURCE_DIR}/docs ${CMAKE_CURRENT_SOURCE_DIR}/docs/_build
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )
endif()
