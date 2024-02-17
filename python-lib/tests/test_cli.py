import sys
from unittest.mock import patch
import pytest
import os

from line_flash.cli import main

class TestCliMiscellanious:

    @pytest.mark.parametrize('command', [
        ['line-flash', '-h'],
        ['line-flash', '--help']
    ])
    def test_HelpCommand(self, command):
        with pytest.raises(SystemExit) as exit_ex, patch.object(sys, 'argv', command):
            main()
        assert exit_ex.value.code == 0

flash_config_path = os.path.join(os.path.dirname(__file__), "data", "flash-config.json")
network_config_path = os.path.join(os.path.dirname(__file__), "data", "network.json")

class TestCliWithTarget:

    def test_Target_Config_Network(self):
        pass

    def test_Target_Config_Baudrate(self):
        pass

    def test_Target_File_Network(self):
        pass

    def test_Target_File_Baudrate(self):
        # invalid combination, cannot resolve node id's or serial number
        pass

class TestCliWithSerialNumber:

    # TODO: error cases for each
    #  - files not found
    #  - invalid baudrate

    def test_Serial_File_Baudrate(self):
        pass

    @pytest.mark.skip("Use case not relevant at the moment")
    def test_Serial_Config_Baudrate(self):
        pass

    @pytest.mark.skip("Use case not relevant at the moment")
    def test_Serial_Config_Network(self):
        pass

    @pytest.mark.skip("Use case not relevant at the moment")
    def test_Serial_File_Network(self):
        pass

class TestCliWithAll():

    def test_All_Config_Network(self):
        pass

    def test_All_Config_Baudrate(self):
        pass

    def test_All_File_Network(self):
        # invalid combination
        pass

    def test_All_File_Baudrate(self):
        # invalid combination
        pass
