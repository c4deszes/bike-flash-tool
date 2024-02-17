from line_flash.flash import FlashTool
from line_protocol.protocol.master import LineMaster
from line_protocol.protocol.transport import LineSerialTransport
import logging

logging.basicConfig(level=logging.DEBUG)

with LineSerialTransport('COM4', baudrate=19200, one_wire=True) as transport:
    master = LineMaster(transport)
    flash_tool = FlashTool(master)

    addr = 0x06

    master.wakeup()
    flash_tool.enter_bootloader(boot_address=addr,
                                app_address=addr,
                                serial_number=0xABCDEF01)
    master.get_software_version(addr)
    flash_tool.flash_hex(addr, 'program.hex')
    flash_tool.exit_bootloader(addr)
