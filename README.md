# Flash tool

Project adds flashing support over LINE protocol by extending the diagnostic interface.

## Quick reference

The project can be integrated via CPM.cmake, the two interface targets shown below encapsulate
everything the library needs to work.

```cmake
CPMAddPackage("gh:c4deszes/bike-flash-tool#master")

add_executable(MyProgram
    src/main.c
)
target_link_libraries(MyProgram PRIVATE flash-line-api flash-line-sources)
```

To allow flashing services on the application side they have to be initialized and the boot entry
function has to be implemented. This function must decide whether to accept or reject the boot entry.

The application can enter the bootloader by any means, the time duration shall be less than 1 second.

```c
#include "flash_line_api.h"
#include "flash_line_diag.h"

void APP_Init() {
    LINE_AppInit();
    FLASH_LINE_Init(LINE_DIAG_Peripheral_CHANNEL, FLASH_LINE_APPLICATION_MODE);
}

fl_BootEntryResponse_t FLASH_BL_EnterBoot(void) {
    fl_BootEntryResponse_t response;
    APP_ScheduleBootEntry();

    response.serial_number = 0x12345678;
    response.entry_status = LINE_FLASH_BOOT_ENTRY_SUCCESS;
    return response;
}
```

On the bootloader side there are two callbacks that have to be implemented, the functions for
writing a page and the one returning the write status, these may form an asynchronuous process.

The page write function takes an address, the data and length of data, these can be passed to the
function actually doing the write. The data is referenced from the transport layer, if the write
is delayed then this function MUST copy the data into it's own buffer.

The write status function returns the status of the last page write operation. The master will after
each page write poll the status, after an error it may retry or if the device returned "not written"
it may wait before continuing.

The master has no assumptions of the device's internal memory structure or what data is already in
there. It's up to the device to do proper erasure and possibly buffer then rewrite it's existing data.
For example with a write starting at an offset address and ending before the page end the device
may need to cache the whole sector, clear it then write back everything including the new data.

```c
#include "flash_line_api.h"
#include "flash_line_diag.h"

void BL_Init() {
    LINE_AppInit();
    FLASH_LINE_Init(LINE_DIAG_RotorSensor_CHANNEL, FLASH_LINE_BOOTLOADER_MODE);
}

void FLASH_BL_OnPageWrite(uint32_t address, uint8_t* data, uint8_t size) {
    write_status = NVM_Write(address, data, size);
}

uint8_t FLASH_BL_GetWriteStatus(void) {
    return write_status;
}
```

> Both bootloader and application shall support conditional change address, the flash tool also
> expects the serial numbers in both modes to match
