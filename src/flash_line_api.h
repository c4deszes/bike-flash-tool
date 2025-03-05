#if !defined(FLASH_LINE_API_H_)
#define FLASH_LINE_API_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdint.h>

#define FLASH_LINE_BOOT_ENTRY_SUCCESS 0x00
#define FLASH_LINE_BOOT_ENTRY_FAILURE 0x01
#define FLASH_LINE_BOOT_ENTRY_NO_BL_PRESENT 0x02
#define FLASH_LINE_BOOT_ENTRY_OP_UNSAFE 0x03

#define FLASH_LINE_PAGE_WRITE_SUCCESS 0x00
#define FLASH_LINE_PAGE_WRITE_FAILURE 0x01
#define FLASH_LINE_PAGE_NOT_WRITTEN 0x02
#define FLASH_LINE_PAGE_ADDRESS_ERROR 0x03

typedef struct {
    // TODO: decide what's in the signature
    char mcu_identifier[20];
    uint16_t mcu_revision;
} fl_BootSignature_t;

/**
 * @brief Called when boot entry is requested, the return code then determines whether the
 * peripheral will be following the instruction, or the error reason why it cannot enter that mode
 * 
 * @return uint8_t 
 */
uint8_t FLASH_BL_EnterBoot(void);

/**
 * @brief Called when the signature is requested
 * 
 * @return fl_BootSignature_t* 
 */
fl_BootSignature_t* FLASH_BL_ReadSignature(void);

/**
 * @brief Called when a page write is requested
 * 
 * @param address Start address of the page
 * @param size Size of the data to be written
 * @param data Page content
 */
void FLASH_BL_OnPageWrite(uint32_t address, uint8_t size, uint8_t* data);

/**
 * @brief Called when the write status is requested
 * 
 * @return uint8_t Last page write status
 */
uint8_t FLASH_BL_GetWriteStatus(void);

/**
 * @brief Called when the bootloader mode is requested to be exited
 */
void FLASH_BL_ExitBoot(void);

#ifdef __cplusplus
}
#endif

#endif // FLASH_LINE_API_H_
