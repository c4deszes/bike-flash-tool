# Flash tool

Project adds flashing support over LINE protocol by extending the diagnostic interface.

## Quick reference

The project can be integrated via CPM.cmake, the two interface targets shown below encapsulate
everything the library needs to work

```cmake
CPMAddPackage("gh:c4deszes/bike-flash-tool#master")

add_executable(MyProgram
    src/main.c
)
target_link_libraries(MyProgram PRIVATE flash-line-api flash-line-sources)
```

To allow flashing services on the application side they have to be initialized and the boot entry
function has to be implemented.

```c
#include "flash_line_api.h"
#include "flash_line_diag.h"

void APP_Init() {
    LINE_Transport_Init(true);
    LINE_AppInit();
    LINE_Diag_SetAddress(0x6);
    FLASH_LINE_Init(FLASH_LINE_APPLICATION_MODE);
}

uint8_t FLASH_BL_EnterBoot(void) {
    APP_ScheduleBootEntry();
    return FLASH_LINE_BOOT_ENTRY_SUCCESS;
}
```

On the bootloader side there are a few more callbacks that have to be implemented.

```c
#include "flash_line_api.h"
#include "flash_line_diag.h"

void BL_Init() {
    LINE_Transport_Init(true);
    LINE_AppInit();
    FLASH_LINE_Init(FLASH_LINE_BOOTLOADER_MODE);
}

void FLASH_BL_OnPageWrite(uint32_t address, uint8_t* data) {
    write_status = NVM_Write(address, data);
}

uint8_t FLASH_BL_GetWriteStatus(void) {
    return write_status;
}
```
