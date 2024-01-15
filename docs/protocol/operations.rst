Operations
==========

Enter bootloader
----------------

Master requests ``0x0E1X``, the peripheral then responds with the serial number if it's
able to enter bootloader mode. If not, an error code according to the table below is returned:

.. list-table:: Boot entry error codes
    :header-rows: 1

    * - Code
      - Description

    * - ``0x01``
      - No bootloader is present in the device

    * - ``0x02``
      - Operation is unsafe, e.g: movement detected.

Master sends conditional change address request with the serial number and a free diagnostic address.
A device already using that address but not having the right serial number will unassign itself.

The master then polls the peripheral's status using ``0x020X`` after the ``bootEntryTime`` has
elapsed, if the peripheral has not entered either ``BOOT`` or ``BOOT_ERROR`` mode then we consider
the flashing procedure to have failed.

Read signature
--------------

Master requests ``0x0E6X``, the peripheral then responds with the device signature.

The signature follows a structure:

* Microcontroller identifier, max. 20 characters, null terminated string
* Microcontroller revision, integer/character, 16 bit
* Bootloader version
* Bootloader variant
* Application version
* Application variant

Write page
----------

Master requests ``0x0E8X`` with the page data (128 bytes + 4 byte (address)).

Application write status
------------------------

Master requests ``0x0EAX``, the peripheral then responds with the last write operation's status

* 0x00: OK
* 0x01: Write failure
* 0x02: Addressing error

Exit bootloader
---------------

Master sends ``0x0EFX``, the peripheral shall enter application mode (or reset then enter
the application).

Later the master will poll the peripheral's operational status, if it's still boot or boot error
then the master assumes that something went wrong (e.g.: incorrect application) and then read it's
signature.

Standard diagnostics
--------------------

In bootloader mode the peripherals shall respond to the following diagnostic requests:

* Operation status
* SW version, and the version shall be the Application software version
* Serial number
