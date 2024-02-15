from line_protocol.protocol import LineMaster, LineTransportTimeout
from .constants import *
import time
import logging
import intelhex

logger = logging.getLogger(__name__)

class FlashTool:

    def __init__(self, master: LineMaster) -> None:
        self.master = master

    def enter_bootloader(self, boot_address: int, app_address: int = None, serial_number: int = None) -> int:
        """
        Puts a target into boot mode

        When app_address is provided the DIAG_BOOT_ENTRY request will be sent, otherwise the
        target is expected to be in boot mode already.

        With either app_address or serial_number the target's diagnostic address will be set,
        otherwise it has to be set beforehand.

        Error is raised if the boot entry is rejected or the target isn't in boot or boot error mode
        at the end.

        :param boot_address: _description_
        :type boot_address: int
        :param app_address: Application diagnostic address, defaults to None
        :type app_address: int, optional
        :param serial_number: _description_, defaults to None
        :type serial_number: int, optional
        :raises RuntimeError: _description_
        :return: _description_
        :rtype: int
        """
        if app_address is not None:
            try:
                response = self.master.request(FLASH_LINE_DIAG_BOOT_ENTRY | app_address)
                if len(response) == 4:
                    received_serial = int.from_bytes(response, 'little')
                    if serial_number != None and received_serial != serial_number:
                        logger.warning("Provided serial number doesn't match the peripheral's serial (Node=%02X)", app_address)
                    serial_number = received_serial
                    logger.info("Bootloader entry success, node=%01X, serial=%08X", app_address, serial_number)
                else:
                    reason = bootentry_str(response[0])
                    logger.error("Bootloader entry rejected (%s)", reason)

                    # TODO: custom error type, message improvement
                    raise RuntimeError("Bootloader entry rejected.")

                time.sleep(0.5) # TODO: wait boot entry time
            except LineTransportTimeout:
                logger.info("Bootloader entry no response.")

        if serial_number:
            self.master.conditional_change_address(serial_number, boot_address)

        op_status = self.master.get_operation_status(boot_address)

        if op_status != 'boot' and op_status != 'boot_error':
            logger.error("Bootloader didn't enter.")
            # TODO: custom error type, message improvement
            raise RuntimeError("didn't enter")

        return boot_address

    def write_page(self, address: int, data_address: int, data: list):
        logger.info("Writing %08X to %08X", data_address, data_address + len(data))
        self.master.send_data(FLASH_LINE_DIAG_APP_WRITE_PAGE | address, list(int.to_bytes(data_address, 4, 'little')) + data)

    def get_write_status(self, address: int):
        response = self.master.request(FLASH_LINE_DIAG_APP_WRITE_STATUS | address)
        logger.info("Write status %s", writestatus_str(response[0]))

        return response[0]

    def exit_bootloader(self, address: int, verify: bool=True):
        self.master.send_data(FLASH_LINE_DIAG_EXIT_BOOTLOADER | address, [])
        logger.info("Exiting bootloader.")

        if verify:
            time.sleep(1)   # TODO: wait boot exit time
            op_status = self.master.get_operation_status(address)

            if op_status == 'boot' or op_status == 'boot_error':
                logger.error("Bootloader didn't exit.")
                # TODO: custom error type, message improvement
                raise RuntimeError("Boot didn't exit.")

    def flash_hex(self, address: int, path: str, page_size: int = 64, write_time: float = 0.100):
        binary = intelhex.IntelHex(path)
        for (start, stop) in binary.segments():
            current_address = start
            while current_address < stop:
                step_size = min(stop - current_address,                         # Capping to end address
                                page_size - (current_address % page_size),      # Capping to nearest page boundary
                                page_size)                                      # Capping to page size
                data = list(binary.tobinarray(start=current_address, size=step_size))

                self.write_page(address, current_address, data)
                time.sleep(write_time)

                # TODO: maybe add the ability to retry writes, unless it's address failure
                if self.get_write_status(address) != FLASH_LINE_PAGE_WRITE_SUCCESS:
                    logger.error("Error writing page (0x%08X)", current_address)
                    # TODO: custom error type, message improvement
                    raise RuntimeError('Error writing page.')

                current_address += step_size
        pass
