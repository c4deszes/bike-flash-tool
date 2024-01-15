Command-line interface
======================

Command
-------

.. code-block:: bash

    line-flash-tool --port <port> [--target <target> | --serial <serial> | --all] [--config <config> | --file <path>] [--network <path> | --baudrate <baudrate>]

Options
-------

Configuration
-------------

The configuration file associates binary files 

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
    line-flash-tool network.json --port COM4 --target RotorSensor --file RotorSensor-1.0.0.hex

    # Use case 2: flashing standalone target with known serial number, first time flashing
    line-flash-tool --port COM4 --serial 0x69696969 --file RotorSensor-1.0.0.hex --baudrate 19200

    # Use case 3: flashing all devices on the network
    line-flash-tool network.json --port COM4 --config config.json --all
