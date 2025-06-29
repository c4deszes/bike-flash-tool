function(add_test TARGET)
    target_compile_options(${TARGET} PRIVATE $<$<COMPILE_LANGUAGE:C>:--coverage>)
    target_link_libraries(${TARGET} PRIVATE gtest fff gcov)
    gtest_discover_tests(${TARGET} DISCOVERY_MODE POST_BUILD)
endfunction()

add_custom_target(
    coverage
    COMMAND ${Python_EXECUTABLE} -m gcovr --html-self-contained --html-details ${CMAKE_BINARY_DIR}/coverage.html
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

## Application mode tests
add_executable(test_FlashLine_App EXCLUDE_FROM_ALL)
target_sources(test_FlashLine_App PRIVATE
    test_FlashLine_App.cpp
)
target_link_libraries(test_FlashLine_App PRIVATE
    flash-line-api flash-line-sources
    line-protocol-api line-protocol-sources
)
add_test(test_FlashLine_App)

## Bootloader mode tests
add_executable(test_FlashLine_Bootloader EXCLUDE_FROM_ALL)
target_sources(test_FlashLine_Bootloader PRIVATE
    test_FlashLine_Bootloader.cpp
)
target_link_libraries(test_FlashLine_Bootloader PRIVATE
    flash-line-api flash-line-sources
    line-protocol-api line-protocol-sources
)
add_test(test_FlashLine_Bootloader)
