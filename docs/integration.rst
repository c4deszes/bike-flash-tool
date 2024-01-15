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
        LINE_Transport_Init(true);
        LINE_App_Init();
        LINE_Diag_Init(address);
        LINE_FLASH_Init(LINE_FLASH_APPLICATION_MODE);
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

.. code-block:: c

    void BOOT_Init() {
        LINE_Transport_Init(true);
        LINE_Diag_Init(address);
        LINE_FLASH_Init(LINE_FLASH_APPLICATION_MODE);
    }

    fl_BootSignature_t* FLASH_BL_ReadSignature(void) {

    }

    void FLASH_BL_OnPageWrite(uint32_t address, uint8_t* data) {
        NVM_Write(address / 128, data);

        writeStatus = LINE_FLASH_PAGE_WRITE_SUCCESS;
    }

    uint8_t FLASH_BL_GetWriteStatus(void) {
        return writeStatus;
    }

CPM
---