# CCS GPIO starter for the MSP-EXP430G2ET

This ready-to-import CCS project builds a copy of the book's `02_gpio_switch.c` example for the MSP430G2553. It was generated and built with CCS 20.4.1 and TI MSP430 compiler 21.6.1.LTS. A physical upload or debug session has not yet been tested.

1. Open Code Composer Studio with MSP430 device support and the TI MSP430 compiler installed.
2. Use CCS's **Import Project** action and select this `CCS_GPIO_Starter` folder. The project has its own `.project`, `.cproject`, `.ccsproject`, device linker file and eZ-FET target configuration. Menu names can vary with CCS version.
3. Select the project and build its **Debug** configuration. The program in `02_gpio_switch.c` is a project-local copy; editing it does not change the original in the parent directory.
4. Connect the G2ET's eZ-FET USB port with a data cable. Check target power and debug jumpers using the [TI board guide](https://www.ti.com/lit/ug/slau772a/slau772a.pdf). Start a CCS debug session for the project; it will attempt to program the MCU and connect to it. This replaces existing firmware.
5. Set a breakpoint at the `if ((P2IN & BIT0) == 0)` line. Run or step and inspect `P2IN` and `P1OUT` in the debugger. The code enables an internal pull-up on P2.0; a momentary switch from P2.0 to ground should change the P1.0 output. Check the board's LED polarity and jumper configuration before interpreting the result.

To try another standalone example, replace the project-local C file with the desired example; include only one file defining `main`. The separate sensor modules require an application and timing verification. Breakpoints halt the CPU, so do not use stopped execution to judge signal timing.
