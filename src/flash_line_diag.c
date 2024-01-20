#include "flash_line_diag.h"

#include "flash_line_api.h"
#include "line_diagnostics.h"

#include <stdlib.h>

static bool _FLASH_LINE_EnterBoot_Handler(uint16_t request, uint8_t* size, uint8_t* payload) {
    uint8_t entryStatus = FLASH_BL_EnterBoot();

    if (entryStatus == FLASH_LINE_BOOT_ENTRY_SUCCESS) {
        *size = sizeof(uint32_t);
        uint32_t serial = LINE_Diag_GetSerialNumber();
        payload[0] = (uint8_t)(serial & 0xFF);
        payload[1] = (uint8_t)((serial >> 8) & 0xFF);
        payload[2] = (uint8_t)((serial >> 16) & 0xFF);
        payload[3] = (uint8_t)((serial >> 24) & 0xFF);
        return true;
    }
    else {
        *size = sizeof(uint8_t);
        payload[0] = entryStatus;
        return true;
    }
}

static bool _FLASH_LINE_ReadSignature_Handler(uint16_t request, uint8_t* size, uint8_t* payload) {
    fl_BootSignature_t* signature = FLASH_BL_ReadSignature();

    if (signature == NULL) {
        return false;
    }

    // TODO: prepare response
    *size = 1;
    payload[0] = 0;

    return true;
}

static void _FLASH_LINE_OnPageWriteHandler(uint16_t request, uint8_t size, uint8_t* payload) {
    // TODO: validate size, etc.
    uint32_t address = payload[0] | (((uint32_t)payload[1]) << 8) | (((uint32_t)payload[2]) << 16) | (((uint32_t)payload[3]) << 24);
    FLASH_BL_OnPageWrite(address, size - 4, payload + sizeof(uint32_t));
}

static bool _FLASH_LINE_GetWriteStatusHandler(uint16_t request, uint8_t* size, uint8_t* payload) {
    uint8_t status = FLASH_BL_GetWriteStatus();

    *size = sizeof(uint8_t);
    payload[0] = status;

    return true;
}

static void _FLASH_LINE_ExitBootloaderHandler(uint16_t request, uint8_t size, uint8_t* payload) {
    FLASH_BL_ExitBoot();
}

void FLASH_LINE_Init(uint8_t mode) {
    if (mode == FLASH_LINE_APPLICATION_MODE) {
        LINE_Diag_RegisterUnicastPublisher(FLASH_LINE_DIAG_BOOT_ENTRY, _FLASH_LINE_EnterBoot_Handler);
    }
    else if (mode == FLASH_LINE_BOOTLOADER_MODE) {
        LINE_Diag_RegisterUnicastPublisher(FLASH_LINE_DIAG_READ_SIGNATURE, _FLASH_LINE_ReadSignature_Handler);
        LINE_Diag_RegisterUnicastListener(FLASH_LINE_DIAG_APP_WRITE_PAGE, _FLASH_LINE_OnPageWriteHandler);
        LINE_Diag_RegisterUnicastPublisher(FLASH_LINE_DIAG_APP_WRITE_STATUS, _FLASH_LINE_GetWriteStatusHandler);
        LINE_Diag_RegisterUnicastListener(FLASH_LINE_DIAG_EXIT_BOOTLOADER, _FLASH_LINE_ExitBootloaderHandler);
    }
}

static uint8_t _FLASH_BL_EnterBoot_Default() {
    return FLASH_LINE_BOOT_ENTRY_FAILURE;
}
uint8_t FLASH_BL_EnterBoot(void) __attribute__((weak,alias("_FLASH_BL_EnterBoot_Default")));

fl_BootSignature_t* _FLASH_BL_ReadSignature_Default(void) {
    return NULL;
}
fl_BootSignature_t* FLASH_BL_ReadSignature(void) __attribute__((weak,alias("_FLASH_BL_ReadSignature_Default")));

void _FLASH_BL_OnPageWrite_Default(uint32_t address, uint8_t size, uint8_t* data) {

}
void FLASH_BL_OnPageWrite(uint32_t address, uint8_t size, uint8_t* data) __attribute__((weak,alias("_FLASH_BL_OnPageWrite_Default")));

uint8_t _FLASH_BL_GetWriteStatus_Default(void) {
    return FLASH_LINE_PAGE_WRITE_FAILURE;
}
uint8_t FLASH_BL_GetWriteStatus(void) __attribute__((weak,alias("_FLASH_BL_GetWriteStatus_Default")));

void FLASH_BL_ExitBoot_default(void) {

}
void FLASH_BL_ExitBoot(void) __attribute__((weak,alias("FLASH_BL_ExitBoot_default")));
