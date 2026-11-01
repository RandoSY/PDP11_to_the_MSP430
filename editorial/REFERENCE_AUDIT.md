# Reference audit and editorial provenance

This is an independently authored educational textbook, not a historical reproduction or an officially approved product from DEC, TI, Raspberry Pi, Robert Krten, or Analog Devices. Historical exposition and technical examples are original; primary references should be consulted for engineering decisions.

## Historical foundation

1. DEC, *Introduction to RSX-11M*, version 3.1 (December 1977), Chapter 2, “RSX-11M Applications.” The chapter discusses process inputs and outputs, steel rolling mills, oil refineries, data acquisition, and feedback control. [Bitsavers copy](https://bitsavers.trailing-edge.com/pdf/dec/pdp11/rsx11m_s/RSX11M_V3.1_Dec77/1A_System_Reference_Information/AA-2555C-TC_Introduction_to_RSX-11M_3.1_Dec77.pdf)
2. DEC, *PDP-11 Processor Handbook* and *PDP-11 Peripherals Handbook*. See the editions indexed at [Bitsavers PDP-11](https://bitsavers.org/pdf/dec/pdp11/). Processor and peripherals differed by model and year; the book discusses the family rather than a specific installed factory machine.
3. Jonathan Kirwan, “A Perspective on the MSP-430 Instructions and Addressing Modes,” 18 July 2003. Comparative interpretation supplied by the reader. RISC/CISC classifications are attributed views rather than settled taxonomy. The instruction-set kinship does not prove documented direct design descent.

## Modern target documentation

4. TI, *MSP430F2xx/MSP430G2xx Family User's Guide*, SLAU144: [TI PDF](https://www.ti.com/lit/ug/slau144/slau144.pdf). CPU, constant generator, Timer_A, USART/USCI and GPIO.
5. TI, *MSP430G2553 Datasheet*: [TI datasheet](https://www.ti.com/lit/ds/symlink/msp430g2553.pdf). Pin functions, electrical operating range, device package and resource limits.
6. TI, *MSP-EXP430G2ET LaunchPad User Guide*: [TI](https://www.ti.com/lit/ug/slau772/slau772.pdf). Debugger-side pin connection and eZ-FET configuration.
7. Analog Devices, *DS18B20 Programmable Resolution 1-Wire Digital Thermometer*, Rev. 6: [Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf). Protocol, scratchpad format, resolution, CRC, and timing. Full time-slot verification requires physical observation.

## Source provenance

The original user's October 29, 2026 *MSP430 Teacher & Operator Guide* provided the practical Day One architecture, custom-board connection assumptions, and a planned DS18B20 trajectory. Those pre-existing project files are referenced rather than reproduced in the book archive, which contains the new educational examples and testing source. The custom board's physical assembly and the current Pico firmware were not reverified during this publication process.

## What is not claimed

No peer-reviewed historical monograph certification, full 2026 industrial standards conformity, actual execution on a PDP-11, target build on MSP430G2553, calibrated Pico timebase, verified GPS traceability, or measured DS18B20 1-Wire bus behavior is claimed.
