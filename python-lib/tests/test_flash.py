import pytest
import os
from unittest.mock import Mock

from line_flash import FlashTool
from line_flash.flash import FlashBootException, FlashWriteException
from line_flash.constants import (FLASH_LINE_BOOT_ENTRY_NO_BL_PRESENT, FLASH_LINE_PAGE_WRITE_SUCCESS,
                                  FLASH_LINE_PAGE_WRITE_FAILURE)
from line_protocol.protocol import LineMaster

class TestFlashBootEntry():

    @pytest.fixture
    def line_master(self):
        mock = Mock(spec=LineMaster)
        return mock

    @pytest.fixture
    def flash_tool(self, line_master):
        return FlashTool(line_master)

    def test_EnterBootloader_InBootModeAddressed(self, flash_tool, line_master):
        line_master.get_operation_status.return_value = 'boot'

        flash_tool.enter_bootloader(0x06)

    def test_EnterBootloader_InBootModeWithSerial(self, flash_tool, line_master):
        line_master.get_operation_status.return_value = 'boot'

        line_master.request.return_value = [0] * 4  # Mocking a response with length 4
        flash_tool.enter_bootloader(0x06, serial_number=0x12345678)

        line_master.conditional_change_address.assert_called_with(0x12345678, 0x06)

    def test_EnterBootloader_AppMode(self, flash_tool, line_master):
        line_master.get_operation_status.return_value = 'boot'
        line_master.request.return_value = [0x78, 0x56, 0x34, 0x12]

        flash_tool.enter_bootloader(boot_address=0x06, app_address=0x06, serial_number=0x12345678)

        line_master.conditional_change_address.assert_called_once_with(0x12345678, 0x06)

    def test_EnterBootloader_AppModeRejected(self, flash_tool, line_master):
        line_master.request.return_value = [FLASH_LINE_BOOT_ENTRY_NO_BL_PRESENT]

        with pytest.raises(FlashBootException):
            flash_tool.enter_bootloader(0x06, app_address=0x06)

    def test_EnterBootloader_NotEntering(self, flash_tool, line_master):
        line_master.get_operation_status.return_value = 'ok'

        with pytest.raises(FlashBootException):
            flash_tool.enter_bootloader(0x06)

class TestFlashBootExit:

    @pytest.fixture
    def line_master(self):
        mock = Mock(spec=LineMaster)
        return mock

    @pytest.fixture
    def flash_tool(self, line_master):
        return FlashTool(line_master)

    def test_ExitBootloader_ExitNoVerify(self, flash_tool, line_master):
        flash_tool.exit_bootloader(0x06, verify=False)

    def test_ExitBootloader_ExitVerifySuccess(self, flash_tool, line_master):
        line_master.get_operation_status.return_value = 'ok'

        flash_tool.exit_bootloader(0x06, 0x06, verify=True)

    def test_ExitBootloader_ExitVerifyFailure(self, flash_tool, line_master):
        line_master.get_operation_status.return_value = 'boot'

        with pytest.raises(FlashBootException):
            flash_tool.exit_bootloader(0x06, 0x06, verify=True)

class TestFlashWriteHex:

    @pytest.fixture
    def line_master(self):
        mock = Mock(spec=LineMaster)
        return mock

    @pytest.fixture
    def flash_tool(self, line_master):
        return FlashTool(line_master)
    
    @pytest.fixture
    def hex_path(self):
        return os.path.join(os.path.dirname(__file__), 'data', 'segmented.hex')

    def test_FlashHex_Segmenting(self, flash_tool, line_master, hex_path):
        line_master.request.return_value = [FLASH_LINE_PAGE_WRITE_SUCCESS]
        
        flash_tool.flash_hex(0x06, hex_path, write_time=0.001)

        # TODO: assert calls

    def test_FlashHex_WriteFailure(self, flash_tool, line_master, hex_path):
        line_master.request.side_effect = [
            [FLASH_LINE_PAGE_WRITE_SUCCESS],
            [FLASH_LINE_PAGE_WRITE_SUCCESS],
            [FLASH_LINE_PAGE_WRITE_FAILURE]
        ]

        with pytest.raises(FlashWriteException):
            flash_tool.flash_hex(0x06, hex_path, write_time=0.001)
