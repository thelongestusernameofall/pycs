# pycs
Python Based ARM CoreSight Debug and Trace Tools

 * PyCS is a python based JTAG/SWD debugger for ARM chips.
 * Its current focus is systems using Cortex-M ARM CPUs.
 * It reads the SoC SVD files to give full peripheral/register decodes for a wide variety of Cortex-M based chips.

## What do I need?
 * A PC with Python installed [host system](https://github.com/deadsy/pycs/blob/master/docs/host.md)
 * A target system with a Cortex-M ARM cpu [targets](https://github.com/deadsy/pycs/blob/master/docs/targets.md)
 * An SWD debug interface [debug interfaces](https://github.com/deadsy/pycs/blob/master/docs/debug_itf.md)

## Installing the tool
  * Run "make" - this will build the ARM disassembler that uses C code.
  * Run "./pycs" in the same directory you extracted the code to.
  * If you don't have permissions to access USB devices you can fix that (with a udev rules file) or run with "sudo ./pycs"

## Current Targets

    $ ./pycs -l
    supported targets:
      frdm_k64f : FRDM-K64F Kinetis Development Board (MK64FN1M0VLL12)
      mb1035b   : STM32F3 Discovery Board (STM32F303xC)
      mb997c    : STM32F4 Discovery Board (STM32F407xx)
      nRF51822  : Adafruit BLE USB dongle (nRF51822)
      nRF52dk   : Nordic nRF52DK Development Board (nRF52832)
      saml21    : Atmel SAM L21 Xplained Pro Evaluation Board (ATSAML21J18B)
      tepo      : Teenage Engineering Pocket Operator (EFM32LG890F128)

## Using the Tool

    $ ./pycs -t mb997c

    pycs: ARM CoreSight Tool 1.0
    STM32F407xx: compiling ./vendor/st/svd/STM32F40x.svd.gz
    ST-Link usb 0483:3748 serial u"H\xffj\x06PuIU'3\x04\x87"
    target voltage 2.889V

    mb997c*>

It has an interactive CLI.
 * '?' for menu help
 * '?' for command completion/argument help
 * TAB for command completion
 * 'help' for general help

## Features
 * display memory
 * disassemble memory
 * display system control registers
 * display peripheral registers
 * halt/go the cpu
 * program flash
 * measure counter frequencies
 * etc. etc.

## Other Documents

 * [HOWTO hookup development boards](https://github.com/deadsy/pycs/blob/master/docs/hookup.md)
