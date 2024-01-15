Questions and answers
=====================

* How do we allow safe flashing while the network is under use?

    * The peripheral may reject the boot entry request if it determines it would be unsafe to
      conduct flashing, e.g.: bike is moving

    * During flashing the master should change the active schedule to a lower rate one,
      e.g.: message previously sent at 100ms can be sent at 1000ms rate, this might trigger certain
      behavior (e.g.: timeout) in certain devices but it's better than not sending the message at
      all.

* How do we verify that the peripheral's operation has not been compromised?

    * Before reentering application mode the tool checks signatures, versions

    * After reentering application mode the master can check whether responses are received, the
      operation mode can also tell if the peripheral is stuck in boot mode

* Do we support product operation while being flashed?

    * Generally no, but with hardware measures in place the product could continue to work during
      the resets.

* How do we distinguish between devices that don't respond (e.g.: cable issue) and those stuck in
  bootloader mode?

    * Peripherals stuck in bootloader mode can be addressed via diagnostics, while a disconnected
      device will not respond to such requests.

* How to make sure that binaries don't get mixed up?

    * This would mostly be a problem on devices that use the same microcontroller and bootloader,
      on such devices we should consider the possibility of mixing up binaries and the possible
      effects of this (e.g.: a pin that's normally an input being driven high/low)

* How is the application flashed the first time?

    * Without a valid application the bootloader would stay in boot mode where it listens to
      diagnostic commands, the user would need to know the serial number of the device to be able to
      set the device's address.

* How do peripherals deal with unintentional boot mode entry?

    * Bootloader should timeout if requests relevant to flashing are not received in time.
