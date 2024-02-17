Command-line interface
======================

Command
-------

.. code-block:: bash

    line-flash-tool --port <port> [--target <target> | --serial <serial> | --all] [--config <config> | --file <path>] [--network <path> | --baudrate <baudrate>]

Options
-------

**--port** : Serial port to use

Target selection
~~~~~~~~~~~~~~~~

**--target**: Target node to flash, if config is provided then it's primarily looked up there,
              otherwise the node in the network config is used.

**--serial**: The target's serial number.

**--all**: Targets all nodes to be flashed, only valid with config provided.

File selection
~~~~~~~~~~~~~~

**--config**: Path to a configuration file, see :ref:`Configuration`

**--file**: Path to a file to flash

Network settings
~~~~~~~~~~~~~~~~

**--network**: Path to the network description file

**--baudrate**: Communication speed

Configuration
-------------

The configuration file associates nodes to binary files. Providing the serial number is also useful
as it allows flashing targets that don't have a diagnostic address assigned like the ones bootloader
mode.

The file path is relative to the configuration file.

.. code-block:: json

    [
        {
            "node": "RotorSensor",
            "serial": "0x69696969",
            "file": "RotorSensor-1.0.0-release.hex"
        },
        {
            "node": "RearLight",
            "serial": "0x12345678",
            "file": "RearLight-1.2.0-debug.hex"
        }
    ]

Examples
--------

.. code-block:: bash

    # Use case 1: flashing single target on the network
    line-flash --port COM4 --target RotorSensor --file RotorSensor-1.0.0.hex --network network.json

    # Use case 2: flashing standalone target with known serial number, first time flashing
    line-flash --port COM4 --serial 0x69696969 --file RotorSensor-1.0.0.hex --baudrate 19200

    # Use case 3: flashing all devices on the network
    line-flash --port COM4 --config config.json --all --network network.json
