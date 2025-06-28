Integration
===========

Application code
----------------

In applications where a bootloader does exist the boot entry command should be supported
at minimum, after initializing the LINE communication stack the Init function of the flashing
interface has to be called.

A function is called whenever the peripheral is requested to enter boot mode, within it the device
can decide whether it's going to, or not.

.. code-block:: c

    void APP_Init() {
        LINE_App_Init();
        LINE_FLASH_Init(DIAG_CHANNEL_NUMBER, LINE_FLASH_APPLICATION_MODE);
    }

    uint8_t FLASH_BL_EnterBoot(void) {
        if (app_movement_detected) {
            return LINE_FLASH_BOOT_ENTRY_OP_UNSAFE;
        }
        APP_ScheduleBootEntry();
        return LINE_FLASH_BOOT_ENTRY_SUCCESS;
    }

Bootloader code
---------------

In bootloader mode the peripheral is expected to accept page writes and then respond with the
status of those writes.

.. code-block:: c

    void BOOT_Init() {
        LINE_App_Init();
        LINE_FLASH_Init(DIAG_CHANNEL_NUMBER, LINE_FLASH_BOOTLOADER_MODE);
    }

    void FLASH_BL_OnPageWrite(uint32_t address, uint8_t* data) {
        NVM_Write(address / 128, data);

        writeStatus = LINE_FLASH_PAGE_WRITE_SUCCESS;
    }

    uint8_t FLASH_BL_GetWriteStatus(void) {
        return writeStatus;
    }

CMake using CPM/subdirectories
------------------------------

The CMake project registers it's headers and source files as interface targets, these should be
linked along with the line-protocol targets.

.. code-block:: cmake

    find_package(Python REQUIRED)

    include(tools/cmake/CPM.cmake)
    CPMAddPackage("gh:c4deszes/bike-flash-tool#master")

    add_executable(MyApp src/main.c)
    target_link_libraries(MyApp PUBLIC ...
                                       flash-line-api flash-line-sources
    )
