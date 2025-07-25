cmake_minimum_required(VERSION 3.20)

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/library.properties" LIBRARY_PROPERTIES_CONTENT)
string(REGEX MATCH "version=([^\n\r]+)" _ ${LIBRARY_PROPERTIES_CONTENT})
set(LIBRARY_VERSION "${CMAKE_MATCH_1}")

project(
    line-flash-adapter
    VERSION ${LIBRARY_VERSION}
    LANGUAGES C CXX)

################################################################################
# Options
################################################################################
option(FLASH_LINE_BUILD_TESTS "Enables library test cases" OFF)
option(FLASH_LINE_BUILD_DOCS "Enables library documentation" OFF)

################################################################################
# Dependencies
################################################################################
include(tools/cmake/CPM.cmake)
CPMAddPackage("gh:c4deszes/bike-line-protocol@0.3.0")

################################################################################
# Source code
################################################################################
add_library(flash-line-api INTERFACE)
target_include_directories(flash-line-api INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_link_libraries(flash-line-api INTERFACE line-protocol-api)

add_library(flash-line-sources INTERFACE)
target_sources(flash-line-sources INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/flash_line_diag.c
)

################################################################################
# Testing
################################################################################
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
endif()

################################################################################
# Documentation
################################################################################
if(FLASH_LINE_BUILD_DOCS)
    add_subdirectory(docs)
endif()
