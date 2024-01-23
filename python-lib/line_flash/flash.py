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
        if app_address is None and serial_number is None:
            raise ValueError('Either application number or serial number must be provided.')

        if app_address is not None:
            try:
                response = self.master.request(FLASH_LINE_DIAG_BOOT_ENTRY | app_address)
                if len(response) == 4:
                    received_serial = int.from_bytes(response, 'little')
                    if received_serial != serial_number:
                        logger.warning("Provided serial number doesn't match the peripheral's serial (Node=%02X)", app_address)
                    serial_number = received_serial
                    logger.info("Bootloader entry success, node=%01X, serial=%08X", app_address, serial_number)
                else:
                    # TODO: decode error code
                    reason = bootentry_str(response[0])
                    logger.error("Bootloader entry rejected (%s)", reason)

                time.sleep(0.5) # TODO: wait boot entry time
            except LineTransportTimeout:
                logger.info("Bootloader entry no response.")
        # TODO: if serial number is None then we cannot continue

        self.master.conditional_change_address(serial_number, boot_address)

        # TODO: expect bootloader or boot error state
        op_status = self.master.get_operation_status(boot_address)
        self.master.get_software_version(boot_address)

        if op_status != 'boot' and op_status != 'boot_error':
            logger.error("Bootloader didn't enter.")
            # TODO: error type, message improvement
            raise RuntimeError("didn't enter")

        return boot_address

    def read_signature(self, address: int):
        pass

    def write_page(self, address: int, data_address: int, data: list):
        logger.info("Writing %08X to %08X", data_address, data_address + len(data))
        self.master.send_data(FLASH_LINE_DIAG_APP_WRITE_PAGE | address, list(int.to_bytes(data_address, 4, 'little')) + data)

    def get_write_status(self, address: int):
        response = self.master.request(FLASH_LINE_DIAG_APP_WRITE_STATUS | address)
        # TODO: decode response
        logger.info("Write status %s", writestatus_str(response[0]))

    def exit_bootloader(self, address: int):
        self.master.send_data(FLASH_LINE_DIAG_EXIT_BOOTLOADER | address, [0x00])
        logger.info("Exiting bootloader.")

    def flash_hex(self, address: int, path: str):
        binary = intelhex.IntelHex(path)
        for (start, stop) in binary.segments():
            current_address = start
            while current_address < stop:
                step_size = min(stop - current_address, 128 - (current_address % 128), 128)
                data = list(binary.tobinarray(start=current_address, size=step_size))

                self.write_page(address, current_address, data)
                time.sleep(1)
                self.get_write_status(address)
                time.sleep(1)

                current_address += step_size
        pass
