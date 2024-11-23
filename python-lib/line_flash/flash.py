from line_protocol.protocol import LineMaster, LineTransportTimeout
from .constants import *
from typing import List
import time
import logging
import intelhex

logger = logging.getLogger(__name__)

class FlashBootException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class FlashWriteException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class FlashTool:

    def __init__(self, master: LineMaster) -> None:
        self.master = master

    def boot_entry(self, address: int, serial_number: int):
        """
        Puts a target into boot mode

        :param address: Diagnostic address in boot mode
        :type address: int
        :param app_address: Application diagnostic address
        :type app_address: int
        :param serial_number: Serial number of the target
        :type serial_number: int
        """
        response = self.master.request(FLASH_LINE_DIAG_BOOT_ENTRY | address)

        if len(response) == 4:
            received_serial = int.from_bytes(response, 'little')
            if serial_number != None and received_serial != serial_number:
                logger.warning("Provided serial number doesn't match the peripheral's serial (Node=%02X)", address)
            serial_number = received_serial
            logger.info("Bootloader entry success, node=%01X, serial=%08X", address, serial_number)

            return serial_number
        elif len(response) == 1:
            reason = bootentry_str(response[0])
            logger.error("Bootloader entry rejected (%s)", reason)

            raise FlashBootException(f"Bootloader entry rejected ({reason}).")
        else:
            logger.error("Bootloader entry response invalid.")

            raise FlashBootException(f"Boot entry response invalid ({response}).")

    def enter_bootloader(self, boot_address: int, app_address: int = None, serial_number: int = None):
        """
        Puts a target into boot mode

        When app_address is provided the DIAG_BOOT_ENTRY request will be sent, otherwise the
        target is expected to be in boot mode already.

        With either app_address or serial_number the target's diagnostic address will be set,
        otherwise it has to be set beforehand.

        Error is raised if the boot entry is rejected or the target isn't in boot or boot error mode
        at the end.

        :param boot_address: Diagnostic address in boot mode
        :type boot_address: int
        :param app_address: Application diagnostic address, defaults to None
        :type app_address: int, optional
        :param serial_number: Serial number of the target, defaults to None
        :type serial_number: int, optional
        :raises RuntimeError: When boot mode is not successfully entered at the end
        """
        try:
            if app_address is not None:
                serial_number = self.boot_entry(app_address, serial_number)
                time.sleep(1.0) # TODO: wait boot entry time
        except LineTransportTimeout:
            logger.info("Bootloader entry no response.")

        if serial_number is not None:
            self.master.conditional_change_address(serial_number, boot_address)
            time.sleep(0.1)

            if app_address is None:
                try:
                    self.boot_entry(boot_address, serial_number)
                    time.sleep(1.0)
                    self.master.conditional_change_address(serial_number, boot_address)
                except LineTransportTimeout:
                    logger.info("Bootloader entry no response.")

        op_status = self.master.get_operation_status(boot_address)

        if op_status != 'boot' and op_status != 'boot_error':
            logger.error("Bootloader didn't enter.")
            # TODO: custom error type, message improvement
            raise FlashBootException("Bootloader didn't enter")

    def write_page(self, address: int, data_address: int, data: List[int]):
        """
        Writes a page

        :param address: Diagnostic address
        :type address: int
        :param data_address: Starting address of the data
        :type data_address: int
        :param data: Data array
        :type data: List[int]
        """
        logger.info("Writing %08X to %08X", data_address, data_address + len(data))
        self.master.send_data(FLASH_LINE_DIAG_APP_WRITE_PAGE | address, list(int.to_bytes(data_address, 4, 'little')) + data)

    def get_write_status(self, address: int) -> int:
        """
        Returns the write status of the last page write operation

        :param address: Diagnostic address
        :type address: int
        :return: Write status code
        :rtype: int
        """
        response = self.master.request(FLASH_LINE_DIAG_APP_WRITE_STATUS | address)
        # TODO: what if the response has 0 length or 2+?
        logger.info("Write status %s", writestatus_str(response[0]))

        return response[0]

    def exit_bootloader(self, boot_address: int, app_address: int = None, verify: bool=True, exit_time: float = 1.0):
        """
        Puts a target into application mode

        When verify is enabled the target's state after exit_time is 

        :param boot_address: Diagnostic address of the target
        :type boot_address: int
        :param app_address: Diagnostic address of the target in application mode
        :type app_address: int
        :param verify: When True verifies that the target has entered application mode, defaults to True
        :type verify: bool, optional
        :param exit_time: Time to wait for the target to enter app. mode, defaults to 1.0
        :type exit_time: float, optional
        :raises RuntimeError: If the target has not entered application mode
        """
        self.master.send_data(FLASH_LINE_DIAG_EXIT_BOOTLOADER | boot_address, [])
        logger.info("Exiting bootloader.")

        if app_address != None and verify:
            time.sleep(exit_time)
            op_status = self.master.get_operation_status(app_address)

            if op_status == 'boot' or op_status == 'boot_error':
                logger.error("Bootloader didn't exit.")
                # TODO: custom error type, message improvement
                raise FlashBootException("Boot didn't exit.")

    def hex_size(self, path: str) -> int:
        """
        Returns the size of the IntelHex file

        :param path: Path to the Hex file
        :type path: str
        :return: Size of the file
        :rtype: int
        """
        binary = intelhex.IntelHex(path)
        size = 0
        for (start, stop) in binary.segments():
            size += stop - start
        return size

    def flash_hex(self, address: int, path: str, page_size: int = 64, write_time: float = 0.100, on_progess=None):
        """
        Writes the given IntelHex file to the target using the write_page function.

        The function goes through the segments in the file therefore to avoid unnecessary erasures
        and writes the file should have minimal gaps. The segments are broken up into write
        operations that will ideally line up with the page boundaries of the target, parts that
        are offset will result in non-aligned writes.

        :param address: Diagnostic address of the target
        :type address: int
        :param path: Path to the Hex file
        :type path: str
        :param page_size: Write operations will use up to this many bytes in a single call, defaults to 64
        :type page_size: int, optional
        :param write_time: Amount of time to wait in between write operations, defaults to 0.100
        :type write_time: float, optional
        :raises RuntimeError: If there was an error writing a page
        """
        binary = intelhex.IntelHex(path)
        size = self.hex_size(path)
        progress = 0
        for (start, stop) in binary.segments():
            current_address = start
            while current_address < stop:
                step_size = min(stop - current_address,                         # Capping to end address
                                page_size - (current_address % page_size),      # Capping to nearest page boundary
                                page_size)                                      # Capping to page size
                data = list(binary.tobinarray(start=current_address, size=step_size))

                self.write_page(address, current_address, data)
                time.sleep(write_time)
                progress += step_size

                if (on_progess):
                    on_progess(size, progress, current_address, step_size)

                # TODO: maybe add the ability to retry writes, unless it's address failure
                if self.get_write_status(address) != FLASH_LINE_PAGE_WRITE_SUCCESS:
                    logger.error("Error writing page (0x%08X)", current_address)
                    # TODO: custom error type, message improvement
                    raise FlashWriteException('Error writing page.')

                current_address += step_size
        pass
