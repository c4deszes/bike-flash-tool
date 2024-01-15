Flow
----

> 0x0E13 00 12 34 56
  - Node 3 entering Bootloader (returned serial number)
...
  - Waiting for entry
> 0x01E0 0A 00 12 34 56
  - Setting the node with the given serial number to ID 0A
> 0x020A 40
  - Requesting operation status of 0A, responds with Bootloader mode
> 0x0E6A A T S A M D 2 1 E 1 8 A 0 0 0 0 0 0  A 0  1 2 6 FF FF FF
  - Reading BL signature, response contains MCU type, revision, BL version, APP version
> 0x0E8A 00 80 00 00 FFFFFFFF FFFFFFFF FFFFFFFF ...
  - Writing page with data
> 0x0EAA 00
  - Page write success
> 0x0E8A 00 80 01 00 FFFFFFFF FFFFFFFF FFFFFFFF ...
  - Writing page with data
> 0x0EAA 01
  - Page write failure
