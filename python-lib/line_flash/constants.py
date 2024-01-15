
FLASH_LINE_DIAG_BOOT_ENTRY = 0x0E40
FLASH_LINE_DIAG_READ_SIGNATURE = 0x0E60
FLASH_LINE_DIAG_APP_WRITE_PAGE = 0x0E80
FLASH_LINE_DIAG_APP_WRITE_STATUS = 0x0EA0
FLASH_LINE_DIAG_EXIT_BOOTLOADER = 0x0EF0

FLASH_LINE_BOOT_ENTRY_FAILURE = 0x01
FLASH_LINE_BOOT_ENTRY_NO_BL_PRESENT = 0x02
FLASH_LINE_BOOT_ENTRY_OP_UNSAFE = 0x03

def bootentry_str(code):
    if code == FLASH_LINE_BOOT_ENTRY_FAILURE:
        return 'Entry failure'
    elif code == FLASH_LINE_BOOT_ENTRY_NO_BL_PRESENT:
        return 'No bootloader present'
    elif code == FLASH_LINE_BOOT_ENTRY_OP_UNSAFE:
        return 'Operation unsafe'
    return 'INVALID'

FLASH_LINE_PAGE_WRITE_SUCCESS = 0x00
FLASH_LINE_PAGE_WRITE_FAILURE = 0x01
FLASH_LINE_PAGE_NOT_WRITTEN = 0x02

def writestatus_str(code):
    if code == FLASH_LINE_PAGE_WRITE_SUCCESS:
        return 'success'
    elif code == FLASH_LINE_PAGE_WRITE_FAILURE:
        return 'failure'
    elif code == FLASH_LINE_PAGE_NOT_WRITTEN:
        return 'not-written'
    return 'INVALID'
