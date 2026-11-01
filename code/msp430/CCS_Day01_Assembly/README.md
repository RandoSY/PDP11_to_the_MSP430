# Day One assembly 1 kHz timer

Import this project folder into CCS, build Debug and use the G2ET eZ-FET. It contains the original `signal_1khz.asm` from the Day One lab board package, with its own reset vector and MSP430G2553 linker configuration. It is a separate image from the book's C timer project.

The source configures P1.6/TA0.1 for nominal 1 kHz using the factory 1 MHz calibration; it stops if either calibration byte is erased. Compare its source, listing, map and measurement with `CCS_01_Timer` for labs 04–05. Confirm the G2ET pin mapping and common ground independently: the J2 numbering in source comments refers to the earlier custom lab board, not the G2ET. Build succeeded with CCS 20.4.1; target upload and measurement remain unverified.

See [Meet the Pico W frequency meter](../../../instruments/pico_w_frequency_meter/README.md) for the companion instrument and measurement procedure.
