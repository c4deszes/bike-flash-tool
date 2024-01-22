from typing import Literal, List, Union, TYPE_CHECKING
from types import SimpleNamespace
import logging
import argparse
import sys
import time

from line_protocol.network import load_network
from line_flash.flash import FlashTool
from line_flash.config import load_config, ConfigEntry
from line_protocol.protocol.master import LineMaster
from line_protocol.protocol.transport import LineSerialTransport, LineTransportTimeout

logger = logging.getLogger(__name__)

def lookup_serial(entries, serial):
    next(next(x for x in entries if x.serial == serial), None)

def lookup_target(entries, target):
    next(next(x for x in entries if x.node == target), None)

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', required=True)

    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument('--target', type=str, dest='target')
    target_group.add_argument('--serial', type=lambda x: int(x, base=0), dest='target')
    target_group.add_argument('--all', action='store_const')

    config_group = parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument('--config', type=str)
    config_group.add_argument('--file', type=str)

    network_group = parser.add_mutually_exclusive_group(required=True)
    network_group.add_argument('--network')
    network_group.add_argument('--baudrate')

    args = parser.parse_args()

    if args.network:
        network = load_network(args.network)
        baudrate = network.baudrate
    else:
        baudrate = args.baudrate

    if args.config:
        config = load_config(args.config)

    with LineSerialTransport(args.port, baudrate=baudrate, one_wire=True) as transport:
        master = LineMaster(transport)
        flash_tool = FlashTool(master)

        if args.all:
            # for every device
            if args.config:
                logger.info("Not implemented.")
                return 1
            else:
                logger.error("Unable to flash all without configuration.")
                return 1
        elif isinstance(args.target, str):
            if args.network:
                node = network.get_node(args.target)
                if args.config:
                    entry = lookup_target(config)
                    flash_tool.enter_bootloader(node.address, node.address, entry.serial if entry else None)
                    flash_tool.flash_hex(node.address, entry.file)
                else:
                    flash_tool.enter_bootloader(node.address, node.address)
                    flash_tool.flash_hex(node.address, args.file)
            elif args.config:
                entry = lookup_target(config)
                if entry is None:
                    logger.error("No target found in config.")
                    return 1
                # find free address for the device
                flash_tool.enter_bootloader(0xE, serial_number=entry.serial)
                flash_tool.flash_hex(0xE, args.file)
            else:
                logger.error('Unable to determine target parameters.')
                return 1
        elif isinstance(args.target, int):
            # find node based on serial
            if args.config:
                entry = lookup_serial(config, args.target)
                if entry is None:
                    logger.error("No target found in config.")
                    return 1
                if args.network:
                    node = network.get_node(args.target)
                    flash_tool.enter_bootloader(node.address, node.address, entry.serial if entry else None)
                    flash_tool.flash_hex(node.address, entry.file)
                else:
                    # find free address for the device
                    flash_tool.enter_bootloader(0xE, serial_number=entry.serial)
                    flash_tool.flash_hex(0xE, entry.file)
            else:
                flash_tool.enter_bootloader(0xE, serial_number=args.target)
                flash_tool.flash_hex(0xE, args.file)

    return 0

if __name__ == '__main__':
    sys.exit(main())
