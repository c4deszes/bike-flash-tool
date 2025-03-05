#if !defined(FLASH_LINE_DIAG_H_)
#define FLASH_LINE_DIAG_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdint.h>

#define FLASH_LINE_APPLICATION_MODE 0x00
#define FLASH_LINE_BOOTLOADER_MODE 0x01

#define FLASH_LINE_DIAG_BOOT_ENTRY 0x0E40
#define FLASH_LINE_DIAG_READ_SIGNATURE 0x0E60
#define FLASH_LINE_DIAG_APP_WRITE_PAGE 0x0E80
#define FLASH_LINE_DIAG_APP_WRITE_STATUS 0x0EA0
#define FLASH_LINE_DIAG_EXIT_BOOTLOADER 0x0EF0

/**
 * @brief Registers the diagnostic services for the given mode
 * 
 * In application mode, only the boot entry request is handled.
 * 
 * In bootloader mode, read and write operations are registered as well.
 */
void FLASH_LINE_Init(uint8_t diag_channel, uint8_t mode);

#ifdef __cplusplus
}
#endif

#endif // FLASH_LINE_DIAG_H_
